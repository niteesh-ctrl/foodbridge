# FoodBridge - Render.com Free Deployment Guide

Complete step-by-step guide to deploy your Flask app on Render.com for FREE with global public URL.

## What You Get

- **Free Hosting**: $0/month on Render's free tier
- **Public URL**: Accessible worldwide (e.g., `https://foodbridge.onrender.com`)
- **Database**: SQLite (included in app, no external DB needed)
- **Auto-Deploy**: Push to GitHub, Render auto-deploys
- **HTTPS**: Free SSL certificate included

---

## Prerequisites

1. **GitHub Account** (free) - https://github.com
2. **Render Account** (free) - https://render.com
3. **Your Code** - Ready to push

---

## Step 1: Push to GitHub (5 minutes)

### Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `foodbridge`
3. Description: `Food waste and hunger platform`
4. **Public** (free hosting requires public repo)
5. Don't initialize with README (we have files)
6. Click **"Create repository"**

### Push Your Code

In your project directory, run:

```bash
# Configure Git (one-time setup)
git config user.email "your-email@example.com"
git config user.name "Your Name"

# Stage all files
git add .

# Commit
git commit -m "Initial commit - FoodBridge ready for deployment"

# Set branch to main
git branch -M main

# Add remote repository (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/foodbridge.git

# Push to GitHub
git push -u origin main
```

**See your code at:** `https://github.com/YOUR_USERNAME/foodbridge`

---

## Step 2: Create Render Account (2 minutes)

1. Go to https://render.com
2. Click **"Get Started"**
3. Sign up with:
   - GitHub (recommended - easiest)
   - Google
   - Email
4. Verify your email if required

---

## Step 3: Deploy on Render (5 minutes)

### Option A: Using render.yaml (Easiest - Auto Configuration)

1. Go to https://dashboard.render.com
2. Click **"New"** → **"Blueprint"**
3. Connect your GitHub account (if not done)
4. Select your `foodbridge` repository
5. Render detects `render.yaml` automatically
6. Review the configuration:
   - Name: `foodbridge`
   - Environment: `Python`
   - Region: `Oregon` (or closest)
   - Branch: `main`
   - Plan: **Free** ✓

7. Click **"Apply"**
8. Wait 3-5 minutes for deployment

### Option B: Manual Configuration (More Control)

1. Go to https://dashboard.render.com
2. Click **"New"** → **"Web Service"**
3. Connect GitHub and select `foodbridge` repository
4. Configure:

   ```
   Name:            foodbridge
   Region:          Oregon (or closest to you)
   Branch:          main
   Root Directory:  . (leave blank)
   Runtime:         Python 3
   Build Command:   pip install -r requirements.txt && python ml/model.py
   Start Command:   gunicorn app:app
   Instance Type:   Free
   ```

5. Click **"Advanced"** and add environment variable:
   - Key: `FLASK_ENV`
   - Value: `production`

6. Click **"Create Web Service"**
7. Wait 3-5 minutes for deployment

---

## Step 4: Watch Deployment (3-5 minutes)

### Deployment Progress

In the Render dashboard, watch your build logs:

```
Installing dependencies from requirements.txt...
Collecting Flask==3.0.0
Collecting gunicorn==21.2.0
...
Successfully installed Flask gunicorn scikit-learn pandas numpy...

Training ML model...
Model trained and saved to ml/model.pkl

Starting deployment...
Running: gunicorn app:app
[INFO] Listening at: http://0.0.0.0:10000
```

### What Happens During Build

1. **Python 3.11.0** installed (from runtime.txt)
2. **Dependencies** installed from requirements.txt
3. **ML model trained** automatically (ml/model.py runs)
4. **Database created** (SQLite foodbridge.db)
5. **Admin user created** automatically
6. **Sample data seeded** (17 food listings across 4 zones)
7. **Gunicorn starts** with your Flask app

---

## Step 5: Get Your Public URL

### After Successfully Deployed

1. In Render dashboard, click your service name (`foodbridge`)
2. At the top, you'll see: **`https://foodbridge-xxxx.onrender.com`**
3. Click the URL or copy it

