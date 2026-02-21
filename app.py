"""
Reddbeat AI - Secure Production Backend
Enterprise-grade security implementation following OWASP Top 10
"""

from flask import Flask, request, jsonify, make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from werkzeug.exceptions import HTTPException
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from pathlib import Path
import secrets
import hashlib
from datetime import datetime
import json

from reddit_client import fetch_reddit_posts
from sentiment_analyzer import analyze_posts_multi_model

# ============================================================================
# ENVIRONMENT & CONFIGURATION
# ============================================================================

if Path('key.env').exists():
    load_dotenv('key.env')
    print("📁 Loaded from key.env (local)")
else:
    load_dotenv()
    print("🌐 Loaded from environment variables (production)")

# ============================================================================
# SECURE LOGGING (No sensitive data in logs)
# ============================================================================

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure rotating file handler (prevents disk fill)
file_handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
))

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s'
))

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)

# Suppress sensitive library logs
logging.getLogger('anthropic').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

# ============================================================================
# FLASK APP INITIALIZATION
# ============================================================================

app = Flask(__name__)

# SECURITY: Disable debug mode in production
app.config['DEBUG'] = os.getenv('FLASK_ENV') != 'production'

# SECURITY: Session security
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # No JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection

# SECURITY: Prevent information disclosure
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['PROPAGATE_EXCEPTIONS'] = False

# SECURITY: Max content length (10MB) - prevents DoS
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

# ============================================================================
# SECURITY HEADERS - OWASP Best Practices
# ============================================================================

csp = {
    'default-src': "'self'",
    'script-src': "'self'",
    'style-src': "'self'",
    'img-src': "'self' data: https:",
    'font-src': "'self'",
    'connect-src': "'self'",
    'frame-ancestors': "'none'",
}

# Conditional HTTPS enforcement (only in production)
if os.getenv('FLASK_ENV') == 'production':
    talisman = Talisman(
        app,
        content_security_policy=csp,
        force_https=True,
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,  # 1 year
        content_security_policy_nonce_in=['script-src']
    )
else:
    # Development mode: relaxed CSP
    talisman = Talisman(
        app,
        content_security_policy=csp,
        force_https=False,
        content_security_policy_nonce_in=['script-src']
    )

# ============================================================================
# RATE LIMITING - DDoS Protection
# ============================================================================

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per hour"],  # Global rate limit
    storage_uri="memory://",
    strategy="fixed-window"
)

# ============================================================================
# INPUT VALIDATION & SANITIZATION
# ============================================================================

def validate_and_sanitize_input(data):
    """
    Comprehensive input validation and sanitization
    Prevents: SQL Injection, XSS, Command Injection, Path Traversal
    
    Returns: (is_valid, error_message, sanitized_data)
    """
    if not data:
        return False, "No data provided", None
    
    if not isinstance(data, dict):
        return False, "Invalid data format", None
    
    # Validate keywords
    keywords = data.get('keywords', '').strip()
    if not keywords:
        return False, "Keywords are required", None
    
    # SECURITY: Length validation (DoS prevention)
    if len(keywords) > 200:
        return False, "Keywords too long (max 200 characters)", None
    
    # SECURITY: Sanitize dangerous characters (XSS, Injection prevention)
    dangerous_chars = ['<', '>', '"', "'", '\\', '/', '`', '{', '}', ';', '|', '&', '$', '(', ')']
    sanitized_keywords = keywords
    for char in dangerous_chars:
        sanitized_keywords = sanitized_keywords.replace(char, '')
    
    # SECURITY: Prevent null bytes (injection attacks)
    if '\x00' in keywords:
        return False, "Invalid characters in keywords", None
    
    # Validate limit parameter
    try:
        limit = int(data.get('limit', 5))
        if limit < 1:
            return False, "Limit must be at least 1", None
        if limit > 50:
            return False, "Limit cannot exceed 50 (performance restriction)", None
    except (ValueError, TypeError):
        return False, "Invalid limit value - must be an integer", None
    
    # Validate sort parameter (whitelist approach)
    sort = data.get('sort', 'hot')
    allowed_sorts = ['hot', 'new', 'top', 'relevance']
    if sort not in allowed_sorts:
        return False, f"Invalid sort parameter. Allowed: {', '.join(allowed_sorts)}", None
    
    sanitized_data = {
        'keywords': sanitized_keywords,
        'limit': limit,
        'sort': sort
    }
    
    return True, None, sanitized_data


