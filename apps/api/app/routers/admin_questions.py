from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import SessionDep
from app.models.enums import ContentStatus
from app.schemas.admin_questions import (
    QuestionDeleteResponse,
    QuestionListResponse,
    QuestionUpdate,
)
from app.schemas.question import QuestionDetailRead
from app.services.admin_questions import (
    QuestionEditorError,
    delete_question,
    get_question_for_editor,
    list_questions_for_editor,
    update_question,
)

router = APIRouter(prefix="/admin/questions", tags=["admin-questions"])

TopicSlugQuery = Annotated[str | None, Query()]
StatusQuery = Annotated[ContentStatus | None, Query()]


@router.get("")
def list_admin_questions(
    session: SessionDep,
    topic_slug: TopicSlugQuery = None,
    status: StatusQuery = None,
) -> QuestionListResponse:
    items = list_questions_for_editor(session, topic_slug=topic_slug, status=status)
    return QuestionListResponse(items=items)


@router.get("/{question_id}")
def get_admin_question(question_id: int, session: SessionDep) -> QuestionDetailRead:
    try:
        return get_question_for_editor(session, question_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/{question_id}")
def patch_admin_question(
    question_id: int,
    payload: QuestionUpdate,
    session: SessionDep,
) -> QuestionDetailRead:
    try:
        return update_question(session, question_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except QuestionEditorError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/{question_id}")
def delete_admin_question(
    question_id: int,
    session: SessionDep,
) -> QuestionDeleteResponse:
    try:
        deleted_id = delete_question(session, question_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return QuestionDeleteResponse(deleted_id=deleted_id)
