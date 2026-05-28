# Quick Start - Deploy to Render in 10 Minutes

Get your public URL: `https://foodbridge.onrender.com`

## 3 Simple Steps

### Step 1: Push to GitHub (5 minutes)

```bash
# In your project directory:

# Configure Git
git config user.email "your-email@example.com"
git config user.name "Your Name"

# Commit
git add .
git commit -m "FoodBridge ready for deployment"
git branch -M main

# Create GitHub repo at https://github.com/new
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/foodbridge.git
git push -u origin main
```

### Step 2: Deploy on Render (3 minutes)

1. Go to https://render.com → Sign up with GitHub
2. Click **"New"** → **"Blueprint"**
3. Select your `foodbridge` repository
4. Click **"Apply"**
5. Wait 3-5 minutes

### Step 3: Get Your URL

Your live URL: `https://foodbridge-xxxx.onrender.com`

Share this URL with anyone worldwide!

---

## What's Configured

✓ **render.yaml** - Auto-configuration
✓ **Procfile** - `web: gunicorn app:app`
✓ **runtime.txt** - `python-3.11.0`
✓ **requirements.txt** - All dependencies
✓ **SQLite database** - Auto-created
✓ **ML model** - Auto-trained on first run
✓ **Sample data** - 17 food listings, 5 donors, 1 receiver

## Demo Accounts

- **Admin**: admin@foodbridge.org / admin123
- **Donor**: green@bistro.com / donor123
- **Receiver**: hope@orphanage.org / receiver123

## Cost: $0/month (Free Tier)

## Need Details?

Read: **RENDER_DEPLOY_GUIDE.md**

---

**Ready? Go to https://render.com and deploy!** 🚀
