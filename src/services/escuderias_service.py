from src.repositories.escuderias_repository import (
    atualizar_escuderia,
    buscar_ou_criar_mentor,
    criar_escuderia,
    excluir_escuderia,
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


def atualizar_escuderia_service(
    id_escuderia: int,
    nome: str,
    turma: str,
    nome_mentor: str,
    curso: str,
    etapa: str,
    periodo: str,
    escola: str,
):
    atualizar_escuderia(
        id_escuderia,
        nome,
        turma,
        nome_mentor,
        curso,
        etapa,
        periodo,
        escola,
    )


def excluir_escuderia_service(id_escuderia: int):
    excluir_escuderia(id_escuderia)


def listar_escuderias_avaliadas_service(id_avaliador: int):
    return listar_escuderias_avaliadas(id_avaliador)


def buscar_ou_criar_mentor_service(nome_mentor: str):
    return buscar_ou_criar_mentor(nome_mentor)
