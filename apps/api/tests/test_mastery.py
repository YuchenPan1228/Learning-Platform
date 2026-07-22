from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from app.models.enums import ContentStatus, Difficulty
from app.models.question import Question
from app.models.user_topic_mastery import UserTopicMastery
from app.services.mastery import recalculate_user_topic_mastery
from app.services.progress import TopicProgressStats


def test_recalculate_user_topic_mastery_upserts_rows() -> None:
    session = MagicMock()
    existing = UserTopicMastery(
        user_id="local",
        topic_id=1,
        mastery_score=0.0,
        attempts_count=0,
    )
    session.scalars.return_value.all.return_value = [existing]
    session.refresh.side_effect = lambda row: row

    with (
        patch(
            "app.services.mastery.get_topic_progress_stats",
            return_value={
                1: TopicProgressStats(
                    mastery_score=25.0,
                    attempts_count=4,
                    solved_count=1,
                    total_questions=4,
                ),
                2: TopicProgressStats(
                    mastery_score=50.0,
                    attempts_count=2,
                    solved_count=1,
                    total_questions=2,
                ),
            },
        ),
        patch(
            "app.services.mastery._last_practiced_by_topic_id",
            return_value={1: datetime(2026, 7, 21, tzinfo=UTC)},
        ),
    ):
        rows = recalculate_user_topic_mastery(session)

    assert len(rows) == 2
    assert existing.mastery_score == 25.0
    assert existing.attempts_count == 4
    assert existing.last_practiced_at == datetime(2026, 7, 21, tzinfo=UTC)
    session.add.assert_called_once()
    added = session.add.call_args.args[0]
    assert isinstance(added, UserTopicMastery)
    assert added.topic_id == 2
    assert added.mastery_score == 50.0
    session.commit.assert_called_once()


def test_recalculate_user_topic_mastery_removes_stale_rows() -> None:
    session = MagicMock()
    stale = UserTopicMastery(
        user_id="local",
        topic_id=99,
        mastery_score=10.0,
        attempts_count=1,
        next_review_at=None,
    )
    session.scalars.return_value.all.return_value = [stale]
    session.refresh.side_effect = lambda row: row

    with (
        patch(
            "app.services.mastery.get_topic_progress_stats",
            return_value={
                1: TopicProgressStats(
                    mastery_score=0.0,
                    attempts_count=0,
                    solved_count=0,
                    total_questions=3,
                ),
            },
        ),
        patch("app.services.mastery._last_practiced_by_topic_id", return_value={}),
    ):
        recalculate_user_topic_mastery(session)

    session.delete.assert_called_once_with(stale)


def test_recalculate_user_topic_mastery_keeps_srs_only_rows() -> None:
    session = MagicMock()
    review_at = datetime(2026, 7, 22, tzinfo=UTC)
    srs_only = UserTopicMastery(
        user_id="local",
        topic_id=99,
        mastery_score=10.0,
        attempts_count=1,
        next_review_at=review_at,
    )
    session.scalars.return_value.all.return_value = [srs_only]
    session.refresh.side_effect = lambda row: row

    with (
        patch(
            "app.services.mastery.get_topic_progress_stats",
            return_value={
                1: TopicProgressStats(
                    mastery_score=0.0,
                    attempts_count=0,
                    solved_count=0,
                    total_questions=3,
                ),
            },
        ),
        patch("app.services.mastery._last_practiced_by_topic_id", return_value={}),
    ):
        rows = recalculate_user_topic_mastery(session)

    session.delete.assert_not_called()
    assert srs_only.next_review_at == review_at
    assert srs_only.mastery_score == 0.0
    assert srs_only.attempts_count == 0
    assert srs_only in rows


def test_topic_progress_stats_formula_uses_solved_ratio() -> None:
    from app.models.enums import QuestionProgressStatus
    from app.services.progress import QuestionProgress, get_topic_progress_stats

    session = MagicMock()
    session.scalars.return_value.all.return_value = [
        Question(
            id=1,
            title="A",
            body="A",
            difficulty=Difficulty.EASY,
            topic_id=10,
            subtopic_id=20,
            status=ContentStatus.APPROVED,
        ),
        Question(
            id=2,
            title="B",
            body="B",
            difficulty=Difficulty.EASY,
            topic_id=10,
            subtopic_id=20,
            status=ContentStatus.APPROVED,
        ),
    ]

    with patch(
        "app.services.progress.get_progress_by_question_id",
        return_value={
            1: QuestionProgress(
                status=QuestionProgressStatus.SOLVED,
                attempt_count=2,
                manually_marked=False,
            ),
            2: QuestionProgress(
                status=QuestionProgressStatus.ATTEMPTED,
                attempt_count=1,
                manually_marked=False,
            ),
        },
    ):
        stats = get_topic_progress_stats(session)

    assert stats[20].mastery_score == 50.0
    assert stats[20].solved_count == 1
    assert stats[20].attempts_count == 3
    assert stats[10].mastery_score == 50.0
