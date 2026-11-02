import asyncio
import json
import unittest
from unittest.mock import patch

import psycopg
from fastapi import Request
from pydantic import ValidationError
from fastapi.security import HTTPAuthorizationCredentials
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.exceptions import (
    DuplicateEvaluationError,
    EvaluationClosedError,
)
from src.config import _normalize_database_url
from src.db.connection import PostgreSQLConnection, PostgreSQLCursor
from src.db.resources import managed_connection, managed_cursor
from src.main import application_error_handler, http_error_handler
from src.models import (
    AdminLogin,
    AvaliacaoCreate,
    AvaliadorCode,
    AvaliadorSessionCreate,
    EscuderiaCreate,
)
from src.routes.avaliacoes import cadastrar_avaliacao
from src.routes.escuderias import obter_escuderias_avaliadas
from src.routes.usuarios import (
    criar_sessao_avaliador,
    validar_codigo_avaliador,
)
from src.security.avaliadores import (
    gerar_token_evento,
    gerar_token_sessao_avaliador,
    validar_sessao_avaliador,
    validar_token_evento,
    verificar_codigo_avaliador,
)


def create_request() -> Request:
    return Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/",
            "raw_path": b"/",
            "query_string": b"",
            "headers": [],
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
        }
    )


class DatabaseUrlConfigTests(unittest.TestCase):
    def test_database_url_removes_accidental_environment_assignment_prefix(self):
        uri = "postgresql://user:password@db.example:6543/postgres"
        self.assertEqual(
            _normalize_database_url(f"DATABASE_URL={uri}"),
            uri,
        )

    def test_database_url_keeps_normal_uri_unchanged(self):
        uri = "postgresql://user:password@db.example:6543/postgres"
        self.assertEqual(_normalize_database_url(uri), uri)


class PostgreSQLCursorTests(unittest.TestCase):
    def test_invalid_connection_string_error_does_not_expose_credentials(self):
        private_value = "private%credential"
        with patch(
            "src.db.connection.psycopg.connect",
            side_effect=psycopg.ProgrammingError(
                f'invalid percent-encoded token: "{private_value}"'
            ),
        ), self.assertLogs("src.db.connection", level="ERROR") as logs:
            with self.assertRaises(RuntimeError) as error:
                PostgreSQLConnection(
                    f"postgresql://user:{private_value}@db.example/postgres"
                )

        self.assertIn("invalid percent escape", str(error.exception))
        self.assertNotIn(private_value, str(error.exception))
        self.assertIn("invalid percent escape", logs.output[0])
        self.assertNotIn(private_value, logs.output[0])
        self.assertIn("has_malformed_percent_escape=True", logs.output[0])
        self.assertIn("has_password=True", logs.output[0])

    def test_invalid_connection_string_error_uses_safe_fallback_reason(self):
        private_value = "private-credential"
        with patch(
            "src.db.connection.psycopg.connect",
            side_effect=psycopg.ProgrammingError(
                f'connection URI contains invalid content: "{private_value}"'
            ),
        ):
            with self.assertRaises(RuntimeError) as error:
                PostgreSQLConnection(
                    f"postgresql://user:{private_value}@db.example/postgres"
                )

        self.assertIn(
            "PostgreSQL rejected the URI syntax",
            str(error.exception),
        )
        self.assertNotIn(private_value, str(error.exception))

    class FakeCursor:
        def __init__(self, row):
            self.row = row
            self.operation = None
            self.parameters = None

        def execute(self, operation, parameters=None):
            self.operation = operation
            self.parameters = parameters

        def fetchone(self):
            row = self.row
            self.row = None
            return row

        def fetchall(self):
            return []

        def close(self):
            pass

    def test_insert_returns_generated_id_for_repository_compatibility(self):
        cursor = self.FakeCursor((42,))
        postgres_cursor = PostgreSQLCursor(cursor)

        postgres_cursor.execute(
            "INSERT INTO escuderia (nome_escuderia) VALUES (%s)",
            ("Equipe",),
        )

        self.assertIn("RETURNING id_escuderia", cursor.operation)
        self.assertEqual(cursor.parameters, ("Equipe",))
        self.assertEqual(postgres_cursor.lastrowid, 42)
        self.assertIsNone(postgres_cursor.lastrowid)

    def test_insert_id_supports_dictionary_rows(self):
        cursor = self.FakeCursor({"id_usuario": 17})
        postgres_cursor = PostgreSQLCursor(cursor)

        postgres_cursor.execute(
            "INSERT INTO usuario (nome) VALUES (%s)",
            ("Avaliador",),
        )

        self.assertEqual(postgres_cursor.lastrowid, 17)


