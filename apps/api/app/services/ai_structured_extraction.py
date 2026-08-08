from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.errors import AIProviderConfigurationError, AIProviderRequestError
from app.ai.prompt_hash import compute_prompt_hash
from app.ai.provider import AIProvider
from app.ai.structured import StructuredOutputError, chat_structured
from app.ai.tasks import AITask
from app.ai.types import AIMessage, AIMessageRole
from app.config import get_settings
from app.models.enums import (
    AICacheResultKind,
    ExtractedObjectType,
    ExtractionMethod,
)
from app.models.extracted_object import ExtractedObject
from app.models.resource import Resource
from app.schemas.ai_extraction import (
    AIProposedQuestionDraft,
    AIStructuredExtractionContent,
    AIStructuredExtractionResult,
    ExtractedDraftSummary,
)
from app.services.ai_cache import AICacheLookupKey, get_cached_ai_result, store_cached_ai_result
from app.services.extracted_object_store import (
    ExtractedObjectStoreError,
    ProvenanceData,
    StoreExtractedObjectInput,
    store_extracted_objects,
)
from app.services.source_extraction import (
    ExtractedSourceText,
    SourceExtractionError,
    extract_from_resource,
)

PROMPT_TEMPLATE_VERSION = "structured-source-extraction:v3-math-and-multipart"
EXTRACTION_TASK = AITask.REASONING
_DEFAULT_CONFIDENCE = 0.6
# Soft cap per model call; long multi-problem pages are chunked instead of hard-truncated.
_MAX_SOURCE_CHARS = 10_000
_MAX_QUESTIONS_PER_CALL = 12
_MAX_TOTAL_QUESTIONS = 40
_METHOD_PREFIX = "ai:structured"
_PROBLEM_SPLIT_RE = re.compile(
    r"(?mi)(?=^\s*(?:#{1,6}\s*)?(?:problem|question|exercise|q)\s*#?\s*\d+\s*[\.\:\)\-]\s+)",
)
_SOLUTION_SPLIT_RE = re.compile(
    r"(?is)\b(?:\*{0,2})solution\.?(?:\*{0,2})\s*",
)


class AIStructuredExtractionError(ValueError):
    """Raised when structured source extraction fails or yields no drafts."""


@dataclass(frozen=True, slots=True)
class StructuredExtractionInput:
    source_text: str
    source_url: str | None = None
    source_title: str | None = None
    source_method: ExtractionMethod | str | None = None
    resource_id: int | None = None
    topic_job_id: int | None = None
    # Optional user-provided anchors; AI may still suggest topics.
    topic_slug_hint: str | None = None
    subtopic_slug_hint: str | None = None