def sanitize_output_data(posts):
    """
    Sanitize output data to prevent information leakage
    Removes sensitive fields and limits data exposure
    """
    if not posts:
        return []
    
    sanitized = []
    for post in posts:
        # Only include safe, necessary fields
        safe_post = {
            'title': str(post.get('title', ''))[:200],  # Limit title length
            'text': str(post.get('text', ''))[:500],    # Limit text length
            'url': str(post.get('url', '')),
            'score': int(post.get('score', 0)),
            'comments': int(post.get('comments', 0)),
            'subreddit': str(post.get('subreddit', '')),
            'claude_sentiment': str(post.get('claude_sentiment', 'Neutral')),
            'claude_score': float(post.get('claude_score', 0)),
        }
        sanitized.append(safe_post)
    
    return sanitized

# ============================================================================
# SECURITY MIDDLEWARE
# ============================================================================

@app.before_request
def security_checks():
    """
    Pre-request security validations
    """
    # SECURITY: Request logging (audit trail)
    client_ip = get_remote_address()
    logger.info(f"Request: {request.method} {request.path} from {client_ip}")
    
    # SECURITY: Validate User-Agent (bot detection)
    user_agent = request.headers.get('User-Agent', '')
    if not user_agent or len(user_agent) < 10:
        logger.warning(f"Suspicious request: Invalid User-Agent from {client_ip}")
        return jsonify({'error': 'Invalid request'}), 400
    
    # SECURITY: Block known malicious user agents
    malicious_agents = ['sqlmap', 'nikto', 'nmap', 'masscan', 'nessus']
    if any(agent in user_agent.lower() for agent in malicious_agents):
        logger.warning(f"Blocked malicious user agent: {user_agent[:50]} from {client_ip}")
        return jsonify({'error': 'Access denied'}), 403
    
    # SECURITY: Content-Type validation for POST requests
    if request.method == 'POST' and request.path != '/health':
        content_type = request.headers.get('Content-Type', '')
        if 'application/json' not in content_type:
            return jsonify({'error': 'Content-Type must be application/json'}), 415
    
    # Handle CORS preflight
    if request.method == "OPTIONS":
        response = make_response()
        allowed_origin = os.getenv('ALLOWED_ORIGIN', '*')
        response.headers["Access-Control-Allow-Origin"] = allowed_origin
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Max-Age"] = "3600"
        return response, 200


@app.after_request
def add_security_headers(response):
    """
    Add comprehensive security headers to all responses
    Implements OWASP security header recommendations
    """
    # CORS headers (configurable for production)
    allowed_origin = os.getenv('ALLOWED_ORIGIN', '*')
    response.headers["Access-Control-Allow-Origin"] = allowed_origin
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Credentials"] = "false"
    
    # SECURITY: Prevent MIME-type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # SECURITY: Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    
    # SECURITY: XSS protection (legacy browsers)
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # SECURITY: Referrer policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # SECURITY: Permissions policy
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    # SECURITY: Remove server version information
    response.headers.pop('Server', None)
    response.headers.pop('X-Powered-By', None)
    
    # SECURITY: Cache control for sensitive endpoints
    if request.path.startswith('/api/'):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    
    return response

# ============================================================================
# ERROR HANDLERS - Prevent Information Disclosure
# ============================================================================

@app.errorhandler(400)
def bad_request(e):
    """Bad Request"""
    logger.warning(f"400 Bad Request: {request.path}")
    return jsonify({'error': 'Invalid request'}), 400


@app.errorhandler(404)
def not_found(e):
    """Not Found - don't reveal valid endpoints"""
    logger.warning(f"404 Not Found: {request.path}")
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    """Method Not Allowed"""
    return jsonify({'error': 'Method not allowed'}), 405


@app.errorhandler(413)
def request_entity_too_large(e):
    """Payload Too Large"""
    logger.warning(f"413 Payload too large from {get_remote_address()}")
    return jsonify({'error': 'Request payload too large'}), 413


@app.errorhandler(415)
def unsupported_media_type(e):
    """Unsupported Media Type"""
    return jsonify({'error': 'Unsupported media type'}), 415


@app.errorhandler(429)
def ratelimit_handler(e):
    """Rate Limit Exceeded"""
    logger.warning(f"Rate limit exceeded: {get_remote_address()}")
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please try again later.',
        'retry_after': '1 hour'
    }), 429


@app.errorhandler(500)
def internal_error(e):
    """Internal Server Error - never expose details"""
    logger.error(f"500 Internal Error: {str(e)}", exc_info=True)
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred. Please try again later.'
    }), 500


