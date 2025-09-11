#!/bin/bash

echo "🔧 Quick fix for deployment issues..."

# Stop services first
echo "🛑 Stopping services..."
sudo systemctl stop data-nexoplus
sudo systemctl stop nginx

# Check if your existing nexoplus.in is using port 80/443
echo "🔍 Checking port conflicts..."
if sudo netstat -tlnp | grep -q ":80.*nginx"; then
    echo "⚠️  Port 80 is already in use by existing nginx"
    echo "📋 Current nginx sites:"
    ls -la /etc/nginx/sites-enabled/
fi

# Fix nginx configuration to use different ports if needed
echo "🔧 Creating nginx config with different ports..."
sudo tee /etc/nginx/sites-available/data.nexoplus.in > /dev/null << 'NGINX_EOF'
server {
    listen 8080;
    server_name data.nexoplus.in;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
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

# Test nginx configuration
echo "🧪 Testing nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
    
    # Enable the site
    sudo ln -sf /etc/nginx/sites-available/data.nexoplus.in /etc/nginx/sites-enabled/
    
    # Start nginx
    sudo systemctl start nginx
    echo "✅ Nginx started"
    
    # Check if Flask app exists and is working
    if [ -f "/var/www/data.nexoplus.in/app.py" ]; then
        echo "✅ Flask app found"
        
        # Start Flask service
        sudo systemctl start data-nexoplus
        sleep 2
        
        # Check service status
        if sudo systemctl is-active --quiet data-nexoplus; then
            echo "✅ Flask service is running"
        else
            echo "❌ Flask service failed to start"
            echo "📋 Flask service logs:"
            sudo journalctl -u data-nexoplus --no-pager -l -n 10
        fi
    else
        echo "❌ Flask app not found at /var/www/data.nexoplus.in/app.py"
        echo "📋 Please copy your Flask app files to the server"
    fi
    
else
    echo "❌ Nginx configuration test failed"
    exit 1
fi

echo ""
echo "🎉 Quick fix completed!"
echo "🌐 Your app should be accessible at: http://data.nexoplus.in:8080"
echo "🔍 Check status with: sudo systemctl status data-nexoplus"
