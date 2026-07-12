import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_dashboard_returns_computed_mastery_from_attempts(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    response = client.get("/dashboard")

    assert response.status_code == 200
    payload = response.json()
    assert payload["user_id"] == "local"
    assert len(payload["topic_mastery"]) == 9
    assert payload["topic_mastery"][0]["slug"] == "probability"
    assert payload["topic_mastery"][0]["mastery_score"] == 0.0
    assert payload["topic_mastery"][0]["attempts_count"] == 0


@pytest.mark.integration
def test_dashboard_mastery_updates_after_correct_attempt(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    questions_response = client.get("/questions", params={"topic_slug": "probability", "limit": 1})
    question = questions_response.json()[0]
    detail_response = client.get(f"/questions/{question['id']}")
    short_answer = detail_response.json()["short_answer"]
    assert short_answer is not None

    attempt_response = client.post(
        "/attempts",
        json={
            "question_id": question["id"],
            "answer": short_answer,
            "time_spent_seconds": 30,
        },
    )
    assert attempt_response.status_code == 200

    dashboard_response = client.get("/dashboard")
    assert dashboard_response.status_code == 200
    probability_card = next(
        item for item in dashboard_response.json()["topic_mastery"] if item["slug"] == "probability"
    )
    assert probability_card["attempts_count"] == 1
    assert probability_card["mastery_score"] > 0.0


@pytest.mark.integration
def test_dashboard_returns_weak_prerequisites(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    response = client.get("/dashboard")
    weak_prerequisites = response.json()["weak_prerequisites"]
    assert len(weak_prerequisites) > 0
    assert (
        weak_prerequisites[0]["prerequisite_mastery_score"]
        <= weak_prerequisites[-1]["prerequisite_mastery_score"]
    )
