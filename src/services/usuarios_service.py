from src.repositories.usuarios_repository import (
    listar_avaliadores as repository_listar_avaliadores,
    obter_avaliador as repository_obter_avaliador,
)


def listar_avaliadores_service():
    return repository_listar_avaliadores()


def obter_avaliador_service(id_avaliador: int):
    return repository_obter_avaliador(id_avaliador)
