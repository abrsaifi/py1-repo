# Multi-stage build: base image with dependencies
FROM python:3.10-slim as builder

WORKDIR /build

# Install system dependencies for heavy packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libopenjp2-7 \
    libtiff-dev \
    libfreetype6-dev \
    libharfbuzz0b \
    libfribidi0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and build wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt


# Final image
FROM python:3.10-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libopenjp2-7 \
    libtiff6 \
    libfreetype6 \
    libharfbuzz0b \
    libfribidi0 \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder and install
COPY --from=builder /build/wheels /wheels
COPY --from=builder /build/requirements.txt .
RUN pip install --no-cache /wheels/*

# Copy application code
COPY . .

# Set environment variables
ENV FLASK_APP=app.main:app \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Create upload directory
RUN mkdir -p /tmp/docpro_uploads

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')" || exit 1

# Run the Flask app via gunicorn (production) or Flask dev server (dev)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "60", "app.main:app"]
