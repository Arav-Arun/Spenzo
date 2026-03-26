# We use Python 3.11-slim as the base image for Render deployments
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy dependency lockfiles first (speeds up caching)
COPY uv.lock pyproject.toml ./

# Sync dependencies - use --no-dev to keep image lean,
# and --python to ensure we match the base image's Python
RUN uv sync --frozen --no-dev --python python3.11

# Copy application source code
COPY . .

# Expose default port (Render will override via $PORT env var)
EXPOSE 8000

# Start the FastAPI bot — reads $PORT from environment (set by Render)
CMD ["sh", "-c", "uv run uvicorn bot:app --host 0.0.0.0 --port ${PORT:-8000}"]
