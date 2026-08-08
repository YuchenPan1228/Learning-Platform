from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.prompt_hash import compute_prompt_hash
from app.ai.provider import AIProvider
from app.ai.structured import StructuredOutputError, chat_structured
from app.ai.tasks import AITask
from app.ai.types import AIMessage, AIMessageRole
from app.models.enums import (
    AICacheResultKind,
    ExtractedObjectType,
    ExtractionMethod,
)
from app.models.extracted_object import ExtractedObject
from app.models.resource import Resource
from app.schemas.ai_extraction import (
    AIProposedFlashcardDraft,
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

PROMPT_TEMPLATE_VERSION = "structured-source-extraction:v1"
EXTRACTION_TASK = AITask.REASONING
_DEFAULT_CONFIDENCE = 0.6
_MAX_SOURCE_CHARS = 12_000
_METHOD_PREFIX = "ai:structured"


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
    """Parse long source text into question/flashcard draft rows (no auto-publish).

    Creates ExtractedObject rows with status draft for the existing review queue.
    Concepts/formulas/examples are intentionally not created (ADR-012).
    """
    cleaned = (data.source_text or "").strip()
    if not cleaned:
        raise AIStructuredExtractionError("source_text must not be blank")

    model = provider.model_for_task(EXTRACTION_TASK)
    truncated = _truncate_source(cleaned)
    prompt_payload = _prompt_payload(
        source_text=truncated,
        source_url=data.source_url,
        source_title=data.source_title,
        topic_slug_hint=data.topic_slug_hint,
        subtopic_slug_hint=data.subtopic_slug_hint,
    )
    prompt_hash = compute_prompt_hash(
        prompt_template_version=PROMPT_TEMPLATE_VERSION,
        prompt_payload=prompt_payload,
    )
    input_object_version = _input_object_version(data=data, source_text=truncated)
    extraction_method = _format_extraction_method(data.source_method)
    cache_key = AICacheLookupKey(
        provider=provider.provider_name,
        model=model,
        result_kind=AICacheResultKind.GENERATED_QUESTION,
        prompt_template_version=PROMPT_TEMPLATE_VERSION,
        prompt_hash=prompt_hash,
        input_object_version=input_object_version,
    )

    cached = get_cached_ai_result(session, cache_key)
    cache_hit = False
    if cached is not None:
        try:
            content = AIStructuredExtractionContent.model_validate(cached.response_json)
            cache_hit = True
        except ValidationError:
            content = None
    else:
        content = None

    if content is None:
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
                max_tokens=2048,
                cache_hit=False,
                prompt_hash=prompt_hash,
                input_object_version=input_object_version,
            )
        except StructuredOutputError as exc:
            raise AIStructuredExtractionError(str(exc)) from exc
        store_cached_ai_result(session, cache_key, content.model_dump(mode="json"))

    if not content.questions and not content.flashcards:
        raise AIStructuredExtractionError(
            "model proposed no question or flashcard drafts",
        )

    drafts = _persist_drafts(
        session,
        content=content,
        data=data,
        source_text=truncated,
        extraction_method=extraction_method,
        model_version=model,
    )
    if commit:
        session.commit()
        for row in drafts:
            session.refresh(row)

    return AIStructuredExtractionResult(
        summary=content.summary,
        topic_slug=content.topic_slug or data.topic_slug_hint,
        subtopic_slug=content.subtopic_slug or data.subtopic_slug_hint,
        source_title=content.source_title or data.source_title,
        model_version=model,
        extraction_method=extraction_method,
        cache_hit=cache_hit,
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


def _persist_drafts(
    session: Session,
    *,
    content: AIStructuredExtractionContent,
    data: StructuredExtractionInput,
    source_text: str,
    extraction_method: str,
    model_version: str,
) -> list[ExtractedObject]:
    topic_slug = _blank_to_none(content.topic_slug) or _blank_to_none(data.topic_slug_hint)
    subtopic_slug = _blank_to_none(content.subtopic_slug) or _blank_to_none(data.subtopic_slug_hint)
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

    for card in content.flashcards:
        payload = _flashcard_payload(
            card,
            topic_slug=topic_slug,
            subtopic_slug=subtopic_slug,
            source_summary=source_summary,
            source_title=source_title,
            source_url=data.source_url,
            source_text=source_text,
        )
        items.append(
            StoreExtractedObjectInput(
                object_type=ExtractedObjectType.FLASHCARD,
                payload_json=payload,
                confidence_score=_confidence(card.confidence_score),
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


def _flashcard_payload(
    card: AIProposedFlashcardDraft,
    *,
    topic_slug: str | None,
    subtopic_slug: str | None,
    source_summary: str | None,
    source_title: str | None,
    source_url: str | None,
    source_text: str,
) -> dict[str, Any]:
    front = card.front.strip()
    back = card.back.strip()
    payload: dict[str, Any] = {
        "front": front,
        "back": back,
        "title": front,
        "extracted_text": back,
        "source_excerpt": _excerpt(source_text),
    }
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
        "You extract quant interview practice material from long educational source text. "
        "Return JSON only matching the schema. "
        "Propose interview questions (title, body, optional short_answer/canonical_solution) "
        "and flashcards (front/back) when the source supports them. "
        "Do not invent proprietary firm secrets. "
        "Suggest a topic_slug and optional subtopic_slug as lowercase kebab-case labels "
        "(examples: probability, conditional-probability, black-scholes). "
        "Also include a short source summary and optional source_title. "
        "Do not create concept, formula, or example records—only questions and flashcards. "
        "Prefer fewer high-quality drafts over many weak ones. "
        "If the source is thin, return empty lists only when nothing is salvageable."
    )


def _prompt_payload(
    *,
    source_text: str,
    source_url: str | None,
    source_title: str | None,
    topic_slug_hint: str | None,
    subtopic_slug_hint: str | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "source_text": source_text,
        "instructions": (
            "Parse the source_text into structured interview questions and flashcards "
            "for a quant interview prep product. Include answer/solution fields when present."
        ),
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


def _input_object_version(*, data: StructuredExtractionInput, source_text: str) -> str:
    if data.resource_id is not None:
        return f"resource:{data.resource_id}:chars:{len(source_text)}"
    return f"source_text:chars:{len(source_text)}"


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None
