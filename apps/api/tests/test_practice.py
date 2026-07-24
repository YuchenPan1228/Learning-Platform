import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_self_check_endpoint_grades_supported_questions(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    questions_response = client.get("/questions", params={"limit": 1})
    question_id = questions_response.json()["items"][0]["id"]
    detail_response = client.get(f"/questions/{question_id}")
    short_answer = detail_response.json()["short_answer"]
    assert short_answer is not None

    graded_response = client.post(
        f"/questions/{question_id}/self-check",
        json={"answer": short_answer},
    )
    assert graded_response.status_code == 200
    payload = graded_response.json()
    assert payload["question_id"] == question_id
    assert payload["supported"] is True
    assert payload["is_correct"] is True
    assert payload["feedback"]

    wrong_response = client.post(
        f"/questions/{question_id}/self-check",
        json={"answer": "definitely-wrong-answer"},
    )
    assert wrong_response.status_code == 200
    assert wrong_response.json()["is_correct"] is False


@pytest.mark.integration
def test_self_check_returns_404_for_missing_question(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    response = client.post("/questions/999999/self-check", json={"answer": "1"})
    assert response.status_code == 404


@pytest.mark.integration
def test_self_check_rejects_empty_answer(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    questions_response = client.get("/questions", params={"limit": 1})
    question_id = questions_response.json()["items"][0]["id"]

    response = client.post(f"/questions/{question_id}/self-check", json={"answer": ""})
    assert response.status_code == 422
