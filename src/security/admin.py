import hmac

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.config import settings
from src.security.signed_tokens import create_signed_token, verify_signed_token


bearer_scheme = HTTPBearer(auto_error=False)
ADMIN_TOKEN_EXPIRACAO = 60 * 60 * 2


def verificar_codigo_admin(codigo: str) -> bool:
    codigo_correto = settings.ADMIN_CODIGO
    if not codigo_correto or len(codigo_correto) < 32:
        raise RuntimeError(
            "ADMIN_CODIGO deve ter pelo menos 32 caracteres."
        )
    return hmac.compare_digest(codigo, codigo_correto)


def gerar_token_admin() -> str:
    return create_signed_token(
        {"tipo": "admin"},
        ADMIN_TOKEN_EXPIRACAO,
    )


def validar_token_admin(
    credenciais: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    if credenciais is None:
        raise HTTPException(
            status_code=401,
            detail="Acesso administrativo não autorizado.",
        )

    if credenciais.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Tipo de autenticação inválido.",
        )

    payload = verify_signed_token(credenciais.credentials)
    if payload.get("tipo") != "admin":
        raise HTTPException(
            status_code=401,
            detail="Token administrativo inválido.",
        )

    return True
