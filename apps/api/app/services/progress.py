from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.attempt import Attempt
from app.models.constants import LOCAL_USER_ID
from app.models.enums import ContentStatus, QuestionProgressStatus
from app.models.question import Question
from app.schemas.progress import QuestionProgressRead


def _status_from_attempts(has_attempt: bool, has_correct: bool) -> QuestionProgressStatus:
    if has_correct:
        return QuestionProgressStatus.SOLVED
    if has_attempt:
        return QuestionProgressStatus.ATTEMPTED
    return QuestionProgressStatus.NOT_ATTEMPTED


def get_question_progress_map(
    session: Session,
    *,
    user_id: str = LOCAL_USER_ID,
) -> dict[int, QuestionProgressStatus]:
    rows = session.execute(
        select(
            Attempt.question_id,
            func.count(Attempt.id),
            func.bool_or(Attempt.is_correct.is_(True)),
        )
        .where(Attempt.user_id == user_id)
        .group_by(Attempt.question_id),
    ).all()

    return {
        question_id: _status_from_attempts(True, bool(has_correct))
        for question_id, _attempt_count, has_correct in rows
    }


def list_question_progress(
    session: Session,
    *,
    user_id: str = LOCAL_USER_ID,
) -> list[QuestionProgressRead]:
    rows = session.execute(
        select(
            Attempt.question_id,
            func.count(Attempt.id),
            func.bool_or(Attempt.is_correct.is_(True)),
        )
        .where(Attempt.user_id == user_id)
        .group_by(Attempt.question_id)
        .order_by(Attempt.question_id),
    ).all()

    return [
        QuestionProgressRead(
            question_id=question_id,
            status=_status_from_attempts(True, bool(has_correct)),
            attempt_count=attempt_count,
        )
        for question_id, attempt_count, has_correct in rows
    ]



def question_ids_for_root_topic(session: Session, root_topic_id: int) -> list[int]:
    return list(
        session.scalars(
            select(Question.id)
            .where(Question.status == ContentStatus.APPROVED)
            .where(Question.topic_id == root_topic_id)
            .order_by(Question.id),
        ).all(),
    )


def question_ids_for_topic_scope(session: Session, topic_id: int) -> list[int]:
    return list(
        session.scalars(
            select(Question.id)
            .where(Question.status == ContentStatus.APPROVED)
            .where(
                or_(
                    Question.topic_id == topic_id,
                    Question.subtopic_id == topic_id,
                ),
            )
            .order_by(Question.id),
        ).all(),
    )


def mastery_for_topic_ids(
    question_ids: list[int],
    progress_map: dict[int, QuestionProgressStatus],
) -> float:
    if not question_ids:
        return 0.0
    solved_count = sum(
        1 for question_id in question_ids if progress_map.get(question_id) == QuestionProgressStatus.SOLVED
    )
    return round((solved_count / len(question_ids)) * 100, 1)


def attempts_count_for_root_topic(
    session: Session,
    root_topic_id: int,
    *,
    user_id: str = LOCAL_USER_ID,
) -> int:
    count = session.scalar(
        select(func.count(Attempt.id))
        .join(Question, Attempt.question_id == Question.id)
        .where(Attempt.user_id == user_id)
        .where(Question.topic_id == root_topic_id),
    )
    return int(count or 0)
