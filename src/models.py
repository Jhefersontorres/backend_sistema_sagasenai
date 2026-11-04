from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints


NonEmptyString = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
]
PositiveId = Annotated[int, Field(gt=0)]
CourseName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=100),
]
TeamName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=100),
]
ClassName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=20),
]
PersonName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=100),
]
CriterionDescription = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=250),
]
StageName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=50),
]
PeriodName = StageName
SchoolName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=150),
]


class EscuderiaCreate(BaseModel):
    nome: TeamName
    turma: ClassName
    nome_mentor: PersonName
    curso: CourseName
    etapa: StageName
    periodo: PeriodName
    escola: SchoolName


class EscuderiaCreated(BaseModel):
    id_escuderia: PositiveId
    message: str


class EscuderiaRead(BaseModel):
    id_escuderia: PositiveId
    nome_escuderia: str
    turma: str
    nome_mentor: str | None
    curso: str | None
    etapa: str | None
    periodo: str | None
    escola: str | None


class AvaliadorCreate(BaseModel):
    nome: PersonName


class CriterioCreate(BaseModel):
    descricao: CriterionDescription


class CriterioRead(BaseModel):
    id_criterio: PositiveId
    descricao: str
    peso: float


class EscuderiaAvaliacaoStatus(BaseModel):
    id_escuderia: PositiveId
    nome_escuderia: str
    turma: str
    mentor: str | None
    curso: str | None
    etapa: str | None
    periodo: str | None
    escola: str | None
    criterios_avaliados: int
    total_criterios: int
    status: Literal["concluida", "em_andamento"]


class AvaliacaoCreate(BaseModel):
    id_escuderia: PositiveId
    id_criterio: PositiveId
    nota: float = Field(ge=0, le=10, allow_inf_nan=False)
    comentario: str | None = None


class AvaliacaoCreated(BaseModel):
    id_avaliacao: PositiveId
    message: str


class DivulgacaoUpdate(BaseModel):
    mostrar_resultado: bool
    data_divulgacao: datetime


class DivulgacaoStatus(BaseModel):
    mostrar_resultado: bool
    data_divulgacao: datetime | None


class AdminLogin(BaseModel):
    codigo: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=32, max_length=128),
    ]


class AdminAuthResponse(BaseModel):
    token: str
    mensagem: str


class AvaliadorAccessResponse(BaseModel):
    token: str
    mensagem: str


class AdminSessionResponse(BaseModel):
    autorizado: bool


class MensagemResponse(BaseModel):
    mensagem: str


class AvaliadorRead(BaseModel):
    id_usuario: PositiveId
    nome: str | None


class AvaliadorCode(BaseModel):
    codigo: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=32, max_length=128),
    ]


class AvaliadorSessionCreate(BaseModel):
    id_avaliador: PositiveId


class AvaliadorSessionResponse(BaseModel):
    token: str
    id_avaliador: PositiveId
    nome: str | None


class RankingEntry(BaseModel):
    id_escuderia: PositiveId
    nome_escuderia: str
    nota_final: float


class CriterioDesempenho(BaseModel):
    id_criterio: PositiveId
    descricao: str
    media: float


class EscuderiaDesempenho(BaseModel):
    id_escuderia: PositiveId
    posicao: PositiveId | None
    nota_final: float | None
    criterios: list[CriterioDesempenho]
    comentarios: list[str]
