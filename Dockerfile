# Multi-stage Dockerfile for AI Design Suite
# Enhanced for production deployment with comprehensive engineering capabilities

# Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    pkg-config \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.container.txt ./requirements.txt

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r aidesign && useradd -r -g aidesign aidesign

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p ./temp ./outputs ./sessions ./logs ./uploads && \
    chown -R aidesign:aidesign /app

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production
ENV LLM_PROVIDER=mock
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV HOST=0.0.0.0
ENV PORT=8000

# Switch to non-root user
USER aidesign

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "app.py", "--host", "0.0.0.0", "--port", "8000"]

# Labels for metadata
LABEL maintainer="AI Design Suite Team"
LABEL version="1.0.0"
LABEL description="Comprehensive AI-powered engineering design suite with 15+ specialized agents"
LABEL org.opencontainers.image.title="AI Design Suite"
LABEL org.opencontainers.image.description="Multi-agent engineering design automation platform"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.vendor="AI Design Suite"