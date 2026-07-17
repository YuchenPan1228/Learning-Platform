from app.models import Base

EXPECTED_TABLES = {
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
    "ai_usage_logs",
}


def test_mvp_tables_are_registered() -> None:
    assert EXPECTED_TABLES.issubset(Base.metadata.tables.keys())
