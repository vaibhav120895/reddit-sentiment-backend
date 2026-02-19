# ⚡ Quick Start - 5 Steps to Deploy

## What You're Building
A backend API that analyzes Reddit posts with 3 AI models and connects to your Lovable frontend.

---

## Step 1: Get Your Claude API Key (2 minutes)

1. Go to: https://console.anthropic.com/
2. Sign up / Log in
3. Click "API Keys" in sidebar
4. Click "Create Key"
5. Copy the key (starts with `sk-ant-`)

**Cost:** ~$0.003 per post analyzed (3 cents for 10 posts)

---

## Step 2: Download & Setup Code (3 minutes)

```bash
# Download the code (from your GitHub or the ZIP file)
cd reddit-sentiment-backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and paste your API key
# (use nano, vim, or any text editor)
nano .env
```

In `.env`, change:
```
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

---

## Step 3: Test Locally (2 minutes)

```bash
# Start the server
python app.py
```

You should see:
```
🚀 Reddit Sentiment Analysis Backend
============================================================
   Server: http://localhost:5000
   Frontend: https://develop-joyfully.lovable.app
============================================================
```

**Test it:** Open http://localhost:5000/health in your browser

Should show: `{"status":"healthy","claude_configured":true}`

---

## Step 4: Push to GitHub (3 minutes)

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR-USERNAME/reddit-sentiment-backend.git
git branch -M main
git push -u origin main
```

**Important:** Your `.env` file is automatically excluded (see `.gitignore`)

---

## Step 5: Deploy (5 minutes)

### Option A: Render.com (Recommended)

1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your `reddit-sentiment-backend` repo
5. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
6. Add environment variable:
   - **Key:** `ANTHROPIC_API_KEY`
   - **Value:** Your Claude API key
7. Click "Create Web Service"
8. Wait 3-5 minutes

You'll get a URL like: `https://reddit-sentiment-api.onrender.com`

### Option B: Railway.app

1. Go to https://railway.app
2. Sign up with GitHub
3. "Deploy from GitHub repo"
4. Select your repo
5. Add variable: `ANTHROPIC_API_KEY` = your key
6. Get your URL from Settings → Generate Domain

---

## Step 6: Connect to Your Frontend

In your Lovable project, update the API URL:

```typescript
const API_URL = 'https://reddit-sentiment-api.onrender.com';

// Make API call
const response = await fetch(`${API_URL}/api/analyze`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    keywords: 'artificial intelligence',
    subreddits: 'artificial,MachineLearning',
    limit: 10,
    sort: 'hot'
  })
});

const data = await response.json();
console.log(data); // Posts with sentiment scores!
```

---

## ✅ Done!

**Total time:** ~15-20 minutes

Your backend is now:
- 🌐 Live on the internet
- 🔗 Connected to Reddit
- 🤖 Analyzing with 3 AI models
- ⚡ Ready for your frontend

---

## 🧪 Test Your Deployed Backend

```bash
# Health check
curl https://your-backend-url.onrender.com/health

# Run analysis
curl -X POST https://your-backend-url.onrender.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"keywords":"AI","subreddits":"artificial","limit":5,"sort":"hot"}'
```

---

## 🐛 Troubleshooting

**"Models loading slowly"**
- First request downloads models (~1-2 GB)
- Takes 2-3 minutes on first run
- Subsequent requests are fast

**"Claude API error"**
- Check your API key in Render environment variables
- Verify you have credits at console.anthropic.com

**"No posts found"**
- Try different subreddit names
- Check if subreddit exists and has posts

---

## 📚 Next Steps

- Read full `README.md` for API documentation
- See `DEPLOYMENT_GUIDE.md` for detailed instructions
- Check your Claude API usage at console.anthropic.com
- Monitor your Render/Railway dashboard

**Questions?** Check the README or reach out!
