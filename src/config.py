import os

from dotenv import load_dotenv

load_dotenv()


def _normalize_database_url(value):
    if value is None:
        return None

    value = value.strip()
    assignment_prefix = "DATABASE_URL="
    if value.startswith(assignment_prefix):
        value = value[len(assignment_prefix):].strip()
    return value


class Settings:
    APP_ENV = os.getenv("APP_ENV", "development").lower()
    DB_DRIVER = os.getenv("DB_DRIVER", "mysql").lower()
    DATABASE_URL = _normalize_database_url(
        os.getenv("DB_TEST_URL" if APP_ENV == "test" else "DATABASE_URL")
    )
    CORS_ALLOWED_ORIGINS = tuple(
        origin.strip()
        for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
        if origin.strip()
    )
    DB_SQLITE_PATH = os.getenv(
        "DB_SQLITE_PATH",
        os.path.join(os.path.dirname(__file__), "..", "data", "sistema_gp.sqlite3"),
    )

    if APP_ENV == "test":
        DB_HOST = os.getenv("DB_TEST_HOST")
        DB_PORT = int(os.getenv("DB_TEST_PORT", 3306))
        DB_USER = os.getenv("DB_TEST_USER")
        DB_PASSWORD = os.getenv("DB_TEST_PASSWORD")
        DB_NAME = os.getenv("DB_TEST_NAME")
    else:
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = int(os.getenv("DB_PORT", 3306))
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_NAME = os.getenv("DB_NAME")

    ADMIN_CODIGO = os.getenv("ADMIN_CODIGO")
    ADMIN_TOKEN_SECRET = os.getenv("ADMIN_TOKEN_SECRET")
    AVALIADOR_CODIGO = os.getenv("AVALIADOR_CODIGO")


settings = Settings()
