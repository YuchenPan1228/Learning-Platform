import json
from unittest.mock import MagicMock

import pytest
from app.ai.types import AIChatResult, AITokenUsage
from app.models.enums import (
    ContentStatus,
    Difficulty,
    ExtractedObjectType,
    ExtractionMethod,
    ResourceSourceType,
)
from app.models.extracted_object import ExtractedObject
from app.models.resource import Resource
from app.services.ai_structured_extraction import (
    AIStructuredExtractionError,
    StructuredExtractionInput,
    _source_chunks,
    _split_stem_and_solution,
    extract_structured_drafts,
    extract_structured_drafts_from_resource,
)


def _provider(*, content: str | dict[str, object]) -> MagicMock:
    if isinstance(content, dict):
        body = json.dumps(content)
    else:
        body = content
    provider = MagicMock()
    provider.provider_name = "ollama"
    provider.chat_model = "qwen2.5:3b"
    provider.model_for_task.return_value = "qwen2.5:3b"
    provider.chat.return_value = AIChatResult(
        content=body,
        provider="ollama",
        model="qwen2.5:3b",
        token_usage=AITokenUsage(input_tokens=100, output_tokens=80),
        latency_ms=200,
    )
    return provider


def _valid_payload() -> dict[str, object]:
    return {
        "summary": "Notes on conditional probability and Bayes theorem.",
        "topic_slug": "probability",
        "subtopic_slug": "conditional-probability",
        "source_title": "Bayes notes",
        "questions": [
            {
                "title": "Two Heads Given One Head",
                "body": (
                    "Two fair coins are flipped. Given at least one is heads, find P both heads."
                ),
                "short_answer": "1/3",
                "canonical_solution": "Condition on HH, HT, TH. Only HH works, so 1/3.",
                "difficulty": "medium",
                "confidence_score": 0.91,
            }
        ],
    }


def test_extract_structured_drafts_creates_question() -> None:
    session = MagicMock()
    session.scalar.return_value = None
    resource = Resource(
        source_type=ResourceSourceType.URL,
        url="https://example.com/bayes",
        title="Bayes notes",
        license="CC-BY-4.0",
        status=ContentStatus.DRAFT,
    )
    resource.id = 7
    session.get.return_value = resource
    session.refresh.side_effect = lambda row: setattr(row, "id", getattr(row, "id", None) or 1)
    created_ids = {"n": 0}

    def add(row: object) -> None:
        if isinstance(row, ExtractedObject):
            created_ids["n"] += 1
            row.id = created_ids["n"]

    session.add.side_effect = add
    provider = _provider(content=_valid_payload())

    result = extract_structured_drafts(
        session,
        provider,
        StructuredExtractionInput(
            source_text=(
                "Bayes theorem updates priors with likelihood. "
                "P(A|B)=P(B|A)P(A)/P(B). Example interview questions follow."
            ),
            source_url="https://example.com/bayes",
            source_title="Bayes notes",
            source_method=ExtractionMethod.URL_TRAFILATURA,
            resource_id=7,
            topic_job_id=3,
            topic_slug_hint="probability",
        ),
    )

    assert result.cache_hit is False
    assert result.topic_slug == "probability"
    assert result.subtopic_slug == "conditional-probability"
    assert result.extraction_method == "ai:structured:url_trafilatura"
    assert result.model_version == "qwen2.5:3b"
    assert len(result.drafts) == 1
    assert result.drafts[0].object_type is ExtractedObjectType.QUESTION

    extracted_rows = [
        call.args[0]
        for call in session.add.call_args_list
        if isinstance(call.args[0], ExtractedObject)
    ]
    assert len(extracted_rows) == 1
    question = extracted_rows[0]

    assert question.status is ContentStatus.DRAFT
    assert question.resource_id == 7
    assert question.topic_job_id == 3
    assert question.extraction_method == "ai:structured:url_trafilatura"
    assert question.model_version == "qwen2.5:3b"
    assert question.confidence_score == 0.91
    assert question.payload_json["title"] == "Two Heads Given One Head"
    assert question.payload_json["topic_slug"] == "probability"
    assert question.payload_json["short_answer"] == "1/3"
    assert question.payload_json["source_summary"]
    assert "canonical_solution" in question.payload_json
    assert question.payload_json["difficulty"] == Difficulty.MEDIUM.value
    session.commit.assert_called()
    provider.chat.assert_called_once()
    assert provider.chat.call_args.kwargs["response_schema"] is not None
    user_msg = provider.chat.call_args.args[0][1].content
    assert "source_text" in user_msg
    assert "Bayes theorem" in user_msg


def test_rejects_blank_source() -> None:
    with pytest.raises(AIStructuredExtractionError, match="blank"):
        extract_structured_drafts(
            MagicMock(),
            _provider(content=_valid_payload()),
            StructuredExtractionInput(source_text="   "),
        )


