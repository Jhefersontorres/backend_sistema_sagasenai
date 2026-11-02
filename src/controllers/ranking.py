from src.services.ranking_service import (
    calcular_ranking_service,
    definir_divulgacao_service,
    obter_desempenho_escuderia_service,
    obter_ranking_service,
    obter_status_divulgacao_service,
)


def obter_status_divulgacao():
    return obter_status_divulgacao_service()


def calcular_ranking():
    return calcular_ranking_service()


def atualizar_divulgacao(mostrar_resultado: bool, data_divulgacao):
    definir_divulgacao_service(mostrar_resultado, data_divulgacao)


def obter_desempenho_escuderia(id_escuderia: int):
    return obter_desempenho_escuderia_service(id_escuderia)


def salvar_snapshot_ranking(id_divulgacao):
    from src.repositories.ranking_repository import salvar_snapshot_ranking as repository_salvar_snapshot_ranking

    return repository_salvar_snapshot_ranking(id_divulgacao)


def obter_ranking_salvo():
    return obter_ranking_service()