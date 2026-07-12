import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_attempt_progress_returns_empty_for_new_user(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    response = client.get("/attempts/progress")
    assert response.status_code == 200
    assert response.json() == {"items": []}


@pytest.mark.integration
def test_attempt_progress_reflects_solved_and_attempted_states(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    questions_response = client.get("/questions", params={"limit": 2})
    questions = questions_response.json()
    first_id = questions[0]["id"]
    second_id = questions[1]["id"]
    short_answer = client.get(f"/questions/{first_id}").json()["short_answer"]
    assert short_answer is not None

    correct_response = client.post(
        "/attempts",
        json={
            "question_id": first_id,
            "answer": short_answer,
            "time_spent_seconds": 12,
        },
    )
    assert correct_response.status_code == 200

    incorrect_response = client.post(
        "/attempts",
        json={
            "question_id": second_id,
            "answer": "definitely-wrong",
            "time_spent_seconds": 8,
        },
    )
    assert incorrect_response.status_code == 200

    progress_response = client.get("/attempts/progress")
    assert progress_response.status_code == 200
    items = {item["question_id"]: item for item in progress_response.json()["items"]}

    assert items[first_id]["status"] == "solved"
    assert items[first_id]["attempt_count"] == 1
    assert items[second_id]["status"] == "attempted"
    assert items[second_id]["attempt_count"] == 1


@pytest.mark.integration
def test_questions_include_progress_when_requested(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    questions_response = client.get("/questions", params={"limit": 1})
    question_id = questions_response.json()[0]["id"]
    short_answer = client.get(f"/questions/{question_id}").json()["short_answer"]
    assert short_answer is not None

    client.post(
        "/attempts",
        json={
            "question_id": question_id,
            "answer": short_answer,
            "time_spent_seconds": 5,
        },
    )

    response = client.get("/questions", params={"limit": 5, "include_progress": True})
    assert response.status_code == 200
    question = next(item for item in response.json() if item["id"] == question_id)
    assert question["progress_status"] == "solved"

    without_progress = client.get("/questions", params={"limit": 5})
    question_without = next(item for item in without_progress.json() if item["id"] == question_id)
    assert question_without["progress_status"] is None
