import requests
from bs4 import BeautifulSoup
import urllib3
import time
import re

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WorkingNRLMFinal:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://nrlm.gov.in"
        self.session.verify = False
        self.session.headers.update({
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
        self.token_parameter = 'reqtrack'
        self.token_value = None
    
    def get_initial_page(self):
        """Get the initial page and extract token"""
        try:
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd=0"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Extract token from the response
            soup = BeautifulSoup(response.text, 'html.parser')
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'tokenValue' in script.string:
                    match = re.search(r"tokenValue\s*=\s*'([^']+)'", script.string)
                    if match:
                        self.token_value = match.group(1)
                        print(f"Found token: {self.token_value}")
                        break
            
            return response.text
        except Exception as e:
            print(f"Error getting initial page: {e}")
            return None
    
    def submit_form_with_encd(self, encd_value):
        """Submit form with encd value using POST method"""
        try:
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do"
            data = {
                'methodName': 'showShgMembers',
                self.token_parameter: self.token_value,
                'encd': encd_value,
                '': encd_value  # Hidden field
            }
            
            print(f"Submitting form with encd: {encd_value}")
            response = self.session.post(url, data=data, timeout=30)
            response.raise_for_status()
            
            return response.text
        except Exception as e:
            print(f"Error submitting form: {e}")
            return None
    
    def get_states(self):
        """Get all states from the initial page"""
        try:
            html = self.get_initial_page()
            if not html:
                return []
            
            soup = BeautifulSoup(html, 'html.parser')
            states = []
            
            state_select = soup.find('select', {'name': 'stateCode'})
            if state_select:
                for option in state_select.find_all('option'):
                    if option.get('value') and option.get('value') != '':
                        states.append({
                            'code': option.get('value'),
                            'name': option.get_text(strip=True)
                        })
            
            return states
        except Exception as e:
            print(f"Error getting states: {e}")
            return []
    
    def get_districts(self, state_code):
        """Get districts for a given state"""
        try:
            html = self.submit_form_with_encd(state_code)
            if not html:
                return []
            
            soup = BeautifulSoup(html, 'html.parser')
            districts = []
            
            district_select = soup.find('select', {'name': 'districtCode'})
            if district_select:
                for option in district_select.find_all('option'):
                    if option.get('value') and option.get('value') != '' and option.get('value') != 'All':
                        districts.append({
                            'code': option.get('value'),
                            'name': option.get_text(strip=True)
                        })
            
            print(f"Found {len(districts)} districts for state {state_code}")
            return districts
        except Exception as e:
            print(f"Error getting districts: {e}")
            return []
    
    def get_blocks(self, district_code):
        """Get blocks for a given district"""
        try:
            html = self.submit_form_with_encd(district_code)
            if not html:
                return []
            
            soup = BeautifulSoup(html, 'html.parser')
            blocks = []
            
            block_select = soup.find('select', {'name': 'blockCode'})
            if block_select:
                for option in block_select.find_all('option'):
                    if option.get('value') and option.get('value') != '' and option.get('value') != 'All':
                        blocks.append({
                            'code': option.get('value'),
                            'name': option.get_text(strip=True)
                        })
            
            print(f"Found {len(blocks)} blocks for district {district_code}")
            return blocks
        except Exception as e:
            print(f"Error getting blocks: {e}")
            return []
    
    def get_grampanchayats(self, block_code):
        """Get grampanchayats for a given block"""
        try:
            html = self.submit_form_with_encd(block_code)
            if not html:
                return []
            
            soup = BeautifulSoup(html, 'html.parser')
            grampanchayats = []
            
            gp_select = soup.find('select', {'name': 'grampanchayatCode'})
            if gp_select:
                for option in gp_select.find_all('option'):
                    if option.get('value') and option.get('value') != '' and option.get('value') != 'All':
                        grampanchayats.append({
                            'code': option.get('value'),
                            'name': option.get_text(strip=True)
                        })
            
            print(f"Found {len(grampanchayats)} grampanchayats for block {block_code}")
            return grampanchayats
        except Exception as e:
            print(f"Error getting grampanchayats: {e}")
            return []
    
    def get_villages(self, grampanchayat_code):
        """Get villages for a given grampanchayat"""
        try:
            html = self.submit_form_with_encd(grampanchayat_code)
            if not html:
                return []
            
            soup = BeautifulSoup(html, 'html.parser')
            villages = []
            
            village_select = soup.find('select', {'name': 'villageCode'})
            if village_select:
                for option in village_select.find_all('option'):
                    if option.get('value') and option.get('value') != '' and option.get('value') != 'All':
                        villages.append({
                            'code': option.get('value'),
                            'name': option.get_text(strip=True)
                        })
            
            print(f"Found {len(villages)} villages for grampanchayat {grampanchayat_code}")
            return villages
        except Exception as e:
            print(f"Error getting villages: {e}")
            return []
    
    def get_shg_members(self, village_code=None, grampanchayat_code=None, block_code=None):
        """Get SHG members data"""
        try:
            # Use the most specific code available
            encd = village_code or grampanchayat_code or block_code
            
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do"
            data = {
                'methodName': 'showShgMembers',
                'abc': '1',  # This parameter is used in the JavaScript
                self.token_parameter: self.token_value,
                'encd': encd,
                '': encd  # Hidden field
            }
            
            print(f"Getting SHG members for encd: {encd}")
            response = self.session.post(url, data=data, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            members = []
            
            # Look for data table
            table = soup.find('table', {'class': 'table'}) or soup.find('table')
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        members.append({
                            'shg_name': cells[0].get_text(strip=True) if len(cells) > 0 else '',
                            'member_name': cells[1].get_text(strip=True) if len(cells) > 1 else '',
                            'member_code': cells[2].get_text(strip=True) if len(cells) > 2 else ''
                        })
            
            print(f"Found {len(members)} SHG members")
            return members
        except Exception as e:
            print(f"Error getting SHG members: {e}")
            return []

def test_working_scraper():
    scraper = WorkingNRLMFinal()
    
    # Test the complete flow
    print("=== Testing complete NRLM data flow ===")
    
    # Get states
    states = scraper.get_states()
    print(f"Found {len(states)} states")
    
    if states:
        # Test with state 01 (ANDAMAN AND NICOBAR)
        state_01 = next((s for s in states if s['code'] == '01'), None)
        if state_01:
            print(f"\n=== Testing with {state_01['name']} ===")
            
            # Get districts
            districts = scraper.get_districts('01')
            if districts:
                print(f"Found {len(districts)} districts")
                for i, district in enumerate(districts):
                    print(f"  {i+1}. {district['code']}: {district['name']}")
                
                # Test with first district
                if len(districts) > 0:
                    district = districts[0]
                    print(f"\n=== Testing with {district['name']} ===")
                    
                    # Get blocks
                    blocks = scraper.get_blocks(district['code'])
                    if blocks:
                        print(f"Found {len(blocks)} blocks")
                        for i, block in enumerate(blocks[:3]):
                            print(f"  {i+1}. {block['code']}: {block['name']}")
                    else:
                        print("No blocks found")
            else:
                print("No districts found")
        else:
            print("State 01 not found")

if __name__ == "__main__":
    test_working_scraper()
