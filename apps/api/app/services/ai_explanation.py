import json

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.prompt_hash import compute_prompt_hash
from app.ai.provider import AIProvider
from app.ai.structured import StructuredOutputError, chat_structured
from app.ai.tasks import AITask
from app.ai.types import AIMessage, AIMessageRole
from app.models.enums import AICacheResultKind
from app.models.question import Question
from app.schemas.ai_explanation import (
    AIExplanationContent,
    AIExplanationResponse,
    AIHintsContent,
    AIHintsResponse,
)
from app.services.ai_cache import (
    AICacheLookupKey,
    get_cached_ai_result,
    store_cached_ai_result,
)
from app.services.ai_usage import AIUsageRecordInput, record_ai_usage

EXPLANATION_PROMPT_TEMPLATE_VERSION = "question-explanation:v5"
HINTS_PROMPT_TEMPLATE_VERSION = "question-hints:v1"
EXPLANATION_TASK = AITask.REASONING
HINTS_TASK = AITask.REASONING


class AIExplanationResponseError(ValueError):
    """Raised when a provider returns an invalid explanation or hints payload."""


def generate_question_hints(
    session: Session,
    provider: AIProvider,
    *,
    question: Question,
    user_answer: str,
) -> AIHintsResponse:
    model = provider.model_for_task(HINTS_TASK)
    prompt_payload = _prompt_payload(question=question, user_answer=user_answer)
    prompt_hash = compute_prompt_hash(
        prompt_template_version=HINTS_PROMPT_TEMPLATE_VERSION,
        prompt_payload=prompt_payload,
    )
    input_object_version = f"question:{question.id}:{question.updated_at.isoformat()}"
    cache_key = AICacheLookupKey(
        provider=provider.provider_name,
        model=model,
        result_kind=AICacheResultKind.HINT,
        prompt_template_version=HINTS_PROMPT_TEMPLATE_VERSION,
        prompt_hash=prompt_hash,
        input_object_version=input_object_version,
    )

    cached = get_cached_ai_result(session, cache_key)
    if cached is not None:
        content = _validate_hints(cached.response_json)
        record_ai_usage(
            session,
            AIUsageRecordInput(
                provider=provider.provider_name,
                model=model,
                input_tokens=None,
                output_tokens=None,
                latency_ms=0,
                cache_hit=True,
                prompt_hash=prompt_hash,
                input_object_version=input_object_version,
            ),
        )
        return AIHintsResponse(
            question_id=question.id,
            cache_hit=True,
            **content.model_dump(),
        )

    try:
        content, _result = chat_structured(
            provider,
            [
                AIMessage(role=AIMessageRole.SYSTEM, content=_hints_system_prompt()),
                AIMessage(
                    role=AIMessageRole.USER,
                    content=json.dumps(prompt_payload, sort_keys=True),
                ),
            ],
            response_model=AIHintsContent,
            model=model,
            temperature=0.2,
            cache_hit=False,
            prompt_hash=prompt_hash,
            input_object_version=input_object_version,
        )
    except StructuredOutputError as exc:
        raise AIExplanationResponseError(str(exc)) from exc

    store_cached_ai_result(session, cache_key, content.model_dump())
    return AIHintsResponse(
        question_id=question.id,
        cache_hit=False,
        **content.model_dump(),
    )


def generate_question_explanation(
    session: Session,
    provider: AIProvider,
    *,
    question: Question,
    user_answer: str,
) -> AIExplanationResponse:
    model = provider.model_for_task(EXPLANATION_TASK)
    prompt_payload = _prompt_payload(question=question, user_answer=user_answer)
    prompt_hash = compute_prompt_hash(
        prompt_template_version=EXPLANATION_PROMPT_TEMPLATE_VERSION,
        prompt_payload=prompt_payload,
    )
    input_object_version = f"question:{question.id}:{question.updated_at.isoformat()}"
    cache_key = AICacheLookupKey(
        provider=provider.provider_name,
        model=model,
        result_kind=AICacheResultKind.EXPLANATION,
        prompt_template_version=EXPLANATION_PROMPT_TEMPLATE_VERSION,
        prompt_hash=prompt_hash,
        input_object_version=input_object_version,
    )

    cached = get_cached_ai_result(session, cache_key)
    if cached is not None:
        content = _validate_explanation(cached.response_json)
        record_ai_usage(
            session,
            AIUsageRecordInput(
                provider=provider.provider_name,
                model=model,
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

    try:
        content, _result = chat_structured(
            provider,
            [
                AIMessage(role=AIMessageRole.SYSTEM, content=_explanation_system_prompt()),
                AIMessage(
                    role=AIMessageRole.USER,
                    content=json.dumps(prompt_payload, sort_keys=True),
                ),
            ],
            response_model=AIExplanationContent,
            model=model,
            temperature=0.2,
            cache_hit=False,
            prompt_hash=prompt_hash,
            input_object_version=input_object_version,
        )
    except StructuredOutputError as exc:
        raise AIExplanationResponseError(str(exc)) from exc

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
        },
        "user_answer": user_answer,
    }


def _hints_system_prompt() -> str:
    return (
        "Quant interview tutor. Return JSON matching the schema. "
        "Give 1-2 short hints only (no full solution, no final answer). "
        "Each hint is one sentence."
    )


def _explanation_system_prompt() -> str:
    return (
        "Quant interview tutor. Return JSON matching the schema. "
        "Write a concise explanation (max ~120 words): "
        "(1) correct solution steps and final answer from the canonical solution; "
        "(2) one short note on the user's answer. No lists of common mistakes."
    )


def _validate_hints(payload: object) -> AIHintsContent:
    try:
        return AIHintsContent.model_validate(payload)
    except ValidationError as exc:
        raise AIExplanationResponseError(
            "AI provider returned an invalid hints payload.",
        ) from exc


def _validate_explanation(payload: object) -> AIExplanationContent:
    try:
        return AIExplanationContent.model_validate(payload)
    except ValidationError as exc:
        raise AIExplanationResponseError(
            "AI provider returned an invalid explanation payload.",
        ) from exc
