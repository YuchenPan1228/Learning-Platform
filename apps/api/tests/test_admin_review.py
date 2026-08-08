from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from app.models.enums import (
    ContentStatus,
    ExtractedObjectType,
    ResourceSourceType,
    SourcePolicyDecision,
)
from app.models.extracted_object import ExtractedObject
from app.models.resource import Resource
from app.schemas.admin_review import ExtractedObjectEdit
from app.schemas.extracted_duplicate import (
    CanonicalSuggestionRead,
    ExtractedDedupeResultRead,
)
from app.services.admin_review import (
    ReviewQueueError,
    approve_review_item,
    edit_review_item,
    get_review_item,
    list_review_items,
)
from fastapi.testclient import TestClient


def _draft_row(
    *,
    object_id: int = 1,
    status: ContentStatus = ContentStatus.DRAFT,
) -> ExtractedObject:
    now = datetime.now(UTC)
    resource = Resource(
        source_type=ResourceSourceType.URL,
        url="https://example.com/bayes",
        title="Bayes source",
        license="CC-BY-4.0",
        attribution="Example author",
        quality_score=0.65,
        domain_reputation_score=0.8,
        status=ContentStatus.DRAFT,
    )
    resource.id = 10
    row = ExtractedObject(
        resource_id=10,
        topic_job_id=None,
        object_type=ExtractedObjectType.QUESTION,
        payload_json={"title": "Bayes draft", "body": "What is P(A|B)?"},
        confidence_score=0.8,
        quality_score=0.7,
        status=status,
        extraction_method="manual",
        model_version="v1",
    )
    row.id = object_id
    row.created_at = now
    row.updated_at = now
    row.resource = resource
    return row


def _empty_dedupe(object_id: int = 1) -> ExtractedDedupeResultRead:
    return ExtractedDedupeResultRead(
        extracted_object_id=object_id,
        object_type=ExtractedObjectType.QUESTION,
        raw_text_hash="raw",
        normalized_text_hash="norm",
        normalized_text="what is p a b",
        matches=[],
        suggested_canonical=CanonicalSuggestionRead(
            kind="self",
            object_id=object_id,
            title="Bayes draft",
            reason="no_duplicates",
        ),
    )


def test_edit_review_item_updates_payload_and_preserves_provenance() -> None:
    session = MagicMock()
    row = _draft_row()
    session.scalar.side_effect = [row, row]

    with patch(
        "app.services.admin_review.get_extracted_object_duplicates",
        return_value=_empty_dedupe(),
    ):
        result = edit_review_item(
            session,
            1,
            ExtractedObjectEdit(
                payload_json={"title": "Edited Bayes", "body": "Define P(A|B)."},
                quality_score=0.9,
            ),
        )

    assert row.payload_json["title"] == "Edited Bayes"
    assert row.quality_score == 0.9
    assert row.resource_id == 10
    assert row.extraction_method == "manual"
    assert row.model_version == "v1"
    assert result.resource is not None
    assert result.resource.license == "CC-BY-4.0"
    assert result.quality is not None
    assert result.quality.overall_score == 0.9
    session.commit.assert_called_once()
    assert session.scalar.call_count == 2


def test_approve_requires_draft_status() -> None:
    session = MagicMock()
    session.scalar.return_value = _draft_row(status=ContentStatus.APPROVED)

    with pytest.raises(ReviewQueueError, match="only draft"):
        approve_review_item(session, 1)


def test_list_review_items_filters_by_status() -> None:
    session = MagicMock()
    draft = _draft_row(object_id=1)
    result_proxy = MagicMock()
    result_proxy.unique.return_value.all.return_value = [draft]
    session.scalars.return_value = result_proxy

    items = list_review_items(session, status=ContentStatus.DRAFT)
    assert len(items) == 1
    assert items[0].id == 1
    assert items[0].status is ContentStatus.DRAFT
    assert items[0].quality is not None
    assert items[0].quality.overall_score == 0.7
    assert items[0].policy is None
    assert items[0].duplicates is None
    session.scalars.assert_called_once()


