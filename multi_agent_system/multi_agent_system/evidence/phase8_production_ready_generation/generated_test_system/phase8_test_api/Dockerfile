# Generated Production Dockerfile for phase8_test_api
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for production
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create config and logs directories
RUN mkdir -p config logs

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose ports (if any API endpoints)
EXPOSE 8080

# Health check for production deployment
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run with Gunicorn WSGI server for production
CMD ["gunicorn", "--config", "gunicorn.conf.py", "main:app"]
