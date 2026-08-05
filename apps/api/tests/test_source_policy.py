from typing import Any

from app.config import Settings
from app.models.enums import (
    AllowlistStatus,
    ContentStatus,
    LicenseStatus,
    ResourceSourceType,
    RobotsStatus,
    SourcePolicyDecision,
)
from app.models.resource import Resource
from app.services.source_policy import (
    SourcePolicyInput,
    check_resource_policy,
    check_source_policy,
    domain_on_allowlist,
    normalize_license_token,
)

_ALLOW_ALL_ROBOTS = "User-agent: *\nAllow: /\n"
_DISALLOW_ALL_ROBOTS = "User-agent: *\nDisallow: /\n"


def _settings(
    *,
    ingestion_source_allowlist: list[str] | None = None,
    ingestion_user_agent: str = "QuantPrepBot/0.1 (+test)",
    ingestion_robots_timeout_seconds: float = 5.0,
) -> Settings:
    values: dict[str, Any] = {
        "ingestion_source_allowlist": list(ingestion_source_allowlist or []),
        "ingestion_user_agent": ingestion_user_agent,
        "ingestion_robots_timeout_seconds": ingestion_robots_timeout_seconds,
    }
    return Settings.model_construct(**values)


def _allow_robots(_robots_url: str) -> str:
    return _ALLOW_ALL_ROBOTS


def _disallow_robots(_robots_url: str) -> str:
    return _DISALLOW_ALL_ROBOTS


def _missing_robots(_robots_url: str) -> None:
    return None


def test_domain_on_allowlist_exact_and_suffix() -> None:
    allowlist = ["mit.edu", "wikipedia.org", ".edu"]
    assert domain_on_allowlist("mit.edu", allowlist)
    assert domain_on_allowlist("web.mit.edu", allowlist)
    assert domain_on_allowlist("www.wikipedia.org", allowlist)
    assert domain_on_allowlist("stanford.edu", allowlist)
    assert not domain_on_allowlist("example.com", allowlist)


def test_normalize_license_token() -> None:
    assert normalize_license_token("  CC BY 4.0 ") == "cc-by-4.0"
    assert normalize_license_token("Public Domain") == "public-domain"
    assert normalize_license_token(None) is None
    assert normalize_license_token("   ") is None


def test_allowlist_denies_unknown_host() -> None:
    result = check_source_policy(
        SourcePolicyInput(
            url="https://blocked.example.com/notes",
            source_type=ResourceSourceType.URL,
            license="CC-BY-4.0",
            attribution="Example author",
        ),
        settings=_settings(ingestion_source_allowlist=["mit.edu"]),
        robots_body_fetcher=_allow_robots,
    )
    assert result.decision is SourcePolicyDecision.DENY
    assert result.allowlist_status is AllowlistStatus.DENIED
    assert result.host == "blocked.example.com"


def test_open_allowlist_with_permissive_license_and_attribution_allows() -> None:
    result = check_source_policy(
        SourcePolicyInput(
            url="https://en.wikipedia.org/wiki/Bayes",
            source_type=ResourceSourceType.URL,
            license="CC-BY-4.0",
            attribution="Wikipedia contributors",
        ),
        settings=_settings(),
        robots_body_fetcher=_allow_robots,
    )
    assert result.decision is SourcePolicyDecision.ALLOW
    assert result.allowlist_status is AllowlistStatus.NOT_CONFIGURED
    assert result.robots_status is RobotsStatus.ALLOWED
    assert result.license_status is LicenseStatus.PERMISSIVE
    assert result.attribution_required is True
    assert result.attribution_present is True


def test_robots_disallow_denies() -> None:
    result = check_source_policy(
        SourcePolicyInput(
            url="https://example.com/private/page",
            source_type=ResourceSourceType.URL,
            license="CC-BY-4.0",
            attribution="Author",
        ),
        settings=_settings(),
        robots_body_fetcher=_disallow_robots,
    )
    assert result.decision is SourcePolicyDecision.DENY
    assert result.robots_status is RobotsStatus.DISALLOWED


def test_robots_unknown_requires_review() -> None:
    result = check_source_policy(
        SourcePolicyInput(
            url="https://example.com/page",
            source_type=ResourceSourceType.URL,
            license="MIT",
            attribution="Author",
        ),
        settings=_settings(),
        robots_body_fetcher=_missing_robots,
    )
    assert result.decision is SourcePolicyDecision.REVIEW
    assert result.robots_status is RobotsStatus.UNKNOWN


def test_restrictive_license_denies() -> None:
    result = check_source_policy(
        SourcePolicyInput(
            url="https://example.com/book",
            source_type=ResourceSourceType.URL,
            license="All Rights Reserved",
            attribution="Publisher",
        ),
        settings=_settings(),
        robots_body_fetcher=_allow_robots,
    )
    assert result.decision is SourcePolicyDecision.DENY
    assert result.license_status is LicenseStatus.RESTRICTIVE


def test_missing_attribution_requires_review() -> None:
    result = check_source_policy(
        SourcePolicyInput(
            url="https://example.com/notes",
            source_type=ResourceSourceType.URL,
            license="CC-BY-4.0",
            attribution=None,
        ),
        settings=_settings(),
        robots_body_fetcher=_allow_robots,
    )
    assert result.decision is SourcePolicyDecision.REVIEW
    assert result.attribution_required is True
    assert result.attribution_present is False


def test_cc0_does_not_require_attribution() -> None:
    result = check_source_policy(
        SourcePolicyInput(
            url="https://example.com/public",
            source_type=ResourceSourceType.URL,
            license="CC0",
            attribution=None,
        ),
        settings=_settings(),
        robots_body_fetcher=_allow_robots,
    )
    assert result.decision is SourcePolicyDecision.ALLOW
    assert result.attribution_required is False
    assert result.license_status is LicenseStatus.PERMISSIVE


def test_missing_license_requires_review() -> None:
    result = check_source_policy(
        SourcePolicyInput(
            url="https://example.com/page",
            source_type=ResourceSourceType.URL,
            license=None,
            attribution="Someone",
        ),
        settings=_settings(),
        robots_body_fetcher=_allow_robots,
    )
    assert result.decision is SourcePolicyDecision.REVIEW
    assert result.license_status is LicenseStatus.MISSING


def test_manual_source_skips_allowlist_and_robots() -> None:
    result = check_source_policy(
        SourcePolicyInput(
            url=None,
            source_type=ResourceSourceType.MANUAL,
            license="private",
            attribution="local notes",
        ),
        settings=_settings(ingestion_source_allowlist=["mit.edu"]),
    )
    assert result.allowlist_status is AllowlistStatus.NOT_APPLICABLE
    assert result.robots_status is RobotsStatus.NOT_APPLICABLE
    assert result.license_status is LicenseStatus.UNKNOWN
    assert result.decision is SourcePolicyDecision.REVIEW


def test_check_resource_policy_uses_resource_fields() -> None:
    resource = Resource(
        source_type=ResourceSourceType.URL,
        url="https://docs.mit.edu/probability",
        license="CC-BY-4.0",
        attribution="MIT OpenCourseWare",
        status=ContentStatus.DRAFT,
    )
    result = check_resource_policy(
        resource,
        settings=_settings(ingestion_source_allowlist=["mit.edu"]),
        robots_body_fetcher=_allow_robots,
    )
    assert result.decision is SourcePolicyDecision.ALLOW
    assert result.allowlist_status is AllowlistStatus.ALLOWED
    assert result.host == "docs.mit.edu"
