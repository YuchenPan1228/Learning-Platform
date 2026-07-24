from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.flashcard import Flashcard
from app.models.topic import Topic
from app.schemas.admin_flashcards import FlashcardUpdate
from app.schemas.flashcard import FlashcardRead
from app.services.flashcard_review import flashcard_to_read


class FlashcardEditorError(ValueError):
    """Raised when a flashcard editor mutation is invalid."""


def list_flashcards_for_editor(
    session: Session,
    *,
    topic_slug: str | None = None,
) -> list[FlashcardRead]:
    query = select(Flashcard).options(joinedload(Flashcard.topic)).order_by(Flashcard.id.desc())
    if topic_slug is not None:
        topic_ids = _topic_scope_ids(session, topic_slug)
        if topic_ids is None:
            return []
        query = query.where(Flashcard.topic_id.in_(topic_ids))

    flashcards = session.scalars(query).unique().all()
    return [flashcard_to_read(flashcard) for flashcard in flashcards]


def get_flashcard_for_editor(session: Session, flashcard_id: int) -> FlashcardRead:
    flashcard = _get_flashcard(session, flashcard_id)
    return flashcard_to_read(flashcard)


def update_flashcard(
    session: Session,
    flashcard_id: int,
    payload: FlashcardUpdate,
) -> FlashcardRead:
    flashcard = _get_flashcard(session, flashcard_id)
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise FlashcardEditorError("no fields provided to update")

    if "front" in updates and updates["front"] is not None:
        front = updates["front"].strip()
        if not front:
            raise FlashcardEditorError("front must not be blank")
        flashcard.front = front

    if "back" in updates and updates["back"] is not None:
        back = updates["back"].strip()
        if not back:
            raise FlashcardEditorError("back must not be blank")
        flashcard.back = back

    if "difficulty" in updates:
        flashcard.difficulty = updates["difficulty"]

    if "topic_slug" in updates and updates["topic_slug"] is not None:
        topic_id = session.scalar(select(Topic.id).where(Topic.slug == updates["topic_slug"]))
        if topic_id is None:
            raise FlashcardEditorError(f"unknown topic_slug '{updates['topic_slug']}'")
        flashcard.topic_id = topic_id

    session.add(flashcard)
    session.commit()
    return get_flashcard_for_editor(session, flashcard.id)


def delete_flashcard(session: Session, flashcard_id: int) -> int:
    flashcard = session.get(Flashcard, flashcard_id)
    if flashcard is None:
        raise LookupError(f"flashcard {flashcard_id} not found")
    session.delete(flashcard)
    session.commit()
    return flashcard_id


def _get_flashcard(session: Session, flashcard_id: int) -> Flashcard:
    flashcard = session.scalar(
        select(Flashcard).where(Flashcard.id == flashcard_id).options(joinedload(Flashcard.topic)),
    )
    if flashcard is None:
        raise LookupError(f"flashcard {flashcard_id} not found")
    return flashcard


def _topic_scope_ids(session: Session, topic_slug: str) -> list[int] | None:
    topic = session.scalar(
        select(Topic).where(Topic.slug == topic_slug).options(selectinload(Topic.subtopics)),
    )
    if topic is None:
        return None
    topic_ids = [topic.id]
    topic_ids.extend(subtopic.id for subtopic in topic.subtopics)
    return topic_ids
