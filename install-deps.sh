#!/bin/bash

echo "📦 Installing missing Python dependencies..."

# Activate virtual environment
cd /var/www/data.nexoplus.in
source venv/bin/activate

echo "🔍 Current installed packages:"
pip list

echo ""
echo "📦 Installing pandas and other common dependencies..."
pip install pandas numpy openpyxl xlsxwriter

echo ""
echo "📦 Installing additional Flask dependencies that might be needed..."
pip install flask-sqlalchemy flask-migrate flask-wtf flask-login

echo ""
echo "🧪 Testing Flask app import again..."
python3 -c "
try:
    import app
    print('✅ Flask app imports successfully!')
except Exception as e:
    print(f'❌ Flask app import failed: {e}')
    print('📋 Trying to import individual modules...')
    
    # Test individual imports
    modules_to_test = ['flask', 'pandas', 'requests', 'bs4', 'sqlite3']
    for module in modules_to_test:
        try:
            __import__(module)
            print(f'✅ {module} - OK')
        except ImportError as ie:
            print(f'❌ {module} - {ie}')
"

echo ""
echo "🔄 Restarting Flask service..."
sudo systemctl restart data-nexoplus
sleep 3

if sudo systemctl is-active --quiet data-nexoplus; then
    echo "✅ Flask service is running!"
    echo "🌐 Your app should be accessible at: http://data.nexoplus.in:8080"
    
    # Test the app endpoint
    echo ""
    echo "🧪 Testing app endpoint..."
    curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/ || echo "Connection failed"
    
else
    echo "❌ Flask service failed to start"
    echo "📋 Service logs:"
    sudo journalctl -u data-nexoplus --no-pager -l -n 15
fi

echo ""
echo "📋 Final service status:"
sudo systemctl status data-nexoplus --no-pager -l
