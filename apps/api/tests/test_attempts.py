import pytest
from app.models.attempt import Attempt
from fastapi.testclient import TestClient
from sqlalchemy import select


@pytest.mark.integration
def test_record_attempt_persists_graded_answer(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    questions_response = client.get("/questions", params={"limit": 1})
    question = questions_response.json()[0]
    detail_response = client.get(f"/questions/{question['id']}")
    short_answer = detail_response.json()["short_answer"]
    assert short_answer is not None

    response = client.post(
        "/attempts",
        json={
            "question_id": question["id"],
            "answer": short_answer,
            "time_spent_seconds": 42,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["question_id"] == question["id"]
    assert payload["topic_id"] == question["topic_id"]
    assert payload["answer"] == short_answer
    assert payload["supported"] is True
    assert payload["is_correct"] is True
    assert payload["score"] == 1.0
    assert payload["time_spent_seconds"] == 42
    assert payload["feedback"]
    assert payload["created_at"]


@pytest.mark.integration
def test_record_attempt_marks_incorrect_answers(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    questions_response = client.get("/questions", params={"limit": 1})
    question_id = questions_response.json()[0]["id"]

    response = client.post(
        "/attempts",
        json={
            "question_id": question_id,
            "answer": "definitely-wrong-answer",
            "time_spent_seconds": 18,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["supported"] is True
    assert payload["is_correct"] is False
    assert payload["score"] == 0.0


@pytest.mark.integration
def test_record_attempt_without_short_answer_stores_null_correctness(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    questions_response = client.get("/questions", params={"limit": 100})
    unsupported_question = next(
        question
        for question in questions_response.json()
        if client.get(f"/questions/{question['id']}").json()["short_answer"] is None
    )

    response = client.post(
        "/attempts",
        json={
            "question_id": unsupported_question["id"],
            "answer": "interval invariant",
            "time_spent_seconds": 90,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["supported"] is False
    assert payload["is_correct"] is None
    assert payload["score"] is None


@pytest.mark.integration
def test_record_attempt_returns_404_for_missing_question(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    response = client.post(
        "/attempts",
        json={
            "question_id": 999999,
            "answer": "1",
            "time_spent_seconds": 5,
        },
    )
    assert response.status_code == 404


@pytest.mark.integration
def test_record_attempt_rejects_invalid_payload(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    questions_response = client.get("/questions", params={"limit": 1})
    question_id = questions_response.json()[0]["id"]

    empty_answer_response = client.post(
        "/attempts",
        json={
            "question_id": question_id,
            "answer": "",
            "time_spent_seconds": 5,
        },
    )
    assert empty_answer_response.status_code == 422

    negative_time_response = client.post(
        "/attempts",
        json={
            "question_id": question_id,
            "answer": "1",
            "time_spent_seconds": -1,
        },
    )
    assert negative_time_response.status_code == 422


@pytest.mark.integration
def test_record_attempt_writes_to_database(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
    database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.config import get_settings
    from app.db import get_session_factory, reset_db_state

    monkeypatch.setenv("DATABASE_URL", database_url)
    get_settings.cache_clear()
    reset_db_state()

    questions_response = client.get("/questions", params={"limit": 1})
    question = questions_response.json()[0]

    response = client.post(
        "/attempts",
        json={
            "question_id": question["id"],
            "answer": "test answer",
            "time_spent_seconds": 12,
        },
    )
    assert response.status_code == 200
    attempt_id = response.json()["id"]

    session = get_session_factory()()
    try:
        attempt = session.scalar(select(Attempt).where(Attempt.id == attempt_id))
        assert attempt is not None
        assert attempt.question_id == question["id"]
        assert attempt.answer == "test answer"
        assert attempt.time_spent_seconds == 12
    finally:
        session.close()
