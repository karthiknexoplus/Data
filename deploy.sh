#!/bin/bash

# Deployment script for data.nexoplus.in
# This script sets up Flask app with nginx, gunicorn, and SSL

set -e  # Exit on any error

echo "🚀 Starting deployment for data.nexoplus.in..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="data-nexoplus"
PROJECT_DIR="/var/www/data.nexoplus.in"
VENV_DIR="/var/www/data.nexoplus.in/venv"
DOMAIN="data.nexoplus.in"
USER="ubuntu"  # Change to your EC2 user
GITHUB_REPO="your-repo-url"  # Update with your actual repo

echo -e "${BLUE}📋 Configuration:${NC}"
echo "Project: $PROJECT_NAME"
echo "Domain: $DOMAIN"
echo "Directory: $PROJECT_DIR"
echo "Virtual Environment: $VENV_DIR"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Update system packages
echo -e "${BLUE}📦 Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y
print_status "System packages updated"

# Install required system packages
echo -e "${BLUE}📦 Installing required packages...${NC}"
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git
print_status "Required packages installed"

# Create project directory
echo -e "${BLUE}📁 Creating project directory...${NC}"
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR
print_status "Project directory created"

# Clone or copy project files
echo -e "${BLUE}📥 Setting up project files...${NC}"
if [ -d "$PROJECT_DIR/.git" ]; then
    cd $PROJECT_DIR
    git pull origin main
    print_status "Project files updated from git"
else
    # If you have the files locally, copy them
    # cp -r /path/to/your/local/project/* $PROJECT_DIR/
    # Or clone from git
    # git clone $GITHUB_REPO $PROJECT_DIR
    print_warning "Please copy your project files to $PROJECT_DIR"
    print_warning "Or update GITHUB_REPO variable and uncomment git clone line"
fi

# Create virtual environment
echo -e "${BLUE}🐍 Creating virtual environment...${NC}"
cd $PROJECT_DIR
python3 -m venv venv
source venv/bin/activate
print_status "Virtual environment created"

# Install Python dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install flask gunicorn requests beautifulsoup4
print_status "Python dependencies installed"

# Create gunicorn configuration
echo -e "${BLUE}⚙️  Creating Gunicorn configuration...${NC}"
cat > $PROJECT_DIR/gunicorn.conf.py << 'GUNICORN_EOF'
# Gunicorn configuration file
bind = "127.0.0.1:8001"
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
user = "ubuntu"
group = "ubuntu"
tmp_upload_dir = None
errorlog = "/var/log/gunicorn/data-nexoplus-error.log"
accesslog = "/var/log/gunicorn/data-nexoplus-access.log"
loglevel = "info"
GUNICORN_EOF
print_status "Gunicorn configuration created"

# Create systemd service
echo -e "${BLUE}🔧 Creating systemd service...${NC}"
sudo tee /etc/systemd/system/data-nexoplus.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=Gunicorn instance to serve data.nexoplus.in
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/data.nexoplus.in
Environment="PATH=/var/www/data.nexoplus.in/venv/bin"
ExecStart=/var/www/data.nexoplus.in/venv/bin/gunicorn --config gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE_EOF
print_status "Systemd service created"

# Create log directory
echo -e "${BLUE}📝 Creating log directory...${NC}"
sudo mkdir -p /var/log/gunicorn
sudo chown ubuntu:ubuntu /var/log/gunicorn
print_status "Log directory created"

# Configure nginx
echo -e "${BLUE}🌐 Configuring Nginx...${NC}"
sudo tee /etc/nginx/sites-available/data.nexoplus.in > /dev/null << 'NGINX_EOF'
server {
    listen 80;
    server_name data.nexoplus.in;

    # Redirect all HTTP requests to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name data.nexoplus.in;

    # SSL Configuration (will be updated by certbot)
    ssl_certificate /etc/letsencrypt/live/data.nexoplus.in/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/data.nexoplus.in/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;

    # Static files
    location /static {
        alias /var/www/data.nexoplus.in/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Main application
    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
NGINX_EOF
print_status "Nginx configuration created"

# Enable the site
echo -e "${BLUE}🔗 Enabling Nginx site...${NC}"
sudo ln -sf /etc/nginx/sites-available/data.nexoplus.in /etc/nginx/sites-enabled/
sudo nginx -t
print_status "Nginx site enabled"

# Start and enable services
echo -e "${BLUE}🚀 Starting services...${NC}"
sudo systemctl daemon-reload
sudo systemctl start data-nexoplus
sudo systemctl enable data-nexoplus
sudo systemctl restart nginx
print_status "Services started"

# Setup SSL with Let's Encrypt
echo -e "${BLUE}🔒 Setting up SSL certificate...${NC}"
print_warning "Make sure your domain data.nexoplus.in points to this server's IP address"
read -p "Press Enter to continue with SSL setup..."

sudo certbot --nginx -d data.nexoplus.in --non-interactive --agree-tos --email admin@nexoplus.in
print_status "SSL certificate installed"

# Setup automatic SSL renewal
echo -e "${BLUE}🔄 Setting up SSL auto-renewal...${NC}"
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
print_status "SSL auto-renewal configured"

# Create deployment script
echo -e "${BLUE}📝 Creating deployment script...${NC}"
cat > $PROJECT_DIR/deploy-update.sh << 'UPDATE_EOF'
#!/bin/bash
# Quick deployment update script

echo "🔄 Updating data.nexoplus.in..."

cd /var/www/data.nexoplus.in

# Pull latest changes (if using git)
# git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Restart services
sudo systemctl restart data-nexoplus
sudo systemctl reload nginx

echo "✅ Deployment update completed!"
UPDATE_EOF

chmod +x $PROJECT_DIR/deploy-update.sh
print_status "Deployment update script created"

# Create requirements.txt
echo -e "${BLUE}📋 Creating requirements.txt...${NC}"
cat > $PROJECT_DIR/requirements.txt << 'REQ_EOF'
Flask==2.3.3
gunicorn==21.2.0
requests==2.31.0
beautifulsoup4==4.12.2
urllib3==2.0.4
REQ_EOF
print_status "Requirements.txt created"

# Set proper permissions
echo -e "${BLUE}🔐 Setting permissions...${NC}"
sudo chown -R ubuntu:www-data $PROJECT_DIR
sudo chmod -R 755 $PROJECT_DIR
sudo chmod -R 755 $PROJECT_DIR/static
print_status "Permissions set"

# Check service status
echo -e "${BLUE}🔍 Checking service status...${NC}"
sudo systemctl status data-nexoplus --no-pager -l
sudo systemctl status nginx --no-pager -l

# Final instructions
echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo "1. Copy your Flask application files to: $PROJECT_DIR"
echo "2. Update the database and run migrations if needed"
echo "3. Test the application: https://data.nexoplus.in"
echo ""
echo -e "${BLUE}🔧 Useful commands:${NC}"
echo "• Check service status: sudo systemctl status data-nexoplus"
echo "• View logs: sudo journalctl -u data-nexoplus -f"
echo "• Restart service: sudo systemctl restart data-nexoplus"
echo "• Update deployment: $PROJECT_DIR/deploy-update.sh"
echo "• Check nginx status: sudo systemctl status nginx"
echo "• View nginx logs: sudo tail -f /var/log/nginx/error.log"
echo ""
echo -e "${BLUE}🌐 Your application will be available at:${NC}"
echo "• HTTP: http://data.nexoplus.in (redirects to HTTPS)"
echo "• HTTPS: https://data.nexoplus.in"
echo ""
echo -e "${GREEN}✅ Deployment script completed!${NC}"
