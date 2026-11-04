class ApplicationError(Exception):
    def __init__(self, message: str, status_code: int, code: str):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code


class EvaluationClosedError(ApplicationError):
    def __init__(self):
        super().__init__(
            "As avaliações estão encerradas enquanto os resultados estiverem divulgados.",
            status_code=403,
            code="evaluations_closed",
        )


class DuplicateEvaluationError(ApplicationError):
    def __init__(self):
        super().__init__(
            "Este avaliador já avaliou esse critério para essa escuderia.",
            status_code=400,
            code="duplicate_evaluation",
        )


class ResourceNotFoundError(ApplicationError):
    def __init__(self, resource: str):
        super().__init__(
            f"{resource} não encontrado.",
            status_code=404,
            code="resource_not_found",
        )


class ResourceInUseError(ApplicationError):
    def __init__(self, resource: str):
        super().__init__(
            f"{resource} possui registros vinculados e não pode ser excluído.",
            status_code=409,
            code="resource_in_use",
        )
