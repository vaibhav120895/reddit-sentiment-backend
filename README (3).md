# 🔐 Reddbeat AI - Secure Backend

**AI-Powered Reddit Sentiment Analysis**  
*Enterprise-grade security • OWASP compliant • Production-ready*

---

## 🎯 Overview

Reddbeat AI analyzes Reddit sentiment using Claude AI, with enterprise-grade security features built in from day one.

### Key Features
- ✅ **OWASP Top 10 Compliant** - Following industry security standards
- ✅ **Rate Limiting** - DDoS protection with configurable limits
- ✅ **Input Validation** - Prevents injection attacks (SQL, XSS, Command)
- ✅ **Security Headers** - CSP, HSTS, X-Frame-Options, and more
- ✅ **Comprehensive Logging** - Audit trail for security events
- ✅ **Production-Ready** - Gunicorn with async workers
- ✅ **Claude AI Integration** - Advanced sentiment analysis

---

## 🚀 Quick Start

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Set Up Environment Variables**
```bash
cp .env.example key.env
nano key.env  # Edit and add your API keys
```

Required:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
SECRET_KEY=your-secret-key-here  # Generate: python -c "import secrets; print(secrets.token_hex(32))"
```

### **3. Run Development Server**
```bash
python app.py
```

### **4. Test**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"keywords": "AI", "limit": 5}'
```

---

## 🔒 Security Features

| Category | Implementation |
|----------|---------------|
| **Access Control** | Rate limiting (200/hour global, 20/min per endpoint) |
| **Injection Prevention** | Input validation, dangerous character filtering |
| **HTTPS** | Enforced in production via Talisman |
| **Security Headers** | CSP, HSTS, X-Frame-Options, X-Content-Type-Options |
| **Error Handling** | Never exposes internal details |
| **Logging** | Audit trail, rotating log files |
| **DDoS Protection** | Rate limiting, request size limits |

**Full documentation:** [SECURITY.md](./SECURITY.md)

---

## 📡 API Endpoints

### **POST /api/analyze**
```json
{
  "keywords": "artificial intelligence",
  "limit": 10,
  "sort": "hot"
}
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_posts": 10,
    "avg_sentiment": 0.45,
    "positive_pct": 60.0
  },
  "posts": [...]
}
```

---

## 🌐 Deployment

### **Deploy to Render**
1. Push to GitHub
2. Create Render Web Service
3. Set environment variables
4. Deploy

**Full guide:** [DEPLOYMENT.md](./DEPLOYMENT.md)

---

## 📚 Documentation

- [SECURITY.md](./SECURITY.md) - Security documentation
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment guide

---

## 👨‍💻 Author

**Vaibhav Singh** - *Understand How the Heart of the Internet Feels*
