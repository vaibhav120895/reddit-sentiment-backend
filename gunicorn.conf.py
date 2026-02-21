# Gunicorn configuration for Reddbeat AI - Secure Production
# Enhanced for security and performance

import os

# ============================================================================
# WORKERS & CONCURRENCY
# ============================================================================

# Number of worker processes
# Updated: 4 workers for better concurrency (was 1)
workers = 4

# Threads per worker (handles multiple requests per worker)
# NEW: Adds threading for better I/O handling
threads = 2

# Worker class - sync works for API calls
worker_class = 'sync'

# ============================================================================
# TIMEOUTS
# ============================================================================

# Timeout for worker processes (seconds)
# Each post takes ~2-5 seconds, so 50 posts * 5s = 250s + buffer
timeout = 300  # 5 minutes (KEEP - good for long analyses)

# Graceful timeout (seconds) - time to finish requests before force kill
graceful_timeout = 300  # KEEP - allows long requests to finish

# Keep-alive timeout (seconds)
keepalive = 5  # KEEP - good setting

# ============================================================================
# LOGGING
# ============================================================================

# Access log (all requests)
accesslog = '-'  # Log to stdout (Render displays this)

# Error log
errorlog = '-'  # Log to stderr (Render displays this)

# Log level
loglevel = 'info'  # KEEP - good balance

# ============================================================================
# BINDING
# ============================================================================

# Bind address (Render uses PORT env variable)
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"

# ============================================================================
# SECURITY (NEW)
# ============================================================================

# Limit request line size (prevents DoS)
limit_request_line = 4096

# Limit request header size
limit_request_field_size = 8190

# Max requests per worker before restart (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 50

# ============================================================================
# PERFORMANCE (NEW)
# ============================================================================

# Preload app for faster worker startup
preload_app = False  # False is safer for development

# Worker restart on code changes (development only)
reload = os.environ.get('FLASK_ENV') != 'production'
