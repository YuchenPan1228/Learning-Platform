from collections.abc import Sequence
from datetime import UTC
from unittest.mock import MagicMock, patch

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


def test_build_daily_study_plan_includes_practice_without_flashcards() -> None:
    session = MagicMock()
    counting = _topic(3, "counting", "Counting", parent_id=1)

    # edges (prereq) → subtopics (practice)
    session.scalars.side_effect = [
        _scalars_result(rows=[], unique=True),
        _scalars_result(rows=[counting]),
    ]

    stats = {
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
    assert not any(item.kind.value == "flashcard_review" for item in plan.items)
    assert any(item.kind.value == "practice" for item in plan.items)
    assert plan.generated_at.tzinfo == UTC


def test_build_daily_study_plan_mixes_practice_items() -> None:
    session = MagicMock()
    practice_topic = _topic(99, "counting", "Counting", parent_id=1)

    session.scalars.side_effect = [
        _scalars_result(rows=[], unique=True),
        _scalars_result(rows=[practice_topic]),
    ]

    stats = {
        99: TopicProgressStats(
            mastery_score=0.0,
            attempts_count=0,
            solved_count=0,
            total_questions=8,
        ),
    }

    with patch("app.services.study_planner.get_topic_progress_stats", return_value=stats):
        plan = build_daily_study_plan(session)

    flashcard_items = [item for item in plan.items if item.kind.value == "flashcard_review"]
    practice_items = [item for item in plan.items if item.kind.value == "practice"]
    assert flashcard_items == []
    assert practice_items
    assert len(plan.items) <= 5


def test_build_daily_study_plan_is_capped_by_target_minutes() -> None:
    session = MagicMock()
    topics = [_topic(i, f"topic-{i}", f"Topic {i}", parent_id=1) for i in range(10, 20)]

    session.scalars.side_effect = [
        _scalars_result(rows=[], unique=True),
        _scalars_result(rows=topics),
    ]

    stats = {
        topic.id: TopicProgressStats(
            mastery_score=0.0,
            attempts_count=0,
            solved_count=0,
            total_questions=5,
        )
        for topic in topics
    }

    with patch("app.services.study_planner.get_topic_progress_stats", return_value=stats):
        plan = build_daily_study_plan(session)

    assert len(plan.items) <= 5
    assert plan.total_minutes <= TARGET_MINUTES
    assert all(item.duration_minutes >= 1 for item in plan.items)
    assert not any(item.kind.value == "flashcard_review" for item in plan.items)
