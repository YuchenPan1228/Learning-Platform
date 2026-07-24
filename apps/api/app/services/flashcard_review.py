from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.constants import LOCAL_USER_ID
from app.models.flashcard import Flashcard
from app.models.topic import Topic
from app.models.user_flashcard_progress import UserFlashcardProgress
from app.models.user_topic_mastery import UserTopicMastery
from app.schemas.flashcard import FlashcardRead, FlashcardReviewRequest, FlashcardReviewResponse
from app.services.spaced_repetition import INITIAL_EASE_FACTOR, schedule_flashcard_review


def _topic_scope_ids(session: Session, topic_slug: str) -> list[int] | None:
    topic = session.scalar(
        select(Topic).where(Topic.slug == topic_slug).options(selectinload(Topic.subtopics)),
    )
    if topic is None:
        return None
    topic_ids = [topic.id]
    topic_ids.extend(subtopic.id for subtopic in topic.subtopics)
    return topic_ids


def _progress_by_flashcard_id(session: Session) -> dict[int, UserFlashcardProgress]:
    rows = session.scalars(
        select(UserFlashcardProgress).where(UserFlashcardProgress.user_id == LOCAL_USER_ID),
    ).all()
    return {row.flashcard_id: row for row in rows}


def flashcard_to_read(
    flashcard: Flashcard,
    progress: UserFlashcardProgress | None = None,
) -> FlashcardRead:
    return FlashcardRead(
        id=flashcard.id,
        front=flashcard.front,
        back=flashcard.back,
        topic_id=flashcard.topic_id,
        topic_slug=flashcard.topic.slug,
        difficulty=flashcard.difficulty,
        next_review_at=progress.next_review_at if progress is not None else None,
        interval_days=progress.interval_days if progress is not None else None,
        ease_factor=progress.ease_factor if progress is not None else None,
        repetitions=progress.repetitions if progress is not None else None,
        last_reviewed_at=progress.last_reviewed_at if progress is not None else None,
        last_rating=progress.last_rating if progress is not None else None,
        is_due=progress is None or progress.next_review_at <= datetime.now(UTC),
    )


def count_due_flashcards(session: Session) -> int:
    """Count flashcards due now (never reviewed or next_review_at <= now)."""
    now = datetime.now(UTC)
    total = session.scalar(select(func.count()).select_from(Flashcard)) or 0
    not_due = (
        session.scalar(
            select(func.count())
            .select_from(UserFlashcardProgress)
            .where(
                UserFlashcardProgress.user_id == LOCAL_USER_ID,
                UserFlashcardProgress.next_review_at > now,
            ),
        )
        or 0
    )
    return max(int(total) - int(not_due), 0)


def list_flashcards_with_progress(
    session: Session,
    *,
    topic_slug: str | None = None,
    due_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[FlashcardRead], int]:
    query = select(Flashcard).options(joinedload(Flashcard.topic)).order_by(Flashcard.id)
    count_query = select(func.count()).select_from(Flashcard)

    if topic_slug is not None:
        topic_ids = _topic_scope_ids(session, topic_slug)
        if topic_ids is None:
            return [], 0
        query = query.where(Flashcard.topic_id.in_(topic_ids))
        count_query = count_query.where(Flashcard.topic_id.in_(topic_ids))

    if due_only:
        now = datetime.now(UTC)
        due_join = (
            UserFlashcardProgress,
            (UserFlashcardProgress.flashcard_id == Flashcard.id)
            & (UserFlashcardProgress.user_id == LOCAL_USER_ID),
        )
        due_filter = or_(
            UserFlashcardProgress.flashcard_id.is_(None),
            UserFlashcardProgress.next_review_at <= now,
        )
        query = query.outerjoin(*due_join).where(due_filter)
        count_query = count_query.outerjoin(*due_join).where(due_filter)

    total = int(session.scalar(count_query) or 0)
    query = query.limit(limit).offset(offset)
    flashcards = session.scalars(query).unique().all()
    progress_by_id = _progress_by_flashcard_id(session)
    items = [
        flashcard_to_read(flashcard, progress_by_id.get(flashcard.id)) for flashcard in flashcards
    ]
    return items, total


