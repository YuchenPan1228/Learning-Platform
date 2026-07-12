from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.attempt import Attempt
from app.models.constants import LOCAL_USER_ID
from app.models.question import Question
from app.schemas.attempt import AttemptRead
from app.services.answer_check import attempt_score, grade_short_answer


def create_attempt(
    session: Session,
    *,
    question_id: int,
    answer: str,
    time_spent_seconds: int,
) -> AttemptRead:
    question = session.get(Question, question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    supported, is_correct, feedback = grade_short_answer(
        short_answer=question.short_answer,
        user_answer=answer,
    )
    attempt = Attempt(
        user_id=LOCAL_USER_ID,
        question_id=question_id,
        answer=answer,
        is_correct=is_correct if supported else None,
        score=attempt_score(supported=supported, is_correct=is_correct),
        feedback=feedback,
        time_spent_seconds=time_spent_seconds,
    )
    session.add(attempt)
    session.commit()
    session.refresh(attempt)

    return AttemptRead(
        id=attempt.id,
        question_id=attempt.question_id,
        topic_id=question.topic_id,
        answer=attempt.answer,
        supported=supported,
        is_correct=attempt.is_correct,
        score=attempt.score,
        feedback=attempt.feedback,
        time_spent_seconds=attempt.time_spent_seconds,
        created_at=attempt.created_at,
    )