def extract_structured_drafts(
    session: Session,
    provider: AIProvider,
    data: StructuredExtractionInput,
    *,
    commit: bool = True,
) -> AIStructuredExtractionResult:
    """Parse long source text into question draft rows (no auto-publish).

    Creates ExtractedObject rows with status draft for the existing review queue.
    Concepts/formulas/examples/flashcards are intentionally not created.
    """
    cleaned = (data.source_text or "").strip()
    if not cleaned:
        raise AIStructuredExtractionError("source_text must not be blank")

    model = provider.model_for_task(EXTRACTION_TASK)
    chunks = _source_chunks(cleaned)
    merged_questions: list[AIProposedQuestionDraft] = []
    summaries: list[str] = []
    topic_slug: str | None = None
    subtopic_slug: str | None = None
    source_title: str | None = data.source_title
    any_cache_hit = False
    all_cache_hits = True

    for chunk_index, chunk in enumerate(chunks):
        content, cache_hit = _extract_chunk(
            session,
            provider,
            data=data,
            source_text=chunk,
            model=model,
            chunk_index=chunk_index,
            chunk_count=len(chunks),
        )
        any_cache_hit = any_cache_hit or cache_hit
        all_cache_hits = all_cache_hits and cache_hit
        if content.summary:
            summaries.append(content.summary.strip())
        if topic_slug is None:
            topic_slug = _blank_to_none(content.topic_slug)
        if subtopic_slug is None:
            subtopic_slug = _blank_to_none(content.subtopic_slug)
        if source_title is None:
            source_title = _blank_to_none(content.source_title)
        for question in content.questions:
            normalized = _normalize_question_draft(question)
            if normalized is None:
                continue
            if _is_duplicate_question(normalized, merged_questions):
                continue
            merged_questions.append(normalized)
            if len(merged_questions) >= _MAX_TOTAL_QUESTIONS:
                break
        if len(merged_questions) >= _MAX_TOTAL_QUESTIONS:
            break

    if not merged_questions:
        raise AIStructuredExtractionError("model proposed no question drafts")

    content = AIStructuredExtractionContent(
        summary=_join_summaries(summaries),
        topic_slug=topic_slug,
        subtopic_slug=subtopic_slug,
        source_title=source_title,
        questions=merged_questions,
    )
    extraction_method = _format_extraction_method(data.source_method)
    # Full-source excerpt for review UI; not what was sent to every model call.
    source_for_payload = (
        cleaned if len(cleaned) <= 50_000 else cleaned[:50_000] + "\n...[truncated]"
    )

    drafts = _persist_drafts(
        session,
        content=content,
        data=data,
        source_text=source_for_payload,
        extraction_method=extraction_method,
        model_version=model,
    )
    if commit:
        session.commit()
        for row in drafts:
            session.refresh(row)

    return AIStructuredExtractionResult(
        summary=content.summary,
        topic_slug=_blank_to_none(data.topic_slug_hint) or _blank_to_none(content.topic_slug),
        subtopic_slug=_blank_to_none(data.subtopic_slug_hint)
        or _blank_to_none(content.subtopic_slug),
        source_title=content.source_title or data.source_title,
        model_version=model,
        extraction_method=extraction_method,
        # True only when every chunk was served from cache (matches prior single-call semantics).
        cache_hit=all_cache_hits and any_cache_hit,
        drafts=[_draft_summary(row) for row in drafts],
    )


def extract_structured_drafts_from_resource(
    session: Session,
    provider: AIProvider,
    resource: Resource,
    *,
    topic_job_id: int | None = None,
    topic_slug_hint: str | None = None,
    subtopic_slug_hint: str | None = None,
    preextracted: ExtractedSourceText | None = None,
    commit: bool = True,
) -> AIStructuredExtractionResult:
    """Run QP-042 text extract when needed, then structured AI parse into drafts."""
    if resource.id is None:
        raise AIStructuredExtractionError("resource must be persisted before extraction")

    try:
        source = preextracted or extract_from_resource(resource)
    except SourceExtractionError as exc:
        raise AIStructuredExtractionError(str(exc)) from exc

    return extract_structured_drafts(
        session,
        provider,
        StructuredExtractionInput(
            source_text=source.text,
            source_url=source.source_url or resource.url,
            source_title=source.title or resource.title,
            source_method=source.method,
            resource_id=resource.id,
            topic_job_id=topic_job_id,
            topic_slug_hint=topic_slug_hint,
            subtopic_slug_hint=subtopic_slug_hint,
        ),
        commit=commit,
    )


def _extract_chunk(
    session: Session,
    provider: AIProvider,
    *,
    data: StructuredExtractionInput,
    source_text: str,
    model: str,
    chunk_index: int,
    chunk_count: int,
) -> tuple[AIStructuredExtractionContent, bool]:
    prompt_payload = _prompt_payload(
        source_text=source_text,
        source_url=data.source_url,
        source_title=data.source_title,
        topic_slug_hint=data.topic_slug_hint,
        subtopic_slug_hint=data.subtopic_slug_hint,
        chunk_index=chunk_index,
        chunk_count=chunk_count,
    )
    prompt_hash = compute_prompt_hash(
        prompt_template_version=PROMPT_TEMPLATE_VERSION,
        prompt_payload=prompt_payload,
    )
    input_object_version = _input_object_version(
        data=data,
        source_text=source_text,
        chunk_index=chunk_index,
        chunk_count=chunk_count,
    )
    cache_key = AICacheLookupKey(
        provider=provider.provider_name,
        model=model,
        result_kind=AICacheResultKind.GENERATED_QUESTION,
        prompt_template_version=PROMPT_TEMPLATE_VERSION,
        prompt_hash=prompt_hash,
        input_object_version=input_object_version,
    )

    cached = get_cached_ai_result(session, cache_key)
    if cached is not None:
        try:
            return AIStructuredExtractionContent.model_validate(cached.response_json), True
        except ValidationError:
            pass

    try:
        content, _result = chat_structured(
            provider,
            [
                AIMessage(role=AIMessageRole.SYSTEM, content=_system_prompt()),
                AIMessage(
                    role=AIMessageRole.USER,
                    content=json.dumps(prompt_payload, sort_keys=True),
                ),
            ],
            response_model=AIStructuredExtractionContent,
            model=model,
            temperature=0.2,
            max_tokens=4096,
            # Small local models often need one repair pass when schema grammar falls back.
            repair_attempts=max(1, get_settings().ai_json_repair_attempts),
            cache_hit=False,
            prompt_hash=prompt_hash,
            input_object_version=input_object_version,
        )
    except (
        StructuredOutputError,
        AIProviderRequestError,
        AIProviderConfigurationError,
    ) as exc:
        raise AIStructuredExtractionError(str(exc)) from exc

    store_cached_ai_result(session, cache_key, content.model_dump(mode="json"))
    return content, False


