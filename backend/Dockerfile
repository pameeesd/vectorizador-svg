FROM python:3.12-slim AS base

# Security: run as non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup -s /bin/false appuser

WORKDIR /app

# Install system dependencies (OpenCV headless needs libglib2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0t64 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create temp directory and set permissions
RUN mkdir -p /tmp/vectorizador && chown appuser:appgroup /tmp/vectorizador

# Switch to non-root user
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/vectorize/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
