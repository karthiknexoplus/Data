#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import re
from urllib.parse import urljoin, urlparse, parse_qs
import sqlite3
from datetime import datetime

class ComprehensiveBAIScraper:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://baionline.in"
        self.members_url = "https://baionline.in/committee_member/coimbatore"
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        self.members_data = []
        self.total_pages = 9  # Based on the pagination info we saw

    def get_page_content(self, url, params=None):
        """Get page content with error handling"""
        try:
            print(f"Fetching: {url}")
            if params:
                print(f"  Params: {params}")
            response = self.session.get(url, timeout=30, params=params)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_member_info(self, text_block):
        """Extract member information from a text block"""
        # Clean up the text
        clean_text = re.sub(r'[‹›]', '', text_block)
        clean_text = re.sub(r'Show Phone Number|Show Email|Contact Member', '', clean_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        member_data = {
            'company_name': '',
            'contact_person': '',
            'address': '',
            'phone': '',
            'email': '',
            'source_url': self.members_url,
            'scraped_at': datetime.now().isoformat()
        }
        
        # Split into lines
        lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
        
        if not lines:
            return None
        
        # Try to extract company name and contact person
        full_text = ' '.join(lines)
        
        # Extract company name (usually the first part before a comma or specific pattern)
        company_match = re.search(r'^([^,]+?)(?:\s*,\s*([^,]+?))?(?:\s*,\s*NO\.)', full_text)
        if company_match:
            member_data['company_name'] = company_match.group(1).strip()
            if company_match.group(2):
                contact_person = company_match.group(2).strip()
                if contact_person and contact_person != 'NA' and len(contact_person) > 2:
                    member_data['contact_person'] = contact_person
        
        # If no company name found, use the first line
        if not member_data['company_name'] and lines:
            member_data['company_name'] = lines[0]
        
        # Extract address (look for lines with NO. or address keywords)
        address_parts = []
        for line in lines:
            if (line.startswith('NO.') or 
                any(keyword in line.upper() for keyword in [
                    'ROAD', 'STREET', 'NAGAR', 'COLONY', 'AVENUE', 'LAYOUT', 
                    'POST', 'COIMBATORE', 'FLOOR', 'BUILDING', 'COMPLEX', 'PALAYAM'
                ])):
                address_parts.append(line)
        
        if address_parts:
            member_data['address'] = ' '.join(address_parts)
        
        # Extract phone number
        phone_pattern = r'(\+?91[\s-]?)?[6-9]\d{9}'
        phone_match = re.search(phone_pattern, clean_text)
        if phone_match:
            member_data['phone'] = phone_match.group(0).strip()
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, clean_text)
        if email_match:
            member_data['email'] = email_match.group(0).strip()
        
        return member_data

    def scrape_all_pages_systematically(self):
        """Scrape all pages systematically"""
        print("Starting systematic BAI Coimbatore members scraping...")
        
        # We know from the pagination info that there are 9 pages total
        # Page 1: Showing 1 - 52 of 461 records
        # Page 2: Showing 53 - 104 of 461 records
        # Page 3: Showing 105 - 156 of 461 records
        # Page 4: Showing 157 - 208 of 461 records
        # Page 5: Showing 209 - 260 of 461 records
        # Page 6: Showing 261 - 312 of 461 records
        # Page 7: Showing 313 - 364 of 461 records
        # Page 8: Showing 365 - 416 of 461 records
        # Page 9: Showing 417 - 461 of 461 records
        
        for page_num in range(1, 10):  # Pages 1-9
            print(f"\n--- Scraping Page {page_num} ---")
            
            # Try the page parameter that worked
            html_content = self.get_page_content(self.members_url, {'page': page_num})
            if html_content:
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Check pagination info
                pagination_info = soup.find_all(string=re.compile(r'Showing.*?records'))
                if pagination_info:
                    print(f"Pagination info: {pagination_info[0].strip()}")
                
                # Parse members from this page
                members_found = self.parse_members_from_page(soup, page_num)
                print(f"Page {page_num}: Found {members_found} members")
                
                # Be respectful with requests
                time.sleep(2)
            else:
                print(f"Failed to fetch page {page_num}")
        
        print(f"\n✅ Successfully scraped {len(self.members_data)} unique BAI members")
        return self.members_data

    def parse_members_from_page(self, soup, page_num):
        """Parse members from a specific page"""
        members_found = 0
        members_found_set = set()
        
        # Get all text content
        all_text = soup.get_text()
        
        # Look for member patterns in the text
        # Based on the patterns we've seen, members are in specific formats
        member_patterns = [
            # Pattern 1: Company name, Contact person, Address with NO.
            r'([A-Z][A-Z\s&.,]+(?:CONSTRUCTION|BUILDERS|ASSOCIATES|INFRASTRUCTURE|PROMOTERS|DEVELOPERS|CONTRACTORS|ENGINEERS|ENTERPRISES)[^,]*,[^,]*,[^,]*NO\.[^,]*COIMBATORE[^,]*)',
            # Pattern 2: Company name, Address with NO.
            r'([A-Z][A-Z\s&.,]+(?:CONSTRUCTION|BUILDERS|ASSOCIATES|INFRASTRUCTURE|PROMOTERS|DEVELOPERS|CONTRACTORS|ENGINEERS|ENTERPRISES)[^,]*,[^,]*NO\.[^,]*COIMBATORE[^,]*)',
            # Pattern 3: More flexible pattern
            r'([A-Z][A-Z\s&.,]+(?:CONSTRUCTION|BUILDERS|ASSOCIATES|INFRASTRUCTURE|PROMOTERS|DEVELOPERS|CONTRACTORS|ENGINEERS|ENTERPRISES)[^,]*COIMBATORE[^,]*)',
        ]
        
        for pattern in member_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if self.is_valid_member_block(match):
                    member_data = self.extract_member_info(match)
                    if member_data and member_data['company_name']:
                        unique_key = f"{member_data['company_name']}_{member_data['contact_person']}"
                        if unique_key not in members_found_set:
                            members_found_set.add(unique_key)
                            self.members_data.append(member_data)
                            members_found += 1
                            print(f"  ✓ {member_data['company_name']} | {member_data['contact_person']}")
        
        # If regex approach doesn't work well, try alternative parsing
        if members_found < 5:  # If we didn't find many members with regex
            print("  Trying alternative parsing method...")
            members_found = self.alternative_parsing(soup, members_found_set)
        
        return members_found

    def alternative_parsing(self, soup, members_found_set):
        """Alternative parsing method"""
        members_found = 0
        
        # Look for specific HTML elements that might contain member data
        potential_containers = soup.find_all(['tr', 'div', 'p', 'td', 'span'])
        
        for container in potential_containers:
            text = container.get_text(strip=True)
            if self.is_valid_member_block(text):
                member_data = self.extract_member_info(text)
                if member_data and member_data['company_name']:
                    unique_key = f"{member_data['company_name']}_{member_data['contact_person']}"
                    if unique_key not in members_found_set:
                        members_found_set.add(unique_key)
                        self.members_data.append(member_data)
                        members_found += 1
                        print(f"  ✓ {member_data['company_name']} | {member_data['contact_person']}")
        
        return members_found

    def is_valid_member_block(self, text_block):
        """Check if a text block looks like a valid member entry"""
        if not text_block or len(text_block) < 30 or len(text_block) > 1000:
            return False
        
        # Must contain company type keywords
        company_keywords = [
            'CONSTRUCTION', 'BUILDERS', 'ASSOCIATES', 'INFRASTRUCTURE', 
            'PROMOTERS', 'DEVELOPERS', 'CONTRACTORS', 'ENGINEERS', 'ENTERPRISES'
        ]
        
        if not any(keyword in text_block.upper() for keyword in company_keywords):
            return False
        
        # Must contain Coimbatore
        if 'COIMBATORE' not in text_block.upper():
            return False
        
        # Should not be just navigation or UI text
        ui_keywords = ['HOME', 'ABOUT', 'CONTACT', 'LOGIN', 'REGISTER', 'MENU', 'NAVIGATION']
        if any(keyword in text_block.upper() for keyword in ui_keywords):
            return False
        
        return True

    def save_to_json(self, filename='bai_members_comprehensive.json'):
        """Save scraped data to JSON file"""
        data = {
            'source': 'Builders Association of India (BAI) - Coimbatore',
            'source_url': self.members_url,
            'scraped_at': datetime.now().isoformat(),
            'total_members': len(self.members_data),
            'members': self.members_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Data saved to {filename}")

    def save_to_csv(self, filename='bai_members_comprehensive.csv'):
        """Save scraped data to CSV file"""
        if not self.members_data:
            print("No data to save")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'company_name', 'contact_person', 'address', 'phone', 'email', 'source_url', 'scraped_at'
            ])
            writer.writeheader()
            writer.writerows(self.members_data)
        
        print(f"Data saved to {filename}")

    def save_to_database(self):
        """Save scraped data to SQLite database"""
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            
            # Create BAI members table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bai_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT NOT NULL,
                    contact_person TEXT,
                    address TEXT,
                    phone TEXT,
                    email TEXT,
                    source_url TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Clear existing data
            cursor.execute('DELETE FROM bai_members')
            
            # Insert new data
            for member in self.members_data:
                cursor.execute('''
                    INSERT INTO bai_members 
                    (company_name, contact_person, address, phone, email, source_url, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    member['company_name'],
                    member['contact_person'],
                    member['address'],
                    member['phone'],
                    member['email'],
                    member['source_url'],
                    member['scraped_at']
                ))
            
            conn.commit()
            conn.close()
            print(f"Data saved to database: {len(self.members_data)} records")
            
        except Exception as e:
            print(f"Error saving to database: {e}")

def main():
    scraper = ComprehensiveBAIScraper()
    
    # Scrape all pages systematically
    members = scraper.scrape_all_pages_systematically()
    
    if members:
        # Save in multiple formats
        scraper.save_to_json()
        scraper.save_to_csv()
        scraper.save_to_database()
        
        print(f"\n✅ Successfully scraped {len(members)} BAI members!")
        print("Files created:")
        print("- bai_members_comprehensive.json")
        print("- bai_members_comprehensive.csv")
        print("- Database table: bai_members")
        
        # Show sample data
        print("\n📋 Sample data:")
        for i, member in enumerate(members[:5]):
            print(f"{i+1}. {member['company_name']}")
            print(f"   Contact: {member['contact_person']}")
            print(f"   Address: {member['address'][:100]}...")
            print(f"   Phone: {member['phone']}")
            print()
    else:
        print("❌ No members data scraped")

if __name__ == "__main__":
    main()
