from fastapi import APIRouter, Depends, HTTPException, Path

from src.models import (
    AdminAuthResponse,
    AdminLogin,
    AdminSessionResponse,
    AvaliadorCreate,
    AvaliadorRead,
    CriterioCreate,
    CriterioRead,
    EscuderiaCreate,
    EscuderiaCreated,
    EscuderiaRead,
    MensagemResponse,
    PositiveId,
)
from src.security.admin import validar_token_admin
from src.services.admin_service import (
    atualizar_avaliador_service,
    atualizar_criterio_service,
    criar_avaliador_service,
    criar_criterio_service,
    excluir_avaliador_service,
    excluir_criterio_service,
    gerar_token_admin_service,
    verificar_codigo_admin_service,
)
from src.services.escuderias_service import (
    atualizar_escuderia_service,
    criar_escuderia_service,
    excluir_escuderia_service,
    listar_escuderias_service,
)
from src.services.criterios_service import listar_criterios_service
from src.services.usuarios_service import listar_avaliadores_service


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


@router.get(
    "/admin/escuderias",
    response_model=list[EscuderiaRead],
)
def listar_escuderias_admin(_admin=Depends(validar_token_admin)):
    return listar_escuderias_service()


@router.post(
    "/admin/escuderias",
    response_model=EscuderiaCreated,
    status_code=201,
)
def criar_escuderia_admin(
    dados: EscuderiaCreate,
    _admin=Depends(validar_token_admin),
):
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
        "message": "Escuderia cadastrada com sucesso.",
    }


@router.put(
    "/admin/escuderias/{id_escuderia}",
    response_model=MensagemResponse,
)
def editar_escuderia_admin(
    dados: EscuderiaCreate,
    id_escuderia: PositiveId = Path(),
    _admin=Depends(validar_token_admin),
):
    atualizar_escuderia_service(
        id_escuderia,
        dados.nome,
        dados.turma,
        dados.nome_mentor,
        dados.curso,
        dados.etapa,
        dados.periodo,
        dados.escola,
    )
    return {"mensagem": "Escuderia atualizada com sucesso."}


@router.delete(
    "/admin/escuderias/{id_escuderia}",
    response_model=MensagemResponse,
)
def remover_escuderia_admin(
    id_escuderia: PositiveId = Path(),
    _admin=Depends(validar_token_admin),
):
    excluir_escuderia_service(id_escuderia)
    return {"mensagem": "Escuderia excluída com sucesso."}


@router.get(
    "/admin/avaliadores",
    response_model=list[AvaliadorRead],
)
def listar_avaliadores_admin(_admin=Depends(validar_token_admin)):
    return listar_avaliadores_service()


@router.post(
    "/admin/avaliadores",
    response_model=AvaliadorRead,
    status_code=201,
)
def criar_avaliador_admin(
    dados: AvaliadorCreate,
    _admin=Depends(validar_token_admin),
):
    return criar_avaliador_service(dados.nome)


@router.put(
    "/admin/avaliadores/{id_avaliador}",
    response_model=AvaliadorRead,
)
def editar_avaliador_admin(
    dados: AvaliadorCreate,
    id_avaliador: PositiveId = Path(),
    _admin=Depends(validar_token_admin),
):
    return atualizar_avaliador_service(id_avaliador, dados.nome)


@router.delete(
    "/admin/avaliadores/{id_avaliador}",
    response_model=MensagemResponse,
)
def remover_avaliador_admin(
    id_avaliador: PositiveId = Path(),
    _admin=Depends(validar_token_admin),
):
    excluir_avaliador_service(id_avaliador)
    return {"mensagem": "Avaliador excluído com sucesso."}


@router.get(
    "/admin/criterios",
    response_model=list[CriterioRead],
)
def listar_criterios_admin(_admin=Depends(validar_token_admin)):
    return listar_criterios_service()


@router.post(
    "/admin/criterios",
    response_model=CriterioRead,
    status_code=201,
)
def criar_criterio_admin(
    dados: CriterioCreate,
    _admin=Depends(validar_token_admin),
):
    return criar_criterio_service(dados.descricao)


@router.put(
    "/admin/criterios/{id_criterio}",
    response_model=CriterioRead,
)
def editar_criterio_admin(
    dados: CriterioCreate,
    id_criterio: PositiveId = Path(),
    _admin=Depends(validar_token_admin),
):
    return atualizar_criterio_service(id_criterio, dados.descricao)


@router.delete(
    "/admin/criterios/{id_criterio}",
    response_model=MensagemResponse,
)
def remover_criterio_admin(
    id_criterio: PositiveId = Path(),
    _admin=Depends(validar_token_admin),
):
    excluir_criterio_service(id_criterio)
    return {"mensagem": "Critério excluído com sucesso."}
