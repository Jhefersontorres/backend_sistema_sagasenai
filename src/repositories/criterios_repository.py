from src.db.connection import get_connection
from src.db.resources import managed_connection, managed_cursor


def listar_criterios():
    with managed_connection(get_connection) as conn:
        with managed_cursor(conn, dictionary=True) as cursor:
            cursor.execute("SELECT * FROM criterio")
            return cursor.fetchall()
