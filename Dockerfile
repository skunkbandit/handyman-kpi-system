# Build stage
FROM python:3.10-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY kpi-system/requirements.txt .

# Install dependencies into a virtual environment
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Production stage
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /app/venv /app/venv

# Set environment variables
ENV PATH="/app/venv/bin:$PATH"
ENV FLASK_APP=backend.run
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Create a non-root user to run the application
RUN groupadd -r kpiuser && useradd -r -g kpiuser kpiuser

# Copy application code
COPY kpi-system/backend /app/backend
COPY kpi-system/database /app/database
COPY kpi-system/frontend/dist /app/frontend/dist
COPY scripts /app/scripts

# Create necessary directories
RUN mkdir -p /app/instance/backups /app/instance/logs /app/instance/temp /app/instance/database

# Set correct permissions
RUN chown -R kpiuser:kpiuser /app/instance && \
    chmod -R 755 /app

# Expose port
EXPOSE 5000

# Switch to non-root user
USER kpiuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "backend.run:app"]
