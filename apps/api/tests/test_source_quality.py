from unittest.mock import MagicMock

import pytest
from app.models.enums import ContentStatus, ResourceSourceType
from app.models.resource import Resource
from app.services.source_quality import (
    CODE_EXAMPLE_WEIGHT,
    CONTENT_LENGTH_WEIGHT,
    DOMAIN_REPUTATION_WEIGHT,
    EDUCATIONAL_STRUCTURE_WEIGHT,
    FORMULA_DENSITY_WEIGHT,
    HUMAN_REVIEW_WEIGHT,
    SourceQualityError,
    SourceQualityInput,
    combine_quality_scores,
    score_and_update_resource,
    score_code_examples,
    score_content_length,
    score_domain_reputation,
    score_educational_structure,
    score_formula_density,
    score_source_quality,
)

_SAMPLE_EDU_TEXT = """
# Conditional Probability

## Definition
The probability of A given B is P(A|B) = P(A and B) / P(B).

## Example
Bayes theorem updates beliefs with evidence.

- prerequisite: sample spaces
- exercise: compute P(A|B)

$$P(A \\mid B) = \\frac{P(A \\cap B)}{P(B)}$$

```python
def bayes(prior, likelihood, evidence):
    return prior * likelihood / evidence
```
"""


def test_component_weights_sum_to_one() -> None:
    total = (
        DOMAIN_REPUTATION_WEIGHT
        + CONTENT_LENGTH_WEIGHT
        + FORMULA_DENSITY_WEIGHT
        + CODE_EXAMPLE_WEIGHT
        + EDUCATIONAL_STRUCTURE_WEIGHT
        + HUMAN_REVIEW_WEIGHT
    )
    assert abs(total - 1.0) < 1e-9


def test_score_domain_reputation_known_and_edu() -> None:
    assert score_domain_reputation("https://ocw.mit.edu/courses/prob") == 0.95
    assert score_domain_reputation("https://web.mit.edu/notes") == 0.95
    assert score_domain_reputation("https://cs.princeton.edu/lecs") == 0.85
    assert score_domain_reputation("https://random-blog.example.com/post") == 0.5
    assert score_domain_reputation(None) == 0.55


def test_score_content_length_bands() -> None:
    assert score_content_length("") == 0.0
    assert score_content_length("x" * 100) == pytest.approx(0.2, abs=0.01)
    assert score_content_length("x" * 1000) == 1.0
    assert score_content_length("x" * 50_000) == 0.85


def test_score_formula_and_code_and_structure() -> None:
    assert score_formula_density("plain prose without math words") == 0.0
    assert score_formula_density("Use $P(A|B)$ and $$x=1$$ and Bayes theorem") >= 0.55
    assert score_code_examples("no code here") == 0.0
    assert score_code_examples("```python\nprint(1)\n```\ndef foo():\n  pass") >= 0.5
    assert score_educational_structure(_SAMPLE_EDU_TEXT) >= 0.75
    assert score_educational_structure("just a short note") < 0.3


def test_combine_renormalizes_missing_human_review() -> None:
    components = {
        "domain_reputation_score": 0.8,
        "content_length_score": 1.0,
        "formula_density_score": 0.6,
        "code_example_score": 0.4,
        "educational_structure_score": 0.7,
        "human_review_score": None,
    }
    quality = combine_quality_scores(components)
    assert quality is not None
    expected_num = (
        0.8 * DOMAIN_REPUTATION_WEIGHT
        + 1.0 * CONTENT_LENGTH_WEIGHT
        + 0.6 * FORMULA_DENSITY_WEIGHT
        + 0.4 * CODE_EXAMPLE_WEIGHT
        + 0.7 * EDUCATIONAL_STRUCTURE_WEIGHT
    )
    expected_den = 1.0 - HUMAN_REVIEW_WEIGHT
    assert quality == round(expected_num / expected_den, 4)


def test_score_source_quality_full_text() -> None:
    result = score_source_quality(
        SourceQualityInput(
            url="https://en.wikipedia.org/wiki/Bayes_theorem",
            raw_text=_SAMPLE_EDU_TEXT,
            human_review_score=0.9,
        )
    )
    assert result.domain_reputation_score == 0.90
    assert result.content_length_score is not None and result.content_length_score > 0
    assert result.formula_density_score is not None and result.formula_density_score > 0
    assert result.code_example_score is not None and result.code_example_score > 0
    assert result.educational_structure_score is not None
    assert result.educational_structure_score >= 0.75
    assert result.human_review_score == 0.9
    assert result.quality_score is not None
    assert 0.0 <= result.quality_score <= 1.0
    assert "human_review_score" in result.components_used


def test_score_source_quality_without_text_uses_domain_only() -> None:
    result = score_source_quality(
        SourceQualityInput(url="https://example.com/notes", raw_text=None)
    )
    assert result.domain_reputation_score == 0.5
    assert result.content_length_score is None
    assert result.formula_density_score is None
    assert result.code_example_score is None
    assert result.educational_structure_score is None
    assert result.quality_score == 0.5
    assert result.components_used == ("domain_reputation_score",)


def test_rejects_out_of_range_human_score() -> None:
    with pytest.raises(SourceQualityError, match="human_review_score"):
        score_source_quality(SourceQualityInput(url=None, human_review_score=1.5))


def test_score_and_update_resource_persists_scores() -> None:
    session = MagicMock()
    resource = Resource(
        source_type=ResourceSourceType.URL,
        url="https://ocw.mit.edu/prob",
        summary=_SAMPLE_EDU_TEXT,
        status=ContentStatus.DRAFT,
    )

    result = score_and_update_resource(session, resource, human_review_score=0.8)

    assert resource.domain_reputation_score == 0.95
    assert resource.content_length_score == result.content_length_score
    assert resource.formula_density_score == result.formula_density_score
    assert resource.code_example_score == result.code_example_score
    assert resource.educational_structure_score == result.educational_structure_score
    assert resource.human_review_score == 0.8
    assert resource.quality_score == result.quality_score
    session.add.assert_called_once_with(resource)
    session.commit.assert_called_once()


def test_score_and_update_resource_can_skip_commit() -> None:
    session = MagicMock()
    resource = Resource(
        source_type=ResourceSourceType.MANUAL,
        url=None,
        summary="Definition of variance. Example calculation follows.",
        status=ContentStatus.DRAFT,
    )
    score_and_update_resource(session, resource, commit=False)
    session.commit.assert_not_called()
    assert resource.quality_score is not None
