from unittest.mock import MagicMock

import pytest
from app.models.concept import Concept
from app.models.enums import ConceptEdgeRelationshipType
from app.models.topic import Topic
from app.schemas.admin_concepts import ConceptUpdate
from app.services.admin_concepts import (
    ConceptEditorError,
    list_concepts_for_editor,
    update_concept,
)
from fastapi.testclient import TestClient


def _concept(*, concept_id: int = 1, slug: str = "bayes") -> Concept:
    topic = Topic(id=10, slug="probability", name="Probability", order_index=0)
    concept = Concept(
        slug=slug,
        name="Bayes Theorem",
        topic_id=10,
        definition="Old definition",
        formula="P(A|B)=P(B|A)P(A)/P(B)",
        intuition="Update beliefs with evidence.",
        worked_example=None,
        common_mistakes="Ignoring base rates",
        interview_tips="State prior and likelihood clearly.",
        prerequisites="Conditional Probability",
    )
    concept.id = concept_id
    concept.topic = topic
    concept.outgoing_edges = []
    concept.incoming_edges = []
    return concept


def test_update_concept_edits_content_and_preserves_slug() -> None:
    session = MagicMock()
    concept = _concept()
    session.scalar.side_effect = [concept, concept]

    result = update_concept(
        session,
        "bayes",
        ConceptUpdate(
            definition="Updated definition",
            formula="P(H|E)=P(E|H)P(H)/P(E)",
            intuition="New intuition",
            worked_example="Coin and disease example",
            common_mistakes="Confusing P(A|B) with P(B|A)",
            interview_tips="Write Bayes in odds form when helpful.",
        ),
    )

    assert concept.slug == "bayes"
    assert concept.definition == "Updated definition"
    assert concept.formula == "P(H|E)=P(E|H)P(H)/P(E)"
    assert concept.worked_example == "Coin and disease example"
    assert result.definition == "Updated definition"
    session.commit.assert_called_once()


def test_update_concept_rejects_empty_patch() -> None:
    session = MagicMock()
    session.scalar.return_value = _concept()

    with pytest.raises(ConceptEditorError, match="no fields"):
        update_concept(session, "bayes", ConceptUpdate())


def test_list_concepts_for_editor_filters_by_topic() -> None:
    session = MagicMock()
    concept = _concept()
    topic = concept.topic
    topic.subtopics = []
    result_proxy = MagicMock()
    result_proxy.unique.return_value.all.return_value = [concept]
    session.scalar.return_value = topic
    session.scalars.return_value = result_proxy

    items = list_concepts_for_editor(session, topic_slug="probability")
    assert len(items) == 1
    assert items[0].slug == "bayes"
    assert items[0].topic_slug == "probability"


@pytest.mark.integration
def test_admin_concept_editor_list_and_patch(
    migrated_database: None,
    require_postgres: None,
    client: TestClient,
) -> None:
    from app.db import get_session_factory
    from app.models.concept import Concept, ConceptEdge

    session = get_session_factory()()
    try:
        topic = Topic(slug="admin-concept-topic", name="Admin Concept Topic", order_index=0)
        session.add(topic)
        session.flush()

        concept = Concept(
            slug="admin-edit-concept",
            name="Admin Edit Concept",
            topic_id=topic.id,
            definition="Before",
            formula="x=1",
            intuition="Old",
            worked_example=None,
            common_mistakes="Old mistake",
            interview_tips="Old tip",
            prerequisites="Basics",
        )
        other = Concept(
            slug="admin-edit-neighbor",
            name="Neighbor Concept",
            topic_id=topic.id,
            definition="Neighbor",
        )
        session.add_all([concept, other])
        session.flush()

        edge = ConceptEdge(
            source_concept_id=concept.id,
            target_concept_id=other.id,
            relationship_type=ConceptEdgeRelationshipType.REQUIRES,
            weight=1.0,
        )
        session.add(edge)
        session.commit()
        concept_slug = concept.slug
    finally:
        session.close()

    list_response = client.get("/admin/concepts", params={"topic_slug": "admin-concept-topic"})
    assert list_response.status_code == 200
    list_body = list_response.json()
    slugs = {item["slug"] for item in list_body["items"]}
    assert "admin-edit-concept" in slugs
    assert "admin-edit-neighbor" in slugs

    get_response = client.get(f"/admin/concepts/{concept_slug}")
    assert get_response.status_code == 200
    detail = get_response.json()
    assert detail["definition"] == "Before"
    assert len(detail["neighbors"]) == 1
    assert detail["neighbors"][0]["slug"] == "admin-edit-neighbor"

    patch_response = client.patch(
        f"/admin/concepts/{concept_slug}",
        json={
            "definition": "After edit",
            "formula": "x=2",
            "intuition": "New intuition",
            "worked_example": "Worked example text",
            "common_mistakes": "New mistake",
            "interview_tips": "New tip",
        },
    )
    assert patch_response.status_code == 200
    patched = patch_response.json()
    assert patched["slug"] == concept_slug
    assert patched["definition"] == "After edit"
    assert patched["formula"] == "x=2"
    assert patched["worked_example"] == "Worked example text"
    assert len(patched["neighbors"]) == 1

    session = get_session_factory()()
    try:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        updated = session.scalar(
            select(Concept)
            .where(Concept.slug == concept_slug)
            .options(selectinload(Concept.outgoing_edges))
        )
        assert updated is not None
        assert updated.definition == "After edit"
        assert len(updated.outgoing_edges) == 1
    finally:
        session.close()
