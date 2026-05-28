#!/bin/bash

#############################################################################
#                                                                           #
#                    FOODBRIDGE DEPLOYMENT AUTOMATION                      #
#                                                                           #
#  This script prepares your app for deployment and shows exact steps      #
#                                                                           #
#############################################################################

PROJECT_NAME="foodbridge"
DEPLOYMENT_DIR=$(pwd)

echo "██████████████████████████████████████████████████████████████████"
echo "█                                                                █"
echo "█            FOODBRIDGE - DEPLOYMENT AUTOMATION                 █"
echo "█                                                                █"
echo "██████████████████████████████████████████████████████████████████"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Initializing Git Repository${NC}"
echo "────────────────────────────────────────────────────────────────────"

if [ -d ".git" ]; then
    echo -e "${GREEN}✓ Git repository already exists${NC}"
else
    git init
    echo -e "${GREEN}✓ Git repository initialized${NC}"
fi
echo ""

echo -e "${BLUE}Step 2: Verifying All Files${NC}"
echo "────────────────────────────────────────────────────────────────────"

# Required files for deployment
required_files=(
    "app.py"
    "models.py"
    "wsgi.py"
    "Procfile"
    "runtime.txt"
    "requirements.txt"
    ".env.example"
)

all_files_ok=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file${NC}"
    else
        echo -e "${YELLOW}✗ $file missing${NC}"
        all_files_ok=false
    fi
done

if [ "$all_files_ok" = false ]; then
    echo ""
    echo "ERROR: Some required files are missing. Please check above."
    exit 1
fi
echo ""

echo -e "${BLUE}Step 3: Generating Secret Key${NC}"
echo "────────────────────────────────────────────────────────────────────"

SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo -e "${GREEN}✓ Generated SECRET_KEY:${NC}"
echo "$SECRET_KEY"
echo ""
echo "Save this key - you'll need it for deployment!"
echo ""

echo -e "${BLUE}Step 4: Staging Files for Git${NC}"
echo "────────────────────────────────────────────────────────────────────"

git add .
files_staged=$(git diff --cached --numstat | wc -l)
echo -e "${GREEN}✓ $files_staged files staged${NC}"
echo ""

echo -e "${BLUE}Step 5: Creating Commit${NC}"
echo "────────────────────────────────────────────────────────────────────"

git commit -m "Production deployment ready - configured for Railway/Render"
echo -e "${GREEN}✓ Commit created${NC}"
echo ""

echo "██████████████████████████████████████████████████████████████████"
echo "█                                                                █"
echo "█                  READY TO DEPLOY!                            █"
echo "█                                                                █"
echo "██████████████████████████████████████████████████████████████████"
echo ""

echo -e "${YELLOW}CHOOSE YOUR DEPLOYMENT PLATFORM:${NC}"
echo ""
echo "OPTION A: Railway (RECOMMENDED - Fastest)"
echo "────────────────────────────────────────────────────────────────────"
echo "1. Go to: https://railway.app"
echo "2. Sign up with GitHub"
echo "3. Click: New Project → Deploy from GitHub repo"
echo "4. Select: Your FoodBridge repository"
echo "5. Add environment variable:"
echo "   Name:  SECRET_KEY"
echo "   Value: $SECRET_KEY"
echo "6. Click: Deploy"
echo "7. Wait 2-3 minutes"
echo "8. Your live URL: https://your-project-name.railway.app"
echo ""
echo "Railway will automatically:"
echo "  ✓ Create PostgreSQL database"
echo "  ✓ Set DATABASE_URL environment variable"
echo "  ✓ Install all Python dependencies"
echo "  ✓ Start Gunicorn server"
echo "  ✓ Provide HTTPS/SSL certificate"
echo ""

echo "OPTION B: Render (More Control)"
echo "────────────────────────────────────────────────────────────────────"
echo "1. Go to: https://render.com"
echo "2. Sign up with GitHub"
echo "3. Click: New → Web Service"
echo "4. Select: Your FoodBridge repository"
echo "5. Configure:"
echo "   Runtime:      Python 3.11"
echo "   Build:       pip install -r requirements.txt && python ml/model.py"
echo "   Start:       gunicorn -w 4 -b 0.0.0.0:\$PORT app:app"
echo "6. Click: New → PostgreSQL"
echo "   - Create database"
echo "   - Copy Internal Database URL"
echo "7. Back to Web Service → Environment:"
echo "   SECRET_KEY = $SECRET_KEY"
echo "   DATABASE_URL = [paste PostgreSQL URL]"
echo "   FLASK_ENV = production"
echo "8. Click: Create Web Service"
echo "9. Wait 3-5 minutes"
echo "10. Your live URL: https://your-project-name.onrender.com"
echo ""

echo "██████████████████████████████████████████████████████████████████"
echo ""
echo -e "${YELLOW}NEXT COMMAND:${NC}"
echo ""
echo "Push to GitHub:"
echo "────────────────────────────────────────────────────────────────────"
echo ""
echo "  git remote add origin https://github.com/YOUR_USERNAME/$PROJECT_NAME.git"
echo "  git push -u origin main"
echo ""
echo "OR if you already have a remote:"
echo "  git push origin main"
echo ""
echo "██████████████████████████████████████████████████████████████████"
echo ""
echo "After deployment, share your live URL with anyone!"
echo ""
echo "Demo Account:"
echo "  Email:    admin@foodbridge.org"
echo "  Password: admin123"
echo ""
echo "██████████████████████████████████████████████████████████████████"
