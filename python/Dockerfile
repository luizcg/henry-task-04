# Multi-stage Dockerfile for Contract Comparison Agent
# Supports both API and Worker targets

# ============================================
# Base stage - common dependencies
# ============================================
FROM python:3.10-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install package in editable mode
RUN pip install -e .

# ============================================
# API target - FastAPI server
# ============================================
FROM base as api

EXPOSE 8080

ENV API_HOST=0.0.0.0
ENV API_PORT=8080

CMD ["uvicorn", "src.adapters.rest_api:app", "--host", "0.0.0.0", "--port", "8080"]

# ============================================
# Worker target - RabbitMQ consumer
# ============================================
FROM base as worker

CMD ["python", "-m", "worker"]

# ============================================
# CLI target - for running CLI commands
# ============================================
FROM base as cli

ENTRYPOINT ["contract-agent"]
CMD ["--help"]
