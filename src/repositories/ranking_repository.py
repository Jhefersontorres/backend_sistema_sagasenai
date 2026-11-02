from src.db.connection import get_connection
from src.db.locks import disclosure_lock
from src.db.resources import managed_connection, managed_cursor


def obter_status_divulgacao():
    with managed_connection(get_connection) as conn:
        with managed_cursor(conn, dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT mostrar_resultado, data_divulgacao
                FROM divulgacao
                ORDER BY id_divulgacao DESC
                LIMIT 1
                """
            )
            return cursor.fetchone()


def calcular_ranking(connection=None):
    if connection is None:
        with managed_connection(get_connection) as conn:
            with managed_cursor(conn, dictionary=True) as cursor:
                linhas = _carregar_linhas_ranking(cursor)
    else:
        with managed_cursor(connection, dictionary=True) as cursor:
            linhas = _carregar_linhas_ranking(cursor)

    escuderias = {}
    for linha in linhas:
        id_escuderia = linha["id_escuderia"]
        if id_escuderia not in escuderias:
            escuderias[id_escuderia] = {
                "id_escuderia": id_escuderia,
                "nome_escuderia": linha["nome_escuderia"],
                "medias_criterios": [],
            }
        escuderias[id_escuderia]["medias_criterios"].append(
            float(linha["media_criterio"])
        )

    ranking = []
    for escuderia in escuderias.values():
        medias = escuderia["medias_criterios"]
        nota_final = sum(medias) / len(medias)
        ranking.append(
            {
                "id_escuderia": escuderia["id_escuderia"],
                "nome_escuderia": escuderia["nome_escuderia"],
                "nota_final": round(nota_final, 2),
            }
        )

    ranking.sort(key=lambda item: item["nota_final"], reverse=True)
    return ranking


def _carregar_linhas_ranking(cursor):
    cursor.execute(
        """
        SELECT
            escuderia.id_escuderia,
            escuderia.nome_escuderia,
            avaliacao.id_criterio,
            AVG(avaliacao.nota) AS media_criterio
        FROM avaliacao
        JOIN escuderia ON avaliacao.id_escuderia = escuderia.id_escuderia
        GROUP BY
            escuderia.id_escuderia,
            escuderia.nome_escuderia,
            avaliacao.id_criterio
        """
    )
    return cursor.fetchall()


def atualizar_divulgacao(mostrar_resultado: bool, data_divulgacao):
    with managed_connection(get_connection) as conn:
        with managed_cursor(conn) as cursor:
            try:
                with disclosure_lock(conn):
                    cursor.execute(
                        """
                        SELECT id_divulgacao
                        FROM divulgacao
                        ORDER BY id_divulgacao DESC
                        LIMIT 1
                        FOR UPDATE
                        """
                    )
                    existente = cursor.fetchone()

                    if existente:
                        id_divulgacao = existente[0]
                        cursor.execute(
                            """
                            UPDATE divulgacao
                            SET mostrar_resultado = %s, data_divulgacao = %s
                            WHERE id_divulgacao = %s
                            """,
                            (
                                mostrar_resultado,
                                data_divulgacao,
                                id_divulgacao,
                            ),
                        )
                    else:
                        cursor.execute(
                            """
                            INSERT INTO divulgacao
                                (mostrar_resultado, data_divulgacao)
                            VALUES (%s, %s)
                            """,
                            (mostrar_resultado, data_divulgacao),
                        )
                        id_divulgacao = cursor.lastrowid

                    if mostrar_resultado:
                        ranking = calcular_ranking(connection=conn)
                        _inserir_snapshot(cursor, id_divulgacao, ranking)

                    conn.commit()
            except Exception:
                conn.rollback()
                raise


def obter_desempenho_escuderia(id_escuderia: int):
    with managed_connection(get_connection) as conn:
        with managed_cursor(conn, dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT
                    criterio.id_criterio,
                    criterio.descricao,
                    AVG(avaliacao.nota) AS media
                FROM avaliacao
                JOIN criterio ON avaliacao.id_criterio = criterio.id_criterio
                WHERE avaliacao.id_escuderia = %s
                GROUP BY criterio.id_criterio, criterio.descricao
                """,
                (id_escuderia,),
            )
            criterios = cursor.fetchall()
            cursor.execute(
                """
                SELECT comentario
                FROM avaliacao
                WHERE id_escuderia = %s
                    AND comentario IS NOT NULL
                    AND comentario != ''
                """,
                (id_escuderia,),
            )
            comentarios = [linha["comentario"] for linha in cursor.fetchall()]

    for criterio in criterios:
        criterio["media"] = float(criterio["media"])

    if not criterios:
        return None

    ranking_geral = calcular_ranking()
    posicao = None
    nota_final = None
    for indice, item in enumerate(ranking_geral):
        if item["id_escuderia"] == id_escuderia:
            posicao = indice + 1
            nota_final = item["nota_final"]
            break

    return {
        "id_escuderia": id_escuderia,
        "posicao": posicao,
        "nota_final": nota_final,
        "criterios": criterios,
        "comentarios": comentarios,
    }


def salvar_snapshot_ranking(id_divulgacao):
    with managed_connection(get_connection) as conn:
        with managed_cursor(conn) as cursor:
            try:
                ranking = calcular_ranking(connection=conn)
                _inserir_snapshot(cursor, id_divulgacao, ranking)
                conn.commit()
            except Exception:
                conn.rollback()
                raise


def _inserir_snapshot(cursor, id_divulgacao, ranking):
    cursor.execute(
        "DELETE FROM resultado WHERE id_divulgacao = %s",
        (id_divulgacao,),
    )
    for item in ranking:
        cursor.execute(
            """
            INSERT INTO resultado (id_escuderia, id_divulgacao, nota_final)
            VALUES (%s, %s, %s)
            """,
            (item["id_escuderia"], id_divulgacao, item["nota_final"]),
        )


def obter_ranking_salvo():
    with managed_connection(get_connection) as conn:
        with managed_cursor(conn, dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT
                    resultado.id_escuderia,
                    escuderia.nome_escuderia,
                    resultado.nota_final
                FROM resultado
                JOIN escuderia
                    ON resultado.id_escuderia = escuderia.id_escuderia
                WHERE resultado.id_divulgacao = (
                    SELECT id_divulgacao
                    FROM divulgacao
                    ORDER BY id_divulgacao DESC
                    LIMIT 1
                )
                ORDER BY resultado.nota_final DESC
                """
            )
            linhas = cursor.fetchall()

    for linha in linhas:
        linha["nota_final"] = float(linha["nota_final"])

    return linhas
