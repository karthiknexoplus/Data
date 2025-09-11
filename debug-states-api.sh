#!/bin/bash

echo "🔍 Debugging 'Failed to get states' error..."

# Check if Flask service is running
echo "�� Checking Flask service status..."
sudo systemctl status data-nexoplus --no-pager -l

echo ""
echo "🧪 Testing Flask app endpoints directly..."

# Test the states API endpoint
echo "📋 Testing /api/states endpoint..."
curl -s -w "HTTP Status: %{http_code}\n" http://localhost:8001/api/states || echo "Connection failed"

echo ""
echo "📋 Testing /api/states endpoint with verbose output..."
curl -v http://localhost:8001/api/states 2>&1 | head -20

echo ""
echo "🧪 Testing Flask app import and NRLM scraper..."

cd /var/www/data.nexoplus.in
source venv/bin/activate

python3 -c "
import app
print('✅ Flask app imported successfully')

# Test the states API function directly
try:
    from app import app as flask_app
    with flask_app.test_client() as client:
        print('📋 Testing /api/states endpoint...')
        response = client.get('/api/states')
        print(f'Status Code: {response.status_code}')
        print(f'Response Data: {response.get_data(as_text=True)[:500]}')
        
        if response.status_code != 200:
            print('❌ API endpoint returned error')
        else:
            print('✅ API endpoint working')
            
except Exception as e:
    print(f'❌ Error testing API: {e}')
    import traceback
    traceback.print_exc()
"

echo ""
echo "🧪 Testing NRLM scraper directly..."

python3 -c "
try:
    # Import the WorkingNRLMScraper class
    from app import WorkingNRLMScraper
    print('✅ WorkingNRLMScraper imported successfully')
    
    # Test creating a scraper instance
    scraper = WorkingNRLMScraper()
    print('✅ Scraper instance created')
    
    # Test getting initial page
    print('📋 Testing get_initial_page()...')
    html = scraper.get_initial_page()
    if html:
        print(f'✅ Initial page loaded, length: {len(html)}')
        
        # Test getting states
        print('📋 Testing get_states()...')
        states = scraper.get_states()
        if states:
            print(f'✅ States loaded: {len(states)} states found')
            for i, state in enumerate(states[:3]):  # Show first 3 states
                print(f'  {i+1}. {state}')
        else:
            print('❌ No states found')
    else:
        print('❌ Failed to load initial page')
        
except Exception as e:
    print(f'❌ Error testing scraper: {e}')
    import traceback
    traceback.print_exc()
"

echo ""
echo "📋 Checking Flask app logs..."
sudo journalctl -u data-nexoplus --no-pager -l -n 20

echo ""
echo "📋 Checking nginx logs..."
sudo tail -10 /var/log/nginx/error.log

echo ""
echo "🔍 Summary - look for any error messages above"
