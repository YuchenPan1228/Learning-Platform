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

        assert first.topics == 75
        assert first.concepts == 66
        assert first.concept_edges == 95
        assert second == first
        assert topic_count == 75
        assert concept_count == 66
        assert edge_count == 95

        probability = session.scalar(select(Topic).where(Topic.slug == "probability"))
        assert probability is not None
        assert probability.name == "Probability"

        counting = session.scalar(select(Concept).where(Concept.slug == "counting"))
        assert counting is not None
        assert counting.name == "Counting & Sample Spaces"
        assert counting.worked_example is not None

        vectors = session.scalar(select(Concept).where(Concept.slug == "vectors-matrices"))
        assert vectors is not None
        assert vectors.worked_example is not None
        assert "cross" in (vectors.formula or "").lower() or "×" in (vectors.formula or "")

        estimation = session.scalar(select(Concept).where(Concept.slug == "estimation"))
        assert estimation is not None
        assert estimation.name == "Point Estimation"
        assert estimation.worked_example is not None

        bias_variance = session.scalar(select(Concept).where(Concept.slug == "bias-variance"))
        assert bias_variance is not None
        assert bias_variance.worked_example is not None

        derivatives = session.scalar(select(Concept).where(Concept.slug == "derivatives"))
        assert derivatives is not None
        assert derivatives.name == "Derivatives Payoffs & Parity"
        assert derivatives.worked_example is not None

        greeks = session.scalar(select(Concept).where(Concept.slug == "greeks"))
        assert greeks is not None
        assert greeks.formula is not None

        python = session.scalar(select(Concept).where(Concept.slug == "python"))
        assert python is not None
        assert python.name == "Python for Quant"
        assert python.worked_example is not None

        sql = session.scalar(select(Concept).where(Concept.slug == "sql"))
        assert sql is not None
        assert sql.worked_example is not None

        conditional_expectation = session.scalar(
            select(Concept).where(Concept.slug == "conditional-expectation")
        )
        assert conditional_expectation is not None
        assert conditional_expectation.worked_example is not None

        bayes = session.scalar(select(Concept).where(Concept.slug == "bayes"))
        assert bayes is not None
        assert bayes.formula is not None
        assert bayes.worked_example is not None
    finally:
        session.close()
        reset_db_state()
        get_settings.cache_clear()
