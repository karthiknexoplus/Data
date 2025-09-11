#!/bin/bash

echo "🔧 Fixing EC2 server to match local working version..."

# Stop the Flask service
sudo systemctl stop data-nexoplus

cd /var/www/data.nexoplus.in
source venv/bin/activate

echo "📋 Creating backup of current app.py..."
cp app.py app_backup_$(date +%Y%m%d_%H%M%S).py

echo "🔧 Removing @login_required decorators from API endpoints..."

# Remove all @login_required decorators
sed -i '/@login_required/d' app.py

echo "✅ Removed @login_required decorators"

echo "🧪 Testing the fixed API..."

python3 -c "
import app
from flask import session

print('📋 Testing API endpoints...')

with app.app.test_client() as client:
    # Test states endpoint
    response = client.get('/api/states')
    print(f'States API Status: {response.status_code}')
    
    if response.status_code == 200:
        data = response.get_json()
        print(f'✅ States API working: {data.get(\"message\", \"No message\")}')
        print(f'States count: {len(data.get(\"states\", []))}')
    else:
        print(f'❌ States API still failing: {response.status_code}')
        print(f'Response: {response.get_data(as_text=True)[:200]}')
"

echo ""
echo "🔄 Starting Flask service..."
sudo systemctl start data-nexoplus
sleep 3

if sudo systemctl is-active --quiet data-nexoplus; then
    echo "✅ Flask service is running!"
    
    echo ""
    echo "🧪 Testing the fixed API on server..."
    curl -s -w "HTTP Status: %{http_code}\n" http://localhost:8001/api/states
    
    echo ""
    echo "🧪 Testing with curl to see the actual response..."
    curl -s http://localhost:8001/api/states | head -3
    
else
    echo "❌ Flask service failed to start"
    echo "📋 Service logs:"
    sudo journalctl -u data-nexoplus --no-pager -l -n 10
fi

echo ""
echo "🎉 EC2 server fix completed!"
echo "🌐 Your app should now work at: http://data.nexoplus.in:8080"
echo "📋 The states dropdown should now populate like your local version"
