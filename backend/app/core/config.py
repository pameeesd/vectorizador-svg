"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App metadata
    APP_NAME: str = "VectorizadorSVG"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "PNG to SVG vectorizer — open source alternative to vectorizer.ai"
    DEBUG: bool = False

    # API
    API_PREFIX: str = "/api/v1"

    # CORS — comma-separated origins in .env, e.g. "http://localhost:3000,https://yourdomain.com"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Upload limits
    MAX_UPLOAD_SIZE_MB: int = 10          # Maximum file size in MB
    MAX_IMAGE_DIMENSION: int = 4096       # Maximum width or height in pixels
    ALLOWED_CONTENT_TYPES: List[str] = [
        "image/png",
        "image/jpeg",
        "image/jpg",
        "image/webp",
        "image/gif",
        "image/bmp",
    ]

    # Vectorization defaults
    DEFAULT_COLOR_MODE: str = "color"     # "color" | "binary"
    DEFAULT_FILTER_SPECKLE: int = 4
    DEFAULT_COLOR_PRECISION: int = 6
    DEFAULT_LAYER_DIFFERENCE: int = 16
    DEFAULT_CORNER_THRESHOLD: int = 60
    DEFAULT_LENGTH_THRESHOLD: float = 4.0
    DEFAULT_MAX_ITERATIONS: int = 10
    DEFAULT_SPLICE_THRESHOLD: int = 45
    DEFAULT_PATH_PRECISION: int = 8

    # Temporary file storage (use a proper object store in production)
    TEMP_DIR: str = "/tmp/vectorizador"
    RESULT_TTL_SECONDS: int = 3600        # 1 hour — clean up generated SVGs after this

    # Rate limiting (requests per minute per IP)
    RATE_LIMIT_PER_MINUTE: int = 20

    # Security
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_USE_32_CHAR_RANDOM_STRING"
    TRUSTED_HOSTS: List[str] = ["localhost", "127.0.0.1"]


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
