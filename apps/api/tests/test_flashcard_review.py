import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.skip(reason="Flashcard learner API is paused product-side")


@pytest.mark.integration
def test_flashcard_review_updates_next_review_date(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    cards = client.get("/flashcards", params={"limit": 1}).json()["items"]
    assert len(cards) == 1
    flashcard_id = cards[0]["id"]
    assert cards[0]["is_due"] is True
    assert cards[0]["next_review_at"] is None

    review = client.post(
        f"/flashcards/{flashcard_id}/review",
        json={"rating": "good"},
    )
    assert review.status_code == 200
    payload = review.json()
    assert payload["rating"] == "good"
    assert payload["interval_days"] == 1.0
    assert payload["repetitions"] == 1
    assert payload["next_review_at"] is not None
    assert payload["flashcard"]["is_due"] is False

    detail = client.get(f"/flashcards/{flashcard_id}").json()
    assert detail["next_review_at"] == payload["next_review_at"]
    assert detail["repetitions"] == 1

    due_only = client.get("/flashcards", params={"due_only": True, "limit": 100}).json()["items"]
    assert all(card["id"] != flashcard_id for card in due_only)


@pytest.mark.integration
def test_flashcard_review_again_keeps_card_due_soon(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    flashcard_id = client.get("/flashcards", params={"limit": 1}).json()["items"][0]["id"]
    response = client.post(
        f"/flashcards/{flashcard_id}/review",
        json={"rating": "again"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["repetitions"] == 0
    assert payload["interval_days"] == 0.0
