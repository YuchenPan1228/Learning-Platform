from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from app.config import Settings, get_settings

_PDF_CONTENT_TYPES = frozenset(
    {
        "application/pdf",
        "application/x-pdf",
        "application/octet-stream",
    }
)
_FILENAME_SAFE = re.compile(r"[^A-Za-z0-9._-]+")


class PdfUploadError(ValueError):
    """Raised when an uploaded PDF cannot be accepted."""


@dataclass(frozen=True, slots=True)
class StoredPdfUpload:
    absolute_path: Path
    relative_path: str
    original_filename: str
    content_sha256: str
    size_bytes: int


def store_pdf_upload(
    *,
    filename: str | None,
    content_type: str | None,
    content: bytes,
    settings: Settings | None = None,
) -> StoredPdfUpload:
    if not content:
        raise PdfUploadError("PDF file is empty")

    resolved = settings or get_settings()
    max_bytes = resolved.pdf_upload_max_bytes
    if len(content) > max_bytes:
        raise PdfUploadError(
            f"PDF exceeds max upload size of {max_bytes // (1024 * 1024)} MB",
        )

    if content_type and content_type.split(";")[0].strip().lower() not in _PDF_CONTENT_TYPES:
        raise PdfUploadError(f"unsupported content type '{content_type}'")

    original_name = _safe_filename(filename)
    if not original_name.lower().endswith(".pdf"):
        raise PdfUploadError("uploaded file must be a PDF")

    if not content.startswith(b"%PDF"):
        raise PdfUploadError("uploaded file is not a valid PDF")

    digest = sha256(content).hexdigest()
    relative_name = f"{uuid.uuid4().hex}_{original_name}"
    absolute_path = _pdf_upload_dir(resolved) / relative_name
    absolute_path.write_bytes(content)

    return StoredPdfUpload(
        absolute_path=absolute_path,
        relative_path=f"pdfs/{relative_name}",
        original_filename=original_name,
        content_sha256=digest,
        size_bytes=len(content),
    )


def _pdf_upload_dir(settings: Settings) -> Path:
    path = Path(settings.upload_dir).expanduser()
    if not path.is_absolute():
        path = settings.repo_root / path
    pdf_dir = path / "pdfs"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    return pdf_dir


def _safe_filename(filename: str | None) -> str:
    raw = (filename or "upload.pdf").strip().replace("\\", "/").split("/")[-1]
    cleaned = _FILENAME_SAFE.sub("_", raw).strip("._")
    if not cleaned:
        return "upload.pdf"
    if not cleaned.lower().endswith(".pdf"):
        cleaned = f"{cleaned}.pdf"
    return cleaned[:180]
