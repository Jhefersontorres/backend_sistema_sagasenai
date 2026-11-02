from src.db.connection import get_connection
from src.db.resources import managed_connection, managed_cursor


def listar_avaliadores():
    with managed_connection(get_connection) as conn:
        with managed_cursor(conn, dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT usuario.id_usuario, usuario.nome
                FROM usuario
                JOIN tipousuario ON usuario.id_tipousuario = tipousuario.id_tipousuario
                WHERE tipousuario.descricao = 'AVALIADOR'
                """
            )
            return cursor.fetchall()


def obter_avaliador(id_avaliador: int):
    with managed_connection(get_connection) as conn:
        with managed_cursor(conn, dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT usuario.id_usuario, usuario.nome
                FROM usuario
                JOIN tipousuario
                    ON usuario.id_tipousuario = tipousuario.id_tipousuario
                WHERE usuario.id_usuario = %s
                    AND tipousuario.descricao = 'AVALIADOR'
                """,
                (id_avaliador,),
            )
            return cursor.fetchone()