def get_flashcard_with_progress(session: Session, flashcard_id: int) -> FlashcardRead:
    flashcard = session.scalar(
        select(Flashcard).where(Flashcard.id == flashcard_id).options(joinedload(Flashcard.topic)),
    )
    if flashcard is None:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    progress = session.scalar(
        select(UserFlashcardProgress).where(
            UserFlashcardProgress.user_id == LOCAL_USER_ID,
            UserFlashcardProgress.flashcard_id == flashcard_id,
        ),
    )
    return flashcard_to_read(flashcard, progress)


def _update_topic_next_review(session: Session, topic_id: int) -> None:
    from sqlalchemy import func

    earliest = session.scalar(
        select(func.min(UserFlashcardProgress.next_review_at))
        .join(Flashcard, Flashcard.id == UserFlashcardProgress.flashcard_id)
        .where(
            UserFlashcardProgress.user_id == LOCAL_USER_ID,
            Flashcard.topic_id == topic_id,
        ),
    )
    row = session.scalar(
        select(UserTopicMastery).where(
            UserTopicMastery.user_id == LOCAL_USER_ID,
            UserTopicMastery.topic_id == topic_id,
        ),
    )
    if row is None:
        row = UserTopicMastery(
            user_id=LOCAL_USER_ID,
            topic_id=topic_id,
            mastery_score=0.0,
            attempts_count=0,
        )
        session.add(row)
    row.next_review_at = earliest


def review_flashcard(
    session: Session,
    *,
    flashcard_id: int,
    payload: FlashcardReviewRequest,
) -> FlashcardReviewResponse:
    flashcard = session.scalar(
        select(Flashcard).where(Flashcard.id == flashcard_id).options(joinedload(Flashcard.topic)),
    )
    if flashcard is None:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    progress = session.scalar(
        select(UserFlashcardProgress).where(
            UserFlashcardProgress.user_id == LOCAL_USER_ID,
            UserFlashcardProgress.flashcard_id == flashcard_id,
        ),
    )
    reviewed_at = datetime.now(UTC)
    if progress is None:
        scheduled = schedule_flashcard_review(
            rating=payload.rating,
            interval_days=0.0,
            ease_factor=INITIAL_EASE_FACTOR,
            repetitions=0,
            reviewed_at=reviewed_at,
        )
        progress = UserFlashcardProgress(
            user_id=LOCAL_USER_ID,
            flashcard_id=flashcard_id,
            interval_days=scheduled.interval_days,
            ease_factor=scheduled.ease_factor,
            repetitions=scheduled.repetitions,
            next_review_at=scheduled.next_review_at,
            last_reviewed_at=reviewed_at,
            last_rating=payload.rating,
        )
        session.add(progress)
    else:
        scheduled = schedule_flashcard_review(
            rating=payload.rating,
            interval_days=progress.interval_days,
            ease_factor=progress.ease_factor,
            repetitions=progress.repetitions,
            reviewed_at=reviewed_at,
        )
        progress.interval_days = scheduled.interval_days
        progress.ease_factor = scheduled.ease_factor
        progress.repetitions = scheduled.repetitions
        progress.next_review_at = scheduled.next_review_at
        progress.last_reviewed_at = reviewed_at
        progress.last_rating = payload.rating

    _update_topic_next_review(session, flashcard.topic_id)
    session.commit()
    session.refresh(progress)
    session.refresh(flashcard)

    card = flashcard_to_read(flashcard, progress)
    return FlashcardReviewResponse(
        flashcard=card,
        rating=payload.rating,
        next_review_at=progress.next_review_at,
        interval_days=progress.interval_days,
        ease_factor=progress.ease_factor,
        repetitions=progress.repetitions,
    )
