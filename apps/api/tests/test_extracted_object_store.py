from unittest.mock import MagicMock

import pytest
from app.models.enums import (
    ContentStatus,
    ExtractedObjectType,
    ResourceSourceType,
)
from app.models.extracted_object import ExtractedObject
from app.models.resource import Resource
from app.services.extracted_object_store import (
    ExtractedObjectStoreError,
    ProvenanceData,
    StoreExtractedObjectInput,
    get_stored_extracted_object,
    load_provenance_from_resource,
    provenance_from_payload,
    store_extracted_object,
    store_extracted_objects,
)


def _resource(*, resource_id: int = 10) -> Resource:
    resource = Resource(
        source_type=ResourceSourceType.URL,
        url="https://example.com/bayes",
        title="Bayes notes",
        author="Alice",
        publisher="Example Pub",
        license="CC-BY-4.0",
        attribution="Alice / Example Pub",
        status=ContentStatus.DRAFT,
    )
    resource.id = resource_id
    return resource


def test_store_extracted_object_persists_payload_scores_method_and_provenance() -> None:
    session = MagicMock()
    resource = _resource()
    session.get.return_value = resource

    def add(row: object) -> None:
        if isinstance(row, ExtractedObject):
            row.id = 42

    session.add.side_effect = add

    result = store_extracted_object(
        session,
        StoreExtractedObjectInput(
            object_type=ExtractedObjectType.QUESTION,
            payload_json={
                "title": "Two Heads",
                "body": "Given at least one head, find P both heads.",
            },
            confidence_score=0.87,
            quality_score=0.7,
            extraction_method="ai:structured:url_trafilatura",
            model_version="qwen2.5:3b",
            provenance=ProvenanceData(resource_id=10, topic_job_id=3),
        ),
        commit=True,
    )

    assert result.id == 42
    assert result.object_type is ExtractedObjectType.QUESTION
    assert result.resource_id == 10
    assert result.topic_job_id == 3
    assert result.confidence_score == 0.87
    assert result.quality_score == 0.7
    assert result.extraction_method == "ai:structured:url_trafilatura"
    assert result.model_version == "qwen2.5:3b"
    assert result.status is ContentStatus.DRAFT
    assert result.payload_json["title"] == "Two Heads"
    assert result.payload_json["provenance"]["resource_id"] == 10
    assert result.payload_json["provenance"]["source_url"] == "https://example.com/bayes"
    assert result.payload_json["provenance"]["source_license"] == "CC-BY-4.0"
    assert result.payload_json["provenance"]["source_attribution"] == "Alice / Example Pub"
    assert result.payload_json["source_url"] == "https://example.com/bayes"
    session.commit.assert_called_once()


def test_store_rejects_invalid_question_payload() -> None:
    session = MagicMock()
    with pytest.raises(ExtractedObjectStoreError, match="title"):
        store_extracted_object(
            session,
            StoreExtractedObjectInput(
                object_type=ExtractedObjectType.QUESTION,
                payload_json={"body": "stem only"},
            ),
        )


def test_store_rejects_out_of_range_confidence() -> None:
    session = MagicMock()
    with pytest.raises(ExtractedObjectStoreError, match="confidence_score"):
        store_extracted_object(
            session,
            StoreExtractedObjectInput(
                object_type=ExtractedObjectType.FLASHCARD,
                payload_json={"front": "Q", "back": "A"},
                confidence_score=1.5,
            ),
        )


def test_store_flashcard_and_batch() -> None:
    session = MagicMock()
    session.get.return_value = None
    n = {"i": 0}

    def add(row: object) -> None:
        if isinstance(row, ExtractedObject):
            n["i"] += 1
            row.id = n["i"]

    session.add.side_effect = add

    rows = store_extracted_objects(
        session,
        [
            StoreExtractedObjectInput(
                object_type=ExtractedObjectType.FLASHCARD,
                payload_json={"front": "P(A|B)", "back": "P(A∩B)/P(B)"},
                confidence_score=0.8,
                extraction_method="manual:import",
                provenance=ProvenanceData(source_title="notes"),
            ),
            StoreExtractedObjectInput(
                object_type=ExtractedObjectType.QUESTION,
                payload_json={"title": "Bayes", "body": "State Bayes theorem."},
                extraction_method="manual:import",
                model_version=None,
            ),
        ],
        commit=True,
    )
    assert len(rows) == 2
    assert rows[0].object_type is ExtractedObjectType.FLASHCARD
    assert rows[0].payload_json["provenance"]["source_title"] == "notes"
    assert rows[1].extraction_method == "manual:import"
    session.commit.assert_called_once()


def test_load_provenance_from_resource_and_payload_roundtrip() -> None:
    resource = _resource(resource_id=5)
    provenance = load_provenance_from_resource(resource, topic_job_id=9)
    assert provenance.resource_id == 5
    assert provenance.topic_job_id == 9
    assert provenance.source_type == "url"

    payload = {
        "title": "x",
        "body": "y",
        "provenance": {
            "resource_id": 5,
            "topic_job_id": 9,
            "source_url": "https://example.com/bayes",
            "source_license": "CC-BY-4.0",
        },
    }
    loaded = provenance_from_payload(payload)
    assert loaded is not None
    assert loaded.resource_id == 5
    assert loaded.source_license == "CC-BY-4.0"


def test_get_stored_extracted_object_missing() -> None:
    session = MagicMock()
    session.scalar.return_value = None
    with pytest.raises(LookupError, match="not found"):
        get_stored_extracted_object(session, 999)


@pytest.mark.integration
def test_store_extracted_object_writes_to_database(
    migrated_database: None,
    require_postgres: None,
) -> None:
    from app.db import get_session_factory

    session = get_session_factory()()
    try:
        resource = Resource(
            source_type=ResourceSourceType.MANUAL,
            title="Local notes",
            license="private",
            attribution="local",
            summary="note body",
            status=ContentStatus.DRAFT,
        )
        session.add(resource)
        session.commit()

        stored = store_extracted_object(
            session,
            StoreExtractedObjectInput(
                object_type=ExtractedObjectType.QUESTION,
                payload_json={
                    "title": "Stored question",
                    "body": "What is a martingale?",
                    "topic_slug": "probability",
                },
                confidence_score=0.75,
                extraction_method="ai:structured:pasted_text",
                model_version="qwen2.5:3b",
                provenance=ProvenanceData(resource_id=resource.id),
            ),
            commit=True,
        )

        loaded = get_stored_extracted_object(session, stored.id)
        assert loaded.payload_json["title"] == "Stored question"
        assert loaded.confidence_score == 0.75
        assert loaded.extraction_method == "ai:structured:pasted_text"
        assert loaded.model_version == "qwen2.5:3b"
        assert loaded.resource_id == resource.id
        assert loaded.payload_json["provenance"]["source_title"] == "Local notes"
        assert loaded.payload_json["provenance"]["source_license"] == "private"
    finally:
        session.close()
