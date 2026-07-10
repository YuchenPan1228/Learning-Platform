from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.dependencies import SessionDep
from app.models.flashcard import Flashcard
from app.models.topic import Topic
from app.schemas.flashcard import FlashcardRead

router = APIRouter(prefix="/flashcards", tags=["flashcards"])


def _flashcard_read(flashcard: Flashcard) -> FlashcardRead:
    return FlashcardRead(
        id=flashcard.id,
        front=flashcard.front,
        back=flashcard.back,
        topic_id=flashcard.topic_id,
        topic_slug=flashcard.topic.slug,
        difficulty=flashcard.difficulty,
    )


@router.get("")
def list_flashcards(
    session: SessionDep,
    topic_slug: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[FlashcardRead]:
    query = (
        select(Flashcard)
        .options(joinedload(Flashcard.topic))
        .order_by(Flashcard.id)
        .limit(limit)
        .offset(offset)
    )
    if topic_slug is not None:
        query = query.join(Flashcard.topic).where(Topic.slug == topic_slug)

    flashcards = session.scalars(query).unique().all()
    return [_flashcard_read(flashcard) for flashcard in flashcards]


@router.get("/{flashcard_id}")
def get_flashcard(flashcard_id: int, session: SessionDep) -> FlashcardRead:
    flashcard = session.scalar(
        select(Flashcard).where(Flashcard.id == flashcard_id).options(joinedload(Flashcard.topic)),
    )
    if flashcard is None:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    return _flashcard_read(flashcard)
