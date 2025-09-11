import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WorkingNRLMScraper:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://nrlm.gov.in"
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Origin': 'https://nrlm.gov.in',
            'Cache-Control': 'max-age=0'
        })
        self.session.verify = False
        self.token = None
    
    def get_initial_page(self):
        """Get the initial page and establish session"""
        try:
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd=0"
            response = self.session.get(url, timeout=30, verify=False)
            response.raise_for_status()
            
            # Extract token from the page
            soup = BeautifulSoup(response.text, 'html.parser')
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'tokenValue' in script.string:
                    import re
                    match = re.search(r"tokenValue\s*=\s*'([^']+)'", script.string)
                    if match:
                        self.token = match.group(1)
                        break
            
            return response.text
        except Exception as e:
            print(f"Error getting initial page: {e}")
            return None
    
    def extract_states(self, html):
        """Extract states from the HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        states = []
        
        # Find state select element
        state_select = soup.find('select', {'name': 'stateCode'})
        if state_select:
            for option in state_select.find_all('option'):
                if option.get('value') and option.get('value') != '':
                    states.append({
                        'code': option.get('value'),
                        'name': option.get_text(strip=True)
                    })
        
        return states
    
    def get_districts(self, state_code):
        """Get districts for a given state"""
        try:
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd={state_code}&reqtrack={self.token}"
            form_data = {
                'methodName': 'showShgMembers',
                'encd': state_code,
                'reqtrack': self.token,
                'stateCode': state_code
            }
            self.session.headers['Referer'] = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&reqtrack={self.token}&encd=0"
            
            response = self.session.post(url, data=form_data, timeout=30, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            districts = []
            
            district_select = soup.find('select', {'name': 'districtCode'})
            if district_select:
                for option in district_select.find_all('option'):
                    if option.get('value') and option.get('value') != '':
                        districts.append({
                            'code': option.get('value'),
                            'name': option.get_text(strip=True)
                        })
            
            return districts
        except Exception as e:
            print(f"Error getting districts for state {state_code}: {e}")
            return []
    
    def get_blocks(self, state_code, district_code):
        """Get blocks for a given state and district"""
        try:
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd={district_code}&reqtrack={self.token}"
            form_data = {
                'methodName': 'showShgMembers',
                'encd': district_code,
                'reqtrack': self.token,
                'stateCode': state_code,
                'districtCode': district_code
            }
            self.session.headers['Referer'] = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&reqtrack={self.token}&encd={state_code}"
            
            response = self.session.post(url, data=form_data, timeout=30, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            blocks = []
            
            block_select = soup.find('select', {'name': 'blockCode'})
            if block_select:
                for option in block_select.find_all('option'):
                    if option.get('value') and option.get('value') != '':
                        blocks.append({
                            'code': option.get('value'),
                            'name': option.get_text(strip=True)
                        })
            
            return blocks
        except Exception as e:
            print(f"Error getting blocks for state {state_code}, district {district_code}: {e}")
            return []
    
    def get_grampanchayats(self, state_code, district_code, block_code):
        """Get grampanchayats for given parameters"""
        try:
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd={block_code}&reqtrack={self.token}"
            form_data = {
                'methodName': 'showShgMembers',
                'encd': block_code,
                'reqtrack': self.token,
                'stateCode': state_code,
                'districtCode': district_code,
                'blockCode': block_code
            }
            self.session.headers['Referer'] = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&reqtrack={self.token}&encd={district_code}"
            
            response = self.session.post(url, data=form_data, timeout=30, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            grampanchayats = []
            
            grampanchayat_select = soup.find('select', {'name': 'grampanchayatCode'})
            if grampanchayat_select:
                for option in grampanchayat_select.find_all('option'):
                    if option.get('value') and option.get('value') != '':
                        grampanchayats.append({
                            'code': option.get('value'),
                            'name': option.get_text(strip=True)
                        })
            
            return grampanchayats
        except Exception as e:
            print(f"Error getting grampanchayats: {e}")
            return []
    
    def get_villages(self, state_code, district_code, block_code, grampanchayat_code):
        """Get villages for given parameters"""
        try:
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd={grampanchayat_code}&reqtrack={self.token}"
            form_data = {
                'methodName': 'showShgMembers',
                'encd': grampanchayat_code,
                'reqtrack': self.token,
                'stateCode': state_code,
                'districtCode': district_code,
                'blockCode': block_code,
                'grampanchayatCode': grampanchayat_code
            }
            self.session.headers['Referer'] = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&reqtrack={self.token}&encd={block_code}"
            
            response = self.session.post(url, data=form_data, timeout=30, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            villages = []
            
            village_select = soup.find('select', {'name': 'villageCode'})
            if village_select:
                for option in village_select.find_all('option'):
                    if option.get('value') and option.get('value') != '':
                        villages.append({
                            'code': option.get('value'),
                            'name': option.get_text(strip=True)
                        })
            
            return villages
        except Exception as e:
            print(f"Error getting villages: {e}")
            return []
    
    def get_shg_members(self, state_code, district_code, block_code, grampanchayat_code, village_code):
        """Get SHG members data"""
        try:
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd={village_code}&reqtrack={self.token}"
            form_data = {
                'methodName': 'showShgMembers',
                'encd': village_code,
                'reqtrack': self.token,
                'stateCode': state_code,
                'districtCode': district_code,
                'blockCode': block_code,
                'grampanchayatCode': grampanchayat_code,
                'villageCode': village_code
            }
            self.session.headers['Referer'] = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&reqtrack={self.token}&encd={grampanchayat_code}"
            
            response = self.session.post(url, data=form_data, timeout=30, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            members = []
            
            # Find the data table
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
            
            return members
        except Exception as e:
            print(f"Error getting SHG members: {e}")
            return []
