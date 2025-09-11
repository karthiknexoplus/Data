#!/bin/bash

echo "🔧 Fixing API and NRLM scraper issues..."

# First, let's check if the API endpoints have login_required decorators
echo "📋 Checking API endpoint decorators..."
cd /var/www/data.nexoplus.in
source venv/bin/activate

python3 -c "
import app
import inspect

# Check the API endpoints
api_endpoints = ['/api/states', '/api/districts', '/api/blocks', '/api/grampanchayats', '/api/villages', '/api/shg-members']

for endpoint in api_endpoints:
    try:
        # Get the function for this endpoint
        for rule in app.app.url_map.iter_rules():
            if rule.rule == endpoint:
                endpoint_func = app.app.view_functions[rule.endpoint]
                print(f'📋 {endpoint}: {endpoint_func.__name__}')
                
                # Check if it has login_required decorator
                if hasattr(endpoint_func, '__wrapped__'):
                    print(f'  ⚠️  Has decorator (likely @login_required)')
                else:
                    print(f'  ✅ No decorator')
                break
    except Exception as e:
        print(f'❌ Error checking {endpoint}: {e}')
"

echo ""
echo "🧪 Testing NRLM website access..."

python3 -c "
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

print('📋 Testing NRLM website access...')

# Create a session with proper headers
session = requests.Session()

# Add retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount('http://', adapter)
session.mount('https://', adapter)

# Set headers to mimic a real browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

try:
    # Test the main NRLM page
    print('📋 Testing main NRLM page...')
    response = session.get('https://nrlm.gov.in/', headers=headers, timeout=30)
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        print('✅ Main page accessible')
        
        # Test the specific endpoint
        print('📋 Testing NRLM API endpoint...')
        api_url = 'https://nrlm.gov.in/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd=0'
        response = session.get(api_url, headers=headers, timeout=30)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            print('✅ API endpoint accessible')
        else:
            print(f'❌ API endpoint failed: {response.status_code}')
            print(f'Response: {response.text[:200]}')
    else:
        print(f'❌ Main page failed: {response.status_code}')
        
except Exception as e:
    print(f'❌ Error: {e}')
"

echo ""
echo "🔧 Creating a fix for the API endpoints..."

# Create a simple test to see if we can make the API work without login
python3 -c "
import app
from flask import session

print('📋 Testing API endpoints with mock session...')

# Create a test client
with app.app.test_client() as client:
    # Try to set a session (mock login)
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'test'
    
    # Test the states endpoint
    response = client.get('/api/states')
    print(f'States API Status: {response.status_code}')
    
    if response.status_code == 200:
        print('✅ States API working with session')
        print(f'Response: {response.get_data(as_text=True)[:200]}')
    else:
        print(f'❌ States API still failing: {response.status_code}')
        print(f'Response: {response.get_data(as_text=True)[:200]}')
"

echo ""
echo "🔍 Summary of findings:"
echo "1. API endpoints likely have @login_required decorator"
echo "2. NRLM website may be blocking requests or changed"
echo "3. Need to either remove login requirement or fix NRLM scraper"
