from fastapi import APIRouter, Depends, HTTPException

from src.models import AdminAuthResponse, AdminLogin, AdminSessionResponse
from src.security.admin import validar_token_admin
from src.services.admin_service import (
    gerar_token_admin_service,
    verificar_codigo_admin_service,
)


router = APIRouter()


@router.post("/admin/validar", response_model=AdminAuthResponse)
def validar_acesso_admin(dados: AdminLogin):
    if not verificar_codigo_admin_service(dados.codigo):
        raise HTTPException(
            status_code=401,
            detail="Código administrativo incorreto.",
        )

    token = gerar_token_admin_service()

    return {
        "token": token,
        "mensagem": "Acesso administrativo autorizado.",
    }


@router.get("/admin/verificar", response_model=AdminSessionResponse)
def verificar_sessao_admin(
    _admin=Depends(validar_token_admin),
):
    return {"autorizado": True}
