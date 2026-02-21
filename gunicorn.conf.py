# Gunicorn configuration for Reddit Sentiment Backend
# This config sets proper timeouts for long-running Claude API requests

# Timeout for worker processes (seconds)
# Each post takes ~2-5 seconds, so 50 posts * 5s = 250s + buffer
timeout = 300  # 5 minutes

# Graceful timeout (seconds) - time to finish requests before force kill
graceful_timeout = 300

# Keep-alive timeout (seconds)
keepalive = 5

# Number of worker processes
# For CPU-bound work like API calls, 1 worker is sufficient
workers = 1

# Worker class - sync is fine for sequential API calls
worker_class = 'sync'

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
loglevel = 'info'

# Bind address (Render uses PORT env variable)
import os
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
