from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.attempt import Attempt
from app.models.constants import LOCAL_USER_ID
from app.models.enums import LearningSignalType
from app.models.learning_signal import LearningSignal
from app.models.question import Question
from app.schemas.analytics import (
    AttemptHistoryItemRead,
    LearningAnalyticsRead,
    SearchMissRead,
    WeakConceptRead,
)
from app.services.flashcard_review import count_due_flashcards
from app.services.mastery import get_mastery

WEAK_MASTERY_THRESHOLD = 50.0
WEAK_CONCEPT_LIMIT = 15
ATTEMPT_HISTORY_LIMIT = 25
SEARCH_MISS_LIMIT = 25


def _weak_concepts(session: Session) -> list[WeakConceptRead]:
    mastery = get_mastery(session)
    weak = [
        concept
        for concept in mastery.concept_mastery
        if concept.mastery_score < WEAK_MASTERY_THRESHOLD
    ]
    weak.sort(key=lambda item: (item.mastery_score, -item.attempts_count, item.concept_id))
    return [
        WeakConceptRead(
            concept_id=concept.concept_id,
            slug=concept.slug,
            name=concept.name,
            topic_id=concept.topic_id,
            topic_slug=concept.topic_slug,
            mastery_score=concept.mastery_score,
            attempts_count=concept.attempts_count,
        )
        for concept in weak[:WEAK_CONCEPT_LIMIT]
    ]


def _attempt_history(session: Session) -> list[AttemptHistoryItemRead]:
    attempts = (
        session.scalars(
            select(Attempt)
            .where(Attempt.user_id == LOCAL_USER_ID)
            .options(joinedload(Attempt.question).joinedload(Question.topic))
            .order_by(Attempt.created_at.desc(), Attempt.id.desc())
            .limit(ATTEMPT_HISTORY_LIMIT),
        )
        .unique()
        .all()
    )

    items: list[AttemptHistoryItemRead] = []
    for attempt in attempts:
        question = attempt.question
        items.append(
            AttemptHistoryItemRead(
                id=attempt.id,
                question_id=attempt.question_id,
                question_title=question.title,
                topic_id=question.topic_id,
                topic_slug=question.topic.slug,
                is_correct=attempt.is_correct,
                score=attempt.score,
                time_spent_seconds=attempt.time_spent_seconds,
                created_at=attempt.created_at,
            ),
        )
    return items


def _search_misses(session: Session) -> list[SearchMissRead]:
    signals = session.scalars(
        select(LearningSignal)
        .where(
            LearningSignal.user_id == LOCAL_USER_ID,
            LearningSignal.signal_type == LearningSignalType.SEARCH_MISS,
        )
        .order_by(LearningSignal.created_at.desc(), LearningSignal.id.desc())
        .limit(SEARCH_MISS_LIMIT),
    ).all()

    misses: list[SearchMissRead] = []
    for signal in signals:
        payload = signal.payload_json or {}
        query = payload.get("query")
        if not isinstance(query, str) or not query:
            continue
        topic_slug = payload.get("topic_slug")
        types_raw = payload.get("types") or []
        types = [str(item) for item in types_raw] if isinstance(types_raw, list) else []
        misses.append(
            SearchMissRead(
                id=signal.id,
                query=query,
                topic_slug=topic_slug if isinstance(topic_slug, str) else None,
                types=types,
                created_at=signal.created_at,
            ),
        )
    return misses


def get_learning_analytics(session: Session) -> LearningAnalyticsRead:
    """Deterministic learning analytics for the local user (QP-031)."""
    return LearningAnalyticsRead(
        user_id=LOCAL_USER_ID,
        weak_concepts=_weak_concepts(session),
        attempt_history=_attempt_history(session),
        review_due_count=count_due_flashcards(session),
        search_misses=_search_misses(session),
    )
