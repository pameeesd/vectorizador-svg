"""Security utilities: input validation, file type checking, and sanitization."""

import hashlib
import io
import os
import re
import unicodedata
from pathlib import Path
from typing import Tuple

from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings

settings = get_settings()

# Magic bytes for allowed image formats
_MAGIC_BYTES: dict[str, bytes] = {
    "image/png": b"\x89PNG",
    "image/jpeg": b"\xff\xd8\xff",
    "image/webp": b"RIFF",
    "image/gif": b"GIF8",
    "image/bmp": b"BM",
}


def _detect_mime_from_magic(header: bytes) -> str | None:
    """Return MIME type based on file magic bytes, or None if unrecognised."""
    for mime, magic in _MAGIC_BYTES.items():
        if header[: len(magic)] == magic:
            # Additional check for WebP (RIFF....WEBP)
            if mime == "image/webp" and header[8:12] != b"WEBP":
                continue
            return mime
    return None


async def validate_upload(file: UploadFile) -> Tuple[bytes, str]:
    """
    Validate an uploaded file for type, size, and content safety.

    Returns the raw file bytes and detected MIME type.
    Raises HTTPException on any validation failure.
    """
    # 1. Read up to MAX_UPLOAD_SIZE_MB + 1 byte to detect oversized files
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    raw = await file.read(max_bytes + 1)

    if len(raw) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB} MB.",
        )

    if len(raw) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    # 2. Verify real MIME type via magic bytes (do NOT trust Content-Type header alone)
    detected_mime = _detect_mime_from_magic(raw[:16])
    if detected_mime is None or detected_mime not in settings.ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Unsupported file type. Allowed types: "
                f"{', '.join(settings.ALLOWED_CONTENT_TYPES)}."
            ),
        )

    # 3. Cross-check against declared Content-Type (allow image/jpg alias)
    declared = (file.content_type or "").lower().replace("image/jpg", "image/jpeg")
    if declared and declared not in settings.ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Content-Type header does not match an allowed image type.",
        )

    return raw, detected_mime


def sanitize_filename(name: str) -> str:
    """
    Return a filesystem-safe filename derived from *name*.

    - Normalises Unicode to ASCII (NFKD)
    - Strips path separators and dangerous characters
    - Limits length to 100 characters
    """
    # Normalise unicode
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")

    # Remove path traversal characters and null bytes
    name = re.sub(r"[^\w\s\-.]", "", name)
    name = re.sub(r"\.\.", "", name)  # prevent ../
    name = name.strip(". ")

    # Replace spaces with underscores
    name = re.sub(r"\s+", "_", name)

    # Limit length (keep extension)
    stem = Path(name).stem[:90]
    suffix = Path(name).suffix[:10]
    return f"{stem}{suffix}" if stem else "upload"


def compute_file_hash(data: bytes) -> str:
    """Return SHA-256 hex digest of *data* (used for deduplication / cache keys)."""
    return hashlib.sha256(data).hexdigest()


def safe_temp_path(directory: str, filename: str) -> Path:
    """
    Build an absolute path inside *directory*, asserting no path traversal.

    Raises ValueError if the resolved path escapes the intended directory.
    """
    base = Path(directory).resolve()
    target = (base / filename).resolve()

    if not str(target).startswith(str(base)):
        raise ValueError(f"Path traversal detected: {filename!r}")

    return target
