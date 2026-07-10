import pytest
from alembic import command
from alembic.config import Config
from app.config import get_settings
from sqlalchemy import create_engine, inspect, text

from tests.paths import ALEMBIC_INI


@pytest.fixture
def alembic_config(database_url: str, monkeypatch: pytest.MonkeyPatch) -> Config:
    monkeypatch.setenv("DATABASE_URL", database_url)
    get_settings.cache_clear()
    return Config(str(ALEMBIC_INI))


@pytest.mark.integration
def test_initial_migration_applies(
    alembic_config: Config,
    database_url: str,
    require_postgres: None,
) -> None:
    command.downgrade(alembic_config, "base")
    command.upgrade(alembic_config, "head")

    engine = create_engine(database_url)
    try:
        inspector = inspect(engine)
        table_names = set(inspector.get_table_names())
        assert {
            "topics",
            "concepts",
            "concept_edges",
            "questions",
            "tags",
            "question_tags",
            "flashcards",
            "learning_paths",
            "learning_path_steps",
            "learning_signals",
            "attempts",
            "user_topic_mastery",
            "alembic_version",
        }.issubset(table_names)

        with engine.connect() as connection:
            question_fts = connection.execute(
                text(
                    "SELECT indexname FROM pg_indexes "
                    "WHERE tablename = 'questions' AND indexname = 'ix_questions_fts'"
                )
            ).scalar_one()
            concept_fts = connection.execute(
                text(
                    "SELECT indexname FROM pg_indexes "
                    "WHERE tablename = 'concepts' AND indexname = 'ix_concepts_fts'"
                )
            ).scalar_one()

        assert question_fts == "ix_questions_fts"
        assert concept_fts == "ix_concepts_fts"
    finally:
        engine.dispose()
        get_settings.cache_clear()
