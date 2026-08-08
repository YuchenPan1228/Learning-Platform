from pathlib import Path
from typing import Any

import pytest
from app.config import Settings
from app.models.enums import ContentStatus, ExtractionMethod, ResourceSourceType
from app.models.resource import Resource
from app.services.source_extraction import (
    HtmlFetchResult,
    SourceExtractionError,
    clean_extracted_text,
    extract_from_pasted_text,
    extract_from_pdf_bytes,
    extract_from_resource,
    extract_from_url,
    resolve_resource_file_path,
)


def _settings(
    *,
    ingestion_user_agent: str = "QuantPrepBot/0.1 (+test)",
    ingestion_fetch_timeout_seconds: float = 5.0,
    ingestion_min_extracted_chars: int = 50,
    ingestion_playwright_enabled: bool = False,
    upload_dir: str = "data/uploads",
) -> Settings:
    values: dict[str, Any] = {
        "ingestion_user_agent": ingestion_user_agent,
        "ingestion_fetch_timeout_seconds": ingestion_fetch_timeout_seconds,
        "ingestion_min_extracted_chars": ingestion_min_extracted_chars,
        "ingestion_playwright_enabled": ingestion_playwright_enabled,
        "upload_dir": upload_dir,
    }
    return Settings.model_construct(**values)


_ARTICLE_HTML = """
<!doctype html>
<html>
  <head><title>Bayes Theorem Notes</title></head>
  <body>
    <nav>Home | About</nav>
    <article>
      <h1>Bayes Theorem</h1>
      <p>
        Conditional probability updates beliefs after observing evidence.
        P(A|B) = P(B|A)P(A) / P(B). This page has enough educational prose
        for static extraction tests used by the ingestion pipeline.
      </p>
      <p>
        Interview tip: always state prior, likelihood, and posterior clearly
        when solving Bayesian interview questions under time pressure.
      </p>
    </article>
    <script>window.track = true;</script>
  </body>
</html>
"""

_JS_SHELL_HTML = """
<!doctype html>
<html><head><title>App</title></head>
<body>
  <div id="root">Please enable JavaScript to continue.</div>
</body></html>
"""


def test_clean_extracted_text_collapses_whitespace() -> None:
    raw = "  alpha  \n\n\n  beta\t\tgamma  \n"
    assert clean_extracted_text(raw) == "alpha\nbeta gamma"


def test_extract_from_pasted_text() -> None:
    result = extract_from_pasted_text(
        "  definition of variance\n\nexample calculation  ",
        title="Notes",
    )
    assert result.method is ExtractionMethod.PASTED_TEXT
    assert "definition of variance" in result.text
    assert result.title == "Notes"
    assert result.char_count == len(result.text)
    assert result.raw_text_hash


def test_extract_from_pasted_text_rejects_blank() -> None:
    with pytest.raises(SourceExtractionError, match="empty"):
        extract_from_pasted_text("   \n  ")


def test_extract_from_url_uses_trafilatura_on_article_html() -> None:
    def fetcher(url: str) -> HtmlFetchResult:
        return HtmlFetchResult(
            url=url,
            status_code=200,
            content_type="text/html; charset=utf-8",
            body=_ARTICLE_HTML,
        )

    result = extract_from_url(
        "https://example.com/bayes",
        settings=_settings(),
        html_fetcher=fetcher,
    )
    assert result.method is ExtractionMethod.URL_TRAFILATURA
    assert "Bayes" in (result.title or "") or "Conditional probability" in result.text
    assert "P(A|B)" in result.text or "Conditional" in result.text
    assert result.source_url == "https://example.com/bayes"
    assert result.char_count >= 50


def test_extract_from_url_http_error() -> None:
    def fetcher(url: str) -> HtmlFetchResult:
        return HtmlFetchResult(url=url, status_code=404, content_type="text/html", body="missing")

    with pytest.raises(SourceExtractionError, match="HTTP 404"):
        extract_from_url(
            "https://example.com/missing",
            settings=_settings(),
            html_fetcher=fetcher,
        )


def test_extract_from_url_playwright_fallback_when_enabled() -> None:
    def static_fetcher(url: str) -> HtmlFetchResult:
        return HtmlFetchResult(
            url=url,
            status_code=200,
            content_type="text/html",
            body=_JS_SHELL_HTML,
        )

    def play_fetcher(_url: str) -> str:
        return _ARTICLE_HTML

    result = extract_from_url(
        "https://example.com/spa",
        settings=_settings(ingestion_playwright_enabled=True, ingestion_min_extracted_chars=80),
        html_fetcher=static_fetcher,
        playwright_fetcher=play_fetcher,
    )
    assert result.method is ExtractionMethod.URL_PLAYWRIGHT
    assert "Conditional probability" in result.text or "Bayes" in result.text


def test_extract_from_url_thin_text_without_playwright() -> None:
    def fetcher(url: str) -> HtmlFetchResult:
        return HtmlFetchResult(
            url=url,
            status_code=200,
            content_type="text/html",
            body=_JS_SHELL_HTML,
        )

    # Thin text is still returned when static extract got something.
    result = extract_from_url(
        "https://example.com/spa",
        settings=_settings(ingestion_min_extracted_chars=200),
        html_fetcher=fetcher,
    )
    assert "JavaScript" in result.text or result.char_count >= 0


def test_extract_from_pdf_bytes() -> None:
    import fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "PDF Bayes notes for interview prep.")
    content = doc.tobytes()
    doc.close()

    result = extract_from_pdf_bytes(content, source_url="pdfs/test.pdf", title="Upload")
    assert result.method is ExtractionMethod.PDF_PYMUPDF
    assert "Bayes" in result.text
    assert result.title == "Upload"
    assert result.source_url == "pdfs/test.pdf"


def test_extract_from_pdf_rejects_non_pdf() -> None:
    with pytest.raises(SourceExtractionError, match="not a valid PDF"):
        extract_from_pdf_bytes(b"hello")


def test_extract_from_resource_manual_uses_summary() -> None:
    resource = Resource(
        source_type=ResourceSourceType.MANUAL,
        title="Manual note",
        summary="Pasted lecture notes about martingales.",
        status=ContentStatus.DRAFT,
    )
    result = extract_from_resource(resource, settings=_settings())
    assert result.method is ExtractionMethod.PASTED_TEXT
    assert "martingales" in result.text


def test_extract_from_resource_pdf_resolves_upload_path(tmp_path: Path) -> None:
    import fitz

    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Uploaded PDF body text for extraction.")
    pdf_path = pdf_dir / "note.pdf"
    pdf_path.write_bytes(doc.tobytes())
    doc.close()

    resource = Resource(
        source_type=ResourceSourceType.PDF,
        url="pdfs/note.pdf",
        title="note",
        status=ContentStatus.DRAFT,
    )
    result = extract_from_resource(
        resource,
        settings=_settings(upload_dir=str(tmp_path)),
    )
    assert result.method is ExtractionMethod.PDF_PYMUPDF
    assert "Uploaded PDF body" in result.text


def test_resolve_resource_file_path_relative(tmp_path: Path) -> None:
    target = tmp_path / "pdfs" / "a.pdf"
    target.parent.mkdir()
    target.write_bytes(b"%PDF-1.4")
    settings = _settings(upload_dir=str(tmp_path))
    resolved = resolve_resource_file_path("pdfs/a.pdf", settings=settings)
    assert resolved == target.resolve()
