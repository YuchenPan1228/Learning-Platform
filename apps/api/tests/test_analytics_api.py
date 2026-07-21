import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_analytics_endpoint_returns_roadmap_sections(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    response = client.get("/analytics")
    assert response.status_code == 200
    payload = response.json()

    assert payload["user_id"] == "local"
    assert isinstance(payload["weak_concepts"], list)
    assert isinstance(payload["attempt_history"], list)
    assert isinstance(payload["search_misses"], list)
    assert isinstance(payload["review_due_count"], int)
    assert payload["review_due_count"] >= 0

    if payload["weak_concepts"]:
        concept = payload["weak_concepts"][0]
        assert concept["slug"]
        assert concept["mastery_score"] < 50.0


@pytest.mark.integration
def test_analytics_includes_attempt_history_and_search_misses(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    questions = client.get("/questions", params={"limit": 1}).json()
    question = questions[0]
    detail = client.get(f"/questions/{question['id']}").json()

    client.post(
        "/attempts",
        json={
            "question_id": question["id"],
            "answer": detail.get("short_answer") or "guess",
            "time_spent_seconds": 12,
        },
    )
    client.get("/search", params={"q": "zzzz-analytics-miss-qp031"})

    payload = client.get("/analytics").json()
    assert any(item["question_id"] == question["id"] for item in payload["attempt_history"])
    assert any(item["query"] == "zzzz-analytics-miss-qp031" for item in payload["search_misses"])
    assert payload["review_due_count"] >= 0
