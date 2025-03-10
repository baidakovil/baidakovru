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
NGINX_SSL_CONFIG_SRC="nginx-ssl.conf"
NGINX_CONFIG_PATH="/etc/nginx/"
REPO_URL="https://github.com/baidakovil/baidakovru.git"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
VENV_DIR="$APP_DIR/venv"

# Update system and install required packages
sudo apt update
sudo apt install -y nginx python3-venv python3-pip python3-certbot-nginx git certbot

# Backup current version
sudo mkdir -p $BACKUP_DIR
sudo tar -czf $BACKUP_DIR/backup_$TIMESTAMP.tar.gz $APP_DIR 

# Rotate backups (keep only last 5)
sudo ls -t $BACKUP_DIR/backup_*.tar.gz | tail -n +6 | xargs sudo rm -f

# Clone or update the repository
if [ ! -d "$APP_DIR" ]; then
    echo "App dir $APP_DIR was not found. Something wrong. Exiting"
    exit 1
else
    echo "App dir $APP_DIR is found. Start git pull"
    # Set ownership and permissions of application directory
    sudo chown -R www-data:www-data $APP_DIR
    sudo chmod -R 2775 $APP_DIR
    cd $APP_DIR
    sudo -u www-data git stash
    sudo -u www-data git stash clear
    sudo -u www-data git pull origin main
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

# Source the .env file to load environment variables
source $APP_DIR/.env

# Set ownership and permissions of application directory
sudo chown -R www-data:www-data $APP_DIR
sudo chmod -R 2775 $APP_DIR

# Create and set up log folder
sudo mkdir -p $LOG_DIR
sudo chown -R www-data:www-data $LOG_DIR
sudo chmod -R 2775 $LOG_DIR

# Obtain SSL certificates if they do not already exist
if [ ! -f "/etc/letsencrypt/live/baidakov.ru/fullchain.pem" ]; then
    # Copy nginx configuration without SSL
    echo "SSL certificate was not found. Stop nginx and copy nginx configuration without SSL and restart nginx"
    # Remove nginx-ssl site config if exists
    sudo systemctl stop nginx
    sudo rm -f /var/run/nginx.pid
    sudo cp "$NGINX_CONFIG_SRC" "${NGINX_CONFIG_PATH}/${NGINX_CONFIG_SRC}"
    sudo systemctl start nginx

    # Run certbot to obtain SSL certificates
    echo "Executing certbot"
    sudo -E certbot --nginx -d baidakov.ru -d www.baidakov.ru --non-interactive --agree-tos --email "$CERTBOT_EMAIL"
    if [ $? -eq 0 ]; then
        echo "Certbot executed successful with email: $CERTBOT_EMAIL"
    else
        echo "Certbot command failed."
    fi
    
    echo "Start copying nginx configuration for SSL and reload nginx"
    sudo cp "$NGINX_SSL_CONFIG_SRC" "${NGINX_CONFIG_PATH}/${NGINX_SSL_CONFIG_SRC}"
    sudo nginx -s reload
else
    echo "SSL certificates already exist"
fi

# Copy nginx-nossl configuration if changed
if ! cmp -s "$NGINX_CONFIG_SRC" "${NGINX_CONFIG_PATH}/${NGINX_CONFIG_SRC}"; then
    sudo cp "$NGINX_CONFIG_SRC" "${NGINX_CONFIG_PATH}/${NGINX_CONFIG_SRC}"
    echo "Nginx-nossl configuration updated."
else
    echo "Nginx-nossl configuration unchanged."
fi

# Copy nginx-ssl configuration if changed
if ! cmp -s "$NGINX_SSL_CONFIG_SRC" "${NGINX_CONFIG_PATH}/${NGINX_SSL_CONFIG_SRC}"; then
    sudo cp "$NGINX_SSL_CONFIG_SRC" "${NGINX_CONFIG_PATH}/${NGINX_SSL_CONFIG_SRC}"
    echo "Nginx-ssl configuration updated."
else
    echo "Nginx-ssl configuration unchanged."
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
response=$(curl -sS -o /dev/null -w "%{http_code}" https://baidakov.ru)
if [ $response = "200" ]; then
    echo "Application is running successfully."
else
    echo "Error: Application is not running. HTTP status code: $response"
    exit 1
fi