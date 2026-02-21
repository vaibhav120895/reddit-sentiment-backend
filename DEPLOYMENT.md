# 🚀 REDDBEAT AI - SECURE DEPLOYMENT GUIDE

## 📋 QUICK START

### **Option 1: Deploy to Render (Recommended)**

1. **Push Code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial secure backend"
   git branch -M main
   git remote add origin https://github.com/yourusername/reddbeat-backend.git
   git push -u origin main
   ```

2. **Create Render Web Service**
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     ```
     Name: reddbeat-backend
     Environment: Python 3
     Build Command: pip install -r requirements.txt
     Start Command: (use Procfile)
     Instance Type: Starter ($7/month) or higher
     ```

3. **Add Environment Variables in Render**
   ```
   FLASK_ENV=production
   SECRET_KEY=(generate with: python -c "import secrets; print(secrets.token_hex(32))")
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ALLOWED_ORIGIN=https://your-frontend-domain.com
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (~5 minutes)
   - Test: `https://your-app.onrender.com/health`

---

## 🔒 SECURITY SETUP (CRITICAL!)

### **Step 1: Environment Variables**

**NEVER** hardcode sensitive values. Always use environment variables.

#### **Generate Secure SECRET_KEY**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

#### **Set in Render Dashboard**
1. Go to your service → Environment
2. Add:
   ```
   FLASK_ENV=production
   SECRET_KEY=<your-generated-key>
   ANTHROPIC_API_KEY=sk-ant-xxxxx
   ALLOWED_ORIGIN=https://your-frontend.com
   ```

### **Step 2: CORS Configuration**

**Development:**
```bash
ALLOWED_ORIGIN=*  # Allow all origins
```

**Production:**
```bash
ALLOWED_ORIGIN=https://your-frontend-domain.com  # Specific domain only
```

### **Step 3: HTTPS Enforcement**

Render automatically provides HTTPS. Verify:
1. Go to service settings
2. Check "Force HTTPS" is enabled
3. Your app should be at `https://...onrender.com`

### **Step 4: Verify Security Headers**

Test your deployment:
```bash
curl -I https://your-app.onrender.com/health
```

You should see:
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
```

---

## 🧪 TESTING YOUR DEPLOYMENT

### **1. Health Check**
```bash
curl https://your-app.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Reddbeat AI",
  "version": "1.0.0",
  "claude_available": true
}
```

### **2. Test Analysis Endpoint**
```bash
curl -X POST https://your-app.onrender.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"keywords": "AI", "limit": 5, "sort": "hot"}'
```

### **3. Test Rate Limiting**
```bash
# Run this multiple times quickly
for i in {1..25}; do
  curl -X POST https://your-app.onrender.com/api/analyze \
    -H "Content-Type: application/json" \
    -d '{"keywords": "test", "limit": 5}'
done
```

After 20 requests per minute, you should get:
```json
{
  "error": "Rate limit exceeded",
  "retry_after": "1 hour"
}
```

---

## 📊 MONITORING & LOGGING

### **View Logs in Render**
1. Go to your service dashboard
2. Click "Logs" tab
3. Monitor for:
   - Security warnings
   - Rate limit violations
   - Error patterns
   - Unusual traffic

### **Log File Access (if needed)**
Logs are automatically rotated:
- Location: `logs/app.log`
- Max size: 10MB per file
- Backups: 10 files

### **Set Up Alerts (Recommended)**
Configure Render to notify you of:
- Service downtime
- High error rates
- Memory/CPU spikes

---

## 🔄 UPDATING YOUR DEPLOYMENT

### **Step 1: Update Code Locally**
```bash
# Make your changes
git add .
git commit -m "Description of changes"
```

### **Step 2: Security Check Before Deploy**
```bash
# Check for vulnerabilities
pip install pip-audit
pip-audit

