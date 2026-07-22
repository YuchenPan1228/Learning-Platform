from unittest.mock import MagicMock

import pytest
from app.dedup.fingerprints import compute_question_fingerprints
from app.models.concept import Concept
from app.models.enums import (
    ContentStatus,
    Difficulty,
    ExtractedObjectType,
    ResourceSourceType,
)
from app.models.extracted_object import ExtractedObject
from app.models.flashcard import Flashcard
from app.models.question import Question
from app.models.resource import Resource
from app.models.topic import Topic
from app.services.admin_publish import (
    PublishDuplicateError,
    PublishError,
    publish_extracted_object,
)
from fastapi.testclient import TestClient


def _approved_question_extracted(
    *,
    topic: Topic,
    resource: Resource | None = None,
    payload: dict[str, object] | None = None,
) -> ExtractedObject:
    return ExtractedObject(
        resource_id=resource.id if resource is not None else None,
        object_type=ExtractedObjectType.QUESTION,
        payload_json=payload
        or {
            "title": "Bayes draft",
            "body": "What is P(A|B)?",
            "difficulty": "medium",
            "topic_slug": topic.slug,
        },
        quality_score=0.8,
        status=ContentStatus.APPROVED,
        extraction_method="manual",
        model_version="test-v1",
    )


def test_publish_question_applies_fingerprints_and_provenance() -> None:
    session = MagicMock()
    topic = Topic(id=1, slug="probability", name="Probability", order_index=0)
    resource = Resource(
        id=9,
        source_type=ResourceSourceType.URL,
        url="https://example.com/bayes",
        title="Bayes notes",
        license="CC-BY-4.0",
        attribution="Example source",
        status=ContentStatus.DRAFT,
    )
    extracted = _approved_question_extracted(topic=topic, resource=resource)
    extracted.id = 5
    extracted.resource = resource

    session.scalar.side_effect = [extracted, 1]
    session.execute.return_value.all.return_value = []

    def refresh_side_effect(row: object) -> None:
        if isinstance(row, Question):
            row.id = 42

    session.refresh.side_effect = refresh_side_effect

    result = publish_extracted_object(session, 5)

    saved_question = session.add.call_args_list[0].args[0]
    assert isinstance(saved_question, Question)
    assert saved_question.title == "Bayes draft"
    assert saved_question.body == "What is P(A|B)?"
    assert saved_question.status is ContentStatus.APPROVED
    assert saved_question.source_id == 9
    assert saved_question.source_url == "https://example.com/bayes"
    assert saved_question.source_license == "CC-BY-4.0"
    assert saved_question.extraction_method == "manual"
    assert saved_question.raw_text_hash is not None
    assert saved_question.normalized_text_hash is not None
    assert result.published.kind == "question"
    assert result.published.id == 42
    assert extracted.payload_json["published"] == {"kind": "question", "id": 42}


def test_publish_question_blocks_exact_duplicate() -> None:
    session = MagicMock()
    topic = Topic(id=1, slug="probability", name="Probability", order_index=0)
    extracted = _approved_question_extracted(topic=topic)
    extracted.id = 6

    existing = Question(
        title="Bayes draft",
        body="What is P(A|B)?",
        difficulty=Difficulty.MEDIUM,
        topic_id=1,
        status=ContentStatus.APPROVED,
    )
    raw_hash, normalized_hash, normalized_text = compute_question_fingerprints(
        existing.title,
        existing.body,
    )
    existing.raw_text_hash = raw_hash
    existing.normalized_text_hash = normalized_hash
    existing.normalized_text = normalized_text
    existing.id = 99

    session.scalar.return_value = extracted
    session.execute.return_value.all.return_value = [
        (
            existing.id,
            existing.title,
            existing.raw_text_hash,
            existing.normalized_text_hash,
            existing.normalized_text,
        )
    ]

    with pytest.raises(PublishDuplicateError):
        publish_extracted_object(session, 6)


def test_publish_requires_approved_status() -> None:
    session = MagicMock()
    topic = Topic(id=1, slug="probability", name="Probability", order_index=0)
    extracted = _approved_question_extracted(topic=topic)
    extracted.status = ContentStatus.DRAFT
    session.scalar.return_value = extracted

    with pytest.raises(PublishError, match="only approved"):
        publish_extracted_object(session, 1)


