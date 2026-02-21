"""
Reddit Sentiment Analysis Backend
Simple Flask API - Claude-only version
"""

from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from pathlib import Path

from reddit_client import fetch_reddit_posts
from sentiment_analyzer import analyze_posts_multi_model

if Path('key.env').exists():
    load_dotenv('key.env')
    print("📁 Loaded from key.env (local)")
else:
    load_dotenv()
    print("🌐 Loaded from environment variables (production)")

app = Flask(__name__)


@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        return response, 200


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response


@app.route('/health', methods=['GET', 'OPTIONS'])
def health_check():
    api_key = os.getenv('ANTHROPIC_API_KEY')
    return jsonify({
        'status': 'healthy',
        'claude_configured': bool(api_key and api_key.startswith('sk-ant-')),
        'models': ['claude']
    }), 200


@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze_sentiment():
    try:
        data = request.get_json()
        keywords = data.get('keywords', 'AI')
        limit = int(data.get('limit', 5))
        sort = data.get('sort', 'hot')
        
        if limit < 1 or limit > 10:
            return jsonify({'error': 'Limit must be between 1 and 10'}), 400
        
        print(f"\n📊 Analysis Request:")
        print(f"   Query: '{keywords}'")
        print(f"   Limit: {limit} posts")
        print(f"   Sort: {sort}")
        
        all_posts = fetch_reddit_posts(keywords, sort, limit)
        
        if not all_posts:
            return jsonify({'error': 'No posts found'}), 404
        
        print(f"✅ Fetched {len(all_posts)} posts")
        
        analyzed_posts = analyze_posts_multi_model(all_posts)
        stats = calculate_stats(analyzed_posts)
        
        return jsonify({
            'success': True,
            'stats': stats,
            'posts': analyzed_posts
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def calculate_stats(posts):
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
        'avg_sentiment': round(sum(scores) / len(scores), 3) if scores else 0,
        'positive_pct': round((positive / total) * 100, 1),
        'negative_pct': round((negative / total) * 100, 1),
        'neutral_pct': round((neutral / total) * 100, 1)
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("\n" + "=" * 60)
    print("🚀 Reddit Sentiment Analysis Backend")
    print("=" * 60)
    print(f"   Server: http://localhost:{port}")
    print(f"   Model: Claude Sonnet 4")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)
