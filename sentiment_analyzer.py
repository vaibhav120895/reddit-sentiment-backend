"""
Claude-Only Sentiment Analyzer
Optimized for minimal memory usage
"""

import os
from anthropic import Anthropic

print("✅ Sentiment analyzer ready (Claude API)\n")


def analyze_with_claude(text, emoji_count=0):
    """Sentiment analysis with Claude API"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        return {
            'sentiment': 'Neutral',
            'score': 0.0,
            'explanation': 'Claude API key not configured'
        }
    
    try:
        client = Anthropic(api_key=api_key)
        
        prompt = f"""Analyze the sentiment of this Reddit post. Consider both words and emojis.

Text: {text}

Emojis detected: {emoji_count}

Provide:
1. Sentiment: Positive, Negative, or Neutral
2. Score: -1.0 (very negative) to +1.0 (very positive)
3. Brief explanation (1-2 sentences)

Format:
SENTIMENT: [classification]
SCORE: [number]
EXPLANATION: [reason]"""
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response = message.content[0].text
        
        # Parse response
        sentiment = 'Neutral'
        score = 0.0
        explanation = ''
        
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('SENTIMENT:'):
                sentiment = line.split(':', 1)[1].strip()
            elif line.startswith('SCORE:'):
                try:
                    score = float(line.split(':', 1)[1].strip())
                except:
                    score = 0.0
            elif line.startswith('EXPLANATION:'):
                explanation = line.split(':', 1)[1].strip()
        
        return {
            'sentiment': sentiment,
            'score': round(score, 3),
            'explanation': explanation
        }
        
    except Exception as e:
        print(f"   ⚠️  Claude API error: {str(e)}")
        return {
            'sentiment': 'Neutral',
            'score': 0.0,
            'explanation': f'Error: {str(e)}'
        }


def analyze_posts_multi_model(posts):
    """Run Claude analysis on all posts"""
    print(f"🧠 Running Claude sentiment analysis on {len(posts)} posts...")
    
    for i, post in enumerate(posts, 1):
        text = post.get('text', post.get('title', ''))
        emoji_count = post.get('emoji_count', 0)
        
        # Run Claude
        claude = analyze_with_claude(text, emoji_count)
        
        # Add results to post (all three columns show Claude for consistency)
        post['traditional_sentiment'] = claude['sentiment']
        post['traditional_score'] = claude['score']
        
        post['transformer_sentiment'] = claude['sentiment']
        post['transformer_score'] = claude['score']
        
        post['claude_sentiment'] = claude['sentiment']
        post['claude_score'] = claude['score']
        post['claude_explanation'] = claude.get('explanation', '')
        
        if i % 5 == 0 or i == len(posts):
            print(f"   Progress: {i}/{len(posts)} posts analyzed")
    
    print("✅ Analysis complete!\n")
    return posts