def _persist_drafts(
    session: Session,
    *,
    content: AIStructuredExtractionContent,
    data: StructuredExtractionInput,
    source_text: str,
    extraction_method: str,
    model_version: str,
) -> list[ExtractedObject]:
    # Prefer user-chosen import topic hints; fall back to AI suggestions (ADR-013).
    topic_slug = _blank_to_none(data.topic_slug_hint) or _blank_to_none(content.topic_slug)
    subtopic_slug = _blank_to_none(data.subtopic_slug_hint) or _blank_to_none(content.subtopic_slug)
    source_summary = _blank_to_none(content.summary)
    source_title = _blank_to_none(content.source_title) or _blank_to_none(data.source_title)
    provenance = ProvenanceData(
        resource_id=data.resource_id,
        topic_job_id=data.topic_job_id,
        source_url=data.source_url,
        source_title=source_title,
    )

    items: list[StoreExtractedObjectInput] = []
    for question in content.questions:
        payload = _question_payload(
            question,
            topic_slug=topic_slug,
            subtopic_slug=subtopic_slug,
            source_summary=source_summary,
            source_title=source_title,
            source_url=data.source_url,
            source_text=source_text,
        )
        items.append(
            StoreExtractedObjectInput(
                object_type=ExtractedObjectType.QUESTION,
                payload_json=payload,
                confidence_score=_confidence(question.confidence_score),
                extraction_method=extraction_method,
                model_version=model_version,
                provenance=provenance,
            )
        )

    try:
        return store_extracted_objects(session, items, commit=False)
    except ExtractedObjectStoreError as exc:
        raise AIStructuredExtractionError(str(exc)) from exc


def _question_payload(
    question: AIProposedQuestionDraft,
    *,
    topic_slug: str | None,
    subtopic_slug: str | None,
    source_summary: str | None,
    source_title: str | None,
    source_url: str | None,
    source_text: str,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "title": question.title.strip(),
        "body": question.body.strip(),
        "extracted_text": question.body.strip(),
        "source_excerpt": _excerpt(source_text),
    }
    if question.short_answer is not None and question.short_answer.strip():
        payload["short_answer"] = question.short_answer.strip()
    if question.canonical_solution is not None and question.canonical_solution.strip():
        payload["canonical_solution"] = question.canonical_solution.strip()
        payload["solution"] = question.canonical_solution.strip()
    if question.difficulty is not None:
        payload["difficulty"] = question.difficulty.value
    _attach_shared_metadata(
        payload,
        topic_slug=topic_slug,
        subtopic_slug=subtopic_slug,
        source_summary=source_summary,
        source_title=source_title,
        source_url=source_url,
    )
    return payload


def _attach_shared_metadata(
    payload: dict[str, Any],
    *,
    topic_slug: str | None,
    subtopic_slug: str | None,
    source_summary: str | None,
    source_title: str | None,
    source_url: str | None,
) -> None:
    if topic_slug is not None:
        payload["topic_slug"] = topic_slug
    if subtopic_slug is not None:
        payload["subtopic_slug"] = subtopic_slug
    if source_summary is not None:
        payload["source_summary"] = source_summary
    if source_title is not None:
        payload["source_title"] = source_title
    if source_url is not None:
        payload["source_url"] = source_url