@app.errorhandler(Exception)
def handle_unexpected_error(e):
    """
    Catch-all handler for unexpected errors
    SECURITY: Never expose stack traces or internal details
    """
    logger.error(f"Unexpected error: {str(e)}", exc_info=True)
    
    # Log full error for debugging but don't send to client
    return jsonify({
        'error': 'An unexpected error occurred',
        'timestamp': datetime.utcnow().isoformat(),
        'reference': hashlib.sha256(str(e).encode()).hexdigest()[:8]  # Error reference ID
    }), 500

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
@limiter.limit("60 per minute")
def health_check():
    """
    Health check endpoint with minimal information disclosure
    """
    try:
        # Check if critical dependencies are available
        api_key = os.getenv('ANTHROPIC_API_KEY')
        
        return jsonify({
            'status': 'healthy',
            'service': 'Reddbeat AI',
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat(),
            'claude_available': bool(api_key and len(api_key) > 20)
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat()
        }), 503


@app.route('/api/analyze', methods=['POST'])
@limiter.limit("20 per minute")  # Stricter limit for expensive endpoint
def analyze_sentiment():
    """
    Main sentiment analysis endpoint
    SECURITY: Input validation, output sanitization, rate limiting
    """
    request_id = hashlib.sha256(
        f"{get_remote_address()}{datetime.utcnow()}".encode()
    ).hexdigest()[:12]
    
    try:
        # Parse JSON with error handling
        try:
            data = request.get_json(force=False, silent=False)
        except Exception as e:
            logger.warning(f"[{request_id}] Invalid JSON: {str(e)}")
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        # Validate and sanitize input
        is_valid, error_msg, sanitized_data = validate_and_sanitize_input(data)
        if not is_valid:
            logger.warning(f"[{request_id}] Validation failed: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        keywords = sanitized_data['keywords']
        limit = sanitized_data['limit']
        sort = sanitized_data['sort']
        
        logger.info(f"[{request_id}] Analysis: keywords='{keywords[:50]}', limit={limit}, sort={sort}")
        
        # Fetch Reddit posts
        all_posts = fetch_reddit_posts(keywords, sort, limit)
        
        if not all_posts:
            logger.info(f"[{request_id}] No posts found")
            return jsonify({
                'error': 'No posts found for the given query',
                'query': keywords
            }), 404
        
        logger.info(f"[{request_id}] Fetched {len(all_posts)} posts")
        
        # Analyze sentiment
        analyzed_posts = analyze_posts_multi_model(all_posts)
        
        # Calculate statistics
        stats = calculate_stats(analyzed_posts)
        
        # Sanitize output (prevent data leakage)
        sanitized_posts = sanitize_output_data(analyzed_posts)
        
        logger.info(f"[{request_id}] Analysis complete: {len(sanitized_posts)} posts analyzed")
        
        return jsonify({
            'success': True,
            'request_id': request_id,
            'stats': stats,
            'posts': sanitized_posts,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except ValueError as e:
        logger.error(f"[{request_id}] Validation error: {str(e)}")
        return jsonify({'error': 'Invalid input data'}), 400
        
    except Exception as e:
        logger.error(f"[{request_id}] Analysis failed: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Analysis failed',
            'message': 'Please try again later',
            'request_id': request_id
        }), 500


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_stats(posts):
    """
    Calculate sentiment statistics from analyzed posts
    """
    if not posts or len(posts) == 0:
        return {
            'total_posts': 0,
            'avg_sentiment': 0,
            'positive_pct': 0,
            'negative_pct': 0,
            'neutral_pct': 0
        }
    
    total = len(posts)
    sentiments = [p.get('claude_sentiment', 'Neutral') for p in posts]
    scores = [p.get('claude_score', 0) for p in posts]
    
    positive = sum(1 for s in sentiments if s == 'Positive')
    negative = sum(1 for s in sentiments if s == 'Negative')
    neutral = sum(1 for s in sentiments if s == 'Neutral')
    
    return {
        'total_posts': total,
        'avg_sentiment': round(sum(scores) / len(scores), 3) if scores else 0,
        'positive_pct': round((positive / total) * 100, 1),
        'negative_pct': round((negative / total) * 100, 1),
        'neutral_pct': round((neutral / total) * 100, 1)
    }


# ============================================================================
# STARTUP
# ============================================================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    is_production = os.getenv('FLASK_ENV') == 'production'
    
    print("\n" + "=" * 70)
    print("🚀 Reddbeat AI - Secure Backend Server")
    print("=" * 70)
    print(f"   Environment: {'PRODUCTION' if is_production else 'DEVELOPMENT'}")
    print(f"   Port: {port}")
    print(f"   Debug Mode: {'OFF' if is_production else 'ON'}")
    print(f"   Security Features:")
    print(f"      ✓ Rate Limiting")
    print(f"      ✓ Input Validation")
    print(f"      ✓ OWASP Security Headers")
    print(f"      ✓ Request Logging")
    print(f"      ✓ Error Handling")
    print(f"      ✓ CORS Protection")
    print("=" * 70 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=not is_production,
        threaded=True
    )
