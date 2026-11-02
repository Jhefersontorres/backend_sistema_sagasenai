from src.services.avaliacoes_service import criar_avaliacao_service


def criar_avaliacao(
    id_escuderia: int,
    id_avaliador: int,
    id_criterio: int,
    nota: float,
    comentario: str | None,
):
    return criar_avaliacao_service(
        id_escuderia,
        id_avaliador,
        id_criterio,
        nota,
        comentario,
    )
