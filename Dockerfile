# Multi-stage Docker build for BOL OCR Extractor
# Production-ready containerization with security hardening

# Build stage for dependencies
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for build
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt /tmp/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true

# Install system dependencies for OCR and Java
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    default-jre-headless \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create application directory
WORKDIR /app

# Create necessary directories with proper permissions
RUN mkdir -p /app/temp /app/logs /app/data && \
    chown -R appuser:appuser /app

# Copy application files
COPY --chown=appuser:appuser app.py /app/
COPY --chown=appuser:appuser requirements.txt /app/

# Switch to non-root user
USER appuser

# Verify installations
RUN tesseract --version && \
    java -version && \
    python -c "import streamlit; print(f'Streamlit version: {streamlit.__version__}')"

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Expose port
EXPOSE 8501

# Create startup script
COPY --chown=appuser:appuser <<EOF /app/entrypoint.sh
#!/bin/bash
set -e

# Ensure temp directory exists and has proper permissions
mkdir -p /app/temp
chmod 755 /app/temp

# Start Streamlit application
exec streamlit run app.py \
    --server.port=\$STREAMLIT_SERVER_PORT \
    --server.address=\$STREAMLIT_SERVER_ADDRESS \
    --server.headless=\$STREAMLIT_SERVER_HEADLESS \
    --browser.gatherUsageStats=\$STREAMLIT_BROWSER_GATHER_USAGE_STATS \
    --server.enableCORS=\$STREAMLIT_SERVER_ENABLE_CORS \
    --server.enableXsrfProtection=\$STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION
EOF

RUN chmod +x /app/entrypoint.sh

# Use custom entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]