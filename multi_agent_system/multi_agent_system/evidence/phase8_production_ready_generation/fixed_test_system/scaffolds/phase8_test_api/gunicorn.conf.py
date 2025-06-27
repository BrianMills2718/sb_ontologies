#!/usr/bin/env python3
"""
Gunicorn Configuration for phase8_test_api
Production WSGI server configuration
"""
import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', 8080)}"
backlog = 2048

# Worker processes
workers = int(os.getenv('WEB_CONCURRENCY', multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"  # Use sync workers for better compatibility with Flask
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True
timeout = 30
keepalive = 2

# Restart workers after this many requests, with up to 50 random jitter
max_requests = 1000
max_requests_jitter = 50

# Restart workers after this much time
max_worker_age = 0
worker_tmp_dir = None

# Server mechanics
daemon = False
pidfile = "/tmp/phase8_test_api_gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# Logging
errorlog = "-"  # Log to stderr
loglevel = os.getenv('LOG_LEVEL', 'info')
accesslog = "-"  # Log to stdout
access_log_format = '%%(h)s %%(l)s %%(u)s %%(t)s "%%(r)s" %%(s)s %%(b)s "%%(f)s" "%%(a)s" %%(D)s'

# Process naming
proc_name = "phase8_test_api"

# Application
wsgi_module = "main:app"

# SSL (if certificates are provided)
keyfile = os.getenv('SSL_KEYFILE')
certfile = os.getenv('SSL_CERTFILE')

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

def when_ready(server):
    """Called just after the server is started."""
    server.log.info(f"{server.proc_name} server is ready. Listening on: {server.address}")

def worker_int(worker):
    """Called when a worker receives the SIGINT or SIGQUIT signal."""
    worker.log.info(f"Worker {worker.pid} received SIGINT/SIGQUIT")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"Worker ready (pid: {worker.pid})")

def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info(f"{server.proc_name} ready to serve requests")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    worker.log.info(f"Worker {worker.pid} received SIGABRT")

# Graceful timeout for worker shutdown
graceful_timeout = 30

# Environment variables to log
raw_env = [
    'ENVIRONMENT=production',
    'LOG_LEVEL=' + os.getenv('LOG_LEVEL', 'info'),
]

# Health check settings
forwarded_allow_ips = "*"
proxy_allow_ips = "*"
