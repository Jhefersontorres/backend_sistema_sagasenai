from src.security.admin import (
    gerar_token_admin,
    verificar_codigo_admin,
)
from src.repositories.admin_repository import (
    atualizar_avaliador,
    atualizar_criterio,
    criar_avaliador,
    criar_criterio,
    excluir_avaliador,
    excluir_criterio,
)


def verificar_codigo_admin_service(codigo: str) -> bool:
    return verificar_codigo_admin(codigo)


def gerar_token_admin_service() -> str:
    return gerar_token_admin()


def criar_avaliador_service(nome: str):
    return criar_avaliador(nome)


def atualizar_avaliador_service(id_avaliador: int, nome: str):
    return atualizar_avaliador(id_avaliador, nome)


def excluir_avaliador_service(id_avaliador: int):
    excluir_avaliador(id_avaliador)


def criar_criterio_service(descricao: str):
    return criar_criterio(descricao)


def atualizar_criterio_service(id_criterio: int, descricao: str):
    return atualizar_criterio(id_criterio, descricao)


def excluir_criterio_service(id_criterio: int):
    excluir_criterio(id_criterio)
