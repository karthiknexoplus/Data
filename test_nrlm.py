import requests
from bs4 import BeautifulSoup
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_nrlm_connection():
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
    })
    
    try:
        url = "https://nrlm.gov.in/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd=0"
        print(f"Testing connection to: {url}")
        
        response = session.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.text)}")
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for state dropdown
        state_select = soup.find('select', {'name': 'stateCode'})
        if state_select:
            print("Found state dropdown!")
            options = state_select.find_all('option')
            print(f"Number of state options: {len(options)}")
            for i, option in enumerate(options[:5]):  # Show first 5
                print(f"  {i+1}. {option.get('value')} - {option.get_text(strip=True)}")
        else:
            print("No state dropdown found!")
            # Look for any select elements
            selects = soup.find_all('select')
            print(f"Found {len(selects)} select elements:")
            for i, select in enumerate(selects):
                print(f"  Select {i+1}: name='{select.get('name')}', id='{select.get('id')}'")
        
        # Look for any forms
        forms = soup.find_all('form')
        print(f"Found {len(forms)} forms:")
        for i, form in enumerate(forms):
            print(f"  Form {i+1}: action='{form.get('action')}', method='{form.get('method')}'")
        
        # Save a sample of the HTML for inspection
        with open('nrlm_sample.html', 'w', encoding='utf-8') as f:
            f.write(response.text[:5000])  # First 5000 characters
        print("Saved sample HTML to nrlm_sample.html")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_nrlm_connection()