@pytest.mark.integration
def test_publish_review_item_creates_approved_question(
    migrated_database: None,
    require_postgres: None,
    client: TestClient,
) -> None:
    from app.db import get_session_factory
    from app.models.extracted_object import ExtractedObject
    from app.models.resource import Resource

    session = get_session_factory()()
    try:
        topic = Topic(
            slug="publish-test-probability",
            name="Publish Test Probability",
            order_index=0,
        )
        session.add(topic)
        session.flush()

        resource = Resource(
            source_type=ResourceSourceType.MANUAL,
            title="Manual Bayes note",
            license="private",
            attribution="local notes",
            status=ContentStatus.DRAFT,
        )
        session.add(resource)
        session.flush()

        extracted = ExtractedObject(
            resource_id=resource.id,
            object_type=ExtractedObjectType.QUESTION,
            payload_json={
                "title": "Unique publish test",
                "body": (
                    "Compute P(A|B) when A and B are independent events with P(A)=0.2 and P(B)=0.3."
                ),
                "difficulty": "easy",
                "topic_slug": topic.slug,
            },
            status=ContentStatus.APPROVED,
            extraction_method="manual",
        )
        session.add(extracted)
        session.commit()
        extracted_id = extracted.id
        resource_id = resource.id
    finally:
        session.close()

    response = client.post(f"/admin/review/{extracted_id}/publish")
    assert response.status_code == 200
    body = response.json()
    assert body["published"]["kind"] == "question"
    assert body["object_type"] == "question"

    session = get_session_factory()()
    try:
        question = session.get(Question, body["published"]["id"])
        assert question is not None
        assert question.title == "Unique publish test"
        assert question.status == "approved"
        assert question.source_id == resource_id
        assert question.source_license == "private"
        assert question.raw_text_hash is not None

        extracted_row = session.get(ExtractedObject, extracted_id)
        assert extracted_row is not None
        assert extracted_row.payload_json["published"]["id"] == question.id
    finally:
        session.close()

    second_publish = client.post(f"/admin/review/{extracted_id}/publish")
    assert second_publish.status_code == 400


@pytest.mark.integration
def test_publish_review_item_creates_concept_and_flashcard(
    migrated_database: None,
    require_postgres: None,
    client: TestClient,
) -> None:
    from app.db import get_session_factory
    from app.models.extracted_object import ExtractedObject

    session = get_session_factory()()
    try:
        topic = Topic(slug="publish-test-topic", name="Publish Test Topic", order_index=0)
        session.add(topic)
        session.flush()

        concept_extracted = ExtractedObject(
            object_type=ExtractedObjectType.CONCEPT,
            payload_json={
                "name": "Publish Test Concept",
                "definition": "A concept created from an approved draft.",
                "topic_slug": topic.slug,
            },
            status=ContentStatus.APPROVED,
            extraction_method="manual",
        )
        flashcard_extracted = ExtractedObject(
            object_type=ExtractedObjectType.FLASHCARD,
            payload_json={
                "front": "What is conditional probability?",
                "back": "P(A|B)",
                "topic_slug": topic.slug,
            },
            status=ContentStatus.APPROVED,
            extraction_method="manual",
        )
        session.add_all([concept_extracted, flashcard_extracted])
        session.commit()
        concept_id = concept_extracted.id
        flashcard_id = flashcard_extracted.id
    finally:
        session.close()

    concept_response = client.post(f"/admin/review/{concept_id}/publish")
    assert concept_response.status_code == 200
    assert concept_response.json()["published"]["kind"] == "concept"

    flashcard_response = client.post(f"/admin/review/{flashcard_id}/publish")
    assert flashcard_response.status_code == 200
    assert flashcard_response.json()["published"]["kind"] == "flashcard"

    session = get_session_factory()()
    try:
        concept = session.get(Concept, concept_response.json()["published"]["id"])
        flashcard = session.get(Flashcard, flashcard_response.json()["published"]["id"])
        assert concept is not None
        assert concept.name == "Publish Test Concept"
        assert flashcard is not None
        assert flashcard.front == "What is conditional probability?"
    finally:
        session.close()
