from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx

from app.config import Settings, get_settings
from app.models.enums import (
    AllowlistStatus,
    LicenseStatus,
    ResourceSourceType,
    RobotsStatus,
    SourcePolicyDecision,
)
from app.models.resource import Resource

RobotsBodyFetcher = Callable[[str], str | None]

# Licenses that permit educational reuse with attribution (normalized forms).
_PERMISSIVE_LICENSES = frozenset(
    {
        "cc0",
        "cc-0",
        "public-domain",
        "pd",
        "cc-by",
        "cc-by-4.0",
        "cc-by-3.0",
        "cc-by-2.0",
        "cc-by-sa",
        "cc-by-sa-4.0",
        "cc-by-sa-3.0",
        "mit",
        "apache-2.0",
        "apache",
        "bsd",
        "bsd-2-clause",
        "bsd-3-clause",
        "unlicense",
        "educational-use",
        "free-educational-use",
    }
)

# Licenses that must not feed the automated pipeline without explicit human override.
_RESTRICTIVE_LICENSES = frozenset(
    {
        "all-rights-reserved",
        "proprietary",
        "copyright",
        "commercial",
        "commercial-only",
        "paid",
        "closed",
        "no-derivatives",
        "cc-by-nd",
        "cc-by-nc-nd",
    }
)

# Permissive licenses that still require attribution / notice.
_ATTRIBUTION_EXEMPT_LICENSES = frozenset(
    {
        "cc0",
        "cc-0",
        "public-domain",
        "pd",
        "unlicense",
    }
)

_URL_LIKE_SOURCE_TYPES = frozenset({ResourceSourceType.URL})


@dataclass(frozen=True, slots=True)
class SourcePolicyInput:
    url: str | None = None
    source_type: ResourceSourceType | None = None
    license: str | None = None
    attribution: str | None = None


@dataclass(frozen=True, slots=True)
class SourcePolicyResult:
    decision: SourcePolicyDecision
    allowlist_status: AllowlistStatus
    robots_status: RobotsStatus
    license_status: LicenseStatus
    attribution_required: bool
    attribution_present: bool
    reasons: tuple[str, ...]
    host: str | None = None


def check_source_policy(
    source: SourcePolicyInput,
    *,
    settings: Settings | None = None,
    robots_body_fetcher: RobotsBodyFetcher | None = None,
) -> SourcePolicyResult:
    """Evaluate ingestion guardrails for a candidate source.

    Decision rules (first hard deny wins):
    - DENY: host not on allowlist (when configured), robots.txt disallows, restrictive license
    - REVIEW: missing/unknown license, robots unknown, attribution required but missing
    - ALLOW: all hard checks pass and no review warnings
    """
    resolved = settings or get_settings()
    reasons: list[str] = []

    needs_network_policy = _needs_network_policy(source)
    host = _extract_host(source.url) if needs_network_policy else None

    allowlist_status = _check_allowlist(
        host=host,
        needs_network_policy=needs_network_policy,
        allowlist=resolved.ingestion_source_allowlist,
        reasons=reasons,
    )
    robots_status = _check_robots(
        url=source.url if needs_network_policy else None,
        needs_network_policy=needs_network_policy,
        user_agent=resolved.ingestion_user_agent,
        timeout_seconds=resolved.ingestion_robots_timeout_seconds,
        robots_body_fetcher=robots_body_fetcher,
        reasons=reasons,
    )
    license_status = _check_license(source.license, reasons=reasons)
    attribution_present = bool((source.attribution or "").strip())
    attribution_required = _attribution_required(source.license)
    if attribution_required and not attribution_present:
        reasons.append("attribution is required but missing")
    elif attribution_present:
        reasons.append("attribution present")

    decision = _decide(
        allowlist_status=allowlist_status,
        robots_status=robots_status,
        license_status=license_status,
        attribution_required=attribution_required,
        attribution_present=attribution_present,
    )

    return SourcePolicyResult(
        decision=decision,
        allowlist_status=allowlist_status,
        robots_status=robots_status,
        license_status=license_status,
        attribution_required=attribution_required,
        attribution_present=attribution_present,
        reasons=tuple(reasons),
        host=host,
    )


def check_resource_policy(
    resource: Resource,
    *,
    settings: Settings | None = None,
    robots_body_fetcher: RobotsBodyFetcher | None = None,
) -> SourcePolicyResult:
    return check_source_policy(
        SourcePolicyInput(
            url=resource.url,
            source_type=resource.source_type,
            license=resource.license,
            attribution=resource.attribution,
        ),
        settings=settings,
        robots_body_fetcher=robots_body_fetcher,
    )


def fetch_robots_txt_body(
    robots_url: str,
    *,
    timeout_seconds: float,
    user_agent: str,
) -> str | None:
    """Fetch robots.txt body. Returns None on transport/HTTP errors; empty string if missing."""
    try:
        with httpx.Client(
            timeout=timeout_seconds,
            headers={"User-Agent": user_agent},
            follow_redirects=True,
            trust_env=False,
        ) as client:
            response = client.get(robots_url)
    except httpx.HTTPError:
        return None

    if response.status_code == 404:
        return ""
    if response.status_code >= 400:
        return None
    return response.text


