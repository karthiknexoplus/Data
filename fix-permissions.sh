#!/bin/bash

echo "🔧 Fixing gunicorn permission issues..."

# Stop the service
sudo systemctl stop data-nexoplus

# Create a custom tmp directory for gunicorn
echo "📁 Creating custom tmp directory for gunicorn..."
sudo mkdir -p /var/www/data.nexoplus.in/tmp
sudo chown ubuntu:ubuntu /var/www/data.nexoplus.in/tmp
sudo chmod 755 /var/www/data.nexoplus.in/tmp

# Create a new gunicorn config that uses the custom tmp directory
echo "⚙️  Creating gunicorn config with custom tmp directory..."
cat > /var/www/data.nexoplus.in/gunicorn-fixed.conf.py << 'GUNICORN_EOF'
# Fixed gunicorn configuration
bind = "127.0.0.1:8001"
workers = 1
worker_class = "sync"
timeout = 30
keepalive = 2
preload_app = False
user = "ubuntu"
group = "ubuntu"
worker_tmp_dir = "/var/www/data.nexoplus.in/tmp"
errorlog = "/var/log/gunicorn/data-nexoplus-error.log"
accesslog = "/var/log/gunicorn/data-nexoplus-access.log"
loglevel = "info"
GUNICORN_EOF

echo "✅ Fixed gunicorn config created"

# Update the systemd service to use the fixed config
echo "🔧 Updating systemd service..."
sudo tee /etc/systemd/system/data-nexoplus.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=Gunicorn instance to serve data.nexoplus.in
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/data.nexoplus.in
Environment="PATH=/var/www/data.nexoplus.in/venv/bin"
Environment="TMPDIR=/var/www/data.nexoplus.in/tmp"
ExecStart=/var/www/data.nexoplus.in/venv/bin/gunicorn --config gunicorn-fixed.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE_EOF

echo "✅ Systemd service updated"

# Test the fixed configuration
echo "🧪 Testing fixed gunicorn configuration..."
cd /var/www/data.nexoplus.in
source venv/bin/activate

echo "📋 Running gunicorn with fixed config (will timeout after 10 seconds)..."
timeout 10s gunicorn --config gunicorn-fixed.conf.py app:app 2>&1 || echo "Fixed gunicorn test completed or timed out"

# Reload systemd and start the service
echo "🔄 Reloading systemd and starting service..."
sudo systemctl daemon-reload
sudo systemctl start data-nexoplus
sleep 3

if sudo systemctl is-active --quiet data-nexoplus; then
    echo "✅ Flask service is running!"
    echo "🌐 Your app should be accessible at: http://data.nexoplus.in:8080"
    
    # Test the app
    echo ""
    echo "🧪 Testing app endpoint..."
    curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8001/ || echo "Connection failed"
    
    # Show service status
    echo ""
    echo "📋 Service status:"
    sudo systemctl status data-nexoplus --no-pager -l
    
else
    echo "❌ Flask service still failed"
    echo "📋 Service logs:"
    sudo journalctl -u data-nexoplus --no-pager -l -n 15
fi

echo ""
echo "🎉 Permission fix completed!"
