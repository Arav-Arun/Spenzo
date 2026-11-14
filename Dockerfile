# The WhatsApp bot and dashboard API (Render).
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app

# Dependencies first so they cache between deploys
COPY pyproject.toml ./
RUN uv sync --no-dev --no-install-project

COPY server ./server

EXPOSE 8000
CMD ["sh", "-c", "uv run --no-dev uvicorn server.bot:app --host 0.0.0.0 --port ${PORT:-8000}"]
