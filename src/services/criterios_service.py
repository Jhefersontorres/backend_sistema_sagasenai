from src.repositories.criterios_repository import listar_criterios as repository_listar_criterios


def listar_criterios_service():
    return repository_listar_criterios()
