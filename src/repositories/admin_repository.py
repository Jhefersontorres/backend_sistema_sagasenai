from src.core.exceptions import ResourceInUseError, ResourceNotFoundError
from src.db.connection import get_connection
from src.db.resources import managed_connection, managed_cursor


def criar_avaliador(nome: str):
    with managed_connection(get_connection) as conn:
        with managed_cursor(conn, dictionary=True) as cursor:
            cursor.execute(
                "SELECT id_tipousuario FROM tipousuario WHERE descricao = 'AVALIADOR'"
            )
            tipo_avaliador = cursor.fetchone()
            if tipo_avaliador is None:
                raise RuntimeError("O tipo de usuário AVALIADOR não está configurado.")

            cursor.execute(
                "INSERT INTO usuario (id_tipousuario, nome) VALUES (%s, %s)",
                (tipo_avaliador["id_tipousuario"], nome),
            )
            id_avaliador = cursor.lastrowid
        conn.commit()
        return {"id_usuario": id_avaliador, "nome": nome}


def atualizar_avaliador(id_avaliador: int, nome: str):
    with managed_connection(get_connection) as conn:
        with managed_cursor(conn, dictionary=True) as cursor:
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
                "UPDATE usuario SET nome = %s WHERE id_usuario = %s",
                (nome, id_avaliador),
            )
        conn.commit()
        return {"id_usuario": id_avaliador, "nome": nome}


def excluir_avaliador(id_avaliador: int):
    with managed_connection(get_connection) as conn:
        with managed_cursor(conn, dictionary=True) as cursor:
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
                "SELECT COUNT(*) AS total FROM avaliacao WHERE id_avaliador = %s",
                (id_avaliador,),
            )
            if cursor.fetchone()["total"]:
                raise ResourceInUseError("Avaliador")

            cursor.execute(
                "SELECT COUNT(*) AS total FROM escuderia WHERE id_mentor = %s",
                (id_avaliador,),
            )
            if cursor.fetchone()["total"]:
                raise ResourceInUseError("Avaliador")

            cursor.execute(
                "DELETE FROM usuario WHERE id_usuario = %s",
                (id_avaliador,),
            )
        conn.commit()


def criar_criterio(descricao: str):
    with managed_connection(get_connection) as conn:
        with managed_cursor(conn, dictionary=True) as cursor:
            cursor.execute(
                "INSERT INTO criterio (descricao) VALUES (%s)",
                (descricao,),
            )
            id_criterio = cursor.lastrowid
            cursor.execute(
                "SELECT id_criterio, descricao, peso FROM criterio WHERE id_criterio = %s",
                (id_criterio,),
            )
            criterio = cursor.fetchone()
        conn.commit()
        return criterio


def atualizar_criterio(id_criterio: int, descricao: str):
    with managed_connection(get_connection) as conn:
        with managed_cursor(conn, dictionary=True) as cursor:
            cursor.execute(
                "SELECT id_criterio FROM criterio WHERE id_criterio = %s FOR UPDATE",
                (id_criterio,),
            )
            if cursor.fetchone() is None:
                raise ResourceNotFoundError("Critério")

            cursor.execute(
                "UPDATE criterio SET descricao = %s WHERE id_criterio = %s",
                (descricao, id_criterio),
            )
            cursor.execute(
                "SELECT id_criterio, descricao, peso FROM criterio WHERE id_criterio = %s",
                (id_criterio,),
            )
            criterio = cursor.fetchone()
        conn.commit()
        return criterio


def excluir_criterio(id_criterio: int):
    with managed_connection(get_connection) as conn:
        with managed_cursor(conn, dictionary=True) as cursor:
            cursor.execute(
                "SELECT id_criterio FROM criterio WHERE id_criterio = %s FOR UPDATE",
                (id_criterio,),
            )
            if cursor.fetchone() is None:
                raise ResourceNotFoundError("Critério")

            cursor.execute(
                "SELECT COUNT(*) AS total FROM avaliacao WHERE id_criterio = %s",
                (id_criterio,),
            )
            if cursor.fetchone()["total"]:
                raise ResourceInUseError("Critério")

            cursor.execute(
                "DELETE FROM criterio WHERE id_criterio = %s",
                (id_criterio,),
            )
        conn.commit()
