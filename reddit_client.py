"""
Reddit API Client
Fetches posts from Reddit using requests (no PRAW authentication needed)
"""

import requests
import emoji
from datetime import datetime


def fetch_reddit_posts(subreddit='artificial', sort='hot', limit=10):
    """
    Fetch posts from Reddit using JSON API (no auth needed)
    
    Args:
        subreddit: Subreddit name (e.g., 'artificial')
        sort: 'hot', 'new', or 'top'
        limit: Number of posts (1-50)
    
    Returns:
        List of post dictionaries
    """
    posts = []
    
    try:
        # Use Reddit's JSON API (public access)
        url = f"https://www.reddit.com/r/{subreddit}/{sort}.json"
        
        headers = {
            'User-Agent': 'SentimentAnalysis/1.0'
        }
        
        params = {
            'limit': limit
        }
        
        print(f"   🔍 Fetching from r/{subreddit}...")
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"   ❌ Reddit returned status code: {response.status_code}")
            return posts
        
        data = response.json()
        
        # Extract posts from response
        if 'data' in data and 'children' in data['data']:
            for item in data['data']['children']:
                post_data = item['data']
                
                # Combine title and body text
                text = post_data.get('title', '')
                selftext = post_data.get('selftext', '')
                if selftext:
                    text += " " + selftext
                
                # Count emojis
                emoji_count = len([c for c in text if c in emoji.EMOJI_DATA])
                
                post = {
                    'title': post_data.get('title', 'Untitled'),
                    'text': text,
                    'author': post_data.get('author', 'unknown'),
                    'url': f"https://reddit.com{post_data.get('permalink', '')}",
                    'score': post_data.get('score', 0),
                    'comments': post_data.get('num_comments', 0),
                    'created_utc': datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat(),
                    'subreddit': subreddit,
                    'emoji_count': emoji_count,
                    'source': 'Reddit'
                }
                
                posts.append(post)
        
        print(f"   ✓ Fetched {len(posts)} posts from r/{subreddit}")
        
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout fetching r/{subreddit}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error fetching r/{subreddit}: {str(e)}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")
    
    return posts