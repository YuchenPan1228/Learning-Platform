from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.models.enums import FlashcardReviewRating

INITIAL_EASE_FACTOR = 2.5
MINIMUM_EASE_FACTOR = 1.3
AGAIN_INTERVAL_MINUTES = 10


@dataclass(frozen=True, slots=True)
class SchedulingState:
    interval_days: float
    ease_factor: float
    repetitions: int
    next_review_at: datetime


def schedule_flashcard_review(
    *,
    rating: FlashcardReviewRating,
    interval_days: float,
    ease_factor: float,
    repetitions: int,
    reviewed_at: datetime | None = None,
) -> SchedulingState:
    """Deterministic SM-2-lite scheduler for again/good/easy ratings."""
    now = reviewed_at or datetime.now(UTC)
    if now.tzinfo is None:
        now = now.replace(tzinfo=UTC)

    ease = ease_factor if ease_factor > 0 else INITIAL_EASE_FACTOR
    interval = max(interval_days, 0.0)
    reps = max(repetitions, 0)

    if rating == FlashcardReviewRating.AGAIN:
        next_ease = max(MINIMUM_EASE_FACTOR, ease - 0.20)
        return SchedulingState(
            interval_days=0.0,
            ease_factor=round(next_ease, 4),
            repetitions=0,
            next_review_at=now + timedelta(minutes=AGAIN_INTERVAL_MINUTES),
        )

    if rating == FlashcardReviewRating.GOOD:
        if reps == 0:
            next_interval = 1.0
        elif reps == 1:
            next_interval = 3.0
        else:
            next_interval = max(1.0, round(interval * ease, 4))
        return SchedulingState(
            interval_days=next_interval,
            ease_factor=round(ease, 4),
            repetitions=reps + 1,
            next_review_at=now + timedelta(days=next_interval),
        )

    # easy
    next_ease = ease + 0.15
    if reps == 0:
        next_interval = 3.0
    elif reps == 1:
        next_interval = 7.0
    else:
        next_interval = max(1.0, round(interval * next_ease * 1.3, 4))
    return SchedulingState(
        interval_days=next_interval,
        ease_factor=round(next_ease, 4),
        repetitions=reps + 1,
        next_review_at=now + timedelta(days=next_interval),
    )
