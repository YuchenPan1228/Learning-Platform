import json

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.prompt_hash import compute_prompt_hash
from app.ai.provider import AIProvider
from app.ai.types import AIMessage, AIMessageRole
from app.models.enums import AICacheResultKind
from app.models.question import Question
from app.schemas.ai_explanation import AIExplanationContent, AIExplanationResponse
from app.services.ai_cache import (
    AICacheLookupKey,
    get_cached_ai_result,
    store_cached_ai_result,
)
from app.services.ai_usage import AIUsageRecordInput, record_ai_usage

EXPLANATION_PROMPT_TEMPLATE_VERSION = "question-explanation:v1"


class AIExplanationResponseError(ValueError):
    """Raised when a provider returns an invalid explanation payload."""


def generate_question_explanation(
    session: Session,
    provider: AIProvider,
    *,
    question: Question,
    user_answer: str,
) -> AIExplanationResponse:
    prompt_payload = _prompt_payload(question=question, user_answer=user_answer)
    prompt_hash = compute_prompt_hash(
        prompt_template_version=EXPLANATION_PROMPT_TEMPLATE_VERSION,
        prompt_payload=prompt_payload,
    )
    input_object_version = f"question:{question.id}:{question.updated_at.isoformat()}"
    cache_key = AICacheLookupKey(
        provider=provider.provider_name,
        model=provider.chat_model,
        result_kind=AICacheResultKind.EXPLANATION,
        prompt_template_version=EXPLANATION_PROMPT_TEMPLATE_VERSION,
        prompt_hash=prompt_hash,
        input_object_version=input_object_version,
    )

    cached = get_cached_ai_result(session, cache_key)
    if cached is not None:
        content = _validate_content(cached.response_json)
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
        return AIExplanationResponse(
            question_id=question.id,
            cache_hit=True,
            **content.model_dump(),
        )

    result = provider.chat(
        [
            AIMessage(
                role=AIMessageRole.SYSTEM,
                content=_system_prompt(),
            ),
            AIMessage(
                role=AIMessageRole.USER,
                content=json.dumps(prompt_payload, sort_keys=True),
            ),
        ],
        temperature=0.2,
        cache_hit=False,
        prompt_hash=prompt_hash,
        input_object_version=input_object_version,
    )
    content = _parse_provider_content(result.content)
    store_cached_ai_result(session, cache_key, content.model_dump())
    return AIExplanationResponse(
        question_id=question.id,
        cache_hit=False,
        **content.model_dump(),
    )


def _prompt_payload(*, question: Question, user_answer: str) -> dict[str, object]:
    return {
        "question": {
            "title": question.title,
            "body": question.body,
            "canonical_solution": question.canonical_solution,
            "expected_solution_pattern": question.expected_solution_pattern,
            "known_common_mistakes": question.common_mistakes or [],
        },
        "user_answer": user_answer,
    }


def _system_prompt() -> str:
    return (
        "You are a quant interview tutor. Explain the supplied question in relation "
        "to the user's answer. Return only a JSON object with exactly these keys: "
        '"explanation" (string), "hints" (non-empty array of strings), and '
        '"common_mistakes" (array of strings). Do not include markdown fences. '
        "Use the canonical solution as reference, but explain the reasoning clearly."
    )


def _parse_provider_content(content: str) -> AIExplanationContent:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise AIExplanationResponseError(
            "AI provider returned invalid explanation JSON.",
        ) from exc
    return _validate_content(payload)


def _validate_content(payload: object) -> AIExplanationContent:
    try:
        return AIExplanationContent.model_validate(payload)
    except ValidationError as exc:
        raise AIExplanationResponseError(
            "AI provider returned an invalid explanation payload.",
        ) from exc
