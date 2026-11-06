"""FastAPI application factory."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.api.vectorize import router as vectorize_router
from app.core.config import get_settings

settings = get_settings()

# Rate limiter — keyed on client IP
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure temp directory exists on startup."""
    os.makedirs(settings.TEMP_DIR, exist_ok=True)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        docs_url="/docs" if settings.DEBUG else None,   # Hide Swagger in production
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # ── Middleware ────────────────────────────────────────────────────────────

    # Trusted host (prevents Host-header injection)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.TRUSTED_HOSTS)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=False,         # No cookies / credentials needed
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Accept"],
        expose_headers=["Content-Disposition", "X-File-Hash"],
    )

    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(vectorize_router, prefix=settings.API_PREFIX)

    return app


app = create_app()
