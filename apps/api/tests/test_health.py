import pytest
from app.config import get_settings
from app.db import reset_db_state
from app.main import create_app
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_health_returns_ok_when_database_is_available(
    client: TestClient,
    require_postgres: None,
) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app_env": "test",
        "database": "ok",
    }


def test_health_returns_degraded_when_database_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://invalid:invalid@127.0.0.1:6543/invalid",
    )
    monkeypatch.setenv("APP_ENV", "test")
    get_settings.cache_clear()
    reset_db_state()

    with TestClient(create_app()) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "degraded",
        "app_env": "test",
        "database": "unavailable",
    }

    reset_db_state()
    get_settings.cache_clear()
