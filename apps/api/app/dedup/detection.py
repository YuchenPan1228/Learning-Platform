from dataclasses import dataclass
from difflib import SequenceMatcher

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dedup.fingerprints import NEAR_DUPLICATE_THRESHOLD, compute_question_fingerprints
from app.dedup.text import aggressively_normalize_question_text, question_canonical_text
from app.models.enums import DuplicateMatchType
from app.models.question import Question


@dataclass(frozen=True, slots=True)
class DuplicateMatch:
    question_id: int
    title: str
    match_type: DuplicateMatchType
    similarity_score: float | None = None


def find_duplicate_matches(
    session: Session,
    *,
    title: str,
    body: str,
    exclude_question_id: int | None = None,
) -> list[DuplicateMatch]:
    raw_hash, normalized_hash, normalized_text = compute_question_fingerprints(title, body)
    aggressive_text = aggressively_normalize_question_text(question_canonical_text(title, body))

    statement = select(
        Question.id,
        Question.title,
        Question.raw_text_hash,
        Question.normalized_text_hash,
        Question.normalized_text,
    )
    if exclude_question_id is not None:
        statement = statement.where(Question.id != exclude_question_id)

    candidates = session.execute(statement).all()
    matches: list[DuplicateMatch] = []
    matched_ids: set[int] = set()

    for (
        question_id,
        question_title,
        candidate_raw_hash,
        candidate_normalized_hash,
        _candidate_normalized_text,
    ) in candidates:
        if candidate_raw_hash == raw_hash:
            matches.append(
                DuplicateMatch(
                    question_id=question_id,
                    title=question_title,
                    match_type=DuplicateMatchType.EXACT_RAW,
                    similarity_score=1.0,
                )
            )
            matched_ids.add(question_id)
            continue

        if candidate_normalized_hash == normalized_hash:
            matches.append(
                DuplicateMatch(
                    question_id=question_id,
                    title=question_title,
                    match_type=DuplicateMatchType.EXACT_NORMALIZED,
                    similarity_score=1.0,
                )
            )
            matched_ids.add(question_id)

    for question_id, question_title, _, _, candidate_normalized_text in candidates:
        if question_id in matched_ids or candidate_normalized_text is None:
            continue

        similarity = SequenceMatcher(None, normalized_text, candidate_normalized_text).ratio()
        if similarity >= NEAR_DUPLICATE_THRESHOLD:
            matches.append(
                DuplicateMatch(
                    question_id=question_id,
                    title=question_title,
                    match_type=DuplicateMatchType.NEAR_NORMALIZED,
                    similarity_score=round(similarity, 4),
                )
            )
            matched_ids.add(question_id)
            continue

        candidate_aggressive = aggressively_normalize_question_text(candidate_normalized_text)
        if aggressive_text == candidate_aggressive:
            matches.append(
                DuplicateMatch(
                    question_id=question_id,
                    title=question_title,
                    match_type=DuplicateMatchType.NEAR_NORMALIZED,
                    similarity_score=1.0,
                )
            )

    return sorted(
        matches,
        key=lambda match: (
            _match_priority(match.match_type),
            -(match.similarity_score or 0.0),
            match.question_id,
        ),
    )


def find_question_duplicates(session: Session, question_id: int) -> list[DuplicateMatch]:
    question = session.get(Question, question_id)
    if question is None:
        return []
    return find_duplicate_matches(
        session,
        title=question.title,
        body=question.body,
        exclude_question_id=question_id,
    )


def _match_priority(match_type: DuplicateMatchType) -> int:
    if match_type == DuplicateMatchType.EXACT_RAW:
        return 0
    if match_type == DuplicateMatchType.EXACT_NORMALIZED:
        return 1
    return 2
