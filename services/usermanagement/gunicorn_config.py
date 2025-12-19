"""
Gunicorn configuration for User Management Service
Optimized for 1000-2000 requests/second
"""
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('USER_MANAGEMENT_SERVER_PORT', '9091')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('GUNICORN_WORKERS', '4'))
worker_class = 'sync'
worker_connections = 1000

# Threading
threads = int(os.getenv('GUNICORN_THREADS', '2'))

# Timeouts
timeout = 30
keepalive = 5
graceful_timeout = 30

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'usermanagement-service'

# Server mechanics
daemon = False
preload_app = True

# Performance tuning
max_requests = 1000
max_requests_jitter = 50

