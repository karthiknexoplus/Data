#!/bin/bash

# Quick EC2 setup script for data.nexoplus.in
# Run this on your EC2 server

echo "🚀 Setting up data.nexoplus.in on EC2..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git

# Create project directory
sudo mkdir -p /var/www/data.nexoplus.in
sudo chown ubuntu:ubuntu /var/www/data.nexoplus.in

# Create virtual environment
cd /var/www/data.nexoplus.in
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install Flask==2.3.3 gunicorn==21.2.0 requests==2.31.0 beautifulsoup4==4.12.2

echo "✅ Basic setup completed!"
echo "📁 Project directory: /var/www/data.nexoplus.in"
echo "🐍 Virtual environment: /var/www/data.nexoplus.in/venv"
echo ""
echo "Next steps:"
echo "1. Copy your Flask app files to /var/www/data.nexoplus.in"
echo "2. Run the full deployment script: ./deploy.sh"
