import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_get_attempt_progress_returns_empty_for_new_user(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    response = client.get("/attempts/progress")
    assert response.status_code == 200
    assert response.json() == {"questions": []}


@pytest.mark.integration
def test_list_questions_include_progress_reflects_attempts(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    questions_response = client.get("/questions", params={"limit": 1})
    question = questions_response.json()[0]
    detail_response = client.get(f"/questions/{question['id']}")
    short_answer = detail_response.json()["short_answer"]
    assert short_answer is not None

    client.post(
        "/attempts",
        json={
            "question_id": question["id"],
            "answer": short_answer,
            "time_spent_seconds": 10,
        },
    )

    progress_response = client.get(
        "/questions",
        params={"limit": 100, "include_progress": True},
    )
    assert progress_response.status_code == 200
    updated = next(item for item in progress_response.json() if item["id"] == question["id"])
    assert updated["progress_status"] == "solved"
    assert updated["attempt_count"] == 1

    attempt_progress = client.get("/attempts/progress").json()
    assert any(item["question_id"] == question["id"] for item in attempt_progress["questions"])


@pytest.mark.integration
def test_list_questions_include_progress_marks_incorrect_as_attempted(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    questions_response = client.get("/questions", params={"limit": 1})
    question_id = questions_response.json()[0]["id"]

    client.post(
        "/attempts",
        json={
            "question_id": question_id,
            "answer": "wrong answer",
            "time_spent_seconds": 8,
        },
    )

    progress_response = client.get(
        "/questions",
        params={"limit": 100, "include_progress": True},
    )
    updated = next(item for item in progress_response.json() if item["id"] == question_id)
    assert updated["progress_status"] == "attempted"
    assert updated["attempt_count"] == 1


@pytest.mark.integration
def test_dashboard_mastery_updates_after_solved_attempt(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    initial_dashboard = client.get("/dashboard").json()
    probability = next(
        item for item in initial_dashboard["topic_mastery"] if item["slug"] == "probability"
    )
    assert probability["mastery_score"] == 0.0

    questions_response = client.get(
        "/questions",
        params={"topic_slug": "probability", "limit": 1},
    )
    question = questions_response.json()[0]
    detail_response = client.get(f"/questions/{question['id']}")
    short_answer = detail_response.json()["short_answer"]
    assert short_answer is not None

    client.post(
        "/attempts",
        json={
            "question_id": question["id"],
            "answer": short_answer,
            "time_spent_seconds": 12,
        },
    )

    updated_dashboard = client.get("/dashboard").json()
    updated_probability = next(
        item for item in updated_dashboard["topic_mastery"] if item["slug"] == "probability"
    )
    assert updated_probability["solved_count"] == 1
    assert updated_probability["attempts_count"] == 1
    assert updated_probability["mastery_score"] > 0.0