def test_rejects_empty_draft_lists() -> None:
    session = MagicMock()
    session.scalar.return_value = None
    session.refresh.side_effect = lambda row: row
    provider = _provider(
        content={
            "summary": "Nothing useful",
            "topic_slug": None,
            "subtopic_slug": None,
            "source_title": None,
            "questions": [],
        }
    )
    with pytest.raises(AIStructuredExtractionError, match="no question"):
        extract_structured_drafts(
            session,
            provider,
            StructuredExtractionInput(source_text="thin source with no interview material"),
        )


def test_uses_cache_when_available() -> None:
    session = MagicMock()
    cached = MagicMock()
    cached.response_json = _valid_payload()
    session.scalar.return_value = cached
    session.refresh.side_effect = lambda row: setattr(row, "id", 99)

    def add(row: object) -> None:
        if isinstance(row, ExtractedObject):
            row.id = 99

    session.add.side_effect = add
    provider = _provider(content={"questions": []})

    result = extract_structured_drafts(
        session,
        provider,
        StructuredExtractionInput(source_text="cached bayes source text " * 20),
    )
    assert result.cache_hit is True
    provider.chat.assert_not_called()
    assert len(result.drafts) == 1


def test_source_chunks_splits_numbered_problems() -> None:
    text = (
        "Intro about interview prep.\n\n"
        "Problem 1. Expected tosses for three heads? Solution. Answer is 14.\n\n"
        "Problem 2. Pirates and gold. Solution. Senior pirate keeps 98.\n\n"
        "Problem 3. Stick broken into three pieces forms a triangle with probability 1/4."
    )
    chunks = _source_chunks(text)
    assert len(chunks) >= 1
    joined = "\n".join(chunks)
    assert "Problem 1." in joined
    assert "Problem 3." in joined
    # Prefers problem boundaries over a single truncated blob.
    assert not joined.endswith("...[truncated]")


def test_split_stem_and_solution_separates_marker() -> None:
    stem, solution = _split_stem_and_solution("What is E[X]? Solution. By linearity, E[X]=np.")
    assert stem == "What is E[X]?"
    assert solution == "By linearity, E[X]=np."


def test_extract_multipart_source_makes_multiple_provider_calls() -> None:
    """Long multi-problem pages are chunked so the model sees complete stems."""
    session = MagicMock()
    session.scalar.return_value = None
    session.refresh.side_effect = lambda row: setattr(row, "id", getattr(row, "id", None) or 1)
    created = {"n": 0}

    def add(row: object) -> None:
        if isinstance(row, ExtractedObject):
            created["n"] += 1
            row.id = created["n"]

    session.add.side_effect = add

    def chat(messages, **kwargs):  # noqa: ANN001, ARG001
        payload = json.loads(messages[1].content)
        source = payload["source_text"]
        title = "Heads" if "Problem 1" in source else "Pirates"
        body = (
            "Expected tosses for three consecutive heads?"
            if "Problem 1" in source
            else "How will five pirates divide 100 gold coins?"
        )
        return AIChatResult(
            content=json.dumps(
                {
                    "summary": "probability problems",
                    "topic_slug": "probability",
                    "questions": [
                        {
                            "title": title,
                            "body": body,
                            "canonical_solution": "see source",
                            "confidence_score": 0.8,
                        }
                    ],
                }
            ),
            provider="ollama",
            model="qwen2.5:3b",
            token_usage=AITokenUsage(input_tokens=50, output_tokens=40),
            latency_ms=10,
        )

    provider = MagicMock()
    provider.provider_name = "ollama"
    provider.chat_model = "qwen2.5:3b"
    provider.model_for_task.return_value = "qwen2.5:3b"
    provider.chat.side_effect = chat

    # Force multiple chunks with inflated per-problem size via many problems.
    problems = "\n\n".join(
        f"Problem {i}. This is a long quant interview problem stem number {i} "
        + ("about probability and expected values. " * 40)
        + f"Solution. Work through problem {i} carefully with equations."
        for i in range(1, 8)
    )
    result = extract_structured_drafts(
        session,
        provider,
        StructuredExtractionInput(source_text=problems, topic_slug_hint="probability"),
    )
    assert provider.chat.call_count >= 2
    assert len(result.drafts) >= 2


def test_extract_from_resource_uses_summary_for_manual_notes() -> None:
    session = MagicMock()
    session.scalar.return_value = None
    session.refresh.side_effect = lambda row: row

    def add(row: object) -> None:
        if isinstance(row, ExtractedObject):
            row.id = 5

    session.add.side_effect = add
    provider = _provider(content=_valid_payload())
    resource = Resource(
        source_type=ResourceSourceType.MANUAL,
        title="My notes",
        summary=(
            "Martingales and optional stopping. Define a martingale and give an interview "
            "example involving fair games."
        ),
        status=ContentStatus.DRAFT,
    )
    resource.id = 11
    session.get.return_value = resource

    result = extract_structured_drafts_from_resource(
        session,
        provider,
        resource,
        topic_slug_hint="probability",
    )
    assert result.drafts
    assert result.extraction_method == "ai:structured:pasted_text"
    provider.chat.assert_called_once()
