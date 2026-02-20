"""
Multi-Model Sentiment Analyzer
VADER + RoBERTa + Claude (optimized for low memory)
"""

import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from anthropic import Anthropic

# Initialize only VADER at startup (lightweight - only ~10MB)
print("🔄 Loading VADER model...")
vader_analyzer = SentimentIntensityAnalyzer()
print("✅ VADER loaded\n")

# RoBERTa will be loaded on first use (lazy loading to save memory)
_roberta_model = None
_roberta_tokenizer = None


def get_roberta_model():
    """Lazy load RoBERTa model only when first API request comes in"""
    global _roberta_model, _roberta_tokenizer
    
    if _roberta_model is None:
        print("🔄 Loading RoBERTa model (first use - may take 1-2 minutes)...")
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        import torch
        
        MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        _roberta_tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _roberta_model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        print("✅ RoBERTa loaded and ready")
    
    return _roberta_model, _roberta_tokenizer


def analyze_with_vader(text):
    """Traditional sentiment analysis with VADER (rule-based, fast)"""
    scores = vader_analyzer.polarity_scores(text)
    compound = scores['compound']
    
    if compound >= 0.05:
        sentiment = 'Positive'
    elif compound <= -0.05:
        sentiment = 'Negative'
    else:
        sentiment = 'Neutral'
    
    return {'sentiment': sentiment, 'score': compound}


def analyze_with_roberta(text):
    """Transformer-based sentiment analysis (deep learning)"""
    import torch
    
    # Lazy load the model (only loads once, on first use)
    model, tokenizer = get_roberta_model()
    
    # Truncate to model max length
    text = text[:512]
    
    # Tokenize input
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    
    # Run inference (no gradient calculation needed for inference)
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    
    # Get sentiment scores
    scores = predictions[0].tolist()
    labels = ['Negative', 'Neutral', 'Positive']
    sentiment = labels[scores.index(max(scores))]
    
    # Convert to -1 to +1 scale
    score = scores[2] - scores[0]  # positive - negative
    
    return {
        'sentiment': sentiment,
        'score': round(score, 3),
        'confidence': round(max(scores), 3)
    }


def analyze_with_claude(text, emoji_count=0):
    """Advanced sentiment analysis with Claude API (no local model needed)"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        return {
            'sentiment': 'Neutral',
            'score': 0.0,
            'explanation': 'Claude API key not configured'
        }
    
    try:
        # Initialize Claude client (lightweight - just HTTP client)
        client = Anthropic(api_key=api_key)
        
        # Create prompt
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
        
        # Call Claude API (runs on Anthropic's servers, not yours)
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
    """Run all 3 models on all posts"""
    print(f"🧠 Running sentiment analysis on {len(posts)} posts...")
    
    for i, post in enumerate(posts, 1):
        text = post.get('text', post.get('title', ''))
        emoji_count = post.get('emoji_count', 0)
        
        # Run all three models
        vader = analyze_with_vader(text)
        roberta = analyze_with_roberta(text)  # Lazy loads on first call
        claude = analyze_with_claude(text, emoji_count)  # API call
        
        # Add results to post
        post['traditional_sentiment'] = vader['sentiment']
        post['traditional_score'] = vader['score']
        
        post['transformer_sentiment'] = roberta['sentiment']
        post['transformer_score'] = roberta['score']
        
        post['claude_sentiment'] = claude['sentiment']
        post['claude_score'] = claude['score']
        post['claude_explanation'] = claude.get('explanation', '')
        
        # Show progress
        if i % 5 == 0 or i == len(posts):
            print(f"   Progress: {i}/{len(posts)} posts analyzed")
    
    print("✅ Analysis complete!\n")
    return posts
