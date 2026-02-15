# ============================================================
# Stage 1: Install dependencies
# ============================================================
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /install

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install/deps -r requirements.txt


# ============================================================
# Stage 2: Production image
# ============================================================
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && adduser --disabled-password --gecos '' appuser

COPY --from=builder /install/deps /usr/local

WORKDIR /app

ENV FLASK_APP=backend.app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY . .

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 5005

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:5005/health')"

CMD ["gunicorn", "--bind", "0.0.0.0:5005", "--workers", "2", "--threads", "4", \
     "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", \
     "backend.app:app"]
