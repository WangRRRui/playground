#!/bin/bash
# Deployment script for Blog with FastAPI backend
# Run this script on your server after uploading the project files

set -e

# Configuration
BLOG_DIR="/var/www/blog"
BACKEND_DIR="$BLOG_DIR/backend"
FRONTEND_DIR="$BLOG_DIR/website"

echo "=== Blog Deployment Script ==="

# Create directories
echo "[1/7] Creating directories..."
sudo mkdir -p $BLOG_DIR
sudo mkdir -p $BACKEND_DIR/data
sudo mkdir -p $BACKEND_DIR/uploads
sudo mkdir -p $FRONTEND_DIR
sudo chown -R $USER:www-data $BLOG_DIR

# Copy files (assuming you're running from project root)
echo "[2/7] Copying files..."
cp -r backend/* $BACKEND_DIR/
cp -r website/* $FRONTEND_DIR/

# Set up Python environment with uv
echo "[3/7] Setting up Python environment..."
cd $BACKEND_DIR
uv sync

# Set permissions
echo "[4/7] Setting permissions..."
sudo chown -R www-data:www-data $BACKEND_DIR/data
sudo chown -R www-data:www-data $BACKEND_DIR/uploads
chmod 755 $BACKEND_DIR/data
chmod 755 $BACKEND_DIR/uploads

# Configure environment
echo "[5/7] Configuring environment..."
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo "WARNING: .env file not found. Please configure it manually."
    echo "Generate a secure SECRET_KEY and set ADMIN_PASSWORD."
fi

# Set up Nginx
echo "[6/7] Configuring Nginx..."
sudo cp $BLOG_DIR/../deploy/nginx.conf /etc/nginx/sites-available/blog
sudo ln -sf /etc/nginx/sites-available/blog /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Set up Supervisor
echo "[7/7] Configuring Supervisor..."
sudo cp $BLOG_DIR/../deploy/supervisor.conf /etc/supervisor/conf.d/blog.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start blog-api

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit /etc/nginx/sites-available/blog and set your domain"
echo "2. Edit $BACKEND_DIR/.env and set secure credentials"
echo "3. Restart services: sudo systemctl restart nginx && sudo supervisorctl restart blog-api"
echo "4. (Optional) Set up SSL with: sudo certbot --nginx -d your-domain.com"
echo ""
echo "Test the API: curl http://localhost:8000/api/v1/health"
echo "Access admin: http://your-domain.com/admin/login.html"
