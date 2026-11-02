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
