from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.models.resource import Resource

# Weights from README / architecture source quality table (sum to 1.0).
DOMAIN_REPUTATION_WEIGHT = 0.25
CONTENT_LENGTH_WEIGHT = 0.10
FORMULA_DENSITY_WEIGHT = 0.15
CODE_EXAMPLE_WEIGHT = 0.10
EDUCATIONAL_STRUCTURE_WEIGHT = 0.20
HUMAN_REVIEW_WEIGHT = 0.20

_COMPONENT_WEIGHTS: dict[str, float] = {
    "domain_reputation_score": DOMAIN_REPUTATION_WEIGHT,
    "content_length_score": CONTENT_LENGTH_WEIGHT,
    "formula_density_score": FORMULA_DENSITY_WEIGHT,
    "code_example_score": CODE_EXAMPLE_WEIGHT,
    "educational_structure_score": EDUCATIONAL_STRUCTURE_WEIGHT,
    "human_review_score": HUMAN_REVIEW_WEIGHT,
}

# Known educational / reference hosts used for reputation (not a crawl allowlist).
_DOMAIN_REPUTATION: dict[str, float] = {
    "wikipedia.org": 0.90,
    "en.wikipedia.org": 0.90,
    "mit.edu": 0.95,
    "ocw.mit.edu": 0.95,
    "stanford.edu": 0.93,
    "harvard.edu": 0.93,
    "berkeley.edu": 0.93,
    "cam.ac.uk": 0.92,
    "ox.ac.uk": 0.92,
    "arxiv.org": 0.88,
    "ssrn.com": 0.75,
    "khanacademy.org": 0.88,
    "brilliant.org": 0.80,
    "investopedia.com": 0.70,
    "github.com": 0.72,
    "stackoverflow.com": 0.68,
    "quantstart.com": 0.70,
    "quant.stackexchange.com": 0.78,
}

_HIGH_REPUTATION_TLDS = (".edu", ".ac.uk", ".ac.jp", ".edu.au")
_DEFAULT_DOMAIN_SCORE = 0.50
_LOCAL_MANUAL_SCORE = 0.55

_MATH_MARKERS = (
    r"\$\$[^$]+\$\$",
    r"\$[^$\n]+\$",
    r"\\\([^)]+\\\)",
    r"\\\[[^\]]+\\\]",
    r"\\begin\{(?:equation|align|eqnarray|math)\}",
    r"\bP\s*\(",
    r"\bE\s*\[",
    r"\bVar\s*\(",
    r"\bBayes\b",
    r"\btheorem\b",
    r"\blemma\b",
    r"\bproof\b",
    r"\bprobability\b",
    r"\bderivative\b",
    r"\bintegral\b",
)
_MATH_PATTERN = re.compile("|".join(_MATH_MARKERS), re.IGNORECASE)

_CODE_FENCE_PATTERN = re.compile(r"```[\w+-]*\n[\s\S]*?```")
_CODE_INLINE_PATTERN = re.compile(
    r"(?:^|\n)\s*(?:def |class |import |from |public |private |SELECT |CREATE )",
    re.IGNORECASE,
)
_CODE_LANG_HINT = re.compile(
    r"\b(?:python|java|sql|javascript|typescript|c\+\+|numpy|pandas)\b",
    re.IGNORECASE,
)

_STRUCTURE_PATTERNS = (
    re.compile(r"(?m)^#{1,6}\s+\S+"),
    re.compile(
        r"(?m)^#{1,6}\s+.*\b(?:definition|example|exercise|solution|summary)\b",
        re.I,
    ),
    re.compile(
        r"\b(?:definition|prerequisite|intuition|example|exercise|solution|theorem)\b",
        re.I,
    ),
    re.compile(r"(?m)^\s*[-*]\s+\S+"),
    re.compile(r"(?m)^\s*\d+[.)]\s+\S+"),
    re.compile(r"(?m)^(?:Q:|A:|Question:|Answer:)\s*", re.I),
)


@dataclass(frozen=True, slots=True)
class SourceQualityInput:
    url: str | None = None
    raw_text: str | None = None
    human_review_score: float | None = None
    # Optional overrides used when a signal was scored earlier in the pipeline.
    domain_reputation_score: float | None = None
    content_length_score: float | None = None
    formula_density_score: float | None = None
    code_example_score: float | None = None
    educational_structure_score: float | None = None


@dataclass(frozen=True, slots=True)
class SourceQualityResult:
    domain_reputation_score: float | None
    content_length_score: float | None
    formula_density_score: float | None
    code_example_score: float | None
    educational_structure_score: float | None
    human_review_score: float | None
    quality_score: float | None
    components_used: tuple[str, ...]


class SourceQualityError(ValueError):
    """Raised when quality scoring input is invalid."""


