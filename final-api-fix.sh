#!/bin/bash

echo "🔧 Final fix for API endpoints - removing login requirements..."

# Stop the Flask service
sudo systemctl stop data-nexoplus

cd /var/www/data.nexoplus.in
source venv/bin/activate

echo "📋 Creating backup of current app.py..."
cp app.py app_backup_$(date +%Y%m%d_%H%M%S).py

echo "🔧 Removing @login_required from API endpoints..."

# Create a Python script to properly remove login requirements
python3 -c "
import re

# Read the current app.py
with open('app.py', 'r') as f:
    content = f.read()

print('📋 Removing @login_required decorators from API endpoints...')

# Find and remove @login_required from API endpoints
lines = content.split('\n')
new_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    
    # Check if this line has @login_required
    if '@login_required' in line:
        # Check if the next few lines contain an API route
        api_found = False
        for j in range(1, 5):  # Check next 5 lines
            if i + j < len(lines) and '/api/' in lines[i + j]:
                api_found = True
                break
        
        if api_found:
            print(f'Removing @login_required from line {i+1}')
            # Skip this line (don't add it to new_lines)
            i += 1
            continue
    
    new_lines.append(line)
    i += 1

# Write the updated content
with open('app.py', 'w') as f:
    f.write('\n'.join(new_lines))

print('✅ Removed @login_required from API endpoints')
"

echo ""
echo "🔧 Testing the API endpoints..."

# Test if the API endpoints work now
python3 -c "
import app
from flask import session

print('📋 Testing API endpoints without login...')

# Create a test client
with app.app.test_client() as client:
    # Test the states endpoint without session
    response = client.get('/api/states')
    print(f'States API Status: {response.status_code}')
    
    if response.status_code == 200:
        print('✅ States API working without login')
        data = response.get_json()
        print(f'Response: {data}')
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
    echo "🧪 Testing the fixed API..."
    curl -s -w "HTTP Status: %{http_code}\n" http://localhost:8001/api/states
    
    echo ""
    echo "🧪 Testing with curl to see the actual response..."
    curl -s http://localhost:8001/api/states | head -5
    
else
    echo "❌ Flask service failed to start"
    echo "📋 Service logs:"
    sudo journalctl -u data-nexoplus --no-pager -l -n 10
fi

echo ""
echo "🎉 Final API fix completed!"
echo "🌐 Your app should now work at: http://data.nexoplus.in:8080"
echo "📋 The states dropdown should now populate with sample data"
