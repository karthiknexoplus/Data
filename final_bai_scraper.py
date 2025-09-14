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

class FinalBAIScraper:
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
        self.total_pages = 0

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
        lines = [line.strip() for line in text_block.split('\n') if line.strip()]
        
        member_data = {
            'company_name': '',
            'contact_person': '',
            'address': '',
            'phone': '',
            'email': '',
            'source_url': self.members_url,
            'scraped_at': datetime.now().isoformat()
        }
        
        if not lines:
            return None
        
        # Clean up the text - remove HTML artifacts
        clean_text = re.sub(r'[‹›]', '', text_block)
        clean_text = re.sub(r'Show Phone Number|Show Email|Contact Member', '', clean_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # Split into lines again after cleaning
        lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
        
        if not lines:
            return None
        
        # First line is usually the company name
        company_name = lines[0]
        if company_name and len(company_name) > 3:
            member_data['company_name'] = company_name
        
        # Look for contact person (usually second line if not NA)
        if len(lines) > 1:
            contact_person = lines[1]
            if (contact_person and contact_person != 'NA' and 
                not contact_person.startswith('NO.') and 
                not contact_person.startswith('COIMBATORE') and
                len(contact_person) > 2):
                member_data['contact_person'] = contact_person
        
        # Extract address (lines starting with NO. or containing address keywords)
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

    def scrape_page(self, page_num=1):
        """Scrape a specific page"""
        print(f"\n--- Scraping Page {page_num} ---")
        
        # Try different pagination approaches
        pagination_params = [
            {'page': page_num},
            {'p': page_num},
            {'page_num': page_num},
            {'start': (page_num - 1) * 20},
            {'offset': (page_num - 1) * 20}
        ]
        
        for params in pagination_params:
            html_content = self.get_page_content(self.members_url, params)
            if html_content:
                soup = BeautifulSoup(html_content, 'html.parser')
                members_found = self.parse_page_content(soup, page_num)
                if members_found > 0:
                    return members_found
        
        # If pagination params don't work, try direct URL approach
        page_urls = [
            f"{self.members_url}?page={page_num}",
            f"{self.members_url}/page/{page_num}",
            f"{self.members_url}?p={page_num}",
            f"{self.members_url}?page_num={page_num}"
        ]
        
        for url in page_urls:
            html_content = self.get_page_content(url)
            if html_content:
                soup = BeautifulSoup(html_content, 'html.parser')
                members_found = self.parse_page_content(soup, page_num)
                if members_found > 0:
                    return members_found
        
        return 0

    def parse_page_content(self, soup, page_num):
        """Parse content from a page"""
        members_found = 0
        members_found_set = set()  # To avoid duplicates
        
        # Look for pagination info
        pagination_info = soup.find_all(text=re.compile(r'Showing.*of.*records'))
        if pagination_info:
            print(f"Pagination info found: {pagination_info[0].strip()}")
        
        # Try to find member blocks in different ways
        # Method 1: Look for specific divs or containers
        member_containers = soup.find_all(['div', 'p', 'tr', 'td'], 
                                        string=re.compile(r'(CONSTRUCTION|BUILDERS|ASSOCIATES|INFRASTRUCTURE|PROMOTERS)', re.I))
        
        for container in member_containers:
            # Get the parent element that contains the full member info
            parent = container.parent
            if parent:
                text_block = parent.get_text()
                if self.is_valid_member_block(text_block):
                    member_data = self.extract_member_info(text_block)
                    if member_data and member_data['company_name']:
                        unique_key = f"{member_data['company_name']}_{member_data['contact_person']}"
                        if unique_key not in members_found_set:
                            members_found_set.add(unique_key)
                            self.members_data.append(member_data)
                            members_found += 1
                            print(f"  ✓ {member_data['company_name']} | {member_data['contact_person']}")
        
        # Method 2: Look for all text blocks that might contain member data
        if members_found == 0:
            all_text = soup.get_text()
            text_blocks = re.split(r'\n\s*\n', all_text)
            
            for block in text_blocks:
                block = block.strip()
                if self.is_valid_member_block(block):
                    member_data = self.extract_member_info(block)
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

    def scrape_all_pages(self):
        """Scrape all pages with pagination"""
        print("Starting comprehensive BAI Coimbatore members scraping...")
        
        # First, get the first page to understand the structure
        html_content = self.get_page_content(self.members_url)
        if not html_content:
            print("Failed to fetch the main page")
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for total records count
        total_records_text = soup.find_all(text=re.compile(r'(\d+)\s*records'))
        if total_records_text:
            for text in total_records_text:
                match = re.search(r'(\d+)\s*records', text)
                if match:
                    total_records = int(match.group(1))
                    print(f"Found total records: {total_records}")
                    # Estimate pages (assuming 20 records per page)
                    self.total_pages = (total_records // 20) + 1
                    break
        
        # If we can't find total records, try to scrape until we get no new results
        if self.total_pages == 0:
            self.total_pages = 20  # Start with reasonable estimate
        
        print(f"Attempting to scrape {self.total_pages} pages...")
        
        # Scrape first page
        members_found = self.parse_page_content(soup, 1)
        print(f"Page 1: Found {members_found} members")
        
        # Scrape remaining pages
        consecutive_empty_pages = 0
        for page_num in range(2, self.total_pages + 1):
            members_found = self.scrape_page(page_num)
            print(f"Page {page_num}: Found {members_found} members")
            
            if members_found == 0:
                consecutive_empty_pages += 1
                if consecutive_empty_pages >= 3:  # Stop if 3 consecutive pages are empty
                    print(f"Stopping at page {page_num} - no more data found")
                    break
            else:
                consecutive_empty_pages = 0
            
            # Be respectful with requests
            time.sleep(1)
        
        print(f"\n✅ Successfully scraped {len(self.members_data)} unique BAI members")
        return self.members_data

    def save_to_json(self, filename='bai_members_complete.json'):
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

    def save_to_csv(self, filename='bai_members_complete.csv'):
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
    scraper = FinalBAIScraper()
    
    # Scrape all pages
    members = scraper.scrape_all_pages()
    
    if members:
        # Save in multiple formats
        scraper.save_to_json()
        scraper.save_to_csv()
        scraper.save_to_database()
        
        print(f"\n✅ Successfully scraped {len(members)} BAI members!")
        print("Files created:")
        print("- bai_members_complete.json")
        print("- bai_members_complete.csv")
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
