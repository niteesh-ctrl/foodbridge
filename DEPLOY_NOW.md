# Deploy FoodBridge in 5 Minutes

Your application is ready for global deployment! Choose your platform:

## Option 1: Railway (Recommended - Easiest)

### 1. Go to Railway.app
https://railway.app

### 2. Click "New Project" → "Deploy from GitHub repo"

### 3. Select your FoodBridge repository

### 4. Set Environment Variables
In the Variables tab, add:
```
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f
FLASK_ENV=production
```
(Generate your own SECRET_KEY)

### 5. Click Deploy

**Your live URL**: `https://yourproject.railway.app` (auto-generated in 2-3 minutes)

---

## Option 2: Render.com (Free Option)

### 1. Go to Render.com
https://render.com

### 2. Click "New" → "Web Service"

### 3. Select your GitHub repo

### 4. Configure:
- **Runtime**: Python 3.11
- **Build**: `pip install -r requirements.txt && python ml/model.py`
- **Start**: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`

### 5. Create PostgreSQL Database
- Click "New" → "PostgreSQL"
- Copy the connection URL

### 6. Add Environment Variables
```
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f
DATABASE_URL=[paste PostgreSQL URL here]
FLASK_ENV=production
```

### 7. Click Deploy

**Your live URL**: `https://yourproject.onrender.com` (in 3-5 minutes)

---

## What's Already Configured

✅ **Procfile** - Railway/Render know how to start your app  
✅ **runtime.txt** - Python 3.11 specified  
✅ **requirements.txt** - All dependencies listed (Flask, Gunicorn, etc.)  
✅ **app.py** - Configured for PostgreSQL in production  
✅ **DEPLOYMENT.md** - Detailed deployment guide  

## After Deployment

1. **Test your live app**:
   - Go to `https://yourapp-name.railway.app` or `.onrender.com`
   - You should see the FoodBridge home page

2. **Create test accounts**:
   - Go to `/register`
   - Register as a donor
   - Register as a receiver

3. **Admin login** (already in database):
   - Email: `admin@foodbridge.org`
   - Password: `admin123`

## Generate a Strong SECRET_KEY

```python
import secrets
print(secrets.token_hex(32))
```

Copy the output and use it in your environment variables.

## Troubleshooting

**"Build failed"?**
- Check Logs tab on Railway/Render
- All dependencies are in requirements.txt
- Python version is 3.11

**"Database connection error"?**
- Railway auto-creates PostgreSQL
- Render requires manual PostgreSQL setup (see DEPLOYMENT.md)
- DATABASE_URL must be set

**"Page shows error"?**
- Wait 30 seconds for app to fully initialize
- Refresh the page
- Check logs for error messages

## Mobile Responsiveness

Your app is fully responsive:
✓ Desktop (1920px+)  
✓ Tablet (768px - 1024px)  
✓ Mobile (375px - 767px)  

---

## You're Ready! 🚀

Pick Railway or Render above and deploy now!

For detailed setup, see **DEPLOYMENT.md**
