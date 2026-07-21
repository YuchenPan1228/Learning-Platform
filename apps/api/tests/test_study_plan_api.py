import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_study_plan_endpoint_returns_deterministic_daily_plan(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    response = client.get("/study-plan")
    assert response.status_code == 200
    payload = response.json()

    assert payload["user_id"] == "local"
    assert payload["target_minutes"] == 90
    assert payload["total_minutes"] >= 0
    assert payload["summary"]
    assert payload["detail"]
    assert isinstance(payload["items"], list)
    assert len(payload["items"]) <= 5
    if payload["items"]:
        item = payload["items"][0]
        assert item["kind"]
        assert item["title"]
        assert item["duration_minutes"] >= 1


@pytest.mark.integration
def test_dashboard_includes_daily_plan(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    response = client.get("/dashboard")
    assert response.status_code == 200
    payload = response.json()
    assert "daily_plan" in payload
    assert payload["daily_plan"]["summary"]
    assert isinstance(payload["daily_plan"]["items"], list)
