from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import requests
import trafilatura
from bs4 import BeautifulSoup

from app.config import Settings, get_settings
from app.dedup.text import text_hash
from app.models.enums import ExtractionMethod, ResourceSourceType
from app.models.resource import Resource

_SHELL_MARKERS = (
    "enable javascript",
    "enable js",
    "please enable javascript",
    "noscript",
    "you need to enable javascript",
    "loading...",
)

_WHITESPACE_RE = re.compile(r"[ \t]+")
_MULTI_BLANK_RE = re.compile(r"\n{3,}")


class SourceExtractionError(ValueError):
    """Raised when source text cannot be extracted."""


@dataclass(frozen=True, slots=True)
class HtmlFetchResult:
    url: str
    status_code: int
    content_type: str | None
    body: str


@dataclass(frozen=True, slots=True)
class ExtractedSourceText:
    text: str
    method: ExtractionMethod
    title: str | None
    source_url: str | None
    char_count: int
    raw_text_hash: str


HtmlFetcher = Callable[[str], HtmlFetchResult]
PlaywrightFetcher = Callable[[str], str]


def extract_from_pasted_text(
    text: str,
    *,
    title: str | None = None,
) -> ExtractedSourceText:
    cleaned = clean_extracted_text(text)
    if not cleaned:
        raise SourceExtractionError("pasted text is empty after cleaning")
    return _result(
        text=cleaned,
        method=ExtractionMethod.PASTED_TEXT,
        title=_blank_to_none(title),
        source_url=None,
    )


def extract_from_pdf_bytes(
    content: bytes,
    *,
    source_url: str | None = None,
    title: str | None = None,
) -> ExtractedSourceText:
    if not content:
        raise SourceExtractionError("PDF content is empty")
    if not content.startswith(b"%PDF"):
        raise SourceExtractionError("file is not a valid PDF")

    try:
        import fitz  # PyMuPDF
    except ImportError as exc:  # pragma: no cover - dependency guaranteed in install
        raise SourceExtractionError("PyMuPDF is not installed") from exc

    try:
        document = fitz.open(stream=content, filetype="pdf")
    except Exception as exc:  # noqa: BLE001 - surface parse failures as extraction errors
        raise SourceExtractionError(f"failed to open PDF: {exc}") from exc

    try:
        parts: list[str] = []
        for page in document:
            page_text = page.get_text("text")
            if page_text:
                parts.append(page_text)
        meta_title = document.metadata.get("title") if document.metadata else None
    finally:
        document.close()

    cleaned = clean_extracted_text("\n\n".join(parts))
    if not cleaned:
        raise SourceExtractionError("PDF contained no extractable text")

    resolved_title = _blank_to_none(title) or _blank_to_none(meta_title)
    return _result(
        text=cleaned,
        method=ExtractionMethod.PDF_PYMUPDF,
        title=resolved_title,
        source_url=source_url,
    )


def extract_from_pdf_path(
    path: str | Path,
    *,
    source_url: str | None = None,
    title: str | None = None,
) -> ExtractedSourceText:
    pdf_path = Path(path).expanduser()
    if not pdf_path.is_file():
        raise SourceExtractionError(f"PDF not found at '{pdf_path}'")
    return extract_from_pdf_bytes(
        pdf_path.read_bytes(),
        source_url=source_url or str(pdf_path),
        title=title,
    )


