from fastapi import APIRouter, Depends, HTTPException

from src.models import (
    AvaliadorAccessResponse,
    AvaliadorCode,
    AvaliadorRead,
    AvaliadorSessionCreate,
    AvaliadorSessionResponse,
)
from src.security.avaliadores import (
    gerar_token_evento,
    gerar_token_sessao_avaliador,
    validar_token_evento,
    verificar_codigo_avaliador as verificar_codigo_evento,
)
from src.services.usuarios_service import (
    listar_avaliadores_service,
    obter_avaliador_service,
)


router = APIRouter()


@router.post("/avaliadores/validar", response_model=AvaliadorAccessResponse)
def validar_codigo_avaliador(dados: AvaliadorCode):
    if not verificar_codigo_evento(dados.codigo):
        raise HTTPException(
            status_code=401,
            detail="Código do evento incorreto.",
        )

    return {
        "token": gerar_token_evento(),
        "mensagem": "Código do evento validado.",
    }


@router.get("/avaliadores", response_model=list[AvaliadorRead])
def obter_avaliadores(_evento=Depends(validar_token_evento)):
    return listar_avaliadores_service()


@router.post(
    "/avaliadores/sessao",
    response_model=AvaliadorSessionResponse,
)
def criar_sessao_avaliador(
    dados: AvaliadorSessionCreate,
    _evento=Depends(validar_token_evento),
):
    avaliador = obter_avaliador_service(dados.id_avaliador)
    if avaliador is None:
        raise HTTPException(
            status_code=404,
            detail="Avaliador não encontrado.",
        )

    return {
        "token": gerar_token_sessao_avaliador(dados.id_avaliador),
        "id_avaliador": dados.id_avaliador,
        "nome": avaliador["nome"],
    }
