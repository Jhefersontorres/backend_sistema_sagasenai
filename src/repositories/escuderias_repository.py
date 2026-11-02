from src.db.connection import get_connection
from src.db.resources import managed_connection, managed_cursor


def _buscar_ou_criar_mentor(cursor, nome_mentor: str):
    cursor.execute(
        """
        SELECT usuario.id_usuario
        FROM usuario
        JOIN tipousuario ON usuario.id_tipousuario = tipousuario.id_tipousuario
        WHERE usuario.nome = %s AND tipousuario.descricao = 'MENTOR'
        """,
        (nome_mentor,),
    )
    existente = cursor.fetchone()
    if existente:
        return existente["id_usuario"]

    cursor.execute(
        "SELECT id_tipousuario FROM tipousuario WHERE descricao = 'MENTOR'"
    )
    tipo_mentor = cursor.fetchone()
    if tipo_mentor is None:
        raise RuntimeError("O tipo de usuário MENTOR não está configurado.")

    cursor.execute(
        "INSERT INTO usuario (id_tipousuario, nome) VALUES (%s, %s)",
        (tipo_mentor["id_tipousuario"], nome_mentor),
    )
    return cursor.lastrowid


def buscar_ou_criar_mentor(nome_mentor: str):
    with managed_connection(get_connection) as conn:
        with managed_cursor(conn, dictionary=True) as cursor:
            id_mentor = _buscar_ou_criar_mentor(cursor, nome_mentor)
        conn.commit()
        return id_mentor


def criar_escuderia(
    nome: str,
    turma: str,
    nome_mentor: str,
    curso: str,
    etapa: str,
    periodo: str,
    escola: str,
):
    with managed_connection(get_connection) as conn:
        with managed_cursor(conn, dictionary=True) as cursor:
            id_mentor = _buscar_ou_criar_mentor(cursor, nome_mentor)
            cursor.execute(
                """
                INSERT INTO escuderia (
                    nome_escuderia,
                    turma,
                    id_mentor,
                    curso,
                    etapa,
                    periodo,
                    escola
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (nome, turma, id_mentor, curso, etapa, periodo, escola),
            )
            novo_id = cursor.lastrowid
        conn.commit()
        return novo_id


def listar_escuderias():
    with managed_connection(get_connection) as conn:
        with managed_cursor(conn, dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT
                    escuderia.id_escuderia,
                    escuderia.nome_escuderia,
                    escuderia.turma,
                    usuario.nome AS nome_mentor,
                    escuderia.curso,
                    escuderia.etapa,
                    escuderia.periodo,
                    escuderia.escola
                FROM escuderia
                JOIN usuario ON escuderia.id_mentor = usuario.id_usuario
                """
            )
            return cursor.fetchall()


def listar_escuderias_avaliadas(id_avaliador: int):
    query = """
        SELECT
            e.id_escuderia,
            e.nome_escuderia,
            e.turma,
            u.nome AS mentor,
            e.curso,
            e.etapa,
            e.periodo,
            e.escola,
            COUNT(DISTINCT a.id_criterio) AS criterios_avaliados,
            (SELECT COUNT(*) FROM criterio) AS total_criterios,
            CASE
                WHEN COUNT(DISTINCT a.id_criterio) = (SELECT COUNT(*) FROM criterio)
                THEN 'concluida'
                ELSE 'em_andamento'
            END AS status
        FROM avaliacao a
        INNER JOIN escuderia e ON e.id_escuderia = a.id_escuderia
        LEFT JOIN usuario u ON u.id_usuario = e.id_mentor
        WHERE a.id_avaliador = %s
        GROUP BY
            e.id_escuderia,
            e.nome_escuderia,
            e.turma,
            u.nome,
            e.curso,
            e.etapa,
            e.periodo,
            e.escola
        ORDER BY e.nome_escuderia
    """

    with managed_connection(get_connection) as conn:
        with managed_cursor(conn, dictionary=True) as cursor:
            cursor.execute(query, (id_avaliador,))
            return cursor.fetchall()
