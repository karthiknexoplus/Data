#!/bin/bash

# Fix nginx configuration for data.nexoplus.in

echo "🔧 Fixing nginx configuration..."

# Remove the problematic site
sudo rm -f /etc/nginx/sites-enabled/data.nexoplus.in

# Create corrected nginx configuration
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

    # Gzip compression (fixed)
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private auth;
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
    
    # Reload nginx
    sudo systemctl reload nginx
    echo "✅ Nginx reloaded successfully"
    
    # Start the Flask service
    sudo systemctl start data-nexoplus
    sudo systemctl enable data-nexoplus
    echo "✅ Flask service started"
    
    # Check service status
    echo "🔍 Checking service status..."
    sudo systemctl status data-nexoplus --no-pager -l
    
else
    echo "❌ Nginx configuration test failed"
    exit 1
fi

echo ""
echo "🎉 Nginx configuration fixed!"
echo "🌐 Your app should now be accessible at: http://data.nexoplus.in"
echo "🔒 Run SSL setup when ready: sudo certbot --nginx -d data.nexoplus.in"
