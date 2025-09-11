import requests
from bs4 import BeautifulSoup
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def debug_districts_api():
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1'
    })
    
    try:
        # Step 1: Get initial page
        print("=== STEP 1: Getting initial page ===")
        url = "https://nrlm.gov.in/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd=0"
        response = session.get(url, timeout=30)
        print(f"Status: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find state dropdown
        state_select = soup.find('select', {'name': 'stateCode'})
        if state_select:
            options = state_select.find_all('option')
            print(f"Found {len(options)} state options")
            
            # Test with a few different states
            test_states = ['01', '02', '03']  # ANDAMAN, ANDHRA PRADESH, ARUNACHAL PRADESH
            
            for state_code in test_states:
                state_name = None
                for option in options:
                    if option.get('value') == state_code:
                        state_name = option.get_text(strip=True)
                        break
                
                print(f"\n=== Testing State: {state_name} (Code: {state_code}) ===")
                
                # Step 2: Get districts
                print("Getting districts...")
                district_url = "https://nrlm.gov.in/BlockWiseSHGMemebrsAction.do"
                district_data = {
                    'methodName': 'getDistrictList',
                    'stateCode': state_code
                }
                
                print(f"POST URL: {district_url}")
                print(f"POST Data: {district_data}")
                
                district_response = session.post(district_url, data=district_data, timeout=30)
                print(f"District response status: {district_response.status_code}")
                print(f"District response length: {len(district_response.text)}")
                print(f"District response content (first 500 chars):")
                print(district_response.text[:500])
                print("...")
                
                # Parse district response
                district_soup = BeautifulSoup(district_response.text, 'html.parser')
                district_options = district_soup.find_all('option')
                print(f"Found {len(district_options)} district options")
                
                if len(district_options) > 0:
                    print("District options:")
                    for i, option in enumerate(district_options[:10]):  # Show first 10
                        print(f"  {i+1}. Value: '{option.get('value')}', Text: '{option.get_text(strip=True)}'")
                
                # Save the response for inspection
                with open(f'district_response_{state_code}.html', 'w', encoding='utf-8') as f:
                    f.write(district_response.text)
                print(f"Saved district response to district_response_{state_code}.html")
                
                # Try a different approach - maybe we need to include more headers
                print("\n--- Trying with different headers ---")
                session.headers.update({
                    'Referer': 'https://nrlm.gov.in/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd=0',
                    'Origin': 'https://nrlm.gov.in',
                    'X-Requested-With': 'XMLHttpRequest'
                })
                
                district_response2 = session.post(district_url, data=district_data, timeout=30)
                print(f"District response2 status: {district_response2.status_code}")
                print(f"District response2 length: {len(district_response2.text)}")
                print(f"District response2 content (first 500 chars):")
                print(district_response2.text[:500])
                
                if len(district_response2.text) != len(district_response.text):
                    print("Different response with updated headers!")
                    with open(f'district_response2_{state_code}.html', 'w', encoding='utf-8') as f:
                        f.write(district_response2.text)
                
                break  # Only test first state for now
        else:
            print("No state dropdown found!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_districts_api()
