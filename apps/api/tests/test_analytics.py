from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from app.models.attempt import Attempt
from app.models.enums import ContentStatus, Difficulty, LearningSignalType
from app.models.learning_signal import LearningSignal
from app.models.question import Question
from app.models.topic import Topic
from app.schemas.mastery import ConceptMasterySnapshot, MasteryRead
from app.services.analytics import (
    WEAK_CONCEPT_LIMIT,
    get_learning_analytics,
)
from app.services.flashcard_review import count_due_flashcards


def test_get_learning_analytics_assembles_roadmap_sections() -> None:
    session = MagicMock()
    topic = Topic(id=1, slug="probability", name="Probability", order_index=1)
    question = Question(
        id=7,
        title="Bayes warm-up",
        body="Compute P(A|B)",
        topic_id=1,
        difficulty=Difficulty.MEDIUM,
        status=ContentStatus.APPROVED,
    )
    question.topic = topic
    attempt = Attempt(
        id=3,
        question_id=7,
        answer="1/2",
        is_correct=False,
        score=0.0,
        time_spent_seconds=40,
        created_at=datetime.now(UTC),
    )
    attempt.question = question

    miss = LearningSignal(
        id=9,
        user_id="local",
        signal_type=LearningSignalType.SEARCH_MISS,
        payload_json={
            "query": "kalman filter",
            "types": ["questions", "concepts"],
            "topic_slug": None,
            "result_count": 0,
        },
        created_at=datetime.now(UTC),
    )

    session.scalars.side_effect = [
        MagicMock(unique=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[attempt])))),
        MagicMock(all=MagicMock(return_value=[miss])),
    ]

    mastery = MasteryRead(
        user_id="local",
        topic_mastery=[],
        concept_mastery=[
            ConceptMasterySnapshot(
                concept_id=1,
                slug="bayes",
                name="Bayes",
                topic_id=1,
                topic_slug="probability",
                mastery_score=20.0,
                attempts_count=2,
                last_practiced_at=None,
            ),
            ConceptMasterySnapshot(
                concept_id=2,
                slug="strong",
                name="Strong",
                topic_id=1,
                topic_slug="probability",
                mastery_score=80.0,
                attempts_count=5,
                last_practiced_at=None,
            ),
        ],
    )

    with patch("app.services.analytics.get_mastery", return_value=mastery):
        analytics = get_learning_analytics(session)

    assert analytics.user_id == "local"
    assert analytics.review_due_count == 0
    assert len(analytics.weak_concepts) == 1
    assert analytics.weak_concepts[0].slug == "bayes"
    assert len(analytics.attempt_history) == 1
    assert analytics.attempt_history[0].question_title == "Bayes warm-up"
    assert len(analytics.search_misses) == 1
    assert analytics.search_misses[0].query == "kalman filter"


def test_weak_concepts_are_capped_and_sorted_by_mastery() -> None:
    session = MagicMock()
    session.scalars.side_effect = [
        MagicMock(unique=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),
        MagicMock(all=MagicMock(return_value=[])),
    ]

    concepts = [
        ConceptMasterySnapshot(
            concept_id=index,
            slug=f"c-{index}",
            name=f"Concept {index}",
            topic_id=1,
            topic_slug="probability",
            mastery_score=float(index),
            attempts_count=index,
            last_practiced_at=None,
        )
        for index in range(WEAK_CONCEPT_LIMIT + 5)
    ]
    mastery = MasteryRead(user_id="local", topic_mastery=[], concept_mastery=concepts)

    with patch("app.services.analytics.get_mastery", return_value=mastery):
        analytics = get_learning_analytics(session)

    assert len(analytics.weak_concepts) == WEAK_CONCEPT_LIMIT
    scores = [item.mastery_score for item in analytics.weak_concepts]
    assert scores == sorted(scores)


def test_count_due_flashcards_subtracts_future_reviews() -> None:
    session = MagicMock()
    session.scalar.side_effect = [10, 3]
    assert count_due_flashcards(session) == 7

    session.scalar.side_effect = [2, 5]
    assert count_due_flashcards(session) == 0
