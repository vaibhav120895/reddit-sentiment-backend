"""
Reddit API Client
Fetches posts from Reddit using global search
"""

import requests
import emoji
from datetime import datetime
import time


def fetch_reddit_posts(query, sort='hot', limit=10):
    """
    Fetch posts from Reddit using global search (all subreddits)
    
    Args:
        query: Search term (e.g., 'Donald Trump', 'artificial intelligence')
        sort: 'hot', 'new', 'top', or 'relevance'
        limit: Number of posts (1-50)
    
    Returns:
        List of post dictionaries
    """
    posts = []
    
    try:
        url = "https://www.reddit.com/search.json"
        
        headers = {
            'User-Agent': 'SentimentAnalysis/1.0'
        }
        
        params = {
            'q': query,
            'sort': 'relevance' if sort == 'hot' else sort,
            'limit': limit,
            't': 'week',
            'type': 'link'
        }
        
        print(f"   🔍 Searching Reddit for: '{query}'...")
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"   ❌ Reddit returned status code: {response.status_code}")
            return posts
        
        data = response.json()
        
        if 'data' in data and 'children' in data['data']:
            for item in data['data']['children']:
                post_data = item['data']
                
                text = post_data.get('title', '')
                selftext = post_data.get('selftext', '')
                if selftext:
                    text += " " + selftext
                
                emoji_count = len([c for c in text if c in emoji.EMOJI_DATA])
                
                post = {
                    'title': post_data.get('title', 'Untitled'),
                    'text': text,
                    'author': post_data.get('author', 'unknown'),
                    'url': f"https://reddit.com{post_data.get('permalink', '')}",
                    'score': post_data.get('score', 0),
                    'comments': post_data.get('num_comments', 0),
                    'created_utc': datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat(),
                    'subreddit': post_data.get('subreddit', 'unknown'),
                    'emoji_count': emoji_count,
                    'source': 'Reddit'
                }
                
                posts.append(post)
        
        print(f"   ✓ Found {len(posts)} posts across Reddit")
        
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout searching Reddit")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error searching Reddit: {str(e)}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")
    
    return posts