def test_get_review_item_includes_quality_policy_and_duplicates() -> None:
    session = MagicMock()
    row = _draft_row()
    session.scalar.return_value = row
    dedupe = _empty_dedupe()

    with patch(
        "app.services.admin_review.get_extracted_object_duplicates",
        return_value=dedupe,
    ) as mock_dedupe:
        result = get_review_item(session, 1)

    mock_dedupe.assert_called_once_with(session, 1)
    assert result.quality is not None
    assert result.quality.overall_score == 0.7
    assert result.quality.domain_reputation_score == 0.8
    assert result.policy is not None
    assert result.policy.decision is SourcePolicyDecision.ALLOW
    assert result.policy.license_status.value == "permissive"
    assert result.duplicates is not None
    assert result.duplicates.extracted_object_id == 1
    assert result.resource is not None
    assert result.resource.domain_reputation_score == 0.8


@pytest.mark.integration
def test_review_queue_api_list_edit_approve_reject(
    migrated_database: None,
    require_postgres: None,
    client: TestClient,
) -> None:
    from app.db import get_session_factory
    from app.models.enums import ContentStatus, ExtractedObjectType, ResourceSourceType
    from app.models.extracted_object import ExtractedObject
    from app.models.resource import Resource

    session = get_session_factory()()
    try:
        resource = Resource(
            source_type=ResourceSourceType.MANUAL,
            title="Manual note source",
            license="private",
            attribution="local notes",
            summary="source summary",
            status=ContentStatus.DRAFT,
        )
        session.add(resource)
        session.flush()

        draft_a = ExtractedObject(
            resource_id=resource.id,
            object_type=ExtractedObjectType.QUESTION,
            payload_json={"title": "Q1", "body": "Body 1"},
            confidence_score=0.5,
            quality_score=0.4,
            status=ContentStatus.DRAFT,
            extraction_method="manual",
            model_version=None,
        )
        draft_b = ExtractedObject(
            resource_id=resource.id,
            object_type=ExtractedObjectType.QUESTION,
            payload_json={"title": "Q2", "body": "Body 2"},
            status=ContentStatus.DRAFT,
            extraction_method="manual",
        )
        approved = ExtractedObject(
            resource_id=resource.id,
            object_type=ExtractedObjectType.CONCEPT,
            payload_json={"name": "Already approved"},
            status=ContentStatus.APPROVED,
            extraction_method="manual",
        )
        session.add_all([draft_a, draft_b, approved])
        session.commit()
        draft_a_id = draft_a.id
        draft_b_id = draft_b.id
        resource_id = resource.id
    finally:
        session.close()

    list_response = client.get("/admin/review")
    assert list_response.status_code == 200
    list_body = list_response.json()
    ids = {item["id"] for item in list_body["items"]}
    assert draft_a_id in ids
    assert draft_b_id in ids
    assert all(item["status"] == "draft" for item in list_body["items"])
    matched = next(item for item in list_body["items"] if item["id"] == draft_a_id)
    assert matched["resource"]["id"] == resource_id
    assert matched["resource"]["license"] == "private"
    assert matched["extraction_method"] == "manual"

    edit_response = client.patch(
        f"/admin/review/{draft_a_id}",
        json={
            "payload_json": {"title": "Q1 edited", "body": "Body 1 edited"},
            "quality_score": 0.95,
        },
    )
    assert edit_response.status_code == 200
    edited = edit_response.json()
    assert edited["payload_json"]["title"] == "Q1 edited"
    assert edited["quality_score"] == 0.95
    assert edited["resource_id"] == resource_id
    assert edited["extraction_method"] == "manual"
    assert edited["resource"]["attribution"] == "local notes"

    approve_response = client.post(f"/admin/review/{draft_a_id}/approve")
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"
    assert approve_response.json()["resource_id"] == resource_id

    reject_response = client.post(f"/admin/review/{draft_b_id}/reject")
    assert reject_response.status_code == 200
    assert reject_response.json()["status"] == "rejected"

    # Drafts are gone from the default queue.
    after = client.get("/admin/review").json()
    after_ids = {item["id"] for item in after["items"]}
    assert draft_a_id not in after_ids
    assert draft_b_id not in after_ids

    # Cannot re-approve an already approved item.
    second_approve = client.post(f"/admin/review/{draft_a_id}/approve")
    assert second_approve.status_code == 400

    missing = client.get("/admin/review/999999")
    assert missing.status_code == 404
