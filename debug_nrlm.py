import requests
from bs4 import BeautifulSoup
import urllib3
import time

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def debug_nrlm_scraping():
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
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
            
            # Get first real state (skip "All" option)
            for option in options[1:3]:  # Test first 2 states
                state_code = option.get('value')
                state_name = option.get_text(strip=True)
                print(f"\n=== Testing State: {state_name} (Code: {state_code}) ===")
                
                # Step 2: Get districts
                print("Getting districts...")
                district_url = "https://nrlm.gov.in/BlockWiseSHGMemebrsAction.do"
                district_data = {
                    'methodName': 'getDistrictList',
                    'stateCode': state_code
                }
                
                district_response = session.post(district_url, data=district_data, timeout=30)
                print(f"District response status: {district_response.status_code}")
                print(f"District response length: {len(district_response.text)}")
                
                # Parse district response
                district_soup = BeautifulSoup(district_response.text, 'html.parser')
                district_options = district_soup.find_all('option')
                print(f"Found {len(district_options)} district options")
                
                if len(district_options) > 1:  # Skip "All" option
                    for district_option in district_options[1:3]:  # Test first 2 districts
                        district_code = district_option.get('value')
                        district_name = district_option.get_text(strip=True)
                        print(f"\n--- Testing District: {district_name} (Code: {district_code}) ---")
                        
                        # Step 3: Get blocks
                        print("Getting blocks...")
                        block_data = {
                            'methodName': 'getBlockList',
                            'stateCode': state_code,
                            'districtCode': district_code
                        }
                        
                        block_response = session.post(district_url, data=block_data, timeout=30)
                        print(f"Block response status: {block_response.status_code}")
                        print(f"Block response length: {len(block_response.text)}")
                        
                        # Parse block response
                        block_soup = BeautifulSoup(block_response.text, 'html.parser')
                        block_options = block_soup.find_all('option')
                        print(f"Found {len(block_options)} block options")
                        
                        if len(block_options) > 1:
                            for block_option in block_options[1:2]:  # Test first block only
                                block_code = block_option.get('value')
                                block_name = block_option.get_text(strip=True)
                                print(f"\n    Testing Block: {block_name} (Code: {block_code})")
                                
                                # Step 4: Try to get SHG members directly
                                print("    Trying to get SHG members...")
                                member_data = {
                                    'methodName': 'showShgMembers',
                                    'stateCode': state_code,
                                    'districtCode': district_code,
                                    'blockCode': block_code,
                                    'grampanchayatCode': '',
                                    'villageCode': ''
                                }
                                
                                member_response = session.post(district_url, data=member_data, timeout=30)
                                print(f"    Member response status: {member_response.status_code}")
                                print(f"    Member response length: {len(member_response.text)}")
                                
                                # Look for data in response
                                member_soup = BeautifulSoup(member_response.text, 'html.parser')
                                
                                # Look for tables
                                tables = member_soup.find_all('table')
                                print(f"    Found {len(tables)} tables in response")
                                
                                # Look for any data rows
                                rows = member_soup.find_all('tr')
                                print(f"    Found {len(rows)} table rows")
                                
                                # Look for specific text patterns
                                if 'No data found' in member_response.text:
                                    print("    Response contains 'No data found'")
                                elif 'SHG' in member_response.text:
                                    print("    Response contains 'SHG' text")
                                else:
                                    print("    No obvious data indicators found")
                                
                                # Save sample response
                                with open(f'response_{state_code}_{district_code}_{block_code}.html', 'w', encoding='utf-8') as f:
                                    f.write(member_response.text)
                                print(f"    Saved response to response_{state_code}_{district_code}_{block_code}.html")
                                
                                time.sleep(2)  # Be respectful
                                break  # Only test first block
                        break  # Only test first district
                break  # Only test first state
        else:
            print("No state dropdown found!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_nrlm_scraping()
