#!/bin/bash

echo "🔍 Diagnosing deployment issues..."

# Check nginx status and logs
echo "📋 Nginx Status:"
sudo systemctl status nginx --no-pager -l

echo ""
echo "📋 Nginx Error Logs:"
sudo tail -20 /var/log/nginx/error.log

echo ""
echo "📋 Flask Service Status:"
sudo systemctl status data-nexoplus --no-pager -l

echo ""
echo "📋 Flask Service Logs:"
sudo journalctl -u data-nexoplus --no-pager -l -n 20

echo ""
echo "📋 Check if port 8001 is in use:"
sudo netstat -tlnp | grep :8001

echo ""
echo "📋 Check if port 80/443 are in use:"
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

echo ""
echo "📋 Check project directory:"
ls -la /var/www/data.nexoplus.in/

echo ""
echo "📋 Check if app.py exists:"
ls -la /var/www/data.nexoplus.in/app.py

echo ""
echo "📋 Test Flask app manually:"
cd /var/www/data.nexoplus.in
source venv/bin/activate
python3 -c "import app; print('Flask app imports successfully')" 2>&1 || echo "Flask app import failed"

echo ""
echo "📋 Check gunicorn config:"
cat /var/www/data.nexoplus.in/gunicorn.conf.py
