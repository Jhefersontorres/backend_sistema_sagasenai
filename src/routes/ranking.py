from fastapi import APIRouter, Depends, HTTPException, Path

from src.models import (
    DivulgacaoStatus,
    DivulgacaoUpdate,
    EscuderiaDesempenho,
    MensagemResponse,
    RankingEntry,
)
from src.security.admin import validar_token_admin
from src.services.ranking_service import (
    definir_divulgacao_service,
    obter_desempenho_escuderia_service,
    obter_ranking_service,
    obter_status_divulgacao_service,
)


router = APIRouter()


@router.get("/divulgacao", response_model=DivulgacaoStatus)
def status_divulgacao():
    status = obter_status_divulgacao_service()
    if status is None:
        return {"mostrar_resultado": False, "data_divulgacao": None}
    return status


@router.get("/ranking", response_model=list[RankingEntry])
def obter_ranking():
    status = obter_status_divulgacao_service()
    if not status or not status["mostrar_resultado"]:
        raise HTTPException(
            status_code=403,
            detail="O ranking ainda não foi divulgado.",
        )
    return obter_ranking_service()


@router.post("/divulgacao", response_model=MensagemResponse)
def definir_divulgacao(
    dados: DivulgacaoUpdate,
    _admin=Depends(validar_token_admin),
):
    definir_divulgacao_service(
        dados.mostrar_resultado,
        dados.data_divulgacao,
    )
    return {"mensagem": "Divulgação atualizada com sucesso."}


@router.get(
    "/escuderias/{id_escuderia}/desempenho",
    response_model=EscuderiaDesempenho,
)
def desempenho_escuderia(
    id_escuderia: int = Path(gt=0),
):
    status = obter_status_divulgacao_service()
    if not status or not status["mostrar_resultado"]:
        raise HTTPException(
            status_code=403,
            detail="O resultado ainda não foi divulgado.",
        )

    resultado = obter_desempenho_escuderia_service(id_escuderia)
    if resultado is None:
        raise HTTPException(
            status_code=404,
            detail="Escuderia não encontrada ou sem avaliações.",
        )

    return resultado
