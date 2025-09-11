#!/bin/bash

echo "📁 Copying Flask app files to deployment directory..."

# Create deployment directory if it doesn't exist
sudo mkdir -p /var/www/data.nexoplus.in
sudo chown ubuntu:ubuntu /var/www/data.nexoplus.in

# Copy all Flask app files from current directory to deployment directory
echo "📋 Copying files from $(pwd) to /var/www/data.nexoplus.in/"

# Copy main app files
sudo cp app.py /var/www/data.nexoplus.in/ 2>/dev/null || echo "⚠️  app.py not found in current directory"
sudo cp requirements.txt /var/www/data.nexoplus.in/ 2>/dev/null || echo "⚠️  requirements.txt not found"
sudo cp *.py /var/www/data.nexoplus.in/ 2>/dev/null || echo "⚠️  No Python files found"

# Copy templates directory
if [ -d "templates" ]; then
    sudo cp -r templates /var/www/data.nexoplus.in/
    echo "✅ Templates directory copied"
else
    echo "⚠️  Templates directory not found"
fi

# Copy static directory
if [ -d "static" ]; then
    sudo cp -r static /var/www/data.nexoplus.in/
    echo "✅ Static directory copied"
else
    echo "⚠️  Static directory not found"
fi

# Copy any other important files
sudo cp *.html /var/www/data.nexoplus.in/ 2>/dev/null || echo "⚠️  No HTML files found"
sudo cp *.db /var/www/data.nexoplus.in/ 2>/dev/null || echo "⚠️  No database files found"

# Set proper permissions
sudo chown -R ubuntu:www-data /var/www/data.nexoplus.in
sudo chmod -R 755 /var/www/data.nexoplus.in

echo ""
echo "📋 Files in deployment directory:"
ls -la /var/www/data.nexoplus.in/

echo ""
echo "🧪 Testing Flask app import..."
cd /var/www/data.nexoplus.in
source venv/bin/activate
python3 -c "import app; print('✅ Flask app imports successfully')" 2>&1 || echo "❌ Flask app import failed"

echo ""
echo "🚀 Starting Flask service..."
sudo systemctl start data-nexoplus
sleep 2

if sudo systemctl is-active --quiet data-nexoplus; then
    echo "✅ Flask service is running!"
    echo "🌐 Your app should be accessible at: http://data.nexoplus.in:8080"
else
    echo "❌ Flask service failed to start"
    echo "�� Service logs:"
    sudo journalctl -u data-nexoplus --no-pager -l -n 10
fi

echo ""
echo "🔍 Final status check:"
sudo systemctl status data-nexoplus --no-pager -l