def extract_from_url(
    url: str,
    *,
    settings: Settings | None = None,
    html_fetcher: HtmlFetcher | None = None,
    playwright_fetcher: PlaywrightFetcher | None = None,
) -> ExtractedSourceText:
    resolved_url = (url or "").strip()
    if not resolved_url:
        raise SourceExtractionError("url must not be blank")
    if not resolved_url.startswith(("http://", "https://")):
        raise SourceExtractionError("url must start with http:// or https://")

    resolved = settings or get_settings()
    fetcher = html_fetcher or (
        lambda target: fetch_html(
            target,
            timeout_seconds=resolved.ingestion_fetch_timeout_seconds,
            user_agent=resolved.ingestion_user_agent,
        )
    )

    fetched = fetcher(resolved_url)
    if fetched.status_code >= 400:
        raise SourceExtractionError(
            f"failed to fetch url (HTTP {fetched.status_code})",
        )

    content_type = (fetched.content_type or "").lower()
    if content_type and "html" not in content_type and "text/" not in content_type:
        raise SourceExtractionError(
            f"unsupported content type for URL extraction: {fetched.content_type}",
        )

    static = _extract_from_html(fetched.body, source_url=resolved_url)
    adequate = _is_adequate(static.text, resolved.ingestion_min_extracted_chars)
    if adequate and not _looks_like_js_shell(static.text):
        return static

    # Thin/static SPA-like output: optional Playwright fallback (ADR-009 / QP-042).
    if not resolved.ingestion_playwright_enabled:
        if static.text:
            return static
        raise SourceExtractionError(
            "static extraction produced too little text; "
            "enable INGESTION_PLAYWRIGHT_ENABLED for JS-heavy pages",
        )

    play_fetcher = playwright_fetcher or (
        lambda target: fetch_html_with_playwright(
            target,
            timeout_seconds=resolved.ingestion_fetch_timeout_seconds,
            user_agent=resolved.ingestion_user_agent,
        )
    )
    try:
        rendered_html = play_fetcher(resolved_url)
    except SourceExtractionError:
        if static.text:
            return static
        raise

    rendered = _extract_from_html(
        rendered_html,
        source_url=resolved_url,
        preferred_method=ExtractionMethod.URL_PLAYWRIGHT,
    )
    if rendered.text:
        return rendered

    if static.text:
        return static
    raise SourceExtractionError("Playwright extraction produced no usable text")


def extract_from_resource(
    resource: Resource,
    *,
    settings: Settings | None = None,
    html_fetcher: HtmlFetcher | None = None,
    playwright_fetcher: PlaywrightFetcher | None = None,
    pasted_text: str | None = None,
) -> ExtractedSourceText:
    """Extract cleaned text for a Resource without AI parsing (QP-043 owns that)."""
    resolved = settings or get_settings()
    source_type = resource.source_type

    if source_type is ResourceSourceType.URL:
        if not resource.url:
            raise SourceExtractionError("URL resource is missing url")
        return extract_from_url(
            resource.url,
            settings=resolved,
            html_fetcher=html_fetcher,
            playwright_fetcher=playwright_fetcher,
        )

    if source_type is ResourceSourceType.PDF:
        if not resource.url:
            raise SourceExtractionError("PDF resource is missing stored file path")
        pdf_path = resolve_resource_file_path(resource.url, settings=resolved)
        return extract_from_pdf_path(
            pdf_path,
            source_url=resource.url,
            title=resource.title,
        )

    # MANUAL / BOOK_NOTE / GENERATED: already-pasted text on the resource.
    text = pasted_text if pasted_text is not None else resource.summary
    if text is None or not text.strip():
        raise SourceExtractionError(
            f"{source_type.value} resource has no pasted text to extract",
        )
    return extract_from_pasted_text(text, title=resource.title)


def fetch_html(
    url: str,
    *,
    timeout_seconds: float,
    user_agent: str,
) -> HtmlFetchResult:
    try:
        response = requests.get(
            url,
            timeout=timeout_seconds,
            headers={"User-Agent": user_agent, "Accept": "text/html,application/xhtml+xml"},
            allow_redirects=True,
        )
    except requests.RequestException as exc:
        raise SourceExtractionError(f"failed to fetch url: {exc}") from exc

    # Prefer explicit decoding; requests may use apparent encoding for HTML.
    response.encoding = response.encoding or response.apparent_encoding or "utf-8"
    return HtmlFetchResult(
        url=str(response.url),
        status_code=response.status_code,
        content_type=response.headers.get("Content-Type"),
        body=response.text or "",
    )


