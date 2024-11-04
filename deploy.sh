#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Update system and install required packages
sudo apt update
sudo apt install -y python3-venv python3-pip nginx git

# Change to home directory
cd $HOME

# Clone or update the repository
if [ ! -d "$HOME/baidakov.ru" ]; then
    git clone https://github.com/baidakovil/baidakov.ru.git $HOME/baidakov.ru
else
    cd $HOME/baidakov.ru
    git pull origin main
fi

cd $HOME/baidakov.ru

# Create and activate virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Install or upgrade all dependencies
pip install --upgrade -r requirements.txt

# Copy nginx configuration
sudo cp configs/nginx_config /etc/nginx/sites-available/baidakov.ru
sudo ln -sf /etc/nginx/sites-available/baidakov.ru /etc/nginx/sites-enabled/

# Remove default nginx site config
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Copy gunicorn systemd service file
sudo cp gunicornflaskapp.service /etc/systemd/system/

# Create and set up log folder
sudo mkdir -p /var/log/baidakov.ru
sudo chown -R $USER:$USER /var/log/baidakov.ru
sudo chmod 755 /var/log/baidakov.ru

# Reload systemd, restart gunicorn and nginx
sudo systemctl daemon-reload
sudo systemctl restart gunicornflaskapp
sudo systemctl enable gunicornflaskapp.service
sudo systemctl restart nginx

# Set up the database (if needed)
python db/create_database.py

echo "Deployment completed successfully!"