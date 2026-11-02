import hmac

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.config import settings
from src.security.signed_tokens import create_signed_token, verify_signed_token


bearer_scheme = HTTPBearer(auto_error=False)
EVENT_TOKEN_EXPIRATION_SECONDS = 10 * 60
EVALUATOR_TOKEN_EXPIRATION_SECONDS = 2 * 60 * 60


def verificar_codigo_avaliador(codigo: str) -> bool:
    codigo_correto = settings.AVALIADOR_CODIGO
    if not codigo_correto or len(codigo_correto) < 32:
        raise RuntimeError(
            "AVALIADOR_CODIGO deve ter pelo menos 32 caracteres."
        )
    return hmac.compare_digest(codigo, codigo_correto)


def gerar_token_evento() -> str:
    return create_signed_token(
        {"tipo": "evento"},
        EVENT_TOKEN_EXPIRATION_SECONDS,
    )


def validar_token_evento(
    credenciais: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    payload = _validar_credenciais(credenciais)
    if payload.get("tipo") != "evento":
        raise HTTPException(
            status_code=403,
            detail="É necessário validar novamente o código do evento.",
        )
    return payload


def gerar_token_sessao_avaliador(id_avaliador: int) -> str:
    return create_signed_token(
        {
            "tipo": "avaliador",
            "id_avaliador": id_avaliador,
        },
        EVALUATOR_TOKEN_EXPIRATION_SECONDS,
    )


def validar_sessao_avaliador(
    credenciais: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    payload = _validar_credenciais(credenciais)
    id_avaliador = payload.get("id_avaliador")
    if (
        payload.get("tipo") != "avaliador"
        or not isinstance(id_avaliador, int)
        or isinstance(id_avaliador, bool)
        or id_avaliador <= 0
    ):
        raise HTTPException(
            status_code=403,
            detail="Sessão de avaliador inválida.",
        )
    return payload


def _validar_credenciais(
    credenciais: HTTPAuthorizationCredentials | None,
) -> dict:
    if credenciais is None:
        raise HTTPException(
            status_code=401,
            detail="Acesso do avaliador não autorizado.",
        )

    if credenciais.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Tipo de autenticação inválido.",
        )

    return verify_signed_token(credenciais.credentials)
