import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import re
from urllib.parse import urljoin, urlparse

class DCEScraperImproved:
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
        """Parse colleges data from HTML tables"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            colleges = []
            
            # Find all tables
            tables = soup.find_all('table')
            print(f"Found {len(tables)} tables")
            
            for table_idx, table in enumerate(tables):
                print(f"Processing table {table_idx + 1}...")
                rows = table.find_all('tr')
                
                # Skip header row
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 5:  # Ensure we have all required columns
                        college_data = {
                            's_no': cells[0].get_text().strip(),
                            'name': cells[1].get_text().strip(),
                            'district': cells[2].get_text().strip(),
                            'region': cells[3].get_text().strip(),
                            'college_type': cells[4].get_text().strip(),
                            'contact': '',
                            'website': '',
                            'established': '',
                            'affiliation': ''
                        }
                        
                        # Clean up the college name
                        college_data['name'] = self.clean_college_name(college_data['name'])
                        
                        # Determine college category based on type
                        college_data['category'] = self.categorize_college(college_data['college_type'])
                        
                        # Extract additional info from college name if available
                        self.extract_additional_info(college_data)
                        
                        colleges.append(college_data)
            
            # Remove duplicates based on college name
            unique_colleges = []
            seen_names = set()
            for college in colleges:
                if college['name'] not in seen_names:
                    unique_colleges.append(college)
                    seen_names.add(college['name'])
            
            print(f"Total colleges found: {len(colleges)}")
            print(f"Unique colleges: {len(unique_colleges)}")
            
            return unique_colleges
            
        except Exception as e:
            print(f"Error parsing colleges data: {e}")
            return []
    
    def clean_college_name(self, name):
        """Clean and format college name"""
        # Remove extra commas and clean up
        name = re.sub(r',+', ',', name)
        name = re.sub(r'\s+', ' ', name)
        name = name.strip(' ,.')
        return name
    
    def categorize_college(self, college_type):
        """Categorize college based on type"""
        type_lower = college_type.lower()
        
        if 'government' in type_lower or 'govt' in type_lower:
            return 'Government'
        elif 'aided' in type_lower:
            return 'Aided'
        elif 'self' in type_lower and 'financ' in type_lower:
            return 'Self-Financing'
        elif 'private' in type_lower:
            return 'Private'
        elif 'autonomous' in type_lower:
            return 'Autonomous'
        else:
            return 'Other'
    
    def extract_additional_info(self, college_data):
        """Extract additional information from college name/address"""
        name = college_data['name']
        
        # Look for contact information in the name/address
        phone_pattern = r'(\+?91[\s-]?)?[6-9]\d{9}'
        phone_match = re.search(phone_pattern, name)
        if phone_match:
            college_data['contact'] = phone_match.group()
        
        # Look for website
        website_pattern = r'www\.\w+\.\w+'
        website_match = re.search(website_pattern, name)
        if website_match:
            college_data['website'] = website_match.group()
        
        # Look for establishment year
        year_pattern = r'\b(19|20)\d{2}\b'
        year_match = re.search(year_pattern, name)
        if year_match:
            college_data['established'] = year_match.group()
    
    def save_to_database(self, colleges):
        """Save colleges data to database"""
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dce_colleges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    s_no TEXT,
                    name TEXT NOT NULL,
                    district TEXT,
                    region TEXT,
                    college_type TEXT,
                    category TEXT,
                    contact TEXT,
                    website TEXT,
                    established TEXT,
                    affiliation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(name, district)
                )
            ''')
            
            # Insert or update colleges
            inserted_count = 0
            updated_count = 0
            
            for college in colleges:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO dce_colleges 
                        (s_no, name, district, region, college_type, category, contact, website, established, affiliation)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        college.get('s_no', ''),
                        college.get('name', ''),
                        college.get('district', ''),
                        college.get('region', ''),
                        college.get('college_type', ''),
                        college.get('category', ''),
                        college.get('contact', ''),
                        college.get('website', ''),
                        college.get('established', ''),
                        college.get('affiliation', '')
                    ))
                    
                    if cursor.rowcount > 0:
                        if cursor.lastrowid:
                            inserted_count += 1
                        else:
                            updated_count += 1
                            
                except Exception as e:
                    print(f"Error inserting college {college.get('name', 'Unknown')}: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            print(f"Database update completed:")
            print(f"  - New colleges inserted: {inserted_count}")
            print(f"  - Existing colleges updated: {updated_count}")
            return True
            
        except Exception as e:
            print(f"Error saving to database: {e}")
            return False
    
    def get_all_colleges(self):
        """Get all colleges from DCE website"""
        print("Fetching colleges data from DCE website...")
        
        html_content = self.get_colleges_page()
        if not html_content:
            return []
        
        colleges = self.parse_colleges_data(html_content)
        return colleges

# Test the improved scraper
if __name__ == "__main__":
    scraper = DCEScraperImproved()
    colleges = scraper.get_all_colleges()
    
    if colleges:
        scraper.save_to_database(colleges)
        print("Scraping completed successfully!")
        
        # Show sample data
        print("\nSample colleges:")
        for i, college in enumerate(colleges[:5]):
            print(f"{i+1}. {college['name']} - {college['district']} - {college['category']}")
    else:
        print("No colleges found or error occurred")
