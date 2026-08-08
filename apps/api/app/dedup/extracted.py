from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any, Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dedup.detection import find_duplicate_matches
from app.dedup.fingerprints import NEAR_DUPLICATE_THRESHOLD, compute_question_fingerprints
from app.dedup.text import aggressively_normalize_question_text, question_canonical_text
from app.models.enums import ContentStatus, DuplicateMatchType, ExtractedObjectType
from app.models.extracted_object import ExtractedObject

CanonicalKind = Literal["extracted_object", "question", "self"]
MatchSource = Literal["extracted_object", "question"]


@dataclass(frozen=True, slots=True)
class ExtractedFingerprints:
    raw_hash: str
    normalized_hash: str
    normalized_text: str
    title: str
    body: str


@dataclass(frozen=True, slots=True)
class ExtractedDuplicateMatch:
    source: MatchSource
    object_id: int
    title: str
    match_type: DuplicateMatchType
    similarity_score: float | None = None
    status: ContentStatus | None = None
    confidence_score: float | None = None


@dataclass(frozen=True, slots=True)
class CanonicalSuggestion:
    kind: CanonicalKind
    object_id: int
    title: str
    reason: str


@dataclass(frozen=True, slots=True)
class ExtractedDedupeResult:
    extracted_object_id: int
    object_type: ExtractedObjectType
    fingerprints: ExtractedFingerprints
    matches: tuple[ExtractedDuplicateMatch, ...]
    suggested_canonical: CanonicalSuggestion


class ExtractedDedupeError(ValueError):
    """Raised when extracted-object deduplication cannot run."""


def fingerprints_from_extracted_payload(
    object_type: ExtractedObjectType,
    payload: dict[str, Any],
) -> ExtractedFingerprints:
    title, body = _title_body_from_payload(object_type, payload)
    raw_hash, normalized_hash, normalized_text = compute_question_fingerprints(title, body)
    return ExtractedFingerprints(
        raw_hash=raw_hash,
        normalized_hash=normalized_hash,
        normalized_text=normalized_text,
        title=title,
        body=body,
    )


def find_extracted_object_duplicates(
    session: Session,
    extracted_object_id: int,
) -> ExtractedDedupeResult:
    """Find near/exact text duplicates for an extracted draft (no embeddings).

    Compares against other ExtractedObject rows of the same type and, for
    questions, against published Question fingerprints (QP-013).
    """
    extracted = session.get(ExtractedObject, extracted_object_id)
    if extracted is None:
        raise LookupError(f"extracted object {extracted_object_id} not found")

    fingerprints = fingerprints_from_extracted_payload(
        extracted.object_type,
        extracted.payload_json or {},
    )
    matches: list[ExtractedDuplicateMatch] = []
    matches.extend(
        _matches_against_extracted_objects(
            session,
            source=extracted,
            fingerprints=fingerprints,
        )
    )
    if extracted.object_type is ExtractedObjectType.QUESTION:
        matches.extend(
            _matches_against_questions(
                session,
                fingerprints=fingerprints,
            )
        )

    ordered = tuple(_sort_matches(matches))
    suggestion = suggest_canonical_object(
        source=extracted,
        fingerprints=fingerprints,
        matches=ordered,
    )
    return ExtractedDedupeResult(
        extracted_object_id=extracted.id,
        object_type=extracted.object_type,
        fingerprints=fingerprints,
        matches=ordered,
        suggested_canonical=suggestion,
    )


