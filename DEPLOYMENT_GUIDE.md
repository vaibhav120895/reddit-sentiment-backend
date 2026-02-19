# 🚀 Simple Deployment Guide

## Step-by-Step: From Notebook to Production

### Part 1: Create GitHub Repository

#### Step 1: Create New Repo on GitHub
1. Go to https://github.com/new
2. Repository name: `reddit-sentiment-backend`
3. Description: "Backend API for Reddit sentiment analysis"
4. **Select: Public** (or Private if you prefer)
5. **DO NOT** check "Add README" (we already have one)
6. Click "Create repository"

#### Step 2: Push Your Code
```bash
# Navigate to the backend folder
cd reddit-sentiment-backend

# Initialize git
git init

# Add all files EXCEPT .env (already in .gitignore)
git add .

# Commit
git commit -m "Initial commit: Reddit sentiment analysis backend"

# Link to GitHub (replace YOUR-USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR-USERNAME/reddit-sentiment-backend.git

# Push
git branch -M main
git push -u origin main
```

✅ Your code is now on GitHub!

---

### Part 2: Deploy to Render.com (FREE)

Render.com offers free tier for hobby projects.

#### Step 1: Sign Up
1. Go to https://render.com
2. Click "Get Started"
3. Sign up with GitHub (easiest option)

#### Step 2: Create Web Service
1. Click "New +" → "Web Service"
2. Click "Connect account" to connect GitHub
3. Find your `reddit-sentiment-backend` repo
4. Click "Connect"

#### Step 3: Configure Service
Fill in these settings:

**Name:** `reddit-sentiment-api` (or any name you want)

**Environment:** `Python 3`

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
gunicorn app:app
```

**Instance Type:** `Free`

#### Step 4: Add Environment Variable
1. Scroll down to "Environment Variables"
2. Click "Add Environment Variable"
3. Key: `ANTHROPIC_API_KEY`
4. Value: `your-claude-api-key-here`
5. Click "Add"

#### Step 5: Deploy
1. Click "Create Web Service"
2. Wait 3-5 minutes for deployment
3. You'll get a URL like: `https://reddit-sentiment-api.onrender.com`

✅ Your backend is live!

---

### Part 3: Update Your Lovable Frontend

#### Step 1: Update API URL
In your Lovable project, update the API endpoint:

```typescript
// Change from localhost to your Render URL
const API_URL = 'https://reddit-sentiment-api.onrender.com';

// Example API call
const response = await fetch(`${API_URL}/api/analyze`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    keywords: 'AI',
    subreddits: 'artificial,MachineLearning',
    limit: 10,
    sort: 'hot'
  })
});
```

#### Step 2: Test Your Frontend
1. Open https://develop-joyfully.lovable.app/
2. Try running an analysis
3. You should see results from your backend!

---

### Part 4: Alternative - Deploy to Railway.app

If Render doesn't work, try Railway:

#### Step 1: Sign Up
1. Go to https://railway.app
2. Click "Start a New Project"
3. Sign in with GitHub

#### Step 2: Deploy
1. Click "Deploy from GitHub repo"
2. Select your `reddit-sentiment-backend` repo
3. Railway auto-detects Python and deploys

#### Step 3: Add API Key
1. Click on your project
2. Go to "Variables" tab
3. Click "New Variable"
4. Add: `ANTHROPIC_API_KEY` = `your-key`
5. Click "Add"

#### Step 4: Get URL
1. Go to "Settings" tab
2. Click "Generate Domain"
3. You'll get a URL like: `your-app.up.railway.app`

✅ Done!

---

## 🧪 Testing Your Deployed Backend

### Test 1: Health Check
```bash
curl https://your-backend-url.onrender.com/health
```

Expected response:
```json
{"status":"healthy","claude_configured":true}
```

### Test 2: Run Analysis
```bash
curl -X POST https://your-backend-url.onrender.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "AI",
    "subreddits": "artificial",
    "limit": 5,
    "sort": "hot"
  }'
```

Should return posts with sentiment scores!

---

## 📋 Checklist

- [ ] Code pushed to GitHub
- [ ] .env file NOT in repository (check .gitignore)
- [ ] Deployed to Render or Railway
- [ ] Environment variable added (ANTHROPIC_API_KEY)
- [ ] Health check returns 200
- [ ] Analysis endpoint returns data
- [ ] Frontend updated with backend URL
- [ ] End-to-end test successful

---

## 🐛 Common Issues

### Issue: "Models not found"
**Solution:** First request takes 2-3 minutes to download models. Be patient!

### Issue: "CORS error"
**Solution:** Make sure your frontend URL is in `app.py` CORS origins:
```python
CORS(app, origins=[
    "https://develop-joyfully.lovable.app",  # Add your URL here
    ...
])
```

### Issue: "Claude API error"
**Solution:** 
1. Check API key is correct in Render/Railway environment variables
2. Verify you have credits at https://console.anthropic.com/

### Issue: "Build failed"
**Solution:** Check build logs in Render/Railway dashboard

---

## 💡 Tips

1. **Free tier limitations:**
   - Render: Sleeps after 15 min inactivity (first request slow)
   - Railway: 500 hours/month free
   
2. **Keep costs low:**
   - Limit posts to 10-20 per request
   - Cache results on frontend
   
3. **Monitor usage:**
   - Check Claude credits: https://console.anthropic.com/
   - Render dashboard shows request count

---

## 🎉 You're Done!

Your backend is:
- ✅ Running on cloud
- ✅ Connected to your frontend
- ✅ Analyzing Reddit sentiment with 3 AI models
- ✅ Fully functional!

**Next steps:**
- Share your app URL with friends
- Monitor usage in Render/Railway dashboard
- Add more features (save analyses, user accounts, etc.)
