from unittest.mock import MagicMock

import pytest
from app.models.enums import Difficulty
from app.models.flashcard import Flashcard
from app.models.topic import Topic
from app.schemas.admin_flashcards import FlashcardUpdate
from app.services.admin_flashcards import (
    FlashcardEditorError,
    delete_flashcard,
    update_flashcard,
)
from fastapi.testclient import TestClient


def _flashcard(*, flashcard_id: int = 1) -> Flashcard:
    topic = Topic(id=10, slug="bayes", name="Bayes", order_index=0)
    card = Flashcard(
        front="Old front",
        back="Old back",
        topic_id=10,
        difficulty=Difficulty.EASY,
    )
    card.id = flashcard_id
    card.topic = topic
    return card


def test_update_flashcard_edits_content() -> None:
    session = MagicMock()
    card = _flashcard()
    session.scalar.side_effect = [card, card]

    result = update_flashcard(
        session,
        1,
        FlashcardUpdate(front="New front", back="New back", difficulty=Difficulty.MEDIUM),
    )

    assert card.front == "New front"
    assert card.back == "New back"
    assert card.difficulty is Difficulty.MEDIUM
    assert result.front == "New front"
    session.commit.assert_called_once()


def test_update_flashcard_rejects_empty_patch() -> None:
    session = MagicMock()
    session.scalar.return_value = _flashcard()

    with pytest.raises(FlashcardEditorError, match="no fields"):
        update_flashcard(session, 1, FlashcardUpdate())


def test_delete_flashcard_removes_row() -> None:
    session = MagicMock()
    card = _flashcard(flashcard_id=7)
    session.get.return_value = card

    deleted_id = delete_flashcard(session, 7)
    assert deleted_id == 7
    session.delete.assert_called_once_with(card)
    session.commit.assert_called_once()


@pytest.mark.integration
def test_admin_flashcard_editor_update_and_delete(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    list_response = client.get("/admin/flashcards", params={"topic_slug": "probability"})
    assert list_response.status_code == 200
    items = list_response.json()["items"]
    assert len(items) >= 1
    flashcard_id = items[0]["id"]

    patch_response = client.patch(
        f"/admin/flashcards/{flashcard_id}",
        json={"front": "Edited front for admin test", "back": "Edited back"},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["front"] == "Edited front for admin test"

    detail_response = client.get(f"/admin/flashcards/{flashcard_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["back"] == "Edited back"

    delete_response = client.delete(f"/admin/flashcards/{flashcard_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["deleted_id"] == flashcard_id

    missing = client.get(f"/admin/flashcards/{flashcard_id}")
    assert missing.status_code == 404
