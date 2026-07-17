import json

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.prompt_hash import compute_prompt_hash
from app.ai.provider import AIProvider
from app.ai.types import AIMessage, AIMessageRole
from app.dedup.detection import find_duplicate_matches
from app.dedup.fingerprints import apply_question_fingerprints
from app.models.enums import (
    AICacheResultKind,
    ContentStatus,
    DuplicateMatchType,
)
from app.models.question import Question
from app.schemas.ai_similar_question import GeneratedQuestionContent, SimilarQuestionResponse
from app.services.ai_cache import (
    AICacheLookupKey,
    get_cached_ai_result,
    store_cached_ai_result,
)
from app.services.ai_usage import AIUsageRecordInput, record_ai_usage

SIMILAR_QUESTION_PROMPT_TEMPLATE_VERSION = "similar-question:v1"
_EXTRACTION_METHOD = "ai_similar_generation"


class AISimilarQuestionResponseError(ValueError):
    """Raised when a provider returns an invalid similar-question payload."""


class SimilarQuestionDuplicateError(ValueError):
    """Raised when a generated variant is an exact duplicate of an existing question."""


def generate_similar_question(
    session: Session,
    provider: AIProvider,
    *,
    question: Question,
) -> SimilarQuestionResponse:
    prompt_payload = _prompt_payload(question)
    prompt_hash = compute_prompt_hash(
        prompt_template_version=SIMILAR_QUESTION_PROMPT_TEMPLATE_VERSION,
        prompt_payload=prompt_payload,
    )
    input_object_version = f"question:{question.id}:{question.updated_at.isoformat()}"
    cache_key = AICacheLookupKey(
        provider=provider.provider_name,
        model=provider.chat_model,
        result_kind=AICacheResultKind.GENERATED_QUESTION,
        prompt_template_version=SIMILAR_QUESTION_PROMPT_TEMPLATE_VERSION,
        prompt_hash=prompt_hash,
        input_object_version=input_object_version,
    )

    cached = get_cached_ai_result(session, cache_key)
    if cached is not None:
        draft = _draft_from_cache(session, cached.response_json)
        if draft is not None:
            record_ai_usage(
                session,
                AIUsageRecordInput(
                    provider=provider.provider_name,
                    model=provider.chat_model,
                    input_tokens=None,
                    output_tokens=None,
                    latency_ms=0,
                    cache_hit=True,
                    prompt_hash=prompt_hash,
                    input_object_version=input_object_version,
                ),
            )
            return _to_response(source=question, draft=draft, cache_hit=True)

    result = provider.chat(
        [
            AIMessage(role=AIMessageRole.SYSTEM, content=_system_prompt()),
            AIMessage(
                role=AIMessageRole.USER,
                content=json.dumps(prompt_payload, sort_keys=True),
            ),
        ],
        temperature=0.4,
        cache_hit=False,
        prompt_hash=prompt_hash,
        input_object_version=input_object_version,
    )
    content = _parse_provider_content(result.content)
    _ensure_original_variant(session, content=content)

    draft = _create_draft_question(
        session,
        source=question,
        content=content,
        model_version=provider.chat_model,
    )
    store_cached_ai_result(
        session,
        cache_key,
        {
            "draft_question_id": draft.id,
            **content.model_dump(mode="json"),
        },
    )
    return _to_response(source=question, draft=draft, cache_hit=False)


def _prompt_payload(question: Question) -> dict[str, object]:
    return {
        "question": {
            "title": question.title,
            "body": question.body,
            "short_answer": question.short_answer,
            "canonical_solution": question.canonical_solution,
            "difficulty": question.difficulty.value,
            "expected_solution_pattern": question.expected_solution_pattern,
            "common_mistakes": question.common_mistakes or [],
        },
    }


def _system_prompt() -> str:
    return (
        "You are a quant interview question author. Create one original practice "
        "variant of the supplied question. Change numbers, framing, or surface "
        "details while testing the same core concept. Do not copy proprietary "
        "wording. Return only a JSON object with exactly these keys: "
        '"title" (string), "body" (string), "short_answer" (string or null), '
        '"canonical_solution" (string or null), "difficulty" (one of easy, medium, '
        'hard, expert), "common_mistakes" (array of strings), '
        '"expected_solution_pattern" (string or null), and '
        '"estimated_time_seconds" (positive integer or null). '
        "Do not include markdown fences."
    )


def _parse_provider_content(content: str) -> GeneratedQuestionContent:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise AISimilarQuestionResponseError(
            "AI provider returned invalid similar-question JSON.",
        ) from exc
    return _validate_content(payload)


def _validate_content(payload: object) -> GeneratedQuestionContent:
    try:
        return GeneratedQuestionContent.model_validate(payload)
    except ValidationError as exc:
        raise AISimilarQuestionResponseError(
            "AI provider returned an invalid similar-question payload.",
        ) from exc


def _ensure_original_variant(
    session: Session,
    *,
    content: GeneratedQuestionContent,
) -> None:
    matches = find_duplicate_matches(
        session,
        title=content.title,
        body=content.body,
    )
    exact_matches = [
        match
        for match in matches
        if match.match_type in {DuplicateMatchType.EXACT_RAW, DuplicateMatchType.EXACT_NORMALIZED}
    ]
    if exact_matches:
        raise SimilarQuestionDuplicateError(
            "Generated variant matches an existing question exactly; "
            "refusing to store a non-original draft.",
        )


def _create_draft_question(
    session: Session,
    *,
    source: Question,
    content: GeneratedQuestionContent,
    model_version: str,
) -> Question:
    draft = Question(
        title=content.title,
        body=content.body,
        short_answer=content.short_answer,
        canonical_solution=content.canonical_solution,
        difficulty=content.difficulty,
        common_mistakes=content.common_mistakes or None,
        expected_solution_pattern=content.expected_solution_pattern,
        estimated_time_seconds=content.estimated_time_seconds,
        topic_id=source.topic_id,
        subtopic_id=source.subtopic_id,
        prerequisites=source.prerequisites,
        status=ContentStatus.DRAFT,
        generated_from_id=source.id,
        extraction_method=_EXTRACTION_METHOD,
        model_version=model_version,
        source_attribution="AI-generated practice variant pending human review.",
    )
    apply_question_fingerprints(draft)
    session.add(draft)
    session.commit()
    session.refresh(draft)
    return draft


def _draft_from_cache(session: Session, response_json: object) -> Question | None:
    if not isinstance(response_json, dict):
        return None
    draft_question_id = response_json.get("draft_question_id")
    if not isinstance(draft_question_id, int):
        return None
    draft = session.get(Question, draft_question_id)
    if draft is None or draft.status != ContentStatus.DRAFT:
        return None
    return draft


def _to_response(
    *,
    source: Question,
    draft: Question,
    cache_hit: bool,
) -> SimilarQuestionResponse:
    return SimilarQuestionResponse(
        source_question_id=source.id,
        draft_question_id=draft.id,
        generated_from_id=draft.generated_from_id or source.id,
        cache_hit=cache_hit,
        title=draft.title,
        body=draft.body,
        short_answer=draft.short_answer,
        canonical_solution=draft.canonical_solution,
        difficulty=draft.difficulty,
        common_mistakes=draft.common_mistakes,
        expected_solution_pattern=draft.expected_solution_pattern,
        estimated_time_seconds=draft.estimated_time_seconds,
        status=draft.status,
        topic_id=draft.topic_id,
        subtopic_id=draft.subtopic_id,
    )
