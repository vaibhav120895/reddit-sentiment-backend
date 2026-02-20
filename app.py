"""
Reddit Sentiment Analysis Backend
Simple Flask API - Claude-only version
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Import analysis functions
from reddit_client import fetch_reddit_posts
from sentiment_analyzer import analyze_posts_multi_model

# Load environment variables
import os
from pathlib import Path

# Check if key.env exists (local development)
if Path('key.env').exists():
    load_dotenv('key.env')
    print("📁 Loaded from key.env (local)")
else:
    # Production - load from system environment variables
    load_dotenv()
    print("🌐 Loaded from environment variables (production)")

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for your Lovable frontend
from flask_cors import CORS, cross_origin

CORS(app, 
     origins=[
         "https://develop-joyfully.lovable.app",
         "https://*.lovable.app",
         "http://localhost:5173",
         "http://localhost:3000"
     ],
     allow_headers=["Content-Type", "Accept"],
     methods=["GET", "POST", "OPTIONS"],
     supports_credentials=False,
     expose_headers=["Content-Type"])

@app.route('/api/analyze', methods=['POST'])
def analyze_sentiment():
    """
    Analyze Reddit posts for sentiment using Claude
    
    Request body:
    {
        "keywords": "artificial intelligence",
        "subreddits": "artificial,MachineLearning",
        "limit": 10,
        "sort": "hot"
    }
    """
    try:
        data = request.get_json()
        
        # Extract parameters
        keywords = data.get('keywords', 'AI')
        subreddits_str = data.get('subreddits', 'artificial')
        limit = int(data.get('limit', 10))
        sort = data.get('sort', 'hot')
        
        # Validate
        if limit < 1 or limit > 50:
            return jsonify({'error': 'Limit must be between 1 and 50'}), 400
        
        # Parse subreddits
        subreddits = [s.strip() for s in subreddits_str.split(',') if s.strip()]
        
        print(f"\n📊 Analysis Request:")
        print(f"   Keywords: {keywords}")
        print(f"   Subreddits: {subreddits}")
        print(f"   Limit: {limit} per subreddit")
        
        # Fetch Reddit posts
        all_posts = []
        for subreddit in subreddits:
            posts = fetch_reddit_posts(subreddit, sort, limit)
            all_posts.extend(posts)
        
        if not all_posts:
            return jsonify({'error': 'No posts found'}), 404
        
        print(f"✅ Fetched {len(all_posts)} total posts")
        
        # Run sentiment analysis (Claude only)
        analyzed_posts = analyze_posts_multi_model(all_posts)
        
        # Calculate stats
        stats = calculate_stats(analyzed_posts)
        
        return jsonify({
            'success': True,
            'stats': stats,
            'posts': analyzed_posts
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


def calculate_stats(posts):
    """Calculate aggregate statistics"""
    if not posts:
        return {}
    
    total = len(posts)
    sentiments = [p.get('claude_sentiment', 'Neutral') for p in posts]
    scores = [p.get('claude_score', 0) for p in posts]
    
    positive = sum(1 for s in sentiments if s == 'Positive')
    negative = sum(1 for s in sentiments if s == 'Negative')
    neutral = sum(1 for s in sentiments if s == 'Neutral')
    
    return {
        'total_posts': total,
        'avg_sentiment': round(sum(scores) / len(scores), 3),
        'positive_pct': round((positive / total) * 100, 1),
        'negative_pct': round((negative / total) * 100, 1),
        'neutral_pct': round((neutral / total) * 100, 1)
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("\n" + "=" * 60)
    print("🚀 Reddit Sentiment Analysis Backend (Claude-Only)")
    print("=" * 60)
    print(f"   Server: http://localhost:{port}")
    print(f"   Frontend: https://develop-joyfully.lovable.app")
    print(f"   Model: Claude Sonnet 4")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)
