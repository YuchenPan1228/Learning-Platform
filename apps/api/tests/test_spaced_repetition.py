from datetime import UTC, datetime, timedelta

from app.models.enums import FlashcardReviewRating
from app.services.spaced_repetition import schedule_flashcard_review


def test_again_resets_repetitions_and_schedules_soon() -> None:
    reviewed_at = datetime(2026, 7, 21, 12, 0, tzinfo=UTC)
    result = schedule_flashcard_review(
        rating=FlashcardReviewRating.AGAIN,
        interval_days=10.0,
        ease_factor=2.5,
        repetitions=4,
        reviewed_at=reviewed_at,
    )

    assert result.repetitions == 0
    assert result.interval_days == 0.0
    assert result.ease_factor == 2.3
    assert result.next_review_at == reviewed_at + timedelta(minutes=10)


def test_good_uses_learning_steps_then_ease_interval() -> None:
    reviewed_at = datetime(2026, 7, 21, 12, 0, tzinfo=UTC)

    first = schedule_flashcard_review(
        rating=FlashcardReviewRating.GOOD,
        interval_days=0.0,
        ease_factor=2.5,
        repetitions=0,
        reviewed_at=reviewed_at,
    )
    assert first.interval_days == 1.0
    assert first.repetitions == 1
    assert first.next_review_at == reviewed_at + timedelta(days=1)

    second = schedule_flashcard_review(
        rating=FlashcardReviewRating.GOOD,
        interval_days=first.interval_days,
        ease_factor=first.ease_factor,
        repetitions=first.repetitions,
        reviewed_at=reviewed_at,
    )
    assert second.interval_days == 3.0
    assert second.repetitions == 2

    third = schedule_flashcard_review(
        rating=FlashcardReviewRating.GOOD,
        interval_days=second.interval_days,
        ease_factor=second.ease_factor,
        repetitions=second.repetitions,
        reviewed_at=reviewed_at,
    )
    assert third.interval_days == 7.5
    assert third.repetitions == 3
    assert third.next_review_at == reviewed_at + timedelta(days=7.5)


def test_easy_increases_ease_and_interval() -> None:
    reviewed_at = datetime(2026, 7, 21, 12, 0, tzinfo=UTC)
    result = schedule_flashcard_review(
        rating=FlashcardReviewRating.EASY,
        interval_days=3.0,
        ease_factor=2.5,
        repetitions=2,
        reviewed_at=reviewed_at,
    )

    assert result.ease_factor == 2.65
    assert result.repetitions == 3
    assert result.interval_days == round(3.0 * 2.65 * 1.3, 4)
    assert result.next_review_at == reviewed_at + timedelta(days=result.interval_days)
