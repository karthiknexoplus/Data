#!/bin/bash

echo "🔒 Setting up SSL properly - step by step..."

# Stop nginx first
sudo systemctl stop nginx

# Remove the problematic site
sudo rm -f /etc/nginx/sites-enabled/data.nexoplus.in

# Create a basic nginx configuration WITHOUT SSL first
echo "⚙️  Creating basic nginx configuration (no SSL)..."
sudo tee /etc/nginx/sites-available/data.nexoplus.in > /dev/null << 'NGINX_EOF'
server {
    listen 80;
    server_name data.nexoplus.in;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Gzip compression
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
    
    # Start nginx
    sudo systemctl start nginx
    echo "✅ Nginx started successfully"
    
    # Wait a moment for nginx to start
    sleep 2
    
    # Check if nginx is running
    if sudo systemctl is-active --quiet nginx; then
        echo "✅ Nginx is running"
        
        echo ""
        echo "🔒 Now running SSL setup..."
        echo "📋 This will automatically add SSL configuration to nginx"
        
        # Run certbot to get SSL certificate and update nginx config
        sudo certbot --nginx -d data.nexoplus.in --non-interactive --agree-tos --email admin@nexoplus.in
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "🎉 SSL setup completed successfully!"
            echo "🌐 Your app is now accessible at: https://data.nexoplus.in"
            echo "🔄 HTTP requests will automatically redirect to HTTPS"
        else
            echo "❌ SSL setup failed"
            echo "📋 Check the error messages above"
            echo "🌐 Your app is still accessible at: http://data.nexoplus.in:8080"
        fi
        
    else
        echo "❌ Nginx failed to start"
        echo "📋 Nginx status:"
        sudo systemctl status nginx --no-pager -l
    fi
    
else
    echo "❌ Nginx configuration test failed"
    echo "📋 Check the nginx configuration manually"
fi

echo ""
echo "📋 Final nginx status:"
sudo systemctl status nginx --no-pager -l

echo ""
echo "📋 Final Flask service status:"
sudo systemctl status data-nexoplus --no-pager -l
