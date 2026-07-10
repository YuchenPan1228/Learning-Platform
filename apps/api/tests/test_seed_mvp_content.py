import pytest
from app.config import get_settings
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
        second = seed_mvp_content(session)

        assert first.total == 65
        assert first.probability_questions == 20
        assert first.mental_math_questions == 20
        assert first.coding_questions == 10
        assert first.finance_questions == 10
        assert first.market_game_questions == 5
        assert second == first
        assert question_count == 65

        mental_math = session.scalar(
            select(Question).where(Question.extraction_method == "hand_seed:mm-001")
        )
        assert mental_math is not None
        assert mental_math.short_answer == "351"

        market_game = session.scalar(
            select(Question).where(Question.extraction_method == "hand_seed:game-002")
        )
        assert market_game is not None
        assert market_game.expected_solution_pattern is not None
    finally:
        session.close()
        reset_db_state()
        get_settings.cache_clear()