def score_source_quality(source: SourceQualityInput) -> SourceQualityResult:
    """Compute component scores and a weighted quality_score in [0, 1].

    Missing components are skipped and remaining weights are re-normalized so a
    usable score is available before human review (README weights: domain 25%,
    length 10%, formula 15%, code 10%, structure 20%, human review 20%).
    """
    human = _clamp_optional(source.human_review_score, field_name="human_review_score")

    domain = (
        _clamp_optional(source.domain_reputation_score, field_name="domain_reputation_score")
        if source.domain_reputation_score is not None
        else score_domain_reputation(source.url)
    )

    text = (source.raw_text or "").strip()
    has_text = bool(text)

    length = (
        _clamp_optional(source.content_length_score, field_name="content_length_score")
        if source.content_length_score is not None
        else (score_content_length(text) if has_text else None)
    )
    formula = (
        _clamp_optional(source.formula_density_score, field_name="formula_density_score")
        if source.formula_density_score is not None
        else (score_formula_density(text) if has_text else None)
    )
    code = (
        _clamp_optional(source.code_example_score, field_name="code_example_score")
        if source.code_example_score is not None
        else (score_code_examples(text) if has_text else None)
    )
    structure = (
        _clamp_optional(
            source.educational_structure_score,
            field_name="educational_structure_score",
        )
        if source.educational_structure_score is not None
        else (score_educational_structure(text) if has_text else None)
    )

    components: dict[str, float | None] = {
        "domain_reputation_score": domain,
        "content_length_score": length,
        "formula_density_score": formula,
        "code_example_score": code,
        "educational_structure_score": structure,
        "human_review_score": human,
    }
    quality = combine_quality_scores(components)
    used = tuple(name for name, value in components.items() if value is not None)

    return SourceQualityResult(
        domain_reputation_score=domain,
        content_length_score=length,
        formula_density_score=formula,
        code_example_score=code,
        educational_structure_score=structure,
        human_review_score=human,
        quality_score=quality,
        components_used=used,
    )


def score_and_update_resource(
    session: Session,
    resource: Resource,
    *,
    raw_text: str | None = None,
    human_review_score: float | None = None,
    commit: bool = True,
) -> SourceQualityResult:
    """Score a Resource and write component + aggregate scores onto the row."""
    result = score_source_quality(
        SourceQualityInput(
            url=resource.url,
            raw_text=raw_text if raw_text is not None else resource.summary,
            human_review_score=(
                human_review_score
                if human_review_score is not None
                else resource.human_review_score
            ),
            domain_reputation_score=None,
            content_length_score=None,
            formula_density_score=None,
            code_example_score=None,
            educational_structure_score=None,
        )
    )
    resource.domain_reputation_score = result.domain_reputation_score
    resource.content_length_score = result.content_length_score
    resource.formula_density_score = result.formula_density_score
    resource.code_example_score = result.code_example_score
    resource.educational_structure_score = result.educational_structure_score
    resource.human_review_score = result.human_review_score
    resource.quality_score = result.quality_score
    session.add(resource)
    if commit:
        session.commit()
    return result


def combine_quality_scores(components: dict[str, float | None]) -> float | None:
    weighted_sum = 0.0
    weight_sum = 0.0
    for name, weight in _COMPONENT_WEIGHTS.items():
        value = components.get(name)
        if value is None:
            continue
        clamped = _clamp(value)
        weighted_sum += clamped * weight
        weight_sum += weight
    if weight_sum <= 0:
        return None
    return round(weighted_sum / weight_sum, 4)


def score_domain_reputation(url: str | None) -> float | None:
    if not (url or "").strip():
        return _LOCAL_MANUAL_SCORE
    host = _extract_host(url)
    if host is None:
        return _DEFAULT_DOMAIN_SCORE

    if host in _DOMAIN_REPUTATION:
        return _DOMAIN_REPUTATION[host]
    for known, score in _DOMAIN_REPUTATION.items():
        if host == known or host.endswith(f".{known}"):
            return score
    for tld in _HIGH_REPUTATION_TLDS:
        if host.endswith(tld):
            return 0.85
    return _DEFAULT_DOMAIN_SCORE


def score_content_length(text: str) -> float:
    length = len(text.strip())
    if length <= 0:
        return 0.0
    if length < 200:
        return round(length / 200 * 0.4, 4)
    if length < 800:
        return round(0.4 + (length - 200) / 600 * 0.35, 4)
    if length <= 20_000:
        return 1.0
    # Extremely long dumps are slightly less preferred for review prioritization.
    return 0.85


def score_formula_density(text: str) -> float:
    if not text.strip():
        return 0.0
    matches = len(_MATH_PATTERN.findall(text))
    word_count = max(1, len(text.split()))
    density = matches / word_count
    # Soft saturation: a handful of formulas or dense short math notes score high.
    if matches == 0:
        return 0.0
    if matches >= 8 or density >= 0.08:
        return 1.0
    if matches >= 4 or density >= 0.04:
        return 0.8
    if matches >= 2:
        return 0.55
    return 0.3


def score_code_examples(text: str) -> float:
    if not text.strip():
        return 0.0
    fences = len(_CODE_FENCE_PATTERN.findall(text))
    inline_blocks = len(_CODE_INLINE_PATTERN.findall(text))
    lang_hints = len(_CODE_LANG_HINT.findall(text))
    score = 0.0
    if fences:
        score += min(0.7, 0.35 * fences)
    if inline_blocks:
        score += min(0.25, 0.1 * inline_blocks)
    if lang_hints:
        score += min(0.2, 0.05 * lang_hints)
    return round(min(1.0, score), 4)


def score_educational_structure(text: str) -> float:
    if not text.strip():
        return 0.0
    hits = sum(1 for pattern in _STRUCTURE_PATTERNS if pattern.search(text))
    if hits == 0:
        return 0.1 if len(text.split()) >= 40 else 0.0
    if hits >= 5:
        return 1.0
    if hits >= 3:
        return 0.75
    if hits == 2:
        return 0.5
    return 0.3


def _extract_host(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").strip().lower()
    return host or None


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _clamp_optional(value: float | None, *, field_name: str) -> float | None:
    if value is None:
        return None
    if value < 0 or value > 1:
        raise SourceQualityError(f"{field_name} must be between 0 and 1")
    return float(value)