def fetch_html_with_playwright(
    url: str,
    *,
    timeout_seconds: float,
    user_agent: str,
) -> str:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SourceExtractionError(
            "Playwright is not installed; pip install -e '.[playwright]' "
            "and run 'playwright install chromium'",
        ) from exc

    timeout_ms = max(1_000, int(timeout_seconds * 1000))
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page(user_agent=user_agent)
                page.goto(url, wait_until="networkidle", timeout=timeout_ms)
                content = page.content()
                return str(content)
            finally:
                browser.close()
    except SourceExtractionError:
        raise
    except Exception as exc:  # noqa: BLE001 - map browser errors for callers
        raise SourceExtractionError(f"Playwright fetch failed: {exc}") from exc


def resolve_resource_file_path(
    relative_or_absolute: str,
    *,
    settings: Settings | None = None,
) -> Path:
    path = Path(relative_or_absolute).expanduser()
    if path.is_absolute():
        return path

    resolved = settings or get_settings()
    base = Path(resolved.upload_dir).expanduser()
    if not base.is_absolute():
        base = resolved.repo_root / base
    return (base / relative_or_absolute).resolve()


def clean_extracted_text(text: str) -> str:
    if not text:
        return ""
    lines = [_WHITESPACE_RE.sub(" ", line).strip() for line in text.splitlines()]
    collapsed = "\n".join(line for line in lines if line)
    return _MULTI_BLANK_RE.sub("\n\n", collapsed).strip()


def _extract_from_html(
    html: str,
    *,
    source_url: str,
    preferred_method: ExtractionMethod | None = None,
) -> ExtractedSourceText:
    if not (html or "").strip():
        raise SourceExtractionError("HTML body is empty")

    title = _html_title(html)
    trafilatura_text = _extract_with_trafilatura(html, source_url=source_url)
    if trafilatura_text:
        method = preferred_method or ExtractionMethod.URL_TRAFILATURA
        return _result(
            text=trafilatura_text,
            method=method,
            title=title,
            source_url=source_url,
        )

    soup_text = _extract_with_beautifulsoup(html)
    if soup_text:
        method = preferred_method or ExtractionMethod.URL_BEAUTIFULSOUP
        return _result(
            text=soup_text,
            method=method,
            title=title,
            source_url=source_url,
        )

    return _result(
        text="",
        method=preferred_method or ExtractionMethod.URL_BEAUTIFULSOUP,
        title=title,
        source_url=source_url,
    )


def _extract_with_trafilatura(html: str, *, source_url: str) -> str:
    extracted = trafilatura.extract(
        html,
        url=source_url,
        include_comments=False,
        include_tables=True,
        favor_recall=True,
    )
    return clean_extracted_text(extracted or "")


def _extract_with_beautifulsoup(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "template", "svg"]):
        tag.decompose()
    for tag in soup.find_all(["nav", "footer", "header", "aside"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    return clean_extracted_text(text)


def _html_title(html: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    if soup.title and soup.title.string:
        return _blank_to_none(str(soup.title.string))
    return None


def _is_adequate(text: str, min_chars: int) -> bool:
    return len(text.strip()) >= min_chars


def _looks_like_js_shell(text: str) -> bool:
    lowered = text.lower()
    if any(marker in lowered for marker in _SHELL_MARKERS):
        return True
    # Extremely short non-empty shells also look non-useful.
    return 0 < len(text) < 80


def _result(
    *,
    text: str,
    method: ExtractionMethod,
    title: str | None,
    source_url: str | None,
) -> ExtractedSourceText:
    cleaned = clean_extracted_text(text)
    return ExtractedSourceText(
        text=cleaned,
        method=method,
        title=title,
        source_url=source_url,
        char_count=len(cleaned),
        raw_text_hash=text_hash(cleaned) if cleaned else text_hash(""),
    )


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None
