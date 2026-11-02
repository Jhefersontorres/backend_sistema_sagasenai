from src.repositories.ranking_repository import (
    atualizar_divulgacao as repository_atualizar_divulgacao,
    calcular_ranking,
    obter_desempenho_escuderia as repository_obter_desempenho_escuderia,
    obter_ranking_salvo,
    obter_status_divulgacao as repository_obter_status_divulgacao,
)


def obter_status_divulgacao_service():
    return repository_obter_status_divulgacao()


def calcular_ranking_service():
    return calcular_ranking()


def definir_divulgacao_service(mostrar_resultado: bool, data_divulgacao):
    repository_atualizar_divulgacao(mostrar_resultado, data_divulgacao)


def obter_ranking_service():
    return obter_ranking_salvo()


def obter_desempenho_escuderia_service(id_escuderia: int):
    return repository_obter_desempenho_escuderia(id_escuderia)
