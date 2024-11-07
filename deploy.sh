#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define variables
APP_DIR="/var/www/baidakovru"
BACKUP_DIR="/var/backups/baidakovru"
GUNICORN_SERVICE_SRC="gunicornflaskapp.service"
GUNICORN_SERVICE_DEST="/etc/systemd/system/gunicornflaskapp.service"
LOG_DIR="/var/log/baidakovru"
NGINX_CONFIG_SRC="nginx.conf"
NGINX_CONFIG_DEST="/etc/nginx/nginx.conf"
REPO_URL="https://github.com/baidakovil/baidakovru.git"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
VENV_DIR="$APP_DIR/venv"

# Update system and install required packages
sudo apt update
sudo apt install -y python3-venv python3-pip nginx git

# Backup current version
sudo mkdir -p $BACKUP_DIR
sudo tar -czf $BACKUP_DIR/backup_$TIMESTAMP.tar.gz $APP_DIR 

# Rotate backups (keep only last 5)
sudo ls -t $BACKUP_DIR/backup_*.tar.gz | tail -n +6 | xargs sudo rm -f

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

# Create and set up .env file
echo "$ENV_FILE" > $APP_DIR/.env

# Set ownership and permissions of application directory
sudo chown -R www-data:www-data $APP_DIR
sudo chmod -R 755 $APP_DIR

# Create and set up log folder
sudo mkdir -p $LOG_DIR
sudo chown -R www-data:www-data $LOG_DIR
sudo chmod 755 $LOG_DIR

# Create or update the database
sudo -E $VENV_DIR/bin/python -m pyscripts.create_database

# Copy nginx configuration if changed
if ! cmp -s "$NGINX_CONFIG_SRC" "$NGINX_CONFIG_DEST"; then
    sudo cp "$NGINX_CONFIG_SRC" "$NGINX_CONFIG_DEST"
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

# Reload systemd, restart gunicorn and nginx
sudo systemctl daemon-reload
sudo systemctl restart gunicornflaskapp
sudo systemctl enable gunicornflaskapp.service
sudo systemctl restart nginx

echo "Deployment completed successfully"

# Test if the application is running
echo "Testing application..."
response=$(curl -sS -o /dev/null -w "%{http_code}" http://localhost)
if [ $response = "200" ]; then
    echo "Application is running successfully."
else
    echo "Error: Application is not running. HTTP status code: $response"
    exit 1
fi