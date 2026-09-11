# Multi-stage / Production-ready Python Dockerfile
FROM python:3.12-slim AS base

# Prevent python from writing pyc files and enable unbuffered output for log streaming
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    UPLOAD_DIR=/data/uploads \
    CHROMA_PERSIST_DIRECTORY=/data/vector_store

WORKDIR /app

# Install minimal system dependencies (curl for container healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create volume mount directories for persistent storage
RUN mkdir -p /data/uploads /data/vector_store

# Copy application source
COPY . .

# Expose container network port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/ || exit 1

# Start production server with environment variable port binding
CMD ["sh", "-c", "uvicorn main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000}"]
