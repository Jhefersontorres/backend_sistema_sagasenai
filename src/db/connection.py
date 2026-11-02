import os
import re
import sqlite3

import mysql.connector
import psycopg
from psycopg.rows import dict_row, tuple_row

from src.config import settings


class PostgreSQLConnection:
    dialect = "postgresql"

    def __init__(self, database_url):
        try:
            self._connection = psycopg.connect(database_url)
        except psycopg.ProgrammingError as error:
            parser_error = str(error).lower()
            if "invalid percent-encoded token" in parser_error:
                reason = "invalid percent escape in a URI component"
            elif "invalid uri query parameter" in parser_error:
                reason = "invalid URI query parameter"
            else:
                reason = "PostgreSQL rejected the URI syntax"
            raise RuntimeError(
                f"DATABASE_URL is invalid: {reason}. Check its URI format and "
                "URL-encode special characters in the credentials."
            ) from None

    def cursor(self, dictionary=False):
        row_factory = dict_row if dictionary else tuple_row
        return PostgreSQLCursor(
            self._connection.cursor(row_factory=row_factory),
        )

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        self._connection.close()


class PostgreSQLCursor:
    INSERT_ID_COLUMNS = {
        "usuario": "id_usuario",
        "escuderia": "id_escuderia",
        "avaliacao": "id_avaliacao",
        "divulgacao": "id_divulgacao",
        "resultado": "id_resultado",
    }

    def __init__(self, cursor):
        self._cursor = cursor
        self._insert_id_column = None

    @property
    def lastrowid(self):
        if self._insert_id_column is None:
            return None

        id_column = self._insert_id_column
        row = self._cursor.fetchone()
        self._insert_id_column = None
        if row is None:
            return None
        if isinstance(row, dict):
            return row[id_column]
        return row[0]

    def execute(self, operation, parameters=None):
        match = re.match(
            r"\s*INSERT\s+INTO\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            operation,
            flags=re.IGNORECASE,
        )
        self._insert_id_column = None
        if match:
            table = match.group(1).lower()
            id_column = self.INSERT_ID_COLUMNS.get(table)
            if id_column and not re.search(
                r"\bRETURNING\b",
                operation,
                flags=re.IGNORECASE,
            ):
                operation = f"{operation.rstrip().rstrip(';')} RETURNING {id_column}"
                self._insert_id_column = id_column

        if parameters is None:
            return self._cursor.execute(operation)
        return self._cursor.execute(operation, parameters)

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def close(self):
        self._cursor.close()


class SQLiteCursor:
    def __init__(self, cursor, *, dictionary=False):
        self._cursor = cursor
        self._dictionary = dictionary

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    def execute(self, operation, parameters=None):
        operation = re.sub(r"\s+FOR UPDATE\b", "", operation, flags=re.IGNORECASE)
        operation = operation.replace("%s", "?")
        if parameters is None:
            return self._cursor.execute(operation)
        return self._cursor.execute(operation, parameters)

    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None or not self._dictionary:
            return row
        return dict(row)

    def fetchall(self):
        rows = self._cursor.fetchall()
        if not self._dictionary:
            return rows
        return [dict(row) for row in rows]

    def close(self):
        self._cursor.close()


class SQLiteConnection:
    dialect = "sqlite"

    def __init__(self, database_path):
        os.makedirs(os.path.dirname(os.path.abspath(database_path)), exist_ok=True)
        self._connection = sqlite3.connect(database_path, timeout=30)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")

    def cursor(self, dictionary=False):
        return SQLiteCursor(self._connection.cursor(), dictionary=dictionary)

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        self._connection.close()


def get_connection():
    if settings.DB_DRIVER == "sqlite":
        return SQLiteConnection(settings.DB_SQLITE_PATH)
    if settings.DB_DRIVER in {"postgres", "postgresql", "supabase"}:
        if not settings.DATABASE_URL:
            raise RuntimeError(
                "DATABASE_URL is required when DB_DRIVER is PostgreSQL."
            )
        return PostgreSQLConnection(settings.DATABASE_URL)
    if settings.DB_DRIVER != "mysql":
        raise RuntimeError(
            "DB_DRIVER must be 'mysql', 'postgresql', or 'sqlite'."
        )

    required = {
        "DB_HOST": settings.DB_HOST,
        "DB_USER": settings.DB_USER,
        "DB_NAME": settings.DB_NAME,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(
            "Database configuration is incomplete: "
            + ", ".join(missing)
        )

    if settings.APP_ENV == "test" and not settings.DB_NAME.startswith("test_"):
        raise RuntimeError(
            "DB_TEST_NAME must start with 'test_' to protect non-test databases."
        )

    return mysql.connector.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
    )