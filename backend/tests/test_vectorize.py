"""Integration tests for the vectorization API."""

import io
import os
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from app.main import app

client = TestClient(app)


def _make_png(width: int = 64, height: int = 64, color: bool = True) -> bytes:
    """Generate a simple in-memory PNG for testing."""
    if color:
        img = Image.new("RGB", (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.ellipse([10, 10, width - 10, height - 10], fill=(255, 0, 0))
    else:
        img = Image.new("L", (width, height), color=255)
        draw = ImageDraw.Draw(img)
        draw.ellipse([10, 10, width - 10, height - 10], fill=0)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ── Health ────────────────────────────────────────────────────────────────────

def test_health_check():
    response = client.get("/api/v1/vectorize/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ── Happy-path vectorization ──────────────────────────────────────────────────

@pytest.mark.parametrize("color_mode", ["color", "binary"])
def test_vectorize_png(color_mode: str, tmp_path, monkeypatch):
    monkeypatch.setenv("TEMP_DIR", str(tmp_path))
    png_bytes = _make_png(color=color_mode == "color")
    response = client.post(
        "/api/v1/vectorize",
        files={"file": ("test.png", png_bytes, "image/png")},
        data={"color_mode": color_mode},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")
    assert b"<svg" in response.content


# ── Security / validation edge cases ─────────────────────────────────────────

def test_reject_empty_file():
    response = client.post(
        "/api/v1/vectorize",
        files={"file": ("empty.png", b"", "image/png")},
    )
    assert response.status_code == 400


def test_reject_non_image():
    fake_pdf = b"%PDF-1.4 fake content"
    response = client.post(
        "/api/v1/vectorize",
        files={"file": ("evil.pdf", fake_pdf, "application/pdf")},
    )
    assert response.status_code == 415


def test_reject_spoofed_content_type():
    """A file with PNG magic bytes but wrong Content-Type should still be rejected if CT is wrong."""
    png_bytes = _make_png()
    response = client.post(
        "/api/v1/vectorize",
        files={"file": ("disguised.exe", png_bytes, "application/octet-stream")},
    )
    # Content-Type is not in allowed list → 415
    assert response.status_code == 415


def test_invalid_color_mode():
    png_bytes = _make_png()
    response = client.post(
        "/api/v1/vectorize",
        files={"file": ("test.png", png_bytes, "image/png")},
        data={"color_mode": "rainbow"},
    )
    assert response.status_code == 422
