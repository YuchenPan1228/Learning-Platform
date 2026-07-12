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


def test_cors_preflight_allows_attempts_from_local_web_origin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    get_settings.cache_clear()
    reset_db_state()

    with TestClient(create_app()) as client:
        response = client.options(
            "/attempts",
            headers={
                "Origin": "http://127.0.0.1:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"
    assert "POST" in response.headers["access-control-allow-methods"]

    reset_db_state()
    get_settings.cache_clear()


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