class RequestSchemaTests(unittest.TestCase):
    def test_evaluation_accepts_notes_from_zero_through_ten(self):
        for nota in (0, 5.5, 10):
            with self.subTest(nota=nota):
                dados = AvaliacaoCreate(
                    id_escuderia=1,
                    id_criterio=3,
                    nota=nota,
                )
                self.assertEqual(dados.nota, nota)

    def test_evaluation_rejects_invalid_notes_and_ids(self):
        for nota in (-0.01, 10.01, float("nan"), float("inf")):
            with self.subTest(nota=nota):
                with self.assertRaises(ValidationError):
                    AvaliacaoCreate(
                        id_escuderia=1,
                        id_criterio=3,
                        nota=nota,
                    )

        with self.assertRaises(ValidationError):
            AvaliacaoCreate(
                id_escuderia=0,
                id_criterio=3,
                nota=5,
            )

    def test_team_fields_cannot_be_blank(self):
        with self.assertRaises(ValidationError):
            EscuderiaCreate(
                nome="  ",
                turma="T1",
                nome_mentor="Mentor",
                curso="Curso",
                etapa="1",
                periodo="Matutino",
                escola="Escola",
            )

    def test_team_requires_academic_details(self):
        dados = EscuderiaCreate(
            nome="Equipe",
            turma="T1",
            nome_mentor="Mentor",
            curso="Administração",
            etapa="1ª etapa",
            periodo="Matutino",
            escola="Escola SENAI",
        )
        self.assertEqual(dados.curso, "Administração")
        self.assertEqual(dados.etapa, "1ª etapa")
        self.assertEqual(dados.periodo, "Matutino")
        self.assertEqual(dados.escola, "Escola SENAI")

        with self.assertRaises(ValidationError):
            EscuderiaCreate(
                nome="Equipe",
                turma="T1",
                nome_mentor="Mentor",
                curso="Curso",
                etapa="",
                periodo="Matutino",
                escola="Escola",
            )

    def test_evaluation_request_does_not_accept_identity_field(self):
        dados = AvaliacaoCreate.model_validate(
            {
                "id_escuderia": 1,
                "id_avaliador": 999,
                "id_criterio": 3,
                "nota": 8,
            }
        )
        self.assertFalse(hasattr(dados, "id_avaliador"))

    def test_evaluation_route_uses_identity_from_signed_session(self):
        dados = AvaliacaoCreate(
            id_escuderia=4,
            id_criterio=9,
            nota=8.5,
        )
        with patch(
            "src.routes.avaliacoes.criar_avaliacao_service",
            return_value=22,
        ) as create_evaluation:
            response = cadastrar_avaliacao(
                dados,
                {"id_avaliador": 17},
            )

        create_evaluation.assert_called_once_with(4, 17, 9, 8.5, None)
        self.assertEqual(response["id_avaliacao"], 22)

    def test_shared_event_code_requires_a_long_nonblank_value(self):
        with self.assertRaises(ValidationError):
            AvaliadorCode(codigo="1234")
        with self.assertRaises(ValidationError):
            AvaliadorCode(codigo="            ")

    def test_admin_code_requires_a_long_value(self):
        with self.assertRaises(ValidationError):
            AdminLogin(codigo="1234")


class ErrorResponseTests(unittest.IsolatedAsyncioTestCase):
    async def test_business_errors_include_existing_detail_and_stable_code(self):
        casos = (
            (EvaluationClosedError(), 403, "evaluations_closed"),
            (DuplicateEvaluationError(), 400, "duplicate_evaluation"),
        )

        for erro, status_code, code in casos:
            with self.subTest(code=code):
                response = await application_error_handler(
                    create_request(),
                    erro,
                )
                body = json.loads(response.body)
                self.assertEqual(response.status_code, status_code)
                self.assertEqual(body["detail"], str(erro))
                self.assertEqual(body["code"], code)

    async def test_http_errors_keep_detail_and_include_status_code(self):
        response = await http_error_handler(
            create_request(),
            StarletteHTTPException(
                status_code=401,
                detail="Acesso administrativo não autorizado.",
            ),
        )

        body = json.loads(response.body)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            body["detail"],
            "Acesso administrativo não autorizado.",
        )
        self.assertEqual(body["code"], "http_401")