def suggest_canonical_object(
    *,
    source: ExtractedObject,
    fingerprints: ExtractedFingerprints,
    matches: tuple[ExtractedDuplicateMatch, ...] | list[ExtractedDuplicateMatch],
) -> CanonicalSuggestion:
    """Pick a preferred representative for the duplicate cluster.

    Priority: exact match to an existing Question, then approved extracted
    object, then highest confidence, then oldest extracted id. Falls back to self.
    """
    exact_question = next(
        (
            match
            for match in matches
            if match.source == "question"
            and match.match_type
            in {DuplicateMatchType.EXACT_RAW, DuplicateMatchType.EXACT_NORMALIZED}
        ),
        None,
    )
    if exact_question is not None:
        return CanonicalSuggestion(
            kind="question",
            object_id=exact_question.object_id,
            title=exact_question.title,
            reason="exact match to published question",
        )

    candidates: list[tuple[tuple[int, float, int], CanonicalSuggestion]] = []
    # Self is always a candidate for "this cluster's draft representative".
    candidates.append(
        (
            _canonical_rank(
                status=source.status,
                confidence=source.confidence_score,
                object_id=source.id,
            ),
            CanonicalSuggestion(
                kind="self",
                object_id=source.id,
                title=fingerprints.title,
                reason="no stronger match; keep this draft",
            ),
        )
    )

    for match in matches:
        if match.source != "extracted_object":
            continue
        if match.match_type not in {
            DuplicateMatchType.EXACT_RAW,
            DuplicateMatchType.EXACT_NORMALIZED,
            DuplicateMatchType.NEAR_NORMALIZED,
        }:
            continue
        reason = (
            "exact extracted-object text match"
            if match.match_type
            in {DuplicateMatchType.EXACT_RAW, DuplicateMatchType.EXACT_NORMALIZED}
            else "near extracted-object text match"
        )
        if match.status is ContentStatus.APPROVED:
            reason = f"approved extracted object ({reason})"
        candidates.append(
            (
                _canonical_rank(
                    status=match.status or ContentStatus.DRAFT,
                    confidence=match.confidence_score,
                    object_id=match.object_id,
                ),
                CanonicalSuggestion(
                    kind="extracted_object",
                    object_id=match.object_id,
                    title=match.title,
                    reason=reason,
                ),
            )
        )

    candidates.sort(key=lambda item: item[0])
    return candidates[0][1]


def apply_extracted_duplicate_cluster(
    session: Session,
    extracted_object_id: int,
    *,
    commit: bool = True,
) -> ExtractedDedupeResult:
    """Write ``duplicate_cluster_id`` on this object and matching extracted drafts.

    Cluster key is the suggested extracted-object id, or the source id when the
    canonical suggestion is a published question or self.
    """
    result = find_extracted_object_duplicates(session, extracted_object_id)
    cluster_id = _cluster_id_for_result(result)

    source = session.get(ExtractedObject, extracted_object_id)
    if source is None:
        raise LookupError(f"extracted object {extracted_object_id} not found")

    ids = {extracted_object_id}
    for match in result.matches:
        if match.source == "extracted_object":
            ids.add(match.object_id)

    rows = session.scalars(select(ExtractedObject).where(ExtractedObject.id.in_(ids))).all()
    for row in rows:
        row.duplicate_cluster_id = cluster_id
        session.add(row)

    if commit:
        session.commit()
    return result


def _cluster_id_for_result(result: ExtractedDedupeResult) -> int:
    suggestion = result.suggested_canonical
    if suggestion.kind in {"self", "extracted_object"}:
        return suggestion.object_id
    # Question is preferred as content canonical; cluster EOs under the newest draft id.
    return result.extracted_object_id


def _matches_against_extracted_objects(
    session: Session,
    *,
    source: ExtractedObject,
    fingerprints: ExtractedFingerprints,
) -> list[ExtractedDuplicateMatch]:
    statement = select(ExtractedObject).where(
        ExtractedObject.object_type == source.object_type,
        ExtractedObject.id != source.id,
    )
    candidates = session.scalars(statement).all()
    aggressive = aggressively_normalize_question_text(
        question_canonical_text(fingerprints.title, fingerprints.body)
    )
    matches: list[ExtractedDuplicateMatch] = []
    matched_ids: set[int] = set()

    for candidate in candidates:
        try:
            candidate_fp = fingerprints_from_extracted_payload(
                candidate.object_type,
                candidate.payload_json or {},
            )
        except ExtractedDedupeError:
            continue

        if candidate_fp.raw_hash == fingerprints.raw_hash:
            matches.append(
                _eo_match(
                    candidate,
                    candidate_fp,
                    DuplicateMatchType.EXACT_RAW,
                    1.0,
                )
            )
            matched_ids.add(candidate.id)
            continue

        if candidate_fp.normalized_hash == fingerprints.normalized_hash:
            matches.append(
                _eo_match(
                    candidate,
                    candidate_fp,
                    DuplicateMatchType.EXACT_NORMALIZED,
                    1.0,
                )
            )
            matched_ids.add(candidate.id)

    for candidate in candidates:
        if candidate.id in matched_ids:
            continue
        try:
            candidate_fp = fingerprints_from_extracted_payload(
                candidate.object_type,
                candidate.payload_json or {},
            )
        except ExtractedDedupeError:
            continue

        similarity = SequenceMatcher(
            None,
            fingerprints.normalized_text,
            candidate_fp.normalized_text,
        ).ratio()
        if similarity >= NEAR_DUPLICATE_THRESHOLD:
            matches.append(
                _eo_match(
                    candidate,
                    candidate_fp,
                    DuplicateMatchType.NEAR_NORMALIZED,
                    round(similarity, 4),
                )
            )
            matched_ids.add(candidate.id)
            continue

        candidate_aggressive = aggressively_normalize_question_text(
            question_canonical_text(candidate_fp.title, candidate_fp.body)
        )
        if aggressive == candidate_aggressive:
            matches.append(
                _eo_match(
                    candidate,
                    candidate_fp,
                    DuplicateMatchType.NEAR_NORMALIZED,
                    1.0,
                )
            )

    return matches


