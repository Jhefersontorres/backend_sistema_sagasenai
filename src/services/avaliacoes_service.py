from src.repositories.avaliacoes_repository import criar_avaliacao as repository_criar_avaliacao


def criar_avaliacao_service(
    id_escuderia: int,
    id_avaliador: int,
    id_criterio: int,
    nota: float,
    comentario: str | None,
):
    return repository_criar_avaliacao(
        id_escuderia,
        id_avaliador,
        id_criterio,
        nota,
        comentario,
    )
