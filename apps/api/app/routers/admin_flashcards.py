from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import SessionDep
from app.schemas.admin_flashcards import (
    FlashcardDeleteResponse,
    FlashcardListResponse,
    FlashcardUpdate,
)
from app.schemas.flashcard import FlashcardRead
from app.services.admin_flashcards import (
    FlashcardEditorError,
    delete_flashcard,
    get_flashcard_for_editor,
    list_flashcards_for_editor,
    update_flashcard,
)

router = APIRouter(prefix="/admin/flashcards", tags=["admin-flashcards"])

TopicSlugQuery = Annotated[str | None, Query()]


@router.get("")
def list_admin_flashcards(
    session: SessionDep,
    topic_slug: TopicSlugQuery = None,
) -> FlashcardListResponse:
    items = list_flashcards_for_editor(session, topic_slug=topic_slug)
    return FlashcardListResponse(items=items)


@router.get("/{flashcard_id}")
def get_admin_flashcard(flashcard_id: int, session: SessionDep) -> FlashcardRead:
    try:
        return get_flashcard_for_editor(session, flashcard_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/{flashcard_id}")
def patch_admin_flashcard(
    flashcard_id: int,
    payload: FlashcardUpdate,
    session: SessionDep,
) -> FlashcardRead:
    try:
        return update_flashcard(session, flashcard_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except FlashcardEditorError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/{flashcard_id}")
def delete_admin_flashcard(
    flashcard_id: int,
    session: SessionDep,
) -> FlashcardDeleteResponse:
    try:
        deleted_id = delete_flashcard(session, flashcard_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FlashcardDeleteResponse(deleted_id=deleted_id)
