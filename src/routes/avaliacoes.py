from fastapi import APIRouter, Depends

from src.models import AvaliacaoCreate, AvaliacaoCreated
from src.security.avaliadores import validar_sessao_avaliador
from src.services.avaliacoes_service import criar_avaliacao_service


router = APIRouter()


@router.post("/avaliacoes", response_model=AvaliacaoCreated)
def cadastrar_avaliacao(
    dados: AvaliacaoCreate,
    avaliador=Depends(validar_sessao_avaliador),
):
    novo_id = criar_avaliacao_service(
        dados.id_escuderia,
        avaliador["id_avaliador"],
        dados.id_criterio,
        dados.nota,
        dados.comentario,
    )

    return {
        "id_avaliacao": novo_id,
        "message": "Avaliação atribuída com sucesso!",
    }
