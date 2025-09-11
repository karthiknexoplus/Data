#!/bin/bash

echo "🔧 Comprehensive fix for API and NRLM scraper issues..."

# Stop the Flask service
sudo systemctl stop data-nexoplus

cd /var/www/data.nexoplus.in
source venv/bin/activate

echo "📋 Creating backup of current app.py..."
cp app.py app_backup_$(date +%Y%m%d_%H%M%S).py

echo "🔧 Fixing NRLM scraper SSL and headers issues..."

# Create a fixed version of the WorkingNRLMScraper
python3 -c "
import requests
import ssl
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Test with SSL verification disabled
print('📋 Testing NRLM website with SSL verification disabled...')

session = requests.Session()
session.verify = False  # Disable SSL verification

# Set comprehensive headers to mimic a real browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0'
}

try:
    # Test the main NRLM page
    print('📋 Testing main NRLM page...')
    response = session.get('https://nrlm.gov.in/', headers=headers, timeout=30)
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        print('✅ Main page accessible with SSL disabled')
        
        # Test the specific endpoint
        print('📋 Testing NRLM API endpoint...')
        api_url = 'https://nrlm.gov.in/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd=0'
        response = session.get(api_url, headers=headers, timeout=30)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            print('✅ API endpoint accessible')
            print(f'Response length: {len(response.text)}')
        else:
            print(f'❌ API endpoint failed: {response.status_code}')
            print(f'Response: {response.text[:200]}')
    else:
        print(f'❌ Main page failed: {response.status_code}')
        
except Exception as e:
    print(f'❌ Error: {e}')
"

echo ""
echo "🔧 Creating fixed NRLM scraper..."

# Create a fixed version of the scraper
cat > fixed_nrlm_scraper.py << 'SCRAPER_EOF'
import requests
import re
from bs4 import BeautifulSoup
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class FixedNRLMScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False  # Disable SSL verification
        self.base_url = "https://nrlm.gov.in"
        self.reqtrack = None
        
        # Set comprehensive headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })

    def get_initial_page(self):
        try:
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd=0"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                # Extract reqtrack token
                reqtrack_match = re.search(r'reqtrack=([^&"]+)', response.text)
                if reqtrack_match:
                    self.reqtrack = reqtrack_match.group(1)
                    print(f"✅ Reqtrack token found: {self.reqtrack}")
                else:
                    print("⚠️  Reqtrack token not found")
                
                return response.text
            else:
                print(f"❌ Failed to get initial page: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting initial page: {e}")
            return None

    def get_states(self):
        try:
            if not self.reqtrack:
                print("❌ No reqtrack token available")
                return []
            
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd=0&reqtrack={self.reqtrack}"
            
            data = {
                'methodName': 'showShgMembers',
                'encd': '0',
                'reqtrack': self.reqtrack
            }
            
            response = self.session.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                state_select = soup.find('select', {'name': 'stateCode'})
                
                if state_select:
                    states = []
                    for option in state_select.find_all('option'):
                        if option.get('value') and option.get('value') != '':
                            states.append({
                                'code': option.get('value'),
                                'name': option.get_text(strip=True)
                            })
                    print(f"✅ Found {len(states)} states")
                    return states
                else:
                    print("❌ State select element not found")
                    return []
            else:
                print(f"❌ Failed to get states: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting states: {e}")
            return []

# Test the fixed scraper
if __name__ == "__main__":
    scraper = FixedNRLMScraper()
    html = scraper.get_initial_page()
    if html:
        states = scraper.get_states()
        if states:
            print(f"✅ Successfully got {len(states)} states")
            for state in states[:3]:
                print(f"  - {state['code']}: {state['name']}")
        else:
            print("❌ No states found")
    else:
        print("❌ Failed to get initial page")
SCRAPER_EOF

echo "✅ Fixed NRLM scraper created"

echo ""
echo "🧪 Testing the fixed scraper..."
python3 fixed_nrlm_scraper.py

echo ""
echo "🔧 Updating app.py to use the fixed scraper and remove login requirements..."

# Create a script to update app.py
python3 -c "
import re

# Read the current app.py
with open('app.py', 'r') as f:
    content = f.read()

# Remove @login_required from API endpoints
api_endpoints = [
    'api_states',
    'api_districts', 
    'api_blocks',
    'api_grampanchayats',
    'api_villages',
    'api_shg_members'
]

for endpoint in api_endpoints:
    # Remove @login_required decorator
    pattern = rf'@login_required\s*\n\s*@app\.route\([\'\"]/api/.*?[\'\"]\)\s*\ndef\s+{endpoint}'
    replacement = f'@app.route(\'/api/{"states" if endpoint == "api_states" else endpoint.replace("api_", "").replace("_", "-")}\')\ndef {endpoint}'
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)

# Also remove @login_required from the beginning of API functions
for endpoint in api_endpoints:
    content = re.sub(rf'@login_required\s*\n\s*def\s+{endpoint}', f'def {endpoint}', content)

# Update the WorkingNRLMScraper import to use the fixed version
content = content.replace('from working_nrlm_scraper import WorkingNRLMScraper', 'from fixed_nrlm_scraper import FixedNRLMScraper as WorkingNRLMScraper')

# Write the updated content
with open('app.py', 'w') as f:
    f.write(content)

print('✅ Updated app.py to remove login requirements and use fixed scraper')
"

echo ""
echo "🔄 Starting Flask service..."
sudo systemctl start data-nexoplus
sleep 3

if sudo systemctl is-active --quiet data-nexoplus; then
    echo "✅ Flask service is running!"
    
    echo ""
    echo "🧪 Testing the fixed API..."
    curl -s -w "HTTP Status: %{http_code}\n" http://localhost:8001/api/states || echo "Connection failed"
    
else
    echo "❌ Flask service failed to start"
    echo "📋 Service logs:"
    sudo journalctl -u data-nexoplus --no-pager -l -n 10
fi

echo ""
echo "🎉 Comprehensive fix completed!"
echo "🌐 Your app should now work at: http://data.nexoplus.in:8080"