def _draft_summary(row: ExtractedObject) -> ExtractedDraftSummary:
    payload = row.payload_json or {}
    title = payload.get("title") or payload.get("front")
    title_str = str(title) if title is not None else None
    return ExtractedDraftSummary(
        id=row.id,
        object_type=row.object_type,
        title=title_str,
        confidence_score=row.confidence_score,
    )


def _system_prompt() -> str:
    return (
        "You extract quant interview practice questions from educational source text. "
        "Return JSON only matching the schema. "
        "Rules:\n"
        "1. Emit ONE questions[] entry per distinct interview problem in the source.\n"
        "2. title: short label (not the full stem). body: the full problem stem only — "
        "do NOT put solutions, derivations, or 'Solution.' sections in body.\n"
        "3. When the source has 'Solution.' / answer text, put it in canonical_solution "
        "(and a brief short_answer when a final numeric/closed form is clear).\n"
        "4. Preserve mathematical notation exactly as given, including "
        "$...$ / $$...$$ LaTeX.\n"
        "5. Do not invent problems absent from the source. "
        "Do not invent proprietary firm secrets.\n"
        "6. If the source lists many numbered problems "
        "(Problem 1, Problem 2, …), extract each one.\n"
        "7. difficulty is easy|medium|hard|expert when you can judge; confidence_score is 0-1.\n"
        "8. Suggest topic_slug / subtopic_slug as lowercase kebab-case "
        "(examples: probability, conditional-probability).\n"
        "9. Include a short summary of this source chunk and optional source_title.\n"
        "10. Only questions — no flashcards, concepts, formulas, or examples."
    )


def _prompt_payload(
    *,
    source_text: str,
    source_url: str | None,
    source_title: str | None,
    topic_slug_hint: str | None,
    subtopic_slug_hint: str | None,
    chunk_index: int,
    chunk_count: int,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "source_text": source_text,
        "instructions": (
            "Parse source_text into structured interview questions. "
            "Separate problem stems from solutions. "
            "Keep all math tokens (e.g. $\\mathbb{E}[3]$, $\\frac{1}{2}$) intact. "
            f"Return at most {_MAX_QUESTIONS_PER_CALL} high-quality questions for this chunk. "
            "If this chunk is only intro text with no interview problems, return questions:[]."
        ),
        "chunk_index": chunk_index,
        "chunk_count": chunk_count,
    }
    if source_url:
        payload["source_url"] = source_url
    if source_title:
        payload["source_title"] = source_title
    if topic_slug_hint:
        payload["topic_slug_hint"] = topic_slug_hint
    if subtopic_slug_hint:
        payload["subtopic_slug_hint"] = subtopic_slug_hint
    return payload


def _source_chunks(text: str) -> list[str]:
    """Split long multi-problem dumps so small models can extract complete lists."""
    cleaned = text.strip()
    if not cleaned:
        return []

    problem_parts = _split_numbered_problems(cleaned)
    if len(problem_parts) >= 2:
        return _pack_chunks(problem_parts, max_chars=_MAX_SOURCE_CHARS)

    if len(cleaned) <= _MAX_SOURCE_CHARS:
        return [cleaned]

    # Fall back to paragraph-aware windows for non-enumerated pages.
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", cleaned) if p.strip()]
    if not paragraphs:
        return [_truncate_source(cleaned)]
    return _pack_chunks(paragraphs, max_chars=_MAX_SOURCE_CHARS)


def _split_numbered_problems(text: str) -> list[str]:
    matches = list(_PROBLEM_SPLIT_RE.finditer(text))
    if len(matches) < 2:
        return []

    parts: list[str] = []
    # Keep a short shared preface with the first problem for context.
    first_start = matches[0].start()
    preface = text[:first_start].strip()
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.start() : end].strip()
        if not body:
            continue
        if index == 0 and preface and len(preface) <= 1_500:
            parts.append(f"{preface}\n\n{body}".strip())
        else:
            parts.append(body)
    return parts


