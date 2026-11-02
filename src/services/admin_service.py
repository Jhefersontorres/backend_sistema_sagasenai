from src.security.admin import (
    gerar_token_admin,
    verificar_codigo_admin,
)


def verificar_codigo_admin_service(codigo: str) -> bool:
    return verificar_codigo_admin(codigo)


def gerar_token_admin_service() -> str:
    return gerar_token_admin()
