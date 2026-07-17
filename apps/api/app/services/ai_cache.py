from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai_cache_entry import AICacheEntry
from app.models.enums import AICacheResultKind


@dataclass(frozen=True, slots=True)
class AICacheLookupKey:
    provider: str
    model: str
    result_kind: AICacheResultKind
    prompt_template_version: str
    prompt_hash: str
    input_object_version: str


def get_cached_ai_result(session: Session, key: AICacheLookupKey) -> AICacheEntry | None:
    return session.scalar(
        select(AICacheEntry).where(
            AICacheEntry.provider == key.provider,
            AICacheEntry.model == key.model,
            AICacheEntry.result_kind == key.result_kind,
            AICacheEntry.prompt_template_version == key.prompt_template_version,
            AICacheEntry.prompt_hash == key.prompt_hash,
            AICacheEntry.input_object_version == key.input_object_version,
        ),
    )


def store_cached_ai_result(
    session: Session,
    key: AICacheLookupKey,
    response_json: dict[str, Any],
) -> AICacheEntry:
    existing = get_cached_ai_result(session, key)
    if existing is not None:
        existing.response_json = response_json
        session.commit()
        session.refresh(existing)
        return existing

    entry = AICacheEntry(
        provider=key.provider,
        model=key.model,
        result_kind=key.result_kind,
        prompt_template_version=key.prompt_template_version,
        prompt_hash=key.prompt_hash,
        input_object_version=key.input_object_version,
        response_json=response_json,
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry
