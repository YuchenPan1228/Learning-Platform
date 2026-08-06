from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from app.dedup.extracted import (
    ExtractedDedupeError,
    ExtractedDuplicateMatch,
    find_extracted_object_duplicates,
    fingerprints_from_extracted_payload,
    suggest_canonical_object,
)
from app.dedup.fingerprints import compute_question_fingerprints
from app.models.enums import (
    ContentStatus,
    Difficulty,
    DuplicateMatchType,
    ExtractedObjectType,
)
from app.models.extracted_object import ExtractedObject
from app.models.question import Question
from app.services.extracted_object_dedup import (
    get_extracted_object_duplicates,
    link_extracted_object_duplicate_cluster,
)


def _eo(
    *,
    object_id: int,
    title: str,
    body: str,
    status: ContentStatus = ContentStatus.DRAFT,
    confidence: float | None = 0.5,
    object_type: ExtractedObjectType = ExtractedObjectType.QUESTION,
) -> ExtractedObject:
    if object_type is ExtractedObjectType.QUESTION:
        payload: dict[str, str] = {"title": title, "body": body}
    else:
        payload = {"front": title, "back": body}
    row = ExtractedObject(
        object_type=object_type,
        payload_json=payload,
        confidence_score=confidence,
        status=status,
        extraction_method="test",
        model_version=None,
    )
    row.id = object_id
    row.created_at = datetime.now(UTC)
    row.updated_at = datetime.now(UTC)
    return row


def test_fingerprints_normalize_extracted_question_text() -> None:
    first = fingerprints_from_extracted_payload(
        ExtractedObjectType.QUESTION,
        {"title": "Coin Flip", "body": "What is P(heads)?"},
    )
    second = fingerprints_from_extracted_payload(
        ExtractedObjectType.QUESTION,
        {"title": "coin flip", "body": "what is p(heads)?"},
    )
    assert first.raw_hash != second.raw_hash
    assert first.normalized_hash == second.normalized_hash
    assert first.normalized_text == second.normalized_text


def test_fingerprints_for_flashcard_use_front_and_back() -> None:
    fp = fingerprints_from_extracted_payload(
        ExtractedObjectType.FLASHCARD,
        {"front": "P(A|B)", "back": "P(A and B)/P(B)"},
    )
    assert "P(A|B)" in fp.title
    assert fp.normalized_text


def test_fingerprints_reject_empty_question_payload() -> None:
    with pytest.raises(ExtractedDedupeError, match="missing"):
        fingerprints_from_extracted_payload(
            ExtractedObjectType.QUESTION,
            {"title": "Only title"},
        )


def test_find_extracted_duplicates_exact_and_near_against_other_drafts() -> None:
    source = _eo(object_id=1, title="Bayes", body="State Bayes theorem clearly.")
    exact = _eo(
        object_id=2,
        title="bayes",
        body="state bayes theorem clearly.",
        confidence=0.9,
    )
    near = _eo(
        object_id=3,
        title="Bayes",
        body="State Bayes theorem clearly!!",
        confidence=0.4,
    )
    unrelated = _eo(object_id=4, title="Other", body="What is a martingale?")

    session = MagicMock()
    session.get.return_value = source
    session.scalars.return_value.all.return_value = [exact, near, unrelated]
    # Question scan path uses session.execute for find_duplicate_matches; return empty.
    session.execute.return_value.all.return_value = []

    result = find_extracted_object_duplicates(session, 1)
    match_ids = {match.object_id for match in result.matches if match.source == "extracted_object"}
    assert 2 in match_ids
    assert 3 in match_ids
    assert 4 not in match_ids
    types = {
        match.object_id: match.match_type
        for match in result.matches
        if match.source == "extracted_object"
    }
    assert types[2] is DuplicateMatchType.EXACT_NORMALIZED
    assert types[3] in {
        DuplicateMatchType.NEAR_NORMALIZED,
        DuplicateMatchType.EXACT_NORMALIZED,
        DuplicateMatchType.EXACT_RAW,
    }
    assert result.suggested_canonical.object_id in {1, 2, 3}


def test_suggest_canonical_prefers_published_question() -> None:
    source = _eo(object_id=10, title="A", body="B")
    matches = (
        ExtractedDuplicateMatch(
            source="question",
            object_id=99,
            title="Published A",
            match_type=DuplicateMatchType.EXACT_NORMALIZED,
            similarity_score=1.0,
            status=ContentStatus.APPROVED,
        ),
        ExtractedDuplicateMatch(
            source="extracted_object",
            object_id=11,
            title="Draft A",
            match_type=DuplicateMatchType.EXACT_NORMALIZED,
            similarity_score=1.0,
            status=ContentStatus.DRAFT,
            confidence_score=0.99,
        ),
    )
    suggestion = suggest_canonical_object(
        source=source,
        fingerprints=fingerprints_from_extracted_payload(
            ExtractedObjectType.QUESTION,
            {"title": "A", "body": "B"},
        ),
        matches=matches,
    )
    assert suggestion.kind == "question"
    assert suggestion.object_id == 99


def test_suggest_canonical_prefers_approved_extracted_over_draft() -> None:
    source = _eo(object_id=10, title="A", body="B", confidence=0.99)
    matches = (
        ExtractedDuplicateMatch(
            source="extracted_object",
            object_id=11,
            title="Approved A",
            match_type=DuplicateMatchType.EXACT_RAW,
            similarity_score=1.0,
            status=ContentStatus.APPROVED,
            confidence_score=0.2,
        ),
    )
    suggestion = suggest_canonical_object(
        source=source,
        fingerprints=fingerprints_from_extracted_payload(
            ExtractedObjectType.QUESTION,
            {"title": "A", "body": "B"},
        ),
        matches=matches,
    )
    assert suggestion.kind == "extracted_object"
    assert suggestion.object_id == 11


def test_get_extracted_object_duplicates_read_model() -> None:
    source = _eo(object_id=1, title="Coin", body="P(heads)?")
    twin = _eo(object_id=2, title="coin", body="p(heads)?")
    session = MagicMock()
    session.get.return_value = source
    session.scalars.return_value.all.return_value = [twin]
    session.execute.return_value.all.return_value = []

    read = get_extracted_object_duplicates(session, 1)
    assert read.extracted_object_id == 1
    assert read.normalized_text_hash
    assert len(read.matches) == 1
    assert read.matches[0].match_type is DuplicateMatchType.EXACT_NORMALIZED
    assert read.suggested_canonical.object_id in {1, 2}


@pytest.mark.integration
def test_extracted_dedupe_against_published_question(
    migrated_database: None,
    require_postgres: None,
) -> None:
    from app.db import get_session_factory
    from app.models.topic import Topic

    session = get_session_factory()()
    try:
        topic = Topic(slug="dedupe-topic", name="Dedupe Topic", order_index=0)
        session.add(topic)
        session.flush()

        title = "Conditional Coin"
        body = "Two fair coins. Given at least one head, find P(HH)."
        raw, norm_hash, norm_text = compute_question_fingerprints(title, body)
        question = Question(
            title=title,
            body=body,
            difficulty=Difficulty.MEDIUM,
            topic_id=topic.id,
            status=ContentStatus.APPROVED,
            raw_text_hash=raw,
            normalized_text_hash=norm_hash,
            normalized_text=norm_text,
        )
        session.add(question)

        draft = ExtractedObject(
            object_type=ExtractedObjectType.QUESTION,
            payload_json={"title": "conditional coin", "body": body.lower()},
            confidence_score=0.7,
            status=ContentStatus.DRAFT,
            extraction_method="ai:structured:pasted_text",
            model_version="test",
        )
        twin = ExtractedObject(
            object_type=ExtractedObjectType.QUESTION,
            payload_json={"title": "conditional coin", "body": body.lower()},
            confidence_score=0.4,
            status=ContentStatus.DRAFT,
            extraction_method="manual:import",
        )
        session.add(draft)
        session.add(twin)
        session.commit()

        result = link_extracted_object_duplicate_cluster(session, draft.id, commit=True)
        assert any(
            match.source == "question" and match.object_id == question.id
            for match in result.matches
        )
        assert result.suggested_canonical.kind == "question"
        assert result.suggested_canonical.object_id == question.id

        session.refresh(draft)
        session.refresh(twin)
        assert draft.duplicate_cluster_id == draft.id
        assert twin.duplicate_cluster_id == draft.id
    finally:
        session.close()
