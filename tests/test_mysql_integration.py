import os
import unittest
from datetime import datetime

from src.config import settings
from src.core.exceptions import DuplicateEvaluationError, EvaluationClosedError
from src.db.connection import get_connection
from src.repositories.avaliacoes_repository import criar_avaliacao
from src.repositories.ranking_repository import (
    atualizar_divulgacao,
    salvar_snapshot_ranking,
)


@unittest.skipUnless(
    os.getenv("APP_ENV", "").lower() == "test",
    "Set APP_ENV=test and DB_TEST_* variables to enable MySQL integration tests.",
)
class EvaluationRepositoryIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not settings.DB_NAME or not settings.DB_NAME.startswith("test_"):
            raise RuntimeError(
                "MySQL integration tests require DB_TEST_NAME to start with 'test_'."
            )

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES LIKE 'alembic_version'")
        if cursor.fetchone() is None:
            cursor.close()
            connection.close()
            raise RuntimeError(
                "Apply migrations to the isolated test database before running integration tests."
            )

        cursor.execute("SELECT version_num FROM alembic_version")
        version = cursor.fetchone()
        cursor.close()
        connection.close()
        if not version or version[0] != "20260930_03":
            raise RuntimeError(
                "Upgrade the isolated test database to the latest migration before testing."
            )

    def setUp(self):
        self.connection = get_connection()
        self.extra_disclosure_ids = []
        cursor = self.connection.cursor()

        cursor.execute(
            "INSERT INTO tipousuario (descricao) VALUES (%s)",
            ("INTEGRATION_TEST",),
        )
        self.type_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO usuario (id_tipousuario, nome) VALUES (%s, %s)",
            (self.type_id, "Test Mentor"),
        )
        self.mentor_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO usuario (id_tipousuario, nome) VALUES (%s, %s)",
            (self.type_id, "Test Evaluator"),
        )
        self.evaluator_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO escuderia (id_mentor, nome_escuderia, turma)
            VALUES (%s, %s, %s)
            """,
            (self.mentor_id, "Integration Team", "TEST"),
        )
        self.team_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO criterio (descricao) VALUES (%s)",
            ("Integration criterion",),
        )
        self.criterion_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO divulgacao (mostrar_resultado, data_divulgacao)
            VALUES (%s, %s)
            """,
            (False, datetime.now()),
        )
        self.disclosure_id = cursor.lastrowid

        self.connection.commit()
        cursor.close()

    def tearDown(self):
        cursor = self.connection.cursor()
        cursor.execute(
            "DELETE FROM avaliacao WHERE id_escuderia = %s",
            (self.team_id,),
        )
        cursor.execute(
            "DELETE FROM resultado WHERE id_escuderia = %s",
            (self.team_id,),
        )
        cursor.execute(
            "DELETE FROM divulgacao WHERE id_divulgacao = %s",
            (self.disclosure_id,),
        )
        for id_divulgacao in self.extra_disclosure_ids:
            cursor.execute(
                "DELETE FROM divulgacao WHERE id_divulgacao = %s",
                (id_divulgacao,),
            )
        cursor.execute(
            "DELETE FROM escuderia WHERE id_escuderia = %s",
            (self.team_id,),
        )
        cursor.execute(
            "DELETE FROM criterio WHERE id_criterio = %s",
            (self.criterion_id,),
        )
        cursor.execute(
            "DELETE FROM usuario WHERE id_usuario IN (%s, %s)",
            (self.mentor_id, self.evaluator_id),
        )
        cursor.execute(
            "DELETE FROM tipousuario WHERE id_tipousuario = %s",
            (self.type_id,),
        )
        self.connection.commit()
        cursor.close()
        self.connection.close()

    def create_evaluation(self):
        return criar_avaliacao(
            self.team_id,
            self.evaluator_id,
            self.criterion_id,
            8.5,
            "Integration test comment",
        )

    def test_saves_evaluation_and_rejects_duplicate(self):
        evaluation_id = self.create_evaluation()
        self.assertGreater(evaluation_id, 0)

        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT nota, comentario FROM avaliacao WHERE id_avaliacao = %s",
            (evaluation_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        self.assertEqual(float(row[0]), 8.5)
        self.assertEqual(row[1], "Integration test comment")

        with self.assertRaises(DuplicateEvaluationError):
            self.create_evaluation()

    def test_rejects_evaluation_after_results_are_published(self):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE divulgacao
            SET mostrar_resultado = %s
            WHERE id_divulgacao = %s
            """,
            (True, self.disclosure_id),
        )
        self.connection.commit()
        cursor.close()

        with self.assertRaises(EvaluationClosedError):
            self.create_evaluation()

    def test_snapshot_publishes_and_scopes_duplicate_score_to_disclosure(self):
        self.create_evaluation()
        published_at = datetime.now()
        atualizar_divulgacao(True, published_at)

        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT nota_final FROM resultado WHERE id_divulgacao = %s AND id_escuderia = %s",
            (self.disclosure_id, self.team_id),
        )
        first_snapshot = cursor.fetchone()
        self.assertIsNotNone(first_snapshot)

        cursor.execute(
            """
            INSERT INTO divulgacao (mostrar_resultado, data_divulgacao)
            VALUES (%s, %s)
            """,
            (False, published_at),
        )
        second_disclosure_id = cursor.lastrowid
        self.extra_disclosure_ids.append(second_disclosure_id)
        self.connection.commit()
        cursor.close()

        salvar_snapshot_ranking(second_disclosure_id)

        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM resultado
            WHERE id_escuderia = %s
            """,
            (self.team_id,),
        )
        self.assertEqual(cursor.fetchone()[0], 2)
        cursor.close()


if __name__ == "__main__":
    unittest.main()