def domain_on_allowlist(host: str, allowlist: list[str]) -> bool:
    normalized_host = host.strip().lower().removeprefix("www.")
    if not normalized_host:
        return False
    for entry in allowlist:
        pattern = entry.strip().lower()
        if not pattern:
            continue
        if pattern.startswith("*."):
            pattern = pattern[2:]
        if pattern.startswith("."):
            if normalized_host.endswith(pattern) or normalized_host == pattern.lstrip("."):
                return True
            continue
        if normalized_host == pattern or normalized_host.endswith(f".{pattern}"):
            return True
    return False


def normalize_license_token(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip().lower()
    if not stripped:
        return None
    token = (
        stripped.replace("_", "-")
        .replace(" ", "-")
        .replace("licence", "license")
        .replace("creative-commons-attribution", "cc-by")
        .replace("creative-commons", "cc")
    )
    while "--" in token:
        token = token.replace("--", "-")
    return token


def _needs_network_policy(source: SourcePolicyInput) -> bool:
    if not (source.url or "").strip():
        return False
    if source.source_type is None:
        return True
    return source.source_type in _URL_LIKE_SOURCE_TYPES


def _extract_host(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").strip().lower()
    return host or None


def _check_allowlist(
    *,
    host: str | None,
    needs_network_policy: bool,
    allowlist: list[str],
    reasons: list[str],
) -> AllowlistStatus:
    if not needs_network_policy:
        reasons.append("allowlist not applicable for non-URL source")
        return AllowlistStatus.NOT_APPLICABLE

    if not allowlist:
        reasons.append("source allowlist not configured (open mode)")
        return AllowlistStatus.NOT_CONFIGURED

    if not host:
        reasons.append("URL host missing; allowlist check failed")
        return AllowlistStatus.DENIED

    if domain_on_allowlist(host, allowlist):
        reasons.append(f"host '{host}' is on the source allowlist")
        return AllowlistStatus.ALLOWED

    reasons.append(f"host '{host}' is not on the source allowlist")
    return AllowlistStatus.DENIED


def _check_robots(
    *,
    url: str | None,
    needs_network_policy: bool,
    user_agent: str,
    timeout_seconds: float,
    robots_body_fetcher: RobotsBodyFetcher | None,
    reasons: list[str],
) -> RobotsStatus:
    if not needs_network_policy or not url:
        reasons.append("robots.txt not applicable for non-URL source")
        return RobotsStatus.NOT_APPLICABLE

    parsed = urlparse(url.strip())
    if not parsed.scheme or not parsed.netloc:
        reasons.append("URL is invalid for robots.txt check")
        return RobotsStatus.UNKNOWN

    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    if robots_body_fetcher is not None:
        body = robots_body_fetcher(robots_url)
    else:
        body = fetch_robots_txt_body(
            robots_url,
            timeout_seconds=timeout_seconds,
            user_agent=user_agent,
        )
    if body is None:
        reasons.append(f"robots.txt unavailable for {parsed.netloc}")
        return RobotsStatus.UNKNOWN

    parser = RobotFileParser()
    parser.parse(body.splitlines())
    # Empty / missing body → default allow (RobotFileParser allows when no rules).
    if parser.can_fetch(user_agent, url.strip()):
        reasons.append(f"robots.txt allows user-agent fetch of path on {parsed.netloc}")
        return RobotsStatus.ALLOWED

    reasons.append(f"robots.txt disallows user-agent fetch of path on {parsed.netloc}")
    return RobotsStatus.DISALLOWED


def _check_license(license_value: str | None, *, reasons: list[str]) -> LicenseStatus:
    token = normalize_license_token(license_value)
    if token is None:
        reasons.append("license is missing")
        return LicenseStatus.MISSING

    if token in _RESTRICTIVE_LICENSES:
        reasons.append(f"license '{license_value}' is restrictive")
        return LicenseStatus.RESTRICTIVE

    if token in _PERMISSIVE_LICENSES or token.startswith("cc-by"):
        # Treat no-derivatives variants as restrictive even under the cc-by prefix.
        parts = set(token.split("-"))
        if "nd" in parts:
            reasons.append(f"license '{license_value}' is restrictive (no derivatives)")
            return LicenseStatus.RESTRICTIVE
        reasons.append(f"license '{license_value}' is permissive")
        return LicenseStatus.PERMISSIVE

    reasons.append(f"license '{license_value}' is unknown")
    return LicenseStatus.UNKNOWN


def _attribution_required(license_value: str | None) -> bool:
    token = normalize_license_token(license_value)
    if token is not None and token in _ATTRIBUTION_EXEMPT_LICENSES:
        return False
    # Conservative default: require attribution unless the license is explicitly exempt.
    return True


def _decide(
    *,
    allowlist_status: AllowlistStatus,
    robots_status: RobotsStatus,
    license_status: LicenseStatus,
    attribution_required: bool,
    attribution_present: bool,
) -> SourcePolicyDecision:
    if allowlist_status is AllowlistStatus.DENIED:
        return SourcePolicyDecision.DENY
    if robots_status is RobotsStatus.DISALLOWED:
        return SourcePolicyDecision.DENY
    if license_status is LicenseStatus.RESTRICTIVE:
        return SourcePolicyDecision.DENY

    needs_review = False
    if robots_status is RobotsStatus.UNKNOWN:
        needs_review = True
    if license_status in {LicenseStatus.MISSING, LicenseStatus.UNKNOWN}:
        needs_review = True
    if attribution_required and not attribution_present:
        needs_review = True

    if needs_review:
        return SourcePolicyDecision.REVIEW
    return SourcePolicyDecision.ALLOW
