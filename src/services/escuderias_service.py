from src.repositories.escuderias_repository import (
    buscar_ou_criar_mentor,
    criar_escuderia,
    listar_escuderias,
    listar_escuderias_avaliadas,
)


def criar_escuderia_service(
    nome: str,
    turma: str,
    nome_mentor: str,
    curso: str,
    etapa: str,
    periodo: str,
    escola: str,
):
    return criar_escuderia(
        nome,
        turma,
        nome_mentor,
        curso,
        etapa,
        periodo,
        escola,
    )


def listar_escuderias_service():
    return listar_escuderias()


def listar_escuderias_avaliadas_service(id_avaliador: int):
    return listar_escuderias_avaliadas(id_avaliador)


def buscar_ou_criar_mentor_service(nome_mentor: str):
    return buscar_ou_criar_mentor(nome_mentor)
