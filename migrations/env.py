import os

from alembic import context
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import URL, make_url

from src.config import settings


def database_url():
    if settings.DB_DRIVER == "sqlite":
        database_path = os.path.abspath(settings.DB_SQLITE_PATH)
        os.makedirs(os.path.dirname(database_path), exist_ok=True)
        return URL.create(
            "sqlite",
            database=database_path,
        )
    if settings.DB_DRIVER in {"postgres", "postgresql", "supabase"}:
        if not settings.DATABASE_URL:
            raise RuntimeError(
                "DATABASE_URL is required when DB_DRIVER is PostgreSQL."
            )

        url = make_url(settings.DATABASE_URL)
        if settings.APP_ENV == "test" and not (
            url.database and url.database.startswith("test_")
        ):
            raise RuntimeError(
                "The PostgreSQL test database name must start with 'test_'."
            )
        return url.set(drivername="postgresql+psycopg")
    if settings.DB_DRIVER != "mysql":
        raise RuntimeError(
            "DB_DRIVER must be 'mysql', 'postgresql', or 'sqlite'."
        )

    required = {
        "DB_HOST": settings.DB_HOST,
        "DB_USER": settings.DB_USER,
        "DB_NAME": settings.DB_NAME,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(
            "Database configuration is incomplete: "
            + ", ".join(missing)
        )

    if settings.APP_ENV == "test" and not settings.DB_NAME.startswith("test_"):
        raise RuntimeError(
            "DB_TEST_NAME must start with 'test_' to protect non-test databases."
        )

    return URL.create(
        "mysql+mysqlconnector",
        username=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
    )


def run_migrations_offline():
    context.configure(
        url=database_url().render_as_string(hide_password=False),
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = create_engine(
        database_url(),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
