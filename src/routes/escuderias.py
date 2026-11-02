from fastapi import APIRouter, Depends, HTTPException, Path

from src.models import (
    EscuderiaAvaliacaoStatus,
    EscuderiaCreate,
    EscuderiaCreated,
    EscuderiaRead,
)
from src.security.avaliadores import validar_sessao_avaliador
from src.services.escuderias_service import (
    criar_escuderia_service,
    listar_escuderias_avaliadas_service,
    listar_escuderias_service,
)


router = APIRouter()


@router.post("/escuderias", response_model=EscuderiaCreated)
def cadastrar_escuderia(dados: EscuderiaCreate):
    novo_id = criar_escuderia_service(
        dados.nome,
        dados.turma,
        dados.nome_mentor,
        dados.curso,
        dados.etapa,
        dados.periodo,
        dados.escola,
    )
    return {
        "id_escuderia": novo_id,
        "message": "Escuderia cadastrada com sucesso!",
    }


@router.get("/escuderias", response_model=list[EscuderiaRead])
def obter_escuderias():
    return listar_escuderias_service()


@router.get(
    "/avaliadores/{id_avaliador}/escuderias-avaliadas",
    response_model=list[EscuderiaAvaliacaoStatus],
)
def obter_escuderias_avaliadas(
    id_avaliador: int = Path(gt=0),
    avaliador=Depends(validar_sessao_avaliador),
):
    if id_avaliador != avaliador["id_avaliador"]:
        raise HTTPException(
            status_code=403,
            detail="Acesso às avaliações de outro avaliador não autorizado.",
        )
    return listar_escuderias_avaliadas_service(id_avaliador)
