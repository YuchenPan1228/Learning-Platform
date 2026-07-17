from unittest.mock import MagicMock

import pytest
from app.models.ai_cache_entry import AICacheEntry
from app.models.enums import AICacheResultKind
from app.services.ai_cache import (
    AICacheLookupKey,
    get_cached_ai_result,
    store_cached_ai_result,
)


def _lookup_key(**overrides: object) -> AICacheLookupKey:
    values: dict[str, object] = {
        "provider": "ollama",
        "model": "qwen2.5:3b",
        "result_kind": AICacheResultKind.EXPLANATION,
        "prompt_template_version": "explanation:v1",
        "prompt_hash": "abc123",
        "input_object_version": "question:42:v1",
    }
    values.update(overrides)
    return AICacheLookupKey(
        provider=str(values["provider"]),
        model=str(values["model"]),
        result_kind=AICacheResultKind(str(values["result_kind"])),
        prompt_template_version=str(values["prompt_template_version"]),
        prompt_hash=str(values["prompt_hash"]),
        input_object_version=str(values["input_object_version"]),
    )


def test_get_cached_ai_result_returns_none_when_missing() -> None:
    session = MagicMock()
    session.scalar.return_value = None

    result = get_cached_ai_result(session, _lookup_key())

    assert result is None
    session.scalar.assert_called_once()


def test_store_cached_ai_result_inserts_new_entry() -> None:
    session = MagicMock()
    session.scalar.return_value = None
    session.refresh.side_effect = lambda row: row

    entry = store_cached_ai_result(
        session,
        _lookup_key(result_kind=AICacheResultKind.SUMMARY),
        {"content": "Conditional probability refresher."},
    )

    session.add.assert_called_once()
    session.commit.assert_called_once()
    saved = session.add.call_args.args[0]
    assert isinstance(saved, AICacheEntry)
    assert saved.result_kind == AICacheResultKind.SUMMARY
    assert saved.response_json == {"content": "Conditional probability refresher."}
    assert entry is saved


def test_store_cached_ai_result_updates_existing_entry() -> None:
    session = MagicMock()
    existing = AICacheEntry(
        provider="ollama",
        model="qwen2.5:3b",
        result_kind=AICacheResultKind.GENERATED_QUESTION,
        prompt_template_version="generate:v1",
        prompt_hash="deadbeef",
        input_object_version="question:7:v2",
        response_json={"content": "old"},
    )
    session.scalar.return_value = existing
    session.refresh.side_effect = lambda row: row

    entry = store_cached_ai_result(
        session,
        _lookup_key(
            result_kind=AICacheResultKind.GENERATED_QUESTION,
            prompt_template_version="generate:v1",
            prompt_hash="deadbeef",
            input_object_version="question:7:v2",
        ),
        {"content": "new variant"},
    )

    session.add.assert_not_called()
    session.commit.assert_called_once()
    assert entry is existing
    assert existing.response_json == {"content": "new variant"}


@pytest.mark.integration
def test_ai_cache_round_trip(
    migrated_database: None,
    require_postgres: None,
) -> None:
    from app.db import get_session_factory

    session = get_session_factory()()
    try:
        key = _lookup_key(
            result_kind=AICacheResultKind.HINT,
            prompt_hash="f" * 64,
            input_object_version="attempt:9:v1",
        )
        assert get_cached_ai_result(session, key) is None

        stored = store_cached_ai_result(
            session,
            key,
            {"content": "Start from the definition of conditional probability."},
        )
        loaded = get_cached_ai_result(session, key)

        assert loaded is not None
        assert loaded.id == stored.id
        assert loaded.result_kind == AICacheResultKind.HINT
        assert loaded.response_json["content"].startswith("Start from the definition")
    finally:
        session.close()
