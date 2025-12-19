FROM python:3.9-slim

# Create a non-root user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

WORKDIR /app

# Copy requirements and install dependencies
COPY services/usermanagement/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy common library
COPY common /app/common

# Copy service code
COPY services/usermanagement/app /app/app

# Copy Gunicorn config and WSGI entry point
COPY services/usermanagement/gunicorn_config.py /app/gunicorn_config.py
COPY services/usermanagement/wsgi.py /app/wsgi.py

# Create log directory and set permissions before switching user
RUN mkdir -p /app/logs/usermanagement && \
    chown -R appuser:appuser /app

ENV PYTHONPATH=/app

# Switch to non-root user
USER appuser

EXPOSE 9091

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:9091/health', timeout=5)" || exit 1

# Use Gunicorn for production (multi-worker, handles 1000-2000 req/sec)
CMD ["python", "-m", "gunicorn", "--config", "gunicorn_config.py", "wsgi:application"]
