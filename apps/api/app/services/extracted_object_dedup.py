from sqlalchemy.orm import Session

from app.dedup.extracted import (
    CanonicalSuggestion,
    ExtractedDedupeError,
    ExtractedDedupeResult,
    ExtractedDuplicateMatch,
    apply_extracted_duplicate_cluster,
    find_extracted_object_duplicates,
    fingerprints_from_extracted_payload,
    suggest_canonical_object,
)
from app.schemas.extracted_duplicate import (
    CanonicalSuggestionRead,
    ExtractedDedupeResultRead,
    ExtractedDuplicateMatchRead,
)


def get_extracted_object_duplicates(
    session: Session,
    extracted_object_id: int,
) -> ExtractedDedupeResultRead:
    result = find_extracted_object_duplicates(session, extracted_object_id)
    return _to_read(result)


def link_extracted_object_duplicate_cluster(
    session: Session,
    extracted_object_id: int,
    *,
    commit: bool = True,
) -> ExtractedDedupeResultRead:
    result = apply_extracted_duplicate_cluster(
        session,
        extracted_object_id,
        commit=commit,
    )
    return _to_read(result)


def _to_read(result: ExtractedDedupeResult) -> ExtractedDedupeResultRead:
    return ExtractedDedupeResultRead(
        extracted_object_id=result.extracted_object_id,
        object_type=result.object_type,
        raw_text_hash=result.fingerprints.raw_hash,
        normalized_text_hash=result.fingerprints.normalized_hash,
        normalized_text=result.fingerprints.normalized_text,
        matches=[_match_read(match) for match in result.matches],
        suggested_canonical=_canonical_read(result.suggested_canonical),
    )


def _match_read(match: ExtractedDuplicateMatch) -> ExtractedDuplicateMatchRead:
    return ExtractedDuplicateMatchRead(
        source=match.source,
        object_id=match.object_id,
        title=match.title,
        match_type=match.match_type,
        similarity_score=match.similarity_score,
        status=match.status,
        confidence_score=match.confidence_score,
    )


def _canonical_read(suggestion: CanonicalSuggestion) -> CanonicalSuggestionRead:
    return CanonicalSuggestionRead(
        kind=suggestion.kind,
        object_id=suggestion.object_id,
        title=suggestion.title,
        reason=suggestion.reason,
    )


__all__ = [
    "ExtractedDedupeError",
    "apply_extracted_duplicate_cluster",
    "find_extracted_object_duplicates",
    "fingerprints_from_extracted_payload",
    "get_extracted_object_duplicates",
    "link_extracted_object_duplicate_cluster",
    "suggest_canonical_object",
]
