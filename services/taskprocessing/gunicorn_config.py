"""
Gunicorn configuration for Task Processing Service
Optimized for 1000-2000 requests/second
"""
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('TASKPROCESSING_SERVER_PORT', '9092')}"
backlog = 2048

# Worker processes
# Formula: (2 x CPU cores) + 1, but optimized for 1000-2000 req/sec
# Each worker handles ~250-500 req/sec, so 4-8 workers needed
workers = int(os.getenv('GUNICORN_WORKERS', '4'))
worker_class = 'sync'  # Use sync workers for CPU-bound tasks
worker_connections = 1000

# Threading (for I/O-bound operations)
threads = int(os.getenv('GUNICORN_THREADS', '2'))  # 2 threads per worker
# Total concurrent requests = workers × threads = 4 × 2 = 8 per instance

# Timeouts
timeout = 30  # Worker timeout (seconds)
keepalive = 5  # Keep-alive timeout (seconds)
graceful_timeout = 30  # Graceful shutdown timeout

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'taskprocessing-service'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Performance tuning
max_requests = 1000  # Restart worker after this many requests (prevents memory leaks)
max_requests_jitter = 50  # Randomize max_requests to avoid all workers restarting together
preload_app = True  # Load application before forking workers (saves memory)

# Stats
statsd_host = None  # Can be configured for monitoring

