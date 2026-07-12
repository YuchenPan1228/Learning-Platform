from fastapi import APIRouter

from app.dependencies import SessionDep
from app.schemas.attempt import AttemptCreate, AttemptRead
from app.schemas.progress import QuestionProgressMapRead
from app.services.attempts import create_attempt
from app.services.progress import list_question_progress

router = APIRouter(prefix="/attempts", tags=["attempts"])


@router.get("/progress")
def get_attempt_progress(session: SessionDep) -> QuestionProgressMapRead:
    return QuestionProgressMapRead(items=list_question_progress(session))


@router.post("")
def record_attempt(payload: AttemptCreate, session: SessionDep) -> AttemptRead:
    return create_attempt(
        session,
        question_id=payload.question_id,
        answer=payload.answer,
        time_spent_seconds=payload.time_spent_seconds,
    )
