from collections.abc import Sequence
from datetime import UTC
from unittest.mock import MagicMock, patch

from app.models.enums import Difficulty
from app.models.flashcard import Flashcard
from app.models.topic import Topic
from app.services.progress import TopicProgressStats
from app.services.study_planner import (
    TARGET_MINUTES,
    build_daily_study_plan,
)


def _topic(topic_id: int, slug: str, name: str, parent_id: int | None = None) -> Topic:
    return Topic(
        id=topic_id,
        slug=slug,
        name=name,
        parent_topic_id=parent_id,
        order_index=topic_id,
    )


def _scalars_result(*, rows: Sequence[object], unique: bool = False) -> MagicMock:
    result = MagicMock()
    result.all = MagicMock(return_value=rows)
    if unique:
        result.unique = MagicMock(return_value=result)
    return result


def test_build_daily_study_plan_includes_due_flashcards_and_practice() -> None:
    session = MagicMock()
    bayes = _topic(2, "bayes", "Bayes", parent_id=1)
    counting = _topic(3, "counting", "Counting", parent_id=1)
    card = Flashcard(
        id=10,
        front="P(A|B)?",
        back="P(B|A)P(A)/P(B)",
        topic_id=2,
        difficulty=Difficulty.MEDIUM,
    )
    card.topic = bayes

    # progress → flashcards → edges → paths → subtopics
    session.scalars.side_effect = [
        _scalars_result(rows=[]),
        _scalars_result(rows=[card], unique=True),
        _scalars_result(rows=[], unique=True),
        _scalars_result(rows=[]),
        _scalars_result(rows=[counting]),
    ]

    stats = {
        2: TopicProgressStats(
            mastery_score=10.0,
            attempts_count=1,
            solved_count=0,
            total_questions=5,
        ),
        3: TopicProgressStats(
            mastery_score=0.0,
            attempts_count=0,
            solved_count=0,
            total_questions=4,
        ),
    }

    with patch("app.services.study_planner.get_topic_progress_stats", return_value=stats):
        plan = build_daily_study_plan(session)

    assert plan.user_id == "local"
    assert plan.target_minutes == TARGET_MINUTES
    assert plan.total_minutes > 0
    assert plan.summary.endswith("min plan")
    assert any(item.kind.value == "flashcard_review" for item in plan.items)
    assert any(item.kind.value == "practice" for item in plan.items)
    assert plan.generated_at.tzinfo == UTC


def test_build_daily_study_plan_is_capped_by_target_minutes() -> None:
    session = MagicMock()
    topics = [_topic(i, f"topic-{i}", f"Topic {i}", parent_id=1) for i in range(10, 20)]
    cards = []
    for index, topic in enumerate(topics, start=1):
        card = Flashcard(
            id=index,
            front=f"Q{index}",
            back=f"A{index}",
            topic_id=topic.id,
            difficulty=Difficulty.EASY,
        )
        card.topic = topic
        cards.append(card)

    session.scalars.side_effect = [
        _scalars_result(rows=[]),
        _scalars_result(rows=cards, unique=True),
        _scalars_result(rows=[], unique=True),
        _scalars_result(rows=[]),
        _scalars_result(rows=topics),
    ]

    with patch("app.services.study_planner.get_topic_progress_stats", return_value={}):
        plan = build_daily_study_plan(session)

    assert len(plan.items) <= 5
    assert plan.total_minutes <= TARGET_MINUTES
    assert all(item.duration_minutes >= 1 for item in plan.items)
