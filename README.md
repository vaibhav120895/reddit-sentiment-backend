# Reddit Sentiment Analysis Backend

Simple Flask API backend for your Lovable frontend at https://develop-joyfully.lovable.app/

Analyzes Reddit posts using Claude AI for a detailed Sentiment Analysis

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd reddit-sentiment-backend
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Claude API key
nano .env
```

Your `.env` file should look like:
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxx
FLASK_ENV=development
PORT=5000
```

### 4. Run Server
```bash
python app.py
```

Server starts at `http://localhost:5000`

## 📡 API Endpoints

### POST /api/analyze
Analyzes Reddit posts

**Request:**
```json
{
  "keywords": "artificial intelligence",
  "subreddits": "artificial,MachineLearning,ChatGPT",
  "limit": 10,
  "sort": "hot"
}
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_posts": 30,
    "avg_sentiment": 0.234,
    "positive_pct": 45.5,
    "negative_pct": 18.2,
    "neutral_pct": 36.3
  },
  "posts": [
    {
      "title": "Post title",
      "text": "Full post text...",
      "author": "username",
      "url": "https://reddit.com/...",
      "score": 123,
      "comments": 45,
      "subreddit": "artificial",
      "emoji_count": 2,
      "traditional_sentiment": "Positive",
      "traditional_score": 0.75,
      "transformer_sentiment": "Positive", 
      "transformer_score": 0.82,
      "claude_sentiment": "Positive",
      "claude_score": 0.80,
      "claude_explanation": "The text expresses enthusiasm..."
    }
  ]
}
```

### GET /health
Health check

**Response:**
```json
{
  "status": "healthy",
  "claude_configured": true
}
```

## 🤖 Models

1. **VADER** (Traditional) - Rule-based, fast
2. **RoBERTa** (Transformer) - Deep learning, context-aware
3. **Claude** (AI) - Advanced reasoning with emoji awareness

## 🌐 CORS Configuration

Enabled for:
- `https://develop-joyfully.lovable.app`
- `https://*.lovable.app`
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (React dev server)

## 📦 Deployment

### Option 1: Render.com (Free)
1. Create account at render.com
2. Connect your GitHub repo
3. Create new "Web Service"
4. Set environment variable: `ANTHROPIC_API_KEY`
5. Deploy!

### Option 2: Railway.app (Free)
1. Create account at railway.app
2. "New Project" → "Deploy from GitHub"
3. Select your repo
4. Add environment variable: `ANTHROPIC_API_KEY`
5. Deploy!

### Option 3: Heroku
```bash
heroku create your-app-name
heroku config:set ANTHROPIC_API_KEY=your-key
git push heroku main
```

## 🔒 Important: .env File

**DO NOT commit your .env file to GitHub!**

Your `.gitignore` should include:
```
.env
__pycache__/
*.pyc
.DS_Store
```

Add your API key AFTER deploying:
- Render: Dashboard → Environment → Add Variable
- Railway: Project Settings → Variables
- Heroku: `heroku config:set ANTHROPIC_API_KEY=your-key`

## 🧪 Testing Locally

```bash
# Start server
python app.py

# Test in another terminal
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"keywords":"AI","subreddits":"artificial","limit":5,"sort":"hot"}'
```

## 📝 Project Structure

```
reddit-sentiment-backend/
├── app.py                  # Flask API
├── reddit_client.py        # Reddit data fetching
├── sentiment_analyzer.py   # 3 AI models
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
├── .env                   # Your API keys (not in git!)
└── README.md              # This file
```

## 🐛 Troubleshooting

**Models loading slow?**
- First run downloads models (~1GB) - this is normal
- Subsequent runs are faster

**Claude API errors?**
- Check API key is correct in .env
- Verify you have credits at console.anthropic.com

**CORS errors?**
- Make sure your frontend URL is in CORS origins (app.py line 21)

## 💰 Costs

- Reddit API: Free (public access)
- VADER: Free
- RoBERTa: Free (runs locally)
- Claude: ~$0.003 per post (3 cents per 10 posts)

## 🎯 Next Steps

1. Get your Claude API key: https://console.anthropic.com/
2. Clone this repo
3. Add API key to .env
4. Test locally: `python app.py`
5. Deploy to Render/Railway
6. Update your Lovable frontend with backend URL

## 📞 Support

Questions? Check:
- Claude API docs: https://docs.anthropic.com/
- Reddit API (PRAW): https://praw.readthedocs.io/
- Flask docs: https://flask.palletsprojects.com/
