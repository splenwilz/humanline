# Multi-stage Dockerfile for production-grade FastAPI application
# Stage 1: Build stage with uv for dependency management
FROM python:3.13-slim AS builder

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set environment variables for uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

# Create application directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies into virtual environment
# Use build arg to determine if dev dependencies should be installed
ARG INSTALL_DEV=false
RUN if [ "$INSTALL_DEV" = "true" ] ; then \
        uv sync --frozen --no-install-project ; \
    else \
        uv sync --frozen --no-install-project --no-dev ; \
    fi

# Stage 2: Production runtime stage
FROM python:3.13-slim AS runtime

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    # Required for PostgreSQL client
    libpq5 \
    # Required for health checks
    curl \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r humanline && useradd -r -g humanline humanline

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder --chown=humanline:humanline /app/.venv /app/.venv

# Make sure we use venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY --chown=humanline:humanline . .

# Create directories for logs and uploads with proper permissions
RUN mkdir -p /app/logs /app/uploads && \
    chown -R humanline:humanline /app/logs /app/uploads

# Switch to non-root user
USER humanline

# Expose port
EXPOSE 8000

# Health check - use PORT environment variable
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Default command - use Render's PORT environment variable
# Render automatically sets $PORT, fallback to 8000 for local development
CMD ["sh", "-c", "if [ \"$ENVIRONMENT\" = \"development\" ]; then uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --reload --log-level debug; else uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2; fi"]
