from fastapi import APIRouter

from app.dependencies import SessionDep
from app.schemas.attempt import AttemptCreate, AttemptRead
from app.schemas.progress import AttemptProgressResponse, QuestionProgressRead
from app.services.attempts import create_attempt
from app.services.progress import get_progress_by_question_id

router = APIRouter(prefix="/attempts", tags=["attempts"])


@router.get("/progress")
def get_attempt_progress(session: SessionDep) -> AttemptProgressResponse:
    progress_by_question_id = get_progress_by_question_id(session)
    return AttemptProgressResponse(
        questions=[
            QuestionProgressRead(
                question_id=question_id,
                status=progress.status,
                attempt_count=progress.attempt_count,
            )
            for question_id, progress in sorted(progress_by_question_id.items())
        ],
    )


@router.post("")
def record_attempt(payload: AttemptCreate, session: SessionDep) -> AttemptRead:
    return create_attempt(
        session,
        question_id=payload.question_id,
        answer=payload.answer,
        time_spent_seconds=payload.time_spent_seconds,
    )
