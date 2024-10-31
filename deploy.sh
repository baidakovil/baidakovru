#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Update system and install required packages
sudo apt update
sudo apt install -y python3-venv python3-pip nginx

# Change to home directory
cd $HOME

# Clone your git repository (replace with your actual repo URL)
git clone https://github.com/baidakovil/baidakov.ru.git $HOME/baidakov.ru
cd $HOME/baidakov.ru

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt

# Copy nginx configuration
sudo cp configs/nginx_config /etc/nginx/sites-available/baidakov.ru
sudo ln -s /etc/nginx/sites-available/baidakov.ru /etc/nginx/sites-enabled/

# Copy gunicorn systemd service file
sudo cp gunicornflaskapp.service /etc/systemd/system/

# Create and set up log folder
sudo mkdir -p /var/log/baidakov.ru
sudo chown -R $USER:$USER /var/log/baidakov.ru
sudo chmod 755 /var/log/baidakov.ru

# Start gunicorn service
sudo systemctl start gunicornflaskapp
sudo systemctl enable gunicornflaskapp.service

# Restart nginx
sudo systemctl restart nginx

# Set up the database (if needed)
python db/create_database.py

echo "Deployment completed successfully!"