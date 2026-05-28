#!/bin/bash

echo "=========================================================================="
echo "           FOODBRIDGE - PRODUCTION BUILD VERIFICATION"
echo "=========================================================================="
echo ""

echo "1. Checking Python files syntax..."
python3 -m py_compile app.py models.py wsgi.py 2>&1
if [ $? -eq 0 ]; then
    echo "   ✓ All Python files have valid syntax"
else
    echo "   ✗ Syntax errors found"
    exit 1
fi
echo ""

echo "2. Checking deployment files..."
files_ok=true
for file in Procfile runtime.txt wsgi.py requirements.txt .env.example; do
    if [ -f "$file" ]; then
        size=$(wc -c < "$file")
        echo "   ✓ $file exists ($size bytes)"
    else
        echo "   ✗ $file missing"
        files_ok=false
    fi
done

if [ "$files_ok" = false ]; then
    exit 1
fi
echo ""

echo "3. Checking requirements.txt structure..."
if grep -q "gunicorn" requirements.txt && grep -q "Flask" requirements.txt && grep -q "psycopg2" requirements.txt; then
    echo "   ✓ requirements.txt contains all production dependencies"
else
    echo "   ✗ requirements.txt missing dependencies"
    exit 1
fi
echo ""

echo "4. Checking Procfile format..."
if grep -q "^web:" Procfile; then
    echo "   ✓ Procfile has correct 'web:' process definition"
else
    echo "   ✗ Procfile format incorrect"
    exit 1
fi
echo ""

echo "5. Checking runtime.txt..."
python_version=$(cat runtime.txt)
echo "   ✓ Python version: $python_version"
echo ""

echo "6. Checking environment variable template..."
if grep -q "SECRET_KEY" .env.example && grep -q "DATABASE_URL" .env.example; then
    echo "   ✓ .env.example has required variables"
else
    echo "   ✗ .env.example missing variables"
    exit 1
fi
echo ""

echo "7. Checking app.py configuration..."
if grep -q "DATABASE_URL" app.py && grep -q "load_dotenv" app.py; then
    echo "   ✓ app.py configured for production environment"
else
    echo "   ✗ app.py not configured properly"
    exit 1
fi
echo ""

echo "8. Checking static files and templates..."
if [ -d "static" ] && [ -d "templates" ]; then
    static_count=$(find static -type f | wc -l)
    template_count=$(find templates -type f -name "*.html" | wc -l)
    echo "   ✓ Static files: $static_count"
    echo "   ✓ Templates: $template_count"
else
    echo "   ✗ Missing static or templates directories"
    exit 1
fi
echo ""

echo "=========================================================================="
echo "                    ALL CHECKS PASSED ✓"
echo "=========================================================================="
echo ""
echo "Your application is ready to deploy!"
echo ""
echo "Next steps:"
echo "  1. Push to GitHub: git push origin main"
echo "  2. Go to https://railway.app (or render.com)"
echo "  3. Deploy from GitHub repository"
echo "  4. Add SECRET_KEY environment variable"
echo "  5. Get live URL in 2-5 minutes"
echo ""
echo "=========================================================================="
