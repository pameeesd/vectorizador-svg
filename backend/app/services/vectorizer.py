"""Vectorization service: image preprocessing + SVG generation."""

import io
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Tuple

import cv2
import numpy as np
import vtracer

from app.core.config import get_settings

settings = get_settings()

ColorMode = Literal["color", "binary"]
Hierarchical = Literal["stacked", "cutout"]


@dataclass
class VectorizationParams:
    """Parameters controlling the vectorization process."""

    color_mode: ColorMode = "color"
    filter_speckle: int = 4          # Minimum area (px²) of paths to keep
    color_precision: int = 6         # Number of significant bits per channel for clustering
    layer_difference: int = 16       # Minimum luminance difference between layers
    corner_threshold: int = 60       # Corner detection angle (degrees)
    length_threshold: float = 4.0    # Minimum path segment length
    max_iterations: int = 10         # Path simplification iterations
    splice_threshold: int = 45       # Angle below which consecutive segments are merged
    path_precision: int = 8          # Decimal places in SVG path data
    hierarchical: Hierarchical = "stacked"

    @classmethod
    def from_defaults(cls) -> "VectorizationParams":
        s = get_settings()
        return cls(
            color_mode=s.DEFAULT_COLOR_MODE,
            filter_speckle=s.DEFAULT_FILTER_SPECKLE,
            color_precision=s.DEFAULT_COLOR_PRECISION,
            layer_difference=s.DEFAULT_LAYER_DIFFERENCE,
            corner_threshold=s.DEFAULT_CORNER_THRESHOLD,
            length_threshold=s.DEFAULT_LENGTH_THRESHOLD,
            max_iterations=s.DEFAULT_MAX_ITERATIONS,
            splice_threshold=s.DEFAULT_SPLICE_THRESHOLD,
            path_precision=s.DEFAULT_PATH_PRECISION,
        )


class ImageTooLargeError(ValueError):
    """Raised when the input image exceeds the maximum allowed dimensions."""


class VectorizationError(RuntimeError):
    """Raised when the vectorization step fails."""


def _preprocess_image(raw: bytes, color_mode: ColorMode) -> Tuple[bytes, bool]:
    """
    Use OpenCV to clean and normalise the image before tracing.

    Steps:
    1. Decode from memory buffer preserving any alpha channel.
    2. Detect if image genuinely has transparent regions.
    3. Validate dimensions and upscale if too small for tracing.
    4. Denoise and prepare channels while preserving transparency.

    Returns (PNG-encoded bytes suitable for vtracer, has_transparency boolean).
    """
    arr = np.frombuffer(raw, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)

    if img is None:
        raise VectorizationError("Could not decode image. File may be corrupt.")

    has_transparency = False
    if img.ndim == 3 and img.shape[2] == 4:
        alpha = img[:, :, 3]
        # Image genuinely has transparency if any pixel has alpha < 250
        if np.any(alpha < 250):
            has_transparency = True
            # Clean up anti-aliasing edge artifacts on transparency
            clean_alpha = np.where(alpha < 15, 0, alpha)
            img[:, :, 3] = clean_alpha
            # Where transparent, zero out RGB values to prevent color fringes
            img[clean_alpha == 0, :3] = 0

    h, w = img.shape[:2]
    max_dim = settings.MAX_IMAGE_DIMENSION
    if h > max_dim or w > max_dim:
        raise ImageTooLargeError(
            f"Image dimensions ({w}×{h}) exceed the maximum allowed ({max_dim}px per side)."
        )

    # Upscale tiny images to improve tracing quality (min 256px on shortest side)
    min_side = min(h, w)
    if min_side < 256:
        scale = 256 / min_side
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_LANCZOS4)

    if color_mode == "binary":
        if has_transparency:
            alpha = img[:, :, 3]
            gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2GRAY)
            gray = cv2.bilateralFilter(gray, d=5, sigmaColor=75, sigmaSpace=75)
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # Combine binary image with original transparency mask
            output_img = cv2.merge([binary, binary, binary, alpha])
        else:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
            gray = cv2.bilateralFilter(gray, d=5, sigmaColor=75, sigmaSpace=75)
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            output_img = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    else:
        if has_transparency:
            # Preserve 4-channel BGRA. Apply bilateral filter only on color channels
            bgr = img[:, :, :3]
            alpha = img[:, :, 3]
            bgr_filtered = cv2.bilateralFilter(bgr, d=5, sigmaColor=50, sigmaSpace=50)
            output_img = cv2.merge([bgr_filtered, alpha])
        else:
            if img.ndim == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            elif img.ndim == 3 and img.shape[2] == 4:
                # 4 channels but 100% opaque
                img = img[:, :, :3]
            output_img = cv2.bilateralFilter(img, d=5, sigmaColor=50, sigmaSpace=50)

    success, buf = cv2.imencode(".png", output_img)
    if not success:
        raise VectorizationError("Failed to encode preprocessed image.")

    return buf.tobytes(), has_transparency


def _clean_svg_background(svg_content: str, has_transparency: bool) -> str:
    """If original image was transparent, ensure no unwanted full-canvas background rect remains."""
    if not has_transparency:
        return svg_content

    # Remove any <rect ...> that covers full canvas with a solid white or black background
    svg_content = re.sub(
        r'<rect\s+[^>]*?(?:width="100%"|fill="#ffffff"|fill="#fff"|fill="white")[^>]*?>\s*',
        '',
        svg_content,
        flags=re.IGNORECASE,
        count=1
    )
    return svg_content


def vectorize(raw_bytes: bytes, params: VectorizationParams) -> str:
    """
    Vectorize raw image bytes and return the resulting SVG as a string.

    Uses a secure temporary directory; all temp files are cleaned up automatically.
    """
    preprocessed, has_transparency = _preprocess_image(raw_bytes, params.color_mode)

    with tempfile.TemporaryDirectory(prefix="vec_", dir=settings.TEMP_DIR) as tmp:
        input_path = os.path.join(tmp, "input.png")
        output_path = os.path.join(tmp, "output.svg")

        # Write preprocessed image to temp file
        Path(input_path).write_bytes(preprocessed)

        try:
            vtracer.convert_image_to_svg_py(
                image_path=input_path,
                out_path=output_path,
                colormode=params.color_mode,
                hierarchical=params.hierarchical,
                mode="spline",
                filter_speckle=params.filter_speckle,
                color_precision=params.color_precision,
                layer_difference=params.layer_difference,
                corner_threshold=params.corner_threshold,
                length_threshold=params.length_threshold,
                max_iterations=params.max_iterations,
                splice_threshold=params.splice_threshold,
                path_precision=params.path_precision,
            )
        except Exception as exc:
            raise VectorizationError(f"vtracer failed: {exc}") from exc

        svg_path = Path(output_path)
        if not svg_path.exists() or svg_path.stat().st_size == 0:
            raise VectorizationError("Vectorization produced an empty result.")

        svg_text = svg_path.read_text(encoding="utf-8")
        return _clean_svg_background(svg_text, has_transparency)
