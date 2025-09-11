import requests
from bs4 import BeautifulSoup
import urllib3
import time
import re

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class RealNRLMScraper:
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
            'Sec-Fetch-User': '?1',
            'Referer': 'https://nrlm.gov.in/',
            'Origin': 'https://nrlm.gov.in'
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
    
    def get_districts_for_state(self, state_code):
        """Get districts using the exact same method as getDistrictList() JavaScript function"""
        try:
            if not self.token_value:
                print("No token available")
                return []
            
            # Use the exact same URL pattern as the JavaScript
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&{self.token_parameter}={self.token_value}&encd={state_code}"
            
            print(f"Getting districts for state {state_code}")
            print(f"URL: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            districts = []
            
            # Find district dropdown
            district_select = soup.find('select', {'name': 'districtCode'})
            if district_select:
                for option in district_select.find_all('option'):
                    if option.get('value') and option.get('value') != '' and option.get('value') != 'All':
                        districts.append({
                            'code': option.get('value'),
                            'name': option.get_text(strip=True)
                        })
            
            print(f"Found {len(districts)} districts")
            return districts
        except Exception as e:
            print(f"Error getting districts for state {state_code}: {e}")
            return []
    
    def get_blocks_for_district(self, district_code):
        """Get blocks using the exact same method as getBlockList() JavaScript function"""
        try:
            if not self.token_value:
                return []
            
            # Use the exact same URL pattern as the JavaScript
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&{self.token_parameter}={self.token_value}&encd={district_code}"
            
            print(f"Getting blocks for district {district_code}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            blocks = []
            
            block_select = soup.find('select', {'name': 'blockCode'})
            if block_select:
                for option in block_select.find_all('option'):
                    if option.get('value') and option.get('value') != '' and option.get('value') != 'All':
                        blocks.append({
                            'code': option.get('value'),
                            'name': option.get_text(strip=True)
                        })
            
            print(f"Found {len(blocks)} blocks")
            return blocks
        except Exception as e:
            print(f"Error getting blocks: {e}")
            return []
    
    def get_grampanchayats_for_block(self, block_code):
        """Get grampanchayats using the exact same method as getGPList() JavaScript function"""
        try:
            if not self.token_value:
                return []
            
            # Use the exact same URL pattern as the JavaScript
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&{self.token_parameter}={self.token_value}&encd={block_code}"
            
            print(f"Getting grampanchayats for block {block_code}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            grampanchayats = []
            
            gp_select = soup.find('select', {'name': 'grampanchayatCode'})
            if gp_select:
                for option in gp_select.find_all('option'):
                    if option.get('value') and option.get('value') != '' and option.get('value') != 'All':
                        grampanchayats.append({
                            'code': option.get('value'),
                            'name': option.get_text(strip=True)
                        })
            
            print(f"Found {len(grampanchayats)} grampanchayats")
            return grampanchayats
        except Exception as e:
            print(f"Error getting grampanchayats: {e}")
            return []
    
    def get_villages_for_grampanchayat(self, grampanchayat_code):
        """Get villages using the exact same method as getVillageList() JavaScript function"""
        try:
            if not self.token_value:
                return []
            
            # Use the exact same URL pattern as the JavaScript
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd={grampanchayat_code}&{self.token_parameter}={self.token_value}"
            
            print(f"Getting villages for grampanchayat {grampanchayat_code}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            villages = []
            
            village_select = soup.find('select', {'name': 'villageCode'})
            if village_select:
                for option in village_select.find_all('option'):
                    if option.get('value') and option.get('value') != '' and option.get('value') != 'All':
                        villages.append({
                            'code': option.get('value'),
                            'name': option.get_text(strip=True)
                        })
            
            print(f"Found {len(villages)} villages")
            return villages
        except Exception as e:
            print(f"Error getting villages: {e}")
            return []
    
    def get_shg_members(self, village_code=None, grampanchayat_code=None, block_code=None):
        """Get SHG members using the exact same method as getSHGDetailList() JavaScript function"""
        try:
            if not self.token_value:
                return []
            
            # Use the most specific code available
            encd = village_code or grampanchayat_code or block_code
            
            # Use the exact same URL pattern as the JavaScript
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&abc=1&encd={encd}&{self.token_parameter}={self.token_value}"
            
            print(f"Getting SHG members for encd: {encd}")
            response = self.session.get(url, timeout=30)
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

def test_real_scraper():
    scraper = RealNRLMScraper()
    
    # Get initial page and token
    print("=== Getting initial page ===")
    html = scraper.get_initial_page()
    if not html:
        print("Failed to get initial page")
        return
    
    # Test with state 01 (ANDAMAN AND NICOBAR)
    print("\n=== Testing with state 01 (ANDAMAN AND NICOBAR) ===")
    districts = scraper.get_districts_for_state('01')
    
    if districts:
        print(f"Found {len(districts)} districts")
        for i, district in enumerate(districts):
            print(f"  {i+1}. {district['code']}: {district['name']}")
        
        # Test with first district
        if len(districts) > 0:
            district = districts[0]
            print(f"\n=== Testing with district {district['code']} ===")
            blocks = scraper.get_blocks_for_district(district['code'])
            
            if blocks:
                print(f"Found {len(blocks)} blocks")
                for i, block in enumerate(blocks[:3]):
                    print(f"  {i+1}. {block['code']}: {block['name']}")
    else:
        print("No districts found")

if __name__ == "__main__":
    test_real_scraper()
