from fastapi import APIRouter

from src.services.criterios_service import listar_criterios_service


router = APIRouter()


@router.get("/criterios")
def obter_criterios():
    return listar_criterios_service()
