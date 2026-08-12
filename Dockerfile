# ---------------------------------------------------------------------------
# Stage 1 - build the React frontend
# ---------------------------------------------------------------------------
FROM node:22-alpine AS frontend

WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# ---------------------------------------------------------------------------
# Stage 2 - resolve and install the Python dependencies with uv
# ---------------------------------------------------------------------------
FROM python:3.13-slim AS backend

COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app
COPY pyproject.toml uv.lock README.md LICENSE ./
COPY backend/wmf_scraper/ ./backend/wmf_scraper/
# --frozen fails the build if uv.lock is out of date with pyproject.toml.
# --no-editable installs the package into site-packages, so the runtime stage
# only needs the virtualenv.
RUN uv sync --frozen --no-dev --no-editable

# ---------------------------------------------------------------------------
# Stage 3 - runtime
# ---------------------------------------------------------------------------
FROM python:3.13-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    STATIC_DIR=/app/static \
    DATABASE_PATH=/data/wmf_scraper.db

RUN groupadd --system app && useradd --system --gid app --home-dir /app app

WORKDIR /app
COPY --from=backend --chown=app:app /app/.venv /app/.venv
COPY --from=frontend --chown=app:app /build/dist /app/static

# Mount point for the Fly volume holding the SQLite database.
RUN mkdir -p /data && chown app:app /data

USER app
EXPOSE 8000

CMD ["uvicorn", "wmf_scraper.main:app", "--host", "0.0.0.0", "--port", "8000"]
