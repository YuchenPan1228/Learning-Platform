import os
from collections.abc import Generator

import pytest
from alembic import command
from alembic.config import Config
from app.config import get_settings
from app.db import get_session_factory, reset_db_state
from app.main import create_app
from app.seeds.knowledge_graph import seed_knowledge_graph
from app.seeds.mvp_content import seed_mvp_content
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from tests.paths import ALEMBIC_INI

DEFAULT_TEST_DATABASE_URL = (
    "postgresql+psycopg://quant_prep:quant_prep@localhost:5432/quant_prep_test"
)


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "integration: tests that require a running PostgreSQL instance",
    )


@pytest.fixture(scope="session")
def database_url() -> str:
    return os.environ.get("TEST_DATABASE_URL", DEFAULT_TEST_DATABASE_URL)


@pytest.fixture(scope="session")
def postgres_available(database_url: str) -> bool:
    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return False
    finally:
        engine.dispose()
    return True


@pytest.fixture
def migrated_database(
    database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", database_url)
    get_settings.cache_clear()
    alembic_config = Config(str(ALEMBIC_INI))
    command.downgrade(alembic_config, "base")
    command.upgrade(alembic_config, "head")


@pytest.fixture
def require_postgres(postgres_available: bool) -> None:
    if not postgres_available:
        pytest.skip(
            "PostgreSQL is not available. Run ./scripts/start-services.sh from the repo root.",
        )


@pytest.fixture
def seeded_database(
    database_url: str,
    migrated_database: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", database_url)
    get_settings.cache_clear()
    reset_db_state()

    session = get_session_factory()()
    try:
        seed_knowledge_graph(session)
        seed_mvp_content(session)
    finally:
        session.close()


@pytest.fixture
def client(
    monkeypatch: pytest.MonkeyPatch,
    database_url: str,
) -> Generator[TestClient, None, None]:
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("APP_ENV", "test")
    get_settings.cache_clear()
    reset_db_state()

    with TestClient(create_app()) as test_client:
        yield test_client

    reset_db_state()
    get_settings.cache_clear()
