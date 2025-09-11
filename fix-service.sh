#!/bin/bash

echo "🔧 Fixing Flask service issues..."

# Reset the service start limit
echo "🔄 Resetting service start limit..."
sudo systemctl reset-failed data-nexoplus

# Stop the service completely
echo "🛑 Stopping service..."
sudo systemctl stop data-nexoplus

# Test the Flask app manually to see what's wrong
echo "🧪 Testing Flask app manually..."
cd /var/www/data.nexoplus.in
source venv/bin/activate

echo "📋 Testing basic Flask import..."
python3 -c "
import sys
print('Python path:', sys.path)
print('Current directory:', sys.path[0])

try:
    import app
    print('✅ App imported successfully')
    
    # Try to access the app object
    if hasattr(app, 'app'):
        print('✅ Flask app object found')
        print('App name:', app.app.name)
    else:
        print('❌ Flask app object not found')
        
except Exception as e:
    print(f'❌ Import failed: {e}')
    import traceback
    traceback.print_exc()
"

echo ""
echo "🧪 Testing gunicorn directly..."
cd /var/www/data.nexoplus.in
source venv/bin/activate

# Test gunicorn with verbose output
echo "📋 Running gunicorn with debug output..."
timeout 10s gunicorn --config gunicorn.conf.py --log-level debug app:app 2>&1 || echo "Gunicorn test completed or timed out"

echo ""
echo "🔧 Checking gunicorn configuration..."
cat /var/www/data.nexoplus.in/gunicorn.conf.py

echo ""
echo "�� Checking if port 8001 is available..."
if command -v ss >/dev/null 2>&1; then
    ss -tlnp | grep :8001 || echo "Port 8001 is available"
else
    echo "ss command not available, checking with lsof..."
    lsof -i :8001 || echo "Port 8001 is available"
fi

echo ""
echo "🔧 Creating a simpler gunicorn config for testing..."
cat > /var/www/data.nexoplus.in/gunicorn-simple.conf.py << 'GUNICORN_EOF'
# Simple gunicorn configuration for testing
bind = "127.0.0.1:8001"
workers = 1
worker_class = "sync"
timeout = 30
keepalive = 2
preload_app = False
user = "ubuntu"
group = "ubuntu"
errorlog = "/var/log/gunicorn/data-nexoplus-error.log"
accesslog = "/var/log/gunicorn/data-nexoplus-access.log"
loglevel = "debug"
GUNICORN_EOF

echo "✅ Simple gunicorn config created"

echo ""
echo "🧪 Testing with simple config..."
timeout 10s gunicorn --config gunicorn-simple.conf.py app:app 2>&1 || echo "Simple gunicorn test completed or timed out"

echo ""
echo "🔧 Updating systemd service to use simple config..."
sudo tee /etc/systemd/system/data-nexoplus.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=Gunicorn instance to serve data.nexoplus.in
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/data.nexoplus.in
Environment="PATH=/var/www/data.nexoplus.in/venv/bin"
ExecStart=/var/www/data.nexoplus.in/venv/bin/gunicorn --config gunicorn-simple.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE_EOF

echo "✅ Systemd service updated"

echo ""
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
    
else
    echo "❌ Flask service still failed"
    echo "📋 Service logs:"
    sudo journalctl -u data-nexoplus --no-pager -l -n 20
fi

echo ""
echo "📋 Final service status:"
sudo systemctl status data-nexoplus --no-pager -l
