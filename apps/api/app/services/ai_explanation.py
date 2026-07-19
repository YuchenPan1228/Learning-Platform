import json

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.structured import StructuredOutputError, chat_structured
from app.ai.prompt_hash import compute_prompt_hash
from app.ai.provider import AIProvider
from app.ai.tasks import AITask
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

EXPLANATION_PROMPT_TEMPLATE_VERSION = "question-explanation:v4"
EXPLANATION_TASK = AITask.REASONING


class AIExplanationResponseError(ValueError):
    """Raised when a provider returns an invalid explanation payload."""


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
        content = _validate_content(cached.response_json)
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
                AIMessage(
                    role=AIMessageRole.SYSTEM,
                    content=_system_prompt(),
                ),
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
            "expected_solution_pattern": question.expected_solution_pattern,
            "known_common_mistakes": question.common_mistakes or [],
        },
        "user_answer": user_answer,
    }


def _system_prompt() -> str:
    return (
        "You are a quant interview tutor. Respond with a JSON object matching the "
        "provided schema. In explanation, do both of the following in order: "
        "(1) teach the correct answer step by step using the canonical solution as "
        "ground truth, including the final answer; "
        "(2) briefly relate that solution to the user's answer, noting what was right "
        "or wrong. Do not only critique the user's attempt. "
        "Keep explanation concise (a few short paragraphs). "
        "hints must be a non-empty array. common_mistakes may be empty."
    )


def _validate_content(payload: object) -> AIExplanationContent:
    try:
        return AIExplanationContent.model_validate(payload)
    except ValidationError as exc:
        raise AIExplanationResponseError(
            "AI provider returned an invalid explanation payload.",
        ) from exc