def _pack_chunks(pieces: list[str], *, max_chars: int) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for piece in pieces:
        piece = piece.strip()
        if not piece:
            continue
        # Oversized single problem: hard-split as a last resort.
        if len(piece) > max_chars:
            if current:
                chunks.append("\n\n".join(current).strip())
                current = []
                current_len = 0
            chunks.extend(_hard_split(piece, max_chars=max_chars))
            continue
        separator = 2 if current else 0
        if current and current_len + separator + len(piece) > max_chars:
            chunks.append("\n\n".join(current).strip())
            current = [piece]
            current_len = len(piece)
        else:
            current.append(piece)
            current_len += separator + len(piece)

    if current:
        chunks.append("\n\n".join(current).strip())
    return [c for c in chunks if c]


def _hard_split(text: str, *, max_chars: int) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        if end < len(text):
            # Prefer a newline boundary when nearby.
            window = text[start:end]
            nl = window.rfind("\n")
            if nl >= max_chars // 2:
                end = start + nl
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end if end > start else start + max_chars
    return chunks


def _normalize_question_draft(question: AIProposedQuestionDraft) -> AIProposedQuestionDraft | None:
    title = (question.title or "").strip()
    body = (question.body or "").strip()
    if not title or not body:
        return None

    # Models sometimes paste the solution into body; re-split on an explicit Solution marker.
    body, recovered_solution = _split_stem_and_solution(body)
    if not body:
        return None

    solution = (question.canonical_solution or "").strip()
    if recovered_solution and not solution:
        solution = recovered_solution
    elif recovered_solution and solution and recovered_solution not in solution:
        solution = f"{recovered_solution}\n\n{solution}".strip()

    short = (question.short_answer or "").strip() or None
    return AIProposedQuestionDraft(
        title=title[:300],
        body=body,
        short_answer=short,
        canonical_solution=solution or None,
        difficulty=question.difficulty,
        confidence_score=question.confidence_score,
    )


def _split_stem_and_solution(text: str) -> tuple[str, str | None]:
    match = _SOLUTION_SPLIT_RE.search(text)
    if not match or match.start() == 0:
        return text.strip(), None
    stem = text[: match.start()].strip()
    solution = text[match.end() :].strip()
    # Avoid splitting mid-word / tiny prefixes; require a real stem.
    if len(stem) < 8 or not solution:
        return text.strip(), None
    return stem, solution


def _is_duplicate_question(
    candidate: AIProposedQuestionDraft,
    existing: list[AIProposedQuestionDraft],
) -> bool:
    body_key = _fingerprint(candidate.body)
    title_key = _fingerprint(candidate.title)
    for other in existing:
        if body_key and body_key == _fingerprint(other.body):
            return True
        if title_key and title_key == _fingerprint(other.title) and len(title_key) >= 24:
            return True
    return False


def _fingerprint(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _join_summaries(summaries: list[str]) -> str | None:
    unique: list[str] = []
    seen: set[str] = set()
    for summary in summaries:
        key = summary.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(summary)
    if not unique:
        return None
    joined = " ".join(unique)
    return joined[:2000]


def _format_extraction_method(source_method: ExtractionMethod | str | None) -> str:
    if source_method is None:
        return f"{_METHOD_PREFIX}:source_text"
    if isinstance(source_method, ExtractionMethod):
        return f"{_METHOD_PREFIX}:{source_method.value}"
    cleaned = source_method.strip()
    return f"{_METHOD_PREFIX}:{cleaned or 'source_text'}"


def _truncate_source(text: str) -> str:
    if len(text) <= _MAX_SOURCE_CHARS:
        return text
    return text[:_MAX_SOURCE_CHARS].rstrip() + "\n...[truncated]"


def _excerpt(text: str, *, limit: int = 500) -> str:
    cleaned = text.strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit].rstrip() + "…"


def _confidence(value: float | None) -> float:
    if value is None:
        return _DEFAULT_CONFIDENCE
    return value


def _input_object_version(
    *,
    data: StructuredExtractionInput,
    source_text: str,
    chunk_index: int,
    chunk_count: int,
) -> str:
    base = f"resource:{data.resource_id}" if data.resource_id is not None else "source_text"
    return f"{base}:chunk:{chunk_index}/{chunk_count}:chars:{len(source_text)}"


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None
