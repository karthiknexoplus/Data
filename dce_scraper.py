import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import re
from urllib.parse import urljoin, urlparse

class DCEScraper:
    def __init__(self):
        self.base_url = "https://tndce.tn.gov.in"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1'
        })
        
    def get_colleges_page(self):
        """Get the main colleges page"""
        try:
            url = f"{self.base_url}/Colleges"
            response = self.session.get(url, timeout=30, verify=False)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error getting colleges page: {e}")
            return None
    
    def parse_colleges_data(self, html_content):
        """Parse colleges data from HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            colleges = []
            
            # Look for college listings - this might be in tables, divs, or other structures
            # We need to examine the actual HTML structure first
            
            # Try to find college information in various possible structures
            college_elements = soup.find_all(['tr', 'div', 'li'], class_=re.compile(r'college|institution|university', re.I))
            
            if not college_elements:
                # Try alternative selectors
                college_elements = soup.find_all('tr')  # If it's in a table
                if not college_elements:
                    college_elements = soup.find_all('div', class_=re.compile(r'card|item|list', re.I))
            
            for element in college_elements:
                college_data = self.extract_college_info(element)
                if college_data:
                    colleges.append(college_data)
            
            return colleges
            
        except Exception as e:
            print(f"Error parsing colleges data: {e}")
            return []
    
    def extract_college_info(self, element):
        """Extract college information from an HTML element"""
        try:
            college_data = {
                'name': '',
                'type': '',
                'location': '',
                'district': '',
                'contact': '',
                'website': '',
                'established': '',
                'affiliation': ''
            }
            
            # Extract text content
            text_content = element.get_text(strip=True)
            
            # Look for college name (usually the most prominent text)
            links = element.find_all('a')
            if links:
                college_data['name'] = links[0].get_text(strip=True)
                college_data['website'] = links[0].get('href', '')
            
            # Look for contact information
            phone_pattern = r'(\+?91[\s-]?)?[6-9]\d{9}'
            phone_match = re.search(phone_pattern, text_content)
            if phone_match:
                college_data['contact'] = phone_match.group()
            
            # Look for email
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_match = re.search(email_pattern, text_content)
            if email_match:
                college_data['contact'] += f" | {email_match.group()}"
            
            # Determine college type based on text content
            text_lower = text_content.lower()
            if 'government' in text_lower or 'govt' in text_lower:
                college_data['type'] = 'Government'
            elif 'aided' in text_lower:
                college_data['type'] = 'Aided'
            elif 'self' in text_lower and 'financ' in text_lower:
                college_data['type'] = 'Self-Financing'
            elif 'private' in text_lower:
                college_data['type'] = 'Private'
            else:
                college_data['type'] = 'Unknown'
            
            # Extract location/district information
            # Look for common Tamil Nadu district names
            districts = ['Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem', 'Tirunelveli', 
                        'Tiruppur', 'Erode', 'Vellore', 'Thoothukudi', 'Dindigul', 'Thanjavur', 
                        'Ranipet', 'Sivaganga', 'Karur', 'Udhagamandalam', 'Hosur', 'Nagercoil',
                        'Kanchipuram', 'Cuddalore', 'Kumbakonam', 'Tiruvannamalai', 'Pollachi',
                        'Rajapalayam', 'Sivakasi', 'Pudukkottai', 'Vaniyambadi', 'Ambur', 'Nagapattinam',
                        'Gudiyatham', 'Tirupathur', 'Tenkasi', 'Palani', 'Pattukkottai', 'Tiruvallur',
                        'Karaikudi', 'Sankarankovil', 'Sirkazhi', 'Tiruchengode', 'Vandavasi', 'Tiruppuvanam',
                        'Tirukkoyilur', 'Oddanchatram', 'Palladam', 'Vedaranyam', 'Pernampattu', 'Puliyankudi',
                        'Viluppuram', 'Sathyamangalam', 'Sivagiri', 'Tirupathur', 'Tiruttani', 'Ranipet',
                        'Walajapet', 'Arakkonam', 'Tiruvallur', 'Pallavaram', 'Tambaram', 'Chengalpattu',
                        'Kanchipuram', 'Sriperumbudur', 'Gummidipoondi', 'Ponneri', 'Tiruvallur']
            
            for district in districts:
                if district.lower() in text_lower:
                    college_data['district'] = district
                    college_data['location'] = district
                    break
            
            # Only return if we have at least a name
            if college_data['name']:
                return college_data
            
            return None
            
        except Exception as e:
            print(f"Error extracting college info: {e}")
            return None
    
    def get_all_colleges(self):
        """Get all colleges from DCE website"""
        print("Fetching colleges data from DCE website...")
        
        html_content = self.get_colleges_page()
        if not html_content:
            return []
        
        colleges = self.parse_colleges_data(html_content)
        print(f"Found {len(colleges)} colleges")
        
        return colleges
    
    def save_to_database(self, colleges):
        """Save colleges data to database"""
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dce_colleges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT,
                    location TEXT,
                    district TEXT,
                    contact TEXT,
                    website TEXT,
                    established TEXT,
                    affiliation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert or update colleges
            for college in colleges:
                cursor.execute('''
                    INSERT OR REPLACE INTO dce_colleges 
                    (name, type, location, district, contact, website, established, affiliation)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    college.get('name', ''),
                    college.get('type', ''),
                    college.get('location', ''),
                    college.get('district', ''),
                    college.get('contact', ''),
                    college.get('website', ''),
                    college.get('established', ''),
                    college.get('affiliation', '')
                ))
            
            conn.commit()
            conn.close()
            
            print(f"Saved {len(colleges)} colleges to database")
            return True
            
        except Exception as e:
            print(f"Error saving to database: {e}")
            return False

# Test the scraper
if __name__ == "__main__":
    scraper = DCEScraper()
    colleges = scraper.get_all_colleges()
    
    if colleges:
        scraper.save_to_database(colleges)
        print("Scraping completed successfully!")
    else:
        print("No colleges found or error occurred")
