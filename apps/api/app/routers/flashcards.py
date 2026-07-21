from typing import Annotated

from fastapi import APIRouter, Query

from app.dependencies import SessionDep
from app.schemas.flashcard import FlashcardRead, FlashcardReviewRequest, FlashcardReviewResponse
from app.services.flashcard_review import (
    get_flashcard_with_progress,
    list_flashcards_with_progress,
    review_flashcard,
)

router = APIRouter(prefix="/flashcards", tags=["flashcards"])

TopicSlugQuery = Annotated[str | None, Query()]
DueOnlyQuery = Annotated[bool, Query()]
LimitQuery = Annotated[int, Query(ge=1, le=100)]
OffsetQuery = Annotated[int, Query(ge=0)]


@router.get("")
def list_flashcards(
    session: SessionDep,
    topic_slug: TopicSlugQuery = None,
    due_only: DueOnlyQuery = False,
    limit: LimitQuery = 50,
    offset: OffsetQuery = 0,
) -> list[FlashcardRead]:
    return list_flashcards_with_progress(
        session,
        topic_slug=topic_slug,
        due_only=due_only,
        limit=limit,
        offset=offset,
    )


@router.post("/{flashcard_id}/review")
def submit_flashcard_review(
    flashcard_id: int,
    payload: FlashcardReviewRequest,
    session: SessionDep,
) -> FlashcardReviewResponse:
    return review_flashcard(session, flashcard_id=flashcard_id, payload=payload)


@router.get("/{flashcard_id}")
def get_flashcard(flashcard_id: int, session: SessionDep) -> FlashcardRead:
    return get_flashcard_with_progress(session, flashcard_id)
