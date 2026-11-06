"""Vectorization API router."""

import os
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response

from app.core.config import Settings, get_settings
from app.core.security import compute_file_hash, sanitize_filename, validate_upload
from app.services.vectorizer import (
    ImageTooLargeError,
    VectorizationError,
    VectorizationParams,
    vectorize,
)

router = APIRouter(prefix="/vectorize", tags=["vectorization"])


def _params_from_form(
    color_mode: str = Form("color", description="'color' or 'binary'"),
    filter_speckle: int = Form(4, ge=0, le=100),
    color_precision: int = Form(6, ge=1, le=8),
    layer_difference: int = Form(16, ge=1, le=256),
    corner_threshold: int = Form(60, ge=1, le=180),
    length_threshold: float = Form(4.0, ge=0.1, le=10.0),
    max_iterations: int = Form(10, ge=1, le=50),
    splice_threshold: int = Form(45, ge=1, le=180),
    path_precision: int = Form(8, ge=1, le=16),
) -> VectorizationParams:
    if color_mode not in {"color", "binary"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="color_mode must be 'color' or 'binary'.",
        )
    return VectorizationParams(
        color_mode=color_mode,  # type: ignore[arg-type]
        filter_speckle=filter_speckle,
        color_precision=color_precision,
        layer_difference=layer_difference,
        corner_threshold=corner_threshold,
        length_threshold=length_threshold,
        max_iterations=max_iterations,
        splice_threshold=splice_threshold,
        path_precision=path_precision,
    )


@router.post(
    "",
    summary="Vectorize an image",
    description=(
        "Upload a raster image (PNG, JPEG, WebP, GIF, BMP) and receive an SVG vector file. "
        "Optionally tune the vectorization parameters via form fields."
    ),
    response_class=Response,
    responses={
        200: {
            "content": {"image/svg+xml": {}},
            "description": "SVG vector file.",
        },
        400: {"description": "Bad request / empty file."},
        413: {"description": "File too large."},
        415: {"description": "Unsupported media type."},
        422: {"description": "Invalid parameters."},
        500: {"description": "Vectorization failed."},
    },
)
async def vectorize_image(
    file: UploadFile = File(..., description="Raster image to vectorize."),
    params: VectorizationParams = Depends(_params_from_form),
    settings: Settings = Depends(get_settings),
) -> Response:
    """Validate, preprocess, and vectorize the uploaded image."""
    # Ensure temp directory exists
    os.makedirs(settings.TEMP_DIR, exist_ok=True)

    # Validate & read file
    raw_bytes, _mime = await validate_upload(file)

    # Derive a safe output filename for the Content-Disposition header
    original_stem = Path(sanitize_filename(file.filename or "image")).stem
    svg_filename = f"{original_stem}.svg"

    try:
        svg_content = vectorize(raw_bytes, params)
    except ImageTooLargeError as exc:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=str(exc))
    except VectorizationError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    return Response(
        content=svg_content.encode("utf-8"),
        media_type="image/svg+xml",
        headers={
            "Content-Disposition": f'attachment; filename="{svg_filename}"',
            "X-File-Hash": compute_file_hash(raw_bytes),
            "Cache-Control": "no-store",
        },
    )


@router.get(
    "/health",
    summary="Health check",
    tags=["health"],
)
async def health() -> dict:
    """Return service liveness status."""
    return {"status": "ok", "service": "VectorizadorSVG"}
