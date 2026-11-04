import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.routing import APIRoute

from src.core.exceptions import ResourceInUseError
from src.db.connection import SQLiteConnection
from src.models import AvaliadorCreate, CriterioCreate, EscuderiaCreate
from src.repositories import admin_repository, escuderias_repository
from src.routes.admin import router as admin_router
from src.security.admin import validar_token_admin


class AdminRequestTests(unittest.TestCase):
    def test_management_endpoints_require_admin_authentication(self):
        routes = {
            route.path: route
            for route in admin_router.routes
            if isinstance(route, APIRoute) and route.path.startswith("/admin/")
        }
        managed_paths = (
            "/admin/escuderias",
            "/admin/escuderias/{id_escuderia}",
            "/admin/avaliadores",
            "/admin/avaliadores/{id_avaliador}",
            "/admin/criterios",
            "/admin/criterios/{id_criterio}",
        )
        for path in managed_paths:
            with self.subTest(path=path):
                route = routes[path]
                self.assertTrue(
                    any(
                        dependency.call is validar_token_admin
                        for dependency in route.dependant.dependencies
                    )
                )

    def test_admin_create_schema_accepts_trimmed_names(self):
        self.assertEqual(AvaliadorCreate(nome="  Ana  ").nome, "Ana")
        self.assertEqual(CriterioCreate(descricao="  Apresentação ").descricao, "Apresentação")
        self.assertEqual(
            EscuderiaCreate(
                nome=" Equipe ",
                turma=" T1 ",
                nome_mentor=" Mentor ",
                curso=" Curso ",
                etapa=" 1 ",
                periodo=" Matutino ",
                escola=" Escola ",
            ).nome,
            "Equipe",
        )


class AdminRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = str(Path(self.temp_dir.name) / "admin-test.sqlite3")
        self._create_schema()
        self.connections_patch = patch(
            "src.repositories.admin_repository.get_connection",
            side_effect=lambda: SQLiteConnection(self.database_path),
        )
        self.escuderias_connections_patch = patch(
            "src.repositories.escuderias_repository.get_connection",
            side_effect=lambda: SQLiteConnection(self.database_path),
        )
        self.connections_patch.start()
        self.escuderias_connections_patch.start()

    def tearDown(self):
        self.escuderias_connections_patch.stop()
        self.connections_patch.stop()
        self.temp_dir.cleanup()

    def _create_schema(self):
        connection = sqlite3.connect(self.database_path)
        try:
            connection.executescript(
                """
                PRAGMA foreign_keys = ON;
                CREATE TABLE tipousuario (
                    id_tipousuario INTEGER PRIMARY KEY,
                    descricao TEXT NOT NULL
                );
                CREATE TABLE usuario (
                    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_tipousuario INTEGER NOT NULL,
                    nome TEXT,
                    FOREIGN KEY (id_tipousuario)
                        REFERENCES tipousuario(id_tipousuario)
                );
                CREATE TABLE escuderia (
                    id_escuderia INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_mentor INTEGER NOT NULL,
                    nome_escuderia TEXT NOT NULL,
                    turma TEXT NOT NULL,
                    curso TEXT,
                    etapa TEXT,
                    periodo TEXT,
                    escola TEXT,
                    FOREIGN KEY (id_mentor) REFERENCES usuario(id_usuario)
                );
                CREATE TABLE criterio (
                    id_criterio INTEGER PRIMARY KEY AUTOINCREMENT,
                    descricao TEXT NOT NULL,
                    peso NUMERIC NOT NULL DEFAULT 0.25
                );
                CREATE TABLE avaliacao (
                    id_avaliacao INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_escuderia INTEGER NOT NULL,
                    id_avaliador INTEGER NOT NULL,
                    id_criterio INTEGER NOT NULL,
                    nota NUMERIC NOT NULL,
                    FOREIGN KEY (id_escuderia) REFERENCES escuderia(id_escuderia),
                    FOREIGN KEY (id_avaliador) REFERENCES usuario(id_usuario),
                    FOREIGN KEY (id_criterio) REFERENCES criterio(id_criterio)
                );
                CREATE TABLE divulgacao (
                    id_divulgacao INTEGER PRIMARY KEY AUTOINCREMENT,
                    mostrar_resultado BOOLEAN NOT NULL DEFAULT FALSE,
                    data_divulgacao TEXT NOT NULL
                );
                CREATE TABLE resultado (
                    id_resultado INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_escuderia INTEGER NOT NULL,
                    id_divulgacao INTEGER NOT NULL,
                    nota_final NUMERIC NOT NULL,
                    FOREIGN KEY (id_escuderia) REFERENCES escuderia(id_escuderia),
                    FOREIGN KEY (id_divulgacao) REFERENCES divulgacao(id_divulgacao)
                );
                INSERT INTO tipousuario (id_tipousuario, descricao)
                    VALUES (1, 'MENTOR'), (2, 'AVALIADOR');
                """
            )
        finally:
            connection.close()

    def _seed_assessment(self):
        evaluator_id = admin_repository.criar_avaliador("Avaliador")
        team_id = escuderias_repository.criar_escuderia(
            "Equipe",
            "T1",
            "Mentor",
            "Curso",
            "1",
            "Matutino",
            "Escola",
        )
        criterion = admin_repository.criar_criterio("Apresentação")
        connection = sqlite3.connect(self.database_path)
        try:
            connection.execute(
                """
                INSERT INTO avaliacao (id_escuderia, id_avaliador, id_criterio, nota)
                VALUES (?, ?, ?, ?)
                """,
                (team_id, evaluator_id["id_usuario"], criterion["id_criterio"], 8),
            )
            connection.commit()
        finally:
            connection.close()
        return team_id, evaluator_id["id_usuario"], criterion["id_criterio"]

    def test_team_update_changes_fields_without_replacing_evaluation_history(self):
        team_id = escuderias_repository.criar_escuderia(
            "Equipe", "T1", "Mentor", "Curso", "1", "Matutino", "Escola"
        )

        from src.services.escuderias_service import atualizar_escuderia_service

        atualizar_escuderia_service(
            team_id, "Equipe Atualizada", "T2", "Novo Mentor",
            "Engenharia", "2", "Noturno", "Outra Escola",
        )
        team = escuderias_repository.listar_escuderias()[0]
        self.assertEqual(team["nome_escuderia"], "Equipe Atualizada")
        self.assertEqual(team["turma"], "T2")
        self.assertEqual(team["nome_mentor"], "Novo Mentor")

    def test_team_cannot_be_deleted_when_it_has_assessment_history(self):
        team_id, _evaluator_id, _criterion_id = self._seed_assessment()

        with self.assertRaises(ResourceInUseError):
            escuderias_repository.excluir_escuderia(team_id)

        self.assertEqual(len(escuderias_repository.listar_escuderias()), 1)

    def test_team_cannot_be_deleted_when_it_has_published_results(self):
        team_id = escuderias_repository.criar_escuderia(
            "Equipe", "T1", "Mentor", "Curso", "1", "Matutino", "Escola"
        )
        connection = sqlite3.connect(self.database_path)
        try:
            cursor = connection.execute(
                """
                INSERT INTO divulgacao (mostrar_resultado, data_divulgacao)
                VALUES (1, '2026-01-01')
                """
            )
            connection.execute(
                """
                INSERT INTO resultado (id_escuderia, id_divulgacao, nota_final)
                VALUES (?, ?, ?)
                """,
                (team_id, cursor.lastrowid, 8),
            )
            connection.commit()
        finally:
            connection.close()

        with self.assertRaises(ResourceInUseError):
            escuderias_repository.excluir_escuderia(team_id)

    def test_unreferenced_evaluators_and_criteria_can_be_managed(self):
        evaluator = admin_repository.criar_avaliador("Avaliador")
        evaluator = admin_repository.atualizar_avaliador(
            evaluator["id_usuario"],
            "Avaliador atualizado",
        )
        self.assertEqual(evaluator["nome"], "Avaliador atualizado")
        admin_repository.excluir_avaliador(evaluator["id_usuario"])

        criterion = admin_repository.criar_criterio("Apresentação")
        criterion = admin_repository.atualizar_criterio(
            criterion["id_criterio"],
            "Apresentação atualizada",
        )
        self.assertEqual(criterion["descricao"], "Apresentação atualizada")
        admin_repository.excluir_criterio(criterion["id_criterio"])

    def test_evaluator_and_criterion_cannot_be_deleted_with_assessments(self):
        _team_id, evaluator_id, criterion_id = self._seed_assessment()

        with self.assertRaises(ResourceInUseError):
            admin_repository.excluir_avaliador(evaluator_id)
        with self.assertRaises(ResourceInUseError):
            admin_repository.excluir_criterio(criterion_id)