**This is your public URL! Share it with anyone worldwide!**

---

## Step 6: Test Your Live Application

### Open Your URL in Browser

Visit your URL: `https://foodbridge-xxxx.onrender.com`

You should see the FoodBridge home page!

### Test Features

1. **Home Page**: Should load with stats and ML predictions
2. **Register**: Create donor account
3. **Register**: Create receiver account
4. **Login as Admin**:
   - Email: `admin@foodbridge.org`
   - Password: `admin123`
5. **View Donor Dashboard**: Post food donations
6. **View Receiver Dashboard**: Browse and claim donations
7. **Admin Panel**: View statistics, predictions, manage users

### Test on Mobile

Open your URL on your phone - it's fully responsive!

---

## Important Notes

### Free Tier Limitations

- **Spins down after 15 minutes of inactivity**
- **First request after spin-down takes 30-60 seconds** (spin-up time)
- **750 free hours/month** (enough for development/testing)
- **Public repositories only** (for free tier)

### Keeping App Active (Optional)

If you want to prevent spin-down (for demo purposes):

1. Use a service like UptimeRobot (free)
2. Set it to ping your URL every 10 minutes
3. Keeps app active and responsive

---

## Troubleshooting

### "Build Failed" Error

**Check build logs:**
1. Go to Render dashboard → Your service
2. Click **"Logs"** tab
3. Scroll to see error details

**Common issues:**

1. **Missing dependencies:**
   - All packages are in `requirements.txt`
   - Versions are compatible with Python 3.11

2. **ML model training failed:**
   - Non-critical - app still works
   - ML predictions return empty if model fails

3. **Database error:**
   - SQLite is used automatically
   - Database created on first run

### "Application Error" After Deployment

1. Check logs for Python errors
2. Verify `Procfile` has: `web: gunicorn app:app`
3. Verify `runtime.txt` has: `python-3.11.0`
4. Check requirements.txt has gunicorn

### Page Takes Long to Load

- First load after spin-down: 30-60 seconds (normal on free tier)
- Subsequent loads: Fast
- Upgrade to Starter plan ($7/month) for always-on

### Can't Login as Admin

Use exact credentials:
- Email: `admin@foodbridge.org`
- Password: `admin123`

Admin created automatically on first deployment.

---

## Your Deployment Files Explained

### render.yaml
- Blueprint for automatic Render configuration
- Sets Python environment, build commands, start commands
- Specifies free tier plan

### Procfile
- Tells Render how to start your app
- `web: gunicorn app:app` (production WSGI server)

### runtime.txt
- Specifies Python version
- `python-3.11.0` (stable, compatible)

### requirements.txt
- All Python dependencies with exact versions
- No conflicting packages
- Removed psycopg2 (we use SQLite)

---

## Making Updates

### Update Your App

