FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend /app/backend
COPY database /app/database

# Set environment variables
ENV FLASK_APP=backend.run
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Create necessary directories
RUN mkdir -p /app/instance/backups /app/instance/logs /app/instance/temp

# Set permissions
RUN chmod -R 755 /app

# Expose port
EXPOSE 5000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "backend.run:app"]