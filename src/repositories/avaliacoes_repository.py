import sqlite3

import mysql.connector
import psycopg

from src.core.exceptions import (
    DuplicateEvaluationError,
    EvaluationClosedError,
    ResourceNotFoundError,
)
from src.db.connection import get_connection
from src.db.locks import disclosure_lock
from src.db.resources import managed_connection, managed_cursor


def criar_avaliacao(
    id_escuderia: int,
    id_avaliador: int,
    id_criterio: int,
    nota: float,
    comentario: str | None,
):
    try:
        with managed_connection(get_connection) as conn:
            with managed_cursor(conn, dictionary=True) as cursor:
                with disclosure_lock(conn):
                    cursor.execute(
                        """
                        SELECT mostrar_resultado
                        FROM divulgacao
                        ORDER BY id_divulgacao DESC
                        LIMIT 1
                        FOR UPDATE
                        """
                    )
                    divulgacao = cursor.fetchone()

                    if divulgacao and divulgacao["mostrar_resultado"]:
                        raise EvaluationClosedError()

                    cursor.execute(
                        """
                        SELECT usuario.id_usuario
                        FROM usuario
                        JOIN tipousuario
                            ON usuario.id_tipousuario = tipousuario.id_tipousuario
                        WHERE usuario.id_usuario = %s
                            AND tipousuario.descricao = 'AVALIADOR'
                        FOR UPDATE
                        """,
                        (id_avaliador,),
                    )
                    if cursor.fetchone() is None:
                        raise ResourceNotFoundError("Avaliador")

                    cursor.execute(
                        """
                        INSERT INTO avaliacao
                            (id_escuderia, id_avaliador, id_criterio, nota, comentario)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            id_escuderia,
                            id_avaliador,
                            id_criterio,
                            nota,
                            comentario,
                        ),
                    )
                    novo_id = cursor.lastrowid
                    conn.commit()
                return novo_id

    except (
        mysql.connector.errors.IntegrityError,
        psycopg.IntegrityError,
        sqlite3.IntegrityError,
    ) as erro:
        if isinstance(erro, sqlite3.IntegrityError):
            raise DuplicateEvaluationError() from erro

        if isinstance(erro, psycopg.IntegrityError):
            if (
                erro.sqlstate == "23505"
                and erro.diag.constraint_name
                == "uq_avaliacao_escuderia_avaliador_criterio"
            ):
                raise DuplicateEvaluationError() from erro
            raise

        if erro.errno == 1062:
            raise DuplicateEvaluationError() from erro
        raise
