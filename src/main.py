from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.config import settings
from src.core.exceptions import ApplicationError
from src.routes.escuderias import router as escuderias_router
from src.routes.avaliacoes import router as avaliacoes_router
from src.routes.criterios import router as criterios_router
from src.routes.usuarios import router as usuarios_router
from src.routes.ranking import router as ranking_router
from src.routes.admin import router as admin_router

app = FastAPI(
    title="Sistema GP de Avaliação",
    version="1.0.0"
)


@app.exception_handler(ApplicationError)
async def application_error_handler(
    _request: Request,
    erro: ApplicationError,
):
    return JSONResponse(
        status_code=erro.status_code,
        content={
            "detail": erro.message,
            "code": erro.code,
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(
    _request: Request,
    erro: StarletteHTTPException,
):
    return JSONResponse(
        status_code=erro.status_code,
        content={
            "detail": erro.detail,
            "code": f"http_{erro.status_code}",
        },
        headers=erro.headers,
    )


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    _request: Request,
    erro: RequestValidationError,
):
    return JSONResponse(
        status_code=422,
        content={
            "detail": jsonable_encoder(erro.errors()),
            "code": "validation_error",
        },
    )


origins = [
    # FRONTEND LOCAL
    "http://127.0.0.1:5500",
    "http://localhost:5500",

    # BACKEND LOCAL / SWAGGER
    "http://127.0.0.1:8000",
    "http://localhost:8000",

    *settings.CORS_ALLOWED_ORIGINS,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_credentials=True,
    allow_headers=["*"]
)

app.include_router(escuderias_router)

app.include_router(avaliacoes_router)

app.include_router(criterios_router)

app.include_router(usuarios_router)

app.include_router(ranking_router)

app.include_router(admin_router)

@app.get("/")
def root():

    return {
        "status": "Sistema GP rodando"
    }