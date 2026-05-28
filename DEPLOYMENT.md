# FoodBridge - Global Deployment Guide

Deploy your Flask application globally using Railway or Render in 5 minutes.

## Quick Start (Recommended: Railway)

### Step 1: Prepare GitHub Repository

```bash
git init
git add .
git commit -m "Ready for production deployment"
git push origin main
```

### Step 2: Deploy on Railway (Fastest)

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your FoodBridge repository
5. Railway automatically detects `Procfile` and `requirements.txt`

### Step 3: Configure Environment Variables

In Railway Dashboard:
1. Click your project
2. Go to "Variables" tab
3. Add these variables:
   ```
   SECRET_KEY = [Generate random string: python -c "import secrets; print(secrets.token_hex(32))"]
   FLASK_ENV = production
   ```
4. Railway automatically provides:
   - `DATABASE_URL` (PostgreSQL is auto-created)
   - `PORT` environment variable

### Step 4: Deploy

1. Railway detects changes automatically from Git
2. Click "Deploy" button
3. Wait 2-3 minutes for build to complete
4. Your app gets a public URL: `https://yourapp.railway.app`

## Alternative: Deploy on Render

### Step 1: Prepare GitHub Repository
Same as above

### Step 2: Create Web Service on Render

1. Go to https://render.com
2. Sign up with GitHub
3. Click "New" → "Web Service"
4. Select your repository
5. Configure:
   - **Name**: foodbridge
   - **Runtime**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt && python ml/model.py`
   - **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`

### Step 3: Create PostgreSQL Database

1. In Render Dashboard, click "New" → "PostgreSQL"
2. Name: `foodbridge-db`
3. Copy the internal database URL

### Step 4: Link Database to Web Service

1. Go to Web Service settings
2. Add environment variables:
   ```
   SECRET_KEY = [Generate random string]
   DATABASE_URL = [Paste PostgreSQL URL from above]
   FLASK_ENV = production
   ```

### Step 5: Deploy

1. Click "Deploy"
2. Wait 3-5 minutes
3. Your live URL: `https://foodbridge.onrender.com`

## Environment Variables Explained

| Variable | Purpose | Example |
|----------|---------|---------|
| `SECRET_KEY` | Flask session encryption | `a3f9c2e1...` (random hex) |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@host/db` |
| `FLASK_ENV` | Environment mode | `production` |
| `PORT` | Server port (auto-set by platform) | `5000` |

Generate a secure SECRET_KEY:
```python
import secrets
print(secrets.token_hex(32))
```

## File Structure for Deployment

```
project/
├── app.py              # Main Flask app
├── models.py           # Database models
├── wsgi.py             # WSGI entry point
├── Procfile            # Process file for deployment
├── runtime.txt         # Python version specification
├── requirements.txt    # Dependencies
├── .env.example        # Template for environment variables
├── static/             # CSS, JS, images
├── templates/          # HTML templates
├── routes/             # Flask blueprints
├── ml/                 # Machine learning model
└── README.md           # Project documentation
```

## What Gets Deployed

✓ Flask backend with all routes  
✓ PostgreSQL database (auto-created)  
✓ Static files (CSS, JS, images)  
✓ ML model (trained on startup)  
✓ All templates and dependencies  

## Verify Deployment

After deployment, test these endpoints:

1. **Home Page**: `https://yourapp.railway.app/`
2. **Login**: `https://yourapp.railway.app/login`
3. **Register**: `https://yourapp.railway.app/register`
4. **API Test**: `https://yourapp.railway.app/api/listings`

## Demo Accounts After Deployment

- **Admin**: admin@foodbridge.org / admin123
- **Create new donors/receivers**: Use registration page

## Production Features Enabled

✓ **Database**: PostgreSQL (scalable, production-grade)  
✓ **Security**: Environment-based SECRET_KEY  
✓ **Server**: Gunicorn (4 workers, production WSGI)  
✓ **Logging**: Automated error tracking  
✓ **Database Migrations**: Auto-detected on startup  
✓ **Static Files**: Served efficiently  

## Troubleshooting

### "Database URL not found"
- Ensure `DATABASE_URL` environment variable is set
- Railway: Auto-created when adding PostgreSQL
- Render: Must manually add PostgreSQL and copy URL

### "Module not found" errors
- All dependencies listed in `requirements.txt`
- If missing, add to requirements.txt and re-deploy

### "Connection to database failed"
- Wait 30 seconds for database to initialize
- Check DATABASE_URL is correct format: `postgresql://...`

### "Port already in use"
- Railway/Render handle this automatically
- Don't hardcode port in code (uses $PORT env var)

## Scaling for More Users

**Railway Pricing**:
- First 5GB RAM-hours free
- $0.50 per extra GB-hour
- Easily handles 1000+ concurrent users

**Render Pricing**:
- Web Service: $7/month minimum
- PostgreSQL: $15/month
- Auto-scales with traffic

## Next Steps

1. Share your live URL with others
2. Monitor logs in Railway/Render dashboard
3. Add custom domain (in settings)
4. Set up automated backups
5. Monitor performance metrics

## Support

- **Railway Docs**: https://docs.railway.app
- **Render Docs**: https://render.com/docs
- **Flask Docs**: https://flask.palletsprojects.com

Your FoodBridge app is now running globally! 🚀