1. Make changes locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update: description of change"
   git push origin main
   ```
3. Render automatically detects changes
4. Rebuilds and redeploys (2-3 minutes)

### View Deployment History

1. Go to Render dashboard
2. Click your service
3. Click **"Events"** tab
4. See all deployments with timestamps

---

## Custom Domain (Optional)

### Add Your Own Domain

1. In Render dashboard → Your service
2. Click **"Settings"** → **"Custom Domain"**
3. Add your domain (e.g., `foodbridge.yourdomain.com`)
4. Update DNS records as instructed
5. Wait for DNS propagation (up to 24 hours)

**Note:** Custom domain requires Starter plan ($7/month)

---

## Monitoring

### View Logs (Real-Time)

1. Render dashboard → Your service
2. Click **"Logs"** tab
3. See all server requests, errors, and application output

### View Metrics

1. Dashboard → Your service
2. Click **"Metrics"** tab
3. See:
   - CPU usage
   - Memory usage
   - Response time
   - Request count

---

## Environment Variables

### Set in Render Dashboard

1. Dashboard → Your service
2. Click **"Environment"** tab
3. Add variables:
   - `FLASK_ENV` = `production`
   - `SECRET_KEY` (auto-generated by Render)

### Access in Code

```python
import os
secret_key = os.environ.get('SECRET_KEY', 'default-key')
```

---

## Cost Breakdown

### Free Tier (What We're Using)
- Web Service: **$0/month**
- Database: SQLite (free, included)
- Bandwidth: 100GB/month free
- Build minutes: Free
- **Total: $0/month**

### Starter Plan (For Production)
- Web Service: $7/month
- Always-on (no spin-down)
- Custom domain support
- More resources
- **Total: $7/month**

---

## Demo Credentials

### Admin Account
- Email: `admin@foodbridge.org`
- Password: `admin123`
- Full platform access

### Test Donor Accounts (Pre-seeded)
- Email: `green@bistro.com`, Fresh Mart, Sunrise Bakery, etc.
- Password: `donor123`

### Test Receiver Account (Pre-seeded)
- Email: `hope@orphanage.org`
- Password: `receiver123`

Or create your own at `/register` page.

---

## Pre-loaded Data

Your app comes with sample data:

- **5 Donor Organizations** (ready to post donations)
- **1 Receiver** (Hope Orphanage)
- **17 Food Listings** across all zones:
  - Zone A: Vegetable Biryani, Chicken Curry, Tomatoes, Canned Beans
  - Zone B: Dal Makhani, Carrots, Mixed Vegetables, Rice
  - Zone C: Bread Loaves, Pasta Alfredo, Apples
  - Zone D: Fish Stew, Mutton Biryani, Potatoes, Onions, Cereal
- **200 ML Training Records** (for predictions)

---

## What Works After Deployment

✓ User registration (donor/receiver)
✓ User login and authentication
✓ Donor dashboard (post, edit, delete donations)
✓ Receiver dashboard (browse, filter, claim donations)
✓ Admin panel (statistics, ML predictions, user management)
✓ File uploads (food donation photos)
✓ ML predictions (surplus forecasting)
✓ Mobile responsive (works on all devices)
✓ Contact form
✓ All API endpoints

---

## Share Your URL!

Once deployed, share with:

- **Friends and family**
- **Social media** (Twitter, LinkedIn, Facebook)
- **Local NGOs and food banks**
- **Community organizations**
- **Local restaurants and businesses**

Anyone with internet can access your app!

---

## Support Resources

### Render Documentation
- Getting Started: https://render.com/docs
- Python Deployment: https://render.com/docs/deploy-flask
- Free Tier Details: https://render.com/docs/free

### Project Documentation
- `README.md` - Project overview
- `DEPLOYMENT.md` - Detailed deployment guide
- This file - Render-specific instructions

---

## Quick Reference

### Your URLs
- **GitHub**: `https://github.com/YOUR_USERNAME/foodbridge`
- **Live App**: `https://foodbridge-xxxx.onrender.com`
- **Render Dashboard**: `https://dashboard.render.com`

### Important Files
- `render.yaml` - Render configuration
- `Procfile` - App start command
- `runtime.txt` - Python version
- `requirements.txt` - Dependencies
- `app.py` - Main application
- `ml/model.py` - ML training script

### Git Commands
```bash
git status              # Check what changed
git add .              # Stage all changes
git commit -m "msg"     # Commit changes
git push origin main    # Push to GitHub (auto-deploys)
```

---

## Next Steps After Deployment

1. ✅ Test all features on your live URL
2. ✅ Create accounts and test donations
3. ✅ Share URL publicly
4. ✅ Monitor logs in Render dashboard
5. ✅ Make updates and push to GitHub (auto-deploys)
6. ✅ Consider upgrade to Starter plan for production use

---

## Summary

What you've deployed:
- ✅ Flask backend with all routes
- ✅ SQLite database with sample data
- ✅ User authentication system
- ✅ Donor, Receiver, and Admin dashboards
- ✅ ML prediction system (Random Forest)
- ✅ Mobile responsive design
- ✅ File upload capability
- ✅ All running on FREE tier

**Your FoodBridge app is now live and accessible worldwide!**

---

**Deployment Time:** 10-15 minutes (first time)
**Cost:** $0/month (free tier)
**Public URL:** `https://foodbridge-xxxx.onrender.com`
**Status:** Production Ready ✓

**Go deploy now!** 🚀