# Update dependencies if needed
pip install --upgrade package-name
pip freeze > requirements.txt
```

### **Step 3: Push to GitHub**
```bash
git push origin main
```

### **Step 4: Render Auto-Deploy**
Render automatically deploys when you push to main branch.

Monitor deployment:
- Dashboard → Your Service → Deploys
- Watch logs for errors

---

## 🛠️ TROUBLESHOOTING

### **Issue: Service Won't Start**

**Check logs for:**
```
ModuleNotFoundError
ImportError
```

**Solution:**
1. Verify `requirements.txt` has all dependencies
2. Check Python version (should be 3.9+)
3. Clear build cache: Settings → Clear Build Cache

### **Issue: 500 Internal Server Error**

**Check logs for:**
- Missing environment variables
- API key issues
- Import errors

**Solution:**
1. Verify all environment variables are set
2. Check ANTHROPIC_API_KEY format: `sk-ant-...`
3. Review error logs in Render dashboard

### **Issue: CORS Errors**

**Symptoms:**
```
Access to fetch at 'https://...' from origin 'https://...' has been blocked by CORS policy
```

**Solution:**
1. Set `ALLOWED_ORIGIN` to your frontend domain
2. Or set to `*` for development (NOT production)
3. Redeploy after changing environment variables

### **Issue: Rate Limit Too Strict**

**Adjust in code:**
```python
@limiter.limit("20 per minute")  # Change to "30 per minute"
```

Or use environment variable:
```bash
RATELIMIT_OVERRIDE=30  # Override in env vars
```

---

## 📈 PERFORMANCE OPTIMIZATION

### **Gunicorn Workers**

Current: 4 workers (good for Starter plan)

**For higher traffic:**
```
Formula: (2 x CPU cores) + 1

Starter: 0.5 CPU → use 2 workers
Standard: 1 CPU → use 3 workers  
Pro: 2 CPU → use 5 workers
```

Edit `Procfile`:
```
web: gunicorn app:app --workers 5 --worker-class gevent ...
```

### **Timeout Adjustments**

Current: 120 seconds (for long analyses)

**For faster responses:**
```
web: gunicorn app:app ... --timeout 60 ...
```

### **Render Instance Types**

| Plan | CPU | RAM | Price | Recommended For |
|------|-----|-----|-------|----------------|
| Starter | 0.5 | 512MB | $7/mo | Development/Testing |
| Standard | 1 | 2GB | $25/mo | Production (low traffic) |
| Pro | 2 | 4GB | $85/mo | Production (high traffic) |

---

## 🔐 SECURITY BEST PRACTICES CHECKLIST

### **Before Going Live**

- [ ] `FLASK_ENV=production` set
- [ ] Unique `SECRET_KEY` generated
- [ ] `ALLOWED_ORIGIN` set to specific domain (not `*`)
- [ ] HTTPS enabled (automatic on Render)
- [ ] All API keys in environment variables
- [ ] `.env` and `key.env` in `.gitignore`
- [ ] Rate limiting tested
- [ ] Security headers verified
- [ ] Logs reviewed for errors
- [ ] Health endpoint responding

### **Ongoing Maintenance**

- [ ] **Weekly:** Review logs for suspicious activity
- [ ] **Monthly:** Update dependencies (`pip install --upgrade`)
- [ ] **Monthly:** Run security audit (`pip-audit`)
- [ ] **Quarterly:** Review and update rate limits
- [ ] **As needed:** Rotate secrets if compromised

---

## 📞 SUPPORT

### **Render Support**
- Docs: https://render.com/docs
- Status: https://status.render.com
- Support: support@render.com

### **Reddbeat AI Issues**
- GitHub Issues: https://github.com/yourusername/reddbeat-backend/issues
- Email: vaibhav@yourdomain.com

---

## 🎯 PRODUCTION READINESS CHECKLIST

Before announcing your app:

- [ ] SSL certificate valid (check with `curl -I`)
- [ ] All endpoints tested with real traffic
- [ ] Rate limits appropriate for expected load
- [ ] Monitoring and alerts configured
- [ ] Backup and recovery plan documented
- [ ] Security review completed
- [ ] Performance benchmarks established
- [ ] Documentation complete
- [ ] Error handling tested (try invalid inputs)
- [ ] Graceful degradation works (Reddit API down scenarios)

---

**Deployment Status:** ✅ Ready for Production  
**Last Updated:** 2025-02-21  
**Maintained By:** Vaibhav Singh
