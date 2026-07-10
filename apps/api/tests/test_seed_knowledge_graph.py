import pytest
from app.config import get_settings
from app.models.concept import Concept, ConceptEdge
from app.models.topic import Topic
from app.seeds.knowledge_graph import seed_knowledge_graph
from sqlalchemy import func, select


@pytest.mark.integration
def test_seed_knowledge_graph_is_idempotent(
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
        first = seed_knowledge_graph(session)
        topic_count = session.scalar(select(func.count()).select_from(Topic))
        concept_count = session.scalar(select(func.count()).select_from(Concept))
        edge_count = session.scalar(select(func.count()).select_from(ConceptEdge))

        second = seed_knowledge_graph(session)

        assert first.topics == 73
        assert first.concepts == 64
        assert first.concept_edges == 23
        assert second == first
        assert topic_count == 73
        assert concept_count == 64
        assert edge_count == 23

        probability = session.scalar(select(Topic).where(Topic.slug == "probability"))
        assert probability is not None
        assert probability.name == "Probability"

        bayes = session.scalar(select(Concept).where(Concept.slug == "bayes"))
        assert bayes is not None
        assert bayes.formula is not None
    finally:
        session.close()
        reset_db_state()
        get_settings.cache_clear()
