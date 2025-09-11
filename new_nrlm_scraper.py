class NRLMScraper:
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
        self.current_page_url = None
    
    def get_initial_page(self):
        """Get the initial page and establish session"""
        try:
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd=0"
            response = self.session.get(url, timeout=30, verify=False)
            response.raise_for_status()
            self.current_page_url = url
            
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
    
    def submit_form_for_level(self, encd_value, state_code=None, district_code=None, block_code=None, grampanchayat_code=None, village_code=None):
        """Submit form for a specific level and return the response"""
        try:
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd={encd_value}&reqtrack={self.token}"
            
            form_data = {
                'methodName': 'showShgMembers',
                'encd': encd_value,
                'reqtrack': self.token,
                'stateCode': state_code if state_code else '',
                'districtCode': district_code if district_code else '',
                'blockCode': block_code if block_code else '',
                'grampanchayatCode': grampanchayat_code if grampanchayat_code else '',
                'villageCode': village_code if village_code else ''
            }
            
            headers = {
                'Referer': self.current_page_url,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = self.session.post(url, data=form_data, headers=headers, timeout=30, verify=False)
            response.raise_for_status()
            self.current_page_url = url  # Update current page URL for next Referer
            return response.text
        except Exception as e:
            print(f"Error submitting form: {e}")
            return None
    
    def get_districts(self, state_code):
        """Get districts for a given state"""
        try:
            response_html = self.submit_form_for_level(state_code, state_code=state_code)
            if not response_html:
                return []
            
            soup = BeautifulSoup(response_html, 'html.parser')
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
            response_html = self.submit_form_for_level(district_code, state_code=state_code, district_code=district_code)
            if not response_html:
                return []
            
            soup = BeautifulSoup(response_html, 'html.parser')
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
            response_html = self.submit_form_for_level(block_code, state_code=state_code, district_code=district_code, block_code=block_code)
            if not response_html:
                return []
            
            soup = BeautifulSoup(response_html, 'html.parser')
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
            response_html = self.submit_form_for_level(grampanchayat_code, state_code=state_code, district_code=district_code, block_code=block_code, grampanchayat_code=grampanchayat_code)
            if not response_html:
                return []
            
            soup = BeautifulSoup(response_html, 'html.parser')
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
            response_html = self.submit_form_for_level(village_code, state_code=state_code, district_code=district_code, block_code=block_code, grampanchayat_code=grampanchayat_code, village_code=village_code)
            if not response_html:
                return []
            
            soup = BeautifulSoup(response_html, 'html.parser')
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
