from fastapi import APIRouter

from app.dependencies import SessionDep
from app.schemas.attempt import AttemptCreate, AttemptRead
from app.services.attempts import create_attempt

router = APIRouter(prefix="/attempts", tags=["attempts"])


@router.post("")
def record_attempt(payload: AttemptCreate, session: SessionDep) -> AttemptRead:
    return create_attempt(
        session,
        question_id=payload.question_id,
        answer=payload.answer,
        time_spent_seconds=payload.time_spent_seconds,
    )
