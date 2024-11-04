#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define variables
APP_DIR="/var/www/baidakovru"
REPO_URL="https://github.com/baidakovil/baidakovru.git"
VENV_DIR="$APP_DIR/venv"
NGINX_CONFIG_SRC="nginx_config"
NGINX_CONFIG_DEST="/etc/nginx/sites-available/baidakovru"
GUNICORN_SERVICE_SRC="systemd/gunicornflaskapp.service"
GUNICORN_SERVICE_DEST="/etc/systemd/system/gunicornflaskapp.service"
LOG_DIR="/var/log/baidakovru"

# Update system and install required packages
sudo apt update
sudo apt install -y python3-venv python3-pip nginx git

# Clone or update the repository
if [ ! -d "$APP_DIR" ]; then
    sudo git clone $REPO_URL $APP_DIR
else
    cd $APP_DIR
    sudo git pull origin main
fi

cd $APP_DIR

# Create and activate virtual environment
if [ ! -d "$VENV_DIR" ]; then
    sudo python3 -m venv $VENV_DIR
fi
source $VENV_DIR/bin/activate

# Install or upgrade all dependencies
sudo $VENV_DIR/bin/pip install --upgrade -r requirements.txt

# Copy nginx configuration if changed
if ! cmp -s "$NGINX_CONFIG_SRC" "$NGINX_CONFIG_DEST"; then
    sudo cp "$NGINX_CONFIG_SRC" "$NGINX_CONFIG_DEST"
    sudo ln -sf "$NGINX_CONFIG_DEST" /etc/nginx/sites-enabled/
    echo "Nginx configuration updated."
else
    echo "Nginx configuration unchanged."
fi

# Remove default nginx site config
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Copy gunicorn systemd service file if changed
if ! cmp -s "$GUNICORN_SERVICE_SRC" "$GUNICORN_SERVICE_DEST"; then
    sudo cp "$GUNICORN_SERVICE_SRC" "$GUNICORN_SERVICE_DEST"
    echo "Gunicorn service file updated."
else
    echo "Gunicorn service file unchanged."
fi

# Create and set up log folder
sudo mkdir -p $LOG_DIR
sudo chown -R www-data:www-data $LOG_DIR
sudo chmod 755 $LOG_DIR

# Reload systemd, restart gunicorn and nginx
sudo systemctl daemon-reload
sudo systemctl restart gunicornflaskapp
sudo systemctl enable gunicornflaskapp.service
sudo systemctl restart nginx

echo "Deployment completed successfully!"