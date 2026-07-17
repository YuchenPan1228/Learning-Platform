from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.ai.cost import estimate_chat_cost
from app.ai.types import AIChatResult, AITokenUsage
from app.models.ai_usage_log import AIUsageLog


@dataclass(frozen=True, slots=True)
class AIUsageRecordInput:
    provider: str
    model: str
    input_tokens: int | None
    output_tokens: int | None
    latency_ms: int
    cache_hit: bool
    prompt_hash: str | None = None
    input_object_version: str | None = None


def record_ai_usage(session: Session, usage: AIUsageRecordInput) -> AIUsageLog:
    log = AIUsageLog(
        provider=usage.provider,
        model=usage.model,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        latency_ms=usage.latency_ms,
        estimated_cost_usd=estimate_chat_cost(
            provider=usage.provider,
            model=usage.model,
            token_usage=AITokenUsage(
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
            ),
        ),
        cache_hit=usage.cache_hit,
        prompt_hash=usage.prompt_hash,
        input_object_version=usage.input_object_version,
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    return log


def record_ai_usage_from_chat_result(
    session: Session,
    result: AIChatResult,
    *,
    cache_hit: bool,
    prompt_hash: str | None = None,
    input_object_version: str | None = None,
) -> AIUsageLog:
    return record_ai_usage(
        session,
        AIUsageRecordInput(
            provider=result.provider,
            model=result.model,
            input_tokens=result.token_usage.input_tokens,
            output_tokens=result.token_usage.output_tokens,
            latency_ms=result.latency_ms,
            cache_hit=cache_hit,
            prompt_hash=prompt_hash,
            input_object_version=input_object_version,
        ),
    )