class EvaluatorTokenTests(unittest.TestCase):
    def setUp(self):
        self.secret_patch = patch(
            "src.security.signed_tokens.settings.ADMIN_TOKEN_SECRET",
            "test-token-signing-secret-with-at-least-32-characters",
        )
        self.secret_patch.start()
        self.addCleanup(self.secret_patch.stop)

    def test_event_token_can_only_be_used_for_choosing_evaluator(self):
        event_token = gerar_token_evento()
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=event_token,
        )
        self.assertEqual(validar_token_evento(credentials)["tipo"], "evento")

        with self.assertRaises(StarletteHTTPException) as context:
            validar_sessao_avaliador(credentials)
        self.assertEqual(context.exception.status_code, 403)

    def test_evaluator_token_binds_identity_and_cannot_be_rebound(self):
        evaluator_token = gerar_token_sessao_avaliador(27)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=evaluator_token,
        )
        self.assertEqual(validar_sessao_avaliador(credentials)["id_avaliador"], 27)

        with self.assertRaises(StarletteHTTPException) as context:
            validar_token_evento(credentials)
        self.assertEqual(context.exception.status_code, 403)

    def test_tampered_evaluator_token_is_rejected(self):
        evaluator_token = gerar_token_sessao_avaliador(27) + "tampered"
        with self.assertRaises(StarletteHTTPException) as context:
            validar_sessao_avaliador(
                HTTPAuthorizationCredentials(
                    scheme="Bearer",
                    credentials=evaluator_token,
                )
            )
        self.assertEqual(context.exception.status_code, 401)

    def test_token_signing_refuses_weak_server_secret(self):
        with patch(
            "src.security.signed_tokens.settings.ADMIN_TOKEN_SECRET",
            "short",
        ):
            with self.assertRaises(RuntimeError):
                gerar_token_evento()

    def test_shared_code_is_compared_against_server_configuration(self):
        configured_code = "event-code-with-at-least-32-characters"
        with patch(
            "src.security.avaliadores.settings.AVALIADOR_CODIGO",
            configured_code,
        ):
            self.assertTrue(verificar_codigo_avaliador(configured_code))
            self.assertFalse(verificar_codigo_avaliador("other-code"))

    def test_shared_code_refuses_weak_server_configuration(self):
        with patch("src.security.avaliadores.settings.AVALIADOR_CODIGO", "short-code"):
            with self.assertRaises(RuntimeError):
                verificar_codigo_avaliador("short-code")

    def test_event_login_mints_short_lived_event_token(self):
        code = "event-code-with-at-least-32-characters"
        with (
            patch(
                "src.routes.usuarios.verificar_codigo_evento",
                return_value=True,
            ),
            patch(
                "src.routes.usuarios.gerar_token_evento",
                return_value="signed-event-token",
            ),
        ):
            response = validar_codigo_avaliador(AvaliadorCode(codigo=code))
        self.assertEqual(response["token"], "signed-event-token")

    def test_session_issues_token_for_existing_evaluator(self):
        with (
            patch(
                "src.routes.usuarios.obter_avaliador_service",
                return_value={"id_usuario": 27, "nome": "Evaluator"},
            ),
            patch(
                "src.routes.usuarios.gerar_token_sessao_avaliador",
                return_value="signed-evaluator-token",
            ) as create_token,
        ):
            response = criar_sessao_avaliador(
                AvaliadorSessionCreate(id_avaliador=27),
                {"tipo": "evento"},
            )

        create_token.assert_called_once_with(27)
        self.assertEqual(response["id_avaliador"], 27)
        self.assertEqual(response["token"], "signed-evaluator-token")

    def test_evaluator_cannot_read_another_evaluators_progress(self):
        with self.assertRaises(StarletteHTTPException) as context:
            obter_escuderias_avaliadas(
                28,
                {"tipo": "avaliador", "id_avaliador": 27},
            )
        self.assertEqual(context.exception.status_code, 403)


class DatabaseResourceTests(unittest.TestCase):
    class FakeCursor:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    class FakeConnection:
        def __init__(self):
            self.closed = False
            self.rolled_back = False
            self.created_cursor = None

        def cursor(self, *, dictionary=False):
            self.created_cursor = DatabaseResourceTests.FakeCursor()
            return self.created_cursor

        def rollback(self):
            self.rolled_back = True

        def close(self):
            self.closed = True

    def test_connection_and_cursor_close_after_success(self):
        connection = self.FakeConnection()
        with managed_connection(lambda: connection) as managed:
            with managed_cursor(managed, dictionary=True) as cursor:
                self.assertIs(cursor, connection.created_cursor)
                self.assertFalse(cursor.closed)

        self.assertTrue(connection.created_cursor.closed)
        self.assertTrue(connection.closed)

    def test_connection_rolls_back_and_closes_after_failure(self):
        connection = self.FakeConnection()

        with self.assertRaisesRegex(ValueError, "query failed"):
            with managed_connection(lambda: connection):
                raise ValueError("query failed")

        self.assertTrue(connection.rolled_back)
        self.assertTrue(connection.closed)


if __name__ == "__main__":
    unittest.main()
