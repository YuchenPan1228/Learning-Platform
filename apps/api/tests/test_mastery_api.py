import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_mastery_endpoint_returns_topic_and_concept_mastery(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    response = client.get("/mastery")
    assert response.status_code == 200
    payload = response.json()

    assert payload["user_id"] == "local"
    assert len(payload["topic_mastery"]) >= 9
    assert len(payload["concept_mastery"]) >= 1

    probability = next(item for item in payload["topic_mastery"] if item["slug"] == "probability")
    assert probability["mastery_score"] == 0.0
    assert probability["attempts_count"] == 0
    assert "last_practiced_at" in probability
    assert "next_review_at" in probability

    bayes = next(item for item in payload["concept_mastery"] if item["slug"] == "bayes")
    assert bayes["topic_slug"]
    assert bayes["mastery_score"] == 0.0


@pytest.mark.integration
def test_mastery_persists_after_solved_attempt(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    questions_response = client.get(
        "/questions",
        params={"topic_slug": "probability", "limit": 1},
    )
    question = questions_response.json()["items"][0]
    detail = client.get(f"/questions/{question['id']}").json()
    assert detail["short_answer"] is not None

    client.post(
        "/attempts",
        json={
            "question_id": question["id"],
            "answer": detail["short_answer"],
            "time_spent_seconds": 15,
        },
    )

    mastery = client.get("/mastery").json()
    probability = next(item for item in mastery["topic_mastery"] if item["slug"] == "probability")
    assert probability["attempts_count"] >= 1
    assert probability["mastery_score"] > 0.0
    assert probability["last_practiced_at"] is not None

    subtopic_slug = question["subtopic_slug"]
    if subtopic_slug is not None:
        subtopic = next(item for item in mastery["topic_mastery"] if item["slug"] == subtopic_slug)
        assert subtopic["attempts_count"] >= 1
        assert subtopic["mastery_score"] > 0.0