def _matches_against_questions(
    session: Session,
    *,
    fingerprints: ExtractedFingerprints,
) -> list[ExtractedDuplicateMatch]:
    question_matches = find_duplicate_matches(
        session,
        title=fingerprints.title,
        body=fingerprints.body,
    )
    return [
        ExtractedDuplicateMatch(
            source="question",
            object_id=match.question_id,
            title=match.title,
            match_type=match.match_type,
            similarity_score=match.similarity_score,
            status=ContentStatus.APPROVED,
            confidence_score=None,
        )
        for match in question_matches
    ]


def _eo_match(
    candidate: ExtractedObject,
    fingerprints: ExtractedFingerprints,
    match_type: DuplicateMatchType,
    similarity: float,
) -> ExtractedDuplicateMatch:
    return ExtractedDuplicateMatch(
        source="extracted_object",
        object_id=candidate.id,
        title=fingerprints.title,
        match_type=match_type,
        similarity_score=similarity,
        status=candidate.status,
        confidence_score=candidate.confidence_score,
    )


def _title_body_from_payload(
    object_type: ExtractedObjectType,
    payload: dict[str, Any],
) -> tuple[str, str]:
    if object_type is ExtractedObjectType.QUESTION:
        title = _require_text(payload, "title", fallback_keys=("name",))
        body = _require_text(payload, "body", fallback_keys=("text", "question", "extracted_text"))
        return title, body

    if object_type is ExtractedObjectType.FLASHCARD:
        front = _require_text(payload, "front", fallback_keys=("title",))
        back = _require_text(payload, "back", fallback_keys=("extracted_text",))
        return front, f"{front}\n{back}"

    # Concept / formula / example: best-effort text for future use; QP-043 does not create them.
    title = _optional_text(payload, "name", "title", "front") or object_type.value
    body = (
        _optional_text(payload, "definition", "body", "text", "formula", "latex", "extracted_text")
        or title
    )
    if not body.strip():
        raise ExtractedDedupeError(f"{object_type.value} payload has no comparable text")
    return title.strip(), body.strip()


def _require_text(
    payload: dict[str, Any],
    key: str,
    *,
    fallback_keys: tuple[str, ...] = (),
) -> str:
    value = _optional_text(payload, key, *fallback_keys)
    if value is None:
        raise ExtractedDedupeError(f"payload missing comparable field '{key}'")
    return value


def _optional_text(payload: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _canonical_rank(
    *,
    status: ContentStatus,
    confidence: float | None,
    object_id: int,
) -> tuple[int, float, int]:
    # Lower tuple sorts first.
    if status is ContentStatus.APPROVED:
        status_rank = 0
    elif status is ContentStatus.DRAFT:
        status_rank = 1
    else:
        status_rank = 2
    confidence_rank = -(confidence if confidence is not None else -1.0)
    return (status_rank, confidence_rank, object_id)


def _sort_matches(
    matches: list[ExtractedDuplicateMatch],
) -> list[ExtractedDuplicateMatch]:
    return sorted(
        matches,
        key=lambda match: (
            _match_priority(match.match_type),
            0 if match.source == "question" else 1,
            -(match.similarity_score or 0.0),
            match.object_id,
        ),
    )


def _match_priority(match_type: DuplicateMatchType) -> int:
    if match_type is DuplicateMatchType.EXACT_RAW:
        return 0
    if match_type is DuplicateMatchType.EXACT_NORMALIZED:
        return 1
    return 2
