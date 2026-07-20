import pytest
from app.config import get_settings
from app.models.flashcard import Flashcard
from app.models.question import Question
from app.seeds.knowledge_graph import seed_knowledge_graph
from app.seeds.mvp_content import seed_mvp_content
from sqlalchemy import func, select


@pytest.mark.integration
def test_seed_mvp_content_is_idempotent(
    database_url: str,
    migrated_database: None,
    require_postgres: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.db import get_session_factory, reset_db_state

    monkeypatch.setenv("DATABASE_URL", database_url)
    get_settings.cache_clear()
    reset_db_state()

    session = get_session_factory()()
    try:
        seed_knowledge_graph(session)
        first = seed_mvp_content(session)
        question_count = session.scalar(select(func.count()).select_from(Question))
        flashcard_count = session.scalar(select(func.count()).select_from(Flashcard))
        second = seed_mvp_content(session)

        assert first.total == 183
        assert first.probability_questions == 20
        assert first.mathematics_questions == 20
        assert first.statistics_questions == 18
        assert first.programming_questions == 15
        assert first.mental_math_questions == 56
        assert first.coding_questions == 10
        assert first.finance_questions == 21
        assert first.market_game_questions == 5
        assert first.brain_teaser_questions == 18
        assert first.flashcards == 165
        assert first.tags >= 1
        assert second == first
        assert question_count == 183
        assert flashcard_count == 165

        from app.models.tag import QuestionTag, Tag

        tag_count = session.scalar(select(func.count()).select_from(Tag))
        link_count = session.scalar(select(func.count()).select_from(QuestionTag))
        assert tag_count == first.tags
        assert link_count is not None and link_count >= 1

        mental_math = session.scalar(
            select(Question).where(Question.extraction_method == "hand_seed:mm-001")
        )
        assert mental_math is not None
        assert mental_math.short_answer == "351"

        stats = session.scalar(
            select(Question).where(Question.extraction_method == "hand_seed:stats-001")
        )
        assert stats is not None
        assert stats.short_answer == "0.25"

        finance = session.scalar(
            select(Question).where(Question.extraction_method == "hand_seed:fin-001")
        )
        assert finance is not None
        assert finance.short_answer == "10"

        programming = session.scalar(
            select(Question).where(Question.extraction_method == "hand_seed:prog-001")
        )
        assert programming is not None
        assert programming.short_answer == "O(n) vs O(1)"

        market_game = session.scalar(
            select(Question).where(Question.extraction_method == "hand_seed:game-002")
        )
        assert market_game is not None
        assert market_game.expected_solution_pattern is not None
    finally:
        session.close()
        reset_db_state()
        get_settings.cache_clear()
