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

class WorkingBAIScraper:
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
        # Look for patterns like "COMPANY NAME, CONTACT PERSON, ADDRESS"
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

    def scrape_all_members(self):
        """Scrape all BAI members by analyzing the page structure"""
        print("Starting comprehensive BAI Coimbatore members scraping...")
        
        # Get the main page first
        html_content = self.get_page_content(self.members_url)
        if not html_content:
            print("Failed to fetch the main page")
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for total records count
        total_records_text = soup.find_all(string=re.compile(r'(\d+)\s*records'))
        total_records = 461  # Default from your observation
        if total_records_text:
            for text in total_records_text:
                match = re.search(r'(\d+)\s*records', text)
                if match:
                    total_records = int(match.group(1))
                    print(f"Found total records: {total_records}")
                    break
        
        # Try to find all member data on the current page first
        members_found = self.parse_all_members_from_page(soup)
        print(f"Found {members_found} members on first page")
        
        # If we found members, try to get more pages
        if members_found > 0:
            # Try different pagination approaches
            self.try_pagination_methods(total_records)
        
        print(f"\n✅ Successfully scraped {len(self.members_data)} unique BAI members")
        return self.members_data

    def parse_all_members_from_page(self, soup):
        """Parse all members from a single page"""
        members_found = 0
        members_found_set = set()
        
        # Get all text content
        all_text = soup.get_text()
        
        # Look for member patterns in the text
        # Members seem to be separated by specific patterns
        # Try to split the text into member blocks
        
        # Look for patterns that indicate member entries
        member_patterns = [
            r'([A-Z][A-Z\s&.,]+(?:CONSTRUCTION|BUILDERS|ASSOCIATES|INFRASTRUCTURE|PROMOTERS|DEVELOPERS|CONTRACTORS|ENGINEERS|ENTERPRISES)[^,]*,[^,]*,[^,]*NO\.[^,]*COIMBATORE[^,]*)',
            r'([A-Z][A-Z\s&.,]+(?:CONSTRUCTION|BUILDERS|ASSOCIATES|INFRASTRUCTURE|PROMOTERS|DEVELOPERS|CONTRACTORS|ENGINEERS|ENTERPRISES)[^,]*,[^,]*NO\.[^,]*COIMBATORE[^,]*)',
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
        
        # If regex approach doesn't work well, try a different approach
        if members_found < 10:
            print("Trying alternative parsing method...")
            members_found = self.alternative_parsing(soup, members_found_set)
        
        return members_found

    def alternative_parsing(self, soup, members_found_set):
        """Alternative parsing method"""
        members_found = 0
        
        # Look for specific HTML elements that might contain member data
        # Try to find table rows, divs, or other containers
        potential_containers = soup.find_all(['tr', 'div', 'p', 'td'])
        
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

    def try_pagination_methods(self, total_records):
        """Try different pagination methods to get all records"""
        print(f"Trying to get all {total_records} records...")
        
        # Method 1: Try different page parameters
        page_params = [
            {'page': 2}, {'page': 3}, {'page': 4}, {'page': 5},
            {'p': 2}, {'p': 3}, {'p': 4}, {'p': 5},
            {'page_num': 2}, {'page_num': 3}, {'page_num': 4}, {'page_num': 5}
        ]
        
        for params in page_params:
            html_content = self.get_page_content(self.members_url, params)
            if html_content:
                soup = BeautifulSoup(html_content, 'html.parser')
                # Check if we got different content
                page_text = soup.get_text()
                if 'Showing' in page_text and 'records' in page_text:
                    print(f"  Found pagination info: {re.search(r'Showing.*?records', page_text).group()}")
                    members_found = self.parse_all_members_from_page(soup)
                    if members_found > 0:
                        print(f"  Page with params {params}: Found {members_found} new members")
                time.sleep(1)
        
        # Method 2: Try to find AJAX endpoints or API calls
        # This would require analyzing the page's JavaScript
        
        # Method 3: Try to get all data in one request with different parameters
        all_data_params = [
            {'limit': total_records},
            {'per_page': total_records},
            {'all': 'true'},
            {'export': 'true'}
        ]
        
        for params in all_data_params:
            html_content = self.get_page_content(self.members_url, params)
            if html_content:
                soup = BeautifulSoup(html_content, 'html.parser')
                members_found = self.parse_all_members_from_page(soup)
                if members_found > len(self.members_data) * 0.5:  # If we get significantly more data
                    print(f"  Found more data with params {params}: {members_found} members")
                time.sleep(1)

    def save_to_json(self, filename='bai_members_working.json'):
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

    def save_to_csv(self, filename='bai_members_working.csv'):
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
    scraper = WorkingBAIScraper()
    
    # Scrape all members
    members = scraper.scrape_all_members()
    
    if members:
        # Save in multiple formats
        scraper.save_to_json()
        scraper.save_to_csv()
        scraper.save_to_database()
        
        print(f"\n✅ Successfully scraped {len(members)} BAI members!")
        print("Files created:")
        print("- bai_members_working.json")
        print("- bai_members_working.csv")
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
