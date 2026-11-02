from src.services.escuderias_service import (
    buscar_ou_criar_mentor_service,
    criar_escuderia_service,
    listar_escuderias_avaliadas_service,
    listar_escuderias_service,
)


def buscar_ou_criar_mentor(nome_mentor: str):
    return buscar_ou_criar_mentor_service(nome_mentor)


def criar_escuderia(
    nome: str,
    turma: str,
    nome_mentor: str,
    curso: str,
    etapa: str,
    periodo: str,
    escola: str,
):
    return criar_escuderia_service(
        nome,
        turma,
        nome_mentor,
        curso,
        etapa,
        periodo,
        escola,
    )


def listar_escuderias():
    return listar_escuderias_service()


def listar_escuderias_avaliadas(id_avaliador: int):
    return listar_escuderias_avaliadas_service(id_avaliador)
