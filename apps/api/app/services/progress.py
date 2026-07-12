from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.attempt import Attempt
from app.models.constants import LOCAL_USER_ID
from app.models.enums import (
    ContentStatus,
    ManualQuestionProgressStatus,
    QuestionProgressStatus,
)
from app.models.question import Question
from app.models.user_question_progress import UserQuestionProgress
from app.schemas.progress import QuestionProgressRead, SetQuestionProgressRequest


@dataclass(frozen=True, slots=True)
class QuestionProgress:
    status: QuestionProgressStatus
    attempt_count: int
    manually_marked: bool


def _status_from_attempts(*, attempt_count: int, correct_count: int) -> QuestionProgressStatus:
    if attempt_count == 0:
        return QuestionProgressStatus.NOT_ATTEMPTED
    if correct_count > 0:
        return QuestionProgressStatus.SOLVED
    return QuestionProgressStatus.ATTEMPTED


def _load_manual_overrides(session: Session) -> dict[int, ManualQuestionProgressStatus]:
    rows = session.scalars(
        select(UserQuestionProgress).where(UserQuestionProgress.user_id == LOCAL_USER_ID),
    ).all()
    return {row.question_id: row.manual_status for row in rows}


def _resolve_status(
    *,
    attempt_count: int,
    correct_count: int,
    manual_status: ManualQuestionProgressStatus | None,
) -> tuple[QuestionProgressStatus, bool]:
    if manual_status == ManualQuestionProgressStatus.SOLVED:
        return QuestionProgressStatus.SOLVED, True
    if manual_status == ManualQuestionProgressStatus.NOT_ATTEMPTED:
        return QuestionProgressStatus.NOT_ATTEMPTED, True
    return _status_from_attempts(attempt_count=attempt_count, correct_count=correct_count), False


def get_progress_by_question_id(session: Session) -> dict[int, QuestionProgress]:
    manual_overrides = _load_manual_overrides(session)
    attempt_rows = session.execute(
        select(
            Attempt.question_id,
            func.count(Attempt.id).label("attempt_count"),
            func.count(Attempt.id)
            .filter(Attempt.is_correct.is_(True))
            .label("correct_count"),
        )
        .where(Attempt.user_id == LOCAL_USER_ID)
        .group_by(Attempt.question_id),
    ).all()

    progress: dict[int, QuestionProgress] = {}
    for row in attempt_rows:
        question_id = int(row.question_id)
        attempt_count = int(row.attempt_count)
        correct_count = int(row.correct_count)
        status, manually_marked = _resolve_status(
            attempt_count=attempt_count,
            correct_count=correct_count,
            manual_status=manual_overrides.get(question_id),
        )
        progress[question_id] = QuestionProgress(
            status=status,
            attempt_count=attempt_count,
            manually_marked=manually_marked,
        )

    for question_id, manual_status in manual_overrides.items():
        if question_id in progress:
            continue
        status, manually_marked = _resolve_status(
            attempt_count=0,
            correct_count=0,
            manual_status=manual_status,
        )
        progress[question_id] = QuestionProgress(
            status=status,
            attempt_count=0,
            manually_marked=manually_marked,
        )

    return progress


def get_question_progress(session: Session, question_id: int) -> QuestionProgress:
    progress = get_progress_by_question_id(session)
    return progress.get(
        question_id,
        QuestionProgress(
            status=QuestionProgressStatus.NOT_ATTEMPTED,
            attempt_count=0,
            manually_marked=False,
        ),
    )


def set_question_progress(
    session: Session,
    *,
    question_id: int,
    payload: SetQuestionProgressRequest,
) -> QuestionProgressRead:
    existing = session.scalar(
        select(UserQuestionProgress).where(
            UserQuestionProgress.user_id == LOCAL_USER_ID,
            UserQuestionProgress.question_id == question_id,
        ),
    )
    if existing is None:
        session.add(
            UserQuestionProgress(
                user_id=LOCAL_USER_ID,
                question_id=question_id,
                manual_status=payload.status,
            ),
        )
    else:
        existing.manual_status = payload.status

    session.commit()
    progress = get_question_progress(session, question_id)
    return QuestionProgressRead(
        question_id=question_id,
        status=progress.status,
        attempt_count=progress.attempt_count,
        manually_marked=progress.manually_marked,
    )


@dataclass(frozen=True, slots=True)
class TopicProgressStats:
    mastery_score: float
    attempts_count: int
    solved_count: int
    total_questions: int


def get_topic_progress_stats(session: Session) -> dict[int, TopicProgressStats]:
    questions = session.scalars(
        select(Question).where(Question.status == ContentStatus.APPROVED),
    ).all()
    progress_by_question_id = get_progress_by_question_id(session)

    topic_question_ids: dict[int, list[int]] = {}
    subtopic_question_ids: dict[int, list[int]] = {}

    for question in questions:
        topic_question_ids.setdefault(question.topic_id, []).append(question.id)
        if question.subtopic_id is not None:
            subtopic_question_ids.setdefault(question.subtopic_id, []).append(question.id)

    stats: dict[int, TopicProgressStats] = {}

    def build_stats(topic_id: int, question_ids: list[int]) -> TopicProgressStats:
        total = len(question_ids)
        if total == 0:
            return TopicProgressStats(
                mastery_score=0.0,
                attempts_count=0,
                solved_count=0,
                total_questions=0,
            )

        solved_count = sum(
            1
            for question_id in question_ids
            if progress_by_question_id.get(question_id) is not None
            and progress_by_question_id[question_id].status == QuestionProgressStatus.SOLVED
        )
        attempts_count = sum(
            progress_by_question_id.get(
                question_id,
                QuestionProgress(
                    status=QuestionProgressStatus.NOT_ATTEMPTED,
                    attempt_count=0,
                    manually_marked=False,
                ),
            ).attempt_count
            for question_id in question_ids
        )
        mastery_score = round((solved_count / total) * 100, 1)
        return TopicProgressStats(
            mastery_score=mastery_score,
            attempts_count=attempts_count,
            solved_count=solved_count,
            total_questions=total,
        )

    all_topic_ids = set(topic_question_ids) | set(subtopic_question_ids)
    for topic_id in all_topic_ids:
        root_ids = topic_question_ids.get(topic_id, [])
        subtopic_ids = subtopic_question_ids.get(topic_id, [])
        if subtopic_ids:
            stats[topic_id] = build_stats(topic_id, subtopic_ids)
        elif root_ids:
            stats[topic_id] = build_stats(topic_id, root_ids)

    return stats
