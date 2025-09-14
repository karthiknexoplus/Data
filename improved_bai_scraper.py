#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import re
from urllib.parse import urljoin, urlparse
import sqlite3
from datetime import datetime

class ImprovedBAIScraper:
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

    def get_page_content(self, url):
        """Get page content with error handling"""
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
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
        
        # First line is usually the company name (in bold)
        company_name = lines[0]
        if company_name and len(company_name) > 3:
            member_data['company_name'] = company_name
        
        # Look for contact person (usually second line if not NA)
        if len(lines) > 1:
            contact_person = lines[1]
            if contact_person and contact_person != 'NA' and not contact_person.startswith('NO.'):
                member_data['contact_person'] = contact_person
        
        # Extract address (lines starting with NO. or containing address keywords)
        address_parts = []
        for line in lines:
            if (line.startswith('NO.') or 
                any(keyword in line.upper() for keyword in ['ROAD', 'STREET', 'NAGAR', 'COLONY', 'AVENUE', 'LAYOUT', 'POST', 'COIMBATORE', 'FLOOR', 'BUILDING', 'COMPLEX'])):
                address_parts.append(line)
        
        if address_parts:
            member_data['address'] = ' '.join(address_parts)
        
        # Extract phone number
        phone_pattern = r'(\+?91[\s-]?)?[6-9]\d{9}'
        phone_match = re.search(phone_pattern, text_block)
        if phone_match:
            member_data['phone'] = phone_match.group(0).strip()
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text_block)
        if email_match:
            member_data['email'] = email_match.group(0).strip()
        
        return member_data

    def scrape_members(self):
        """Scrape BAI members with improved parsing"""
        print("Starting improved BAI Coimbatore members scraping...")
        
        html_content = self.get_page_content(self.members_url)
        if not html_content:
            print("Failed to fetch the main page")
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for the specific pattern from the website
        # Based on the website structure, members seem to be in specific containers
        members_found = set()  # To avoid duplicates
        
        # Try to find member blocks - they appear to be in specific divs or containers
        # Look for text that contains company names and addresses
        all_text = soup.get_text()
        
        # Split by common separators and look for member patterns
        # The website shows members in a specific format
        text_blocks = re.split(r'\n\s*\n', all_text)
        
        for block in text_blocks:
            block = block.strip()
            if not block or len(block) < 50:
                continue
            
            # Check if this looks like a member entry
            if (any(keyword in block.upper() for keyword in [
                'CONSTRUCTION', 'BUILDERS', 'ASSOCIATES', 'INFRASTRUCTURE', 
                'PROMOTERS', 'DEVELOPERS', 'CONTRACTORS', 'ENGINEERS'
            ]) and 'COIMBATORE' in block.upper()):
                
                member_data = self.extract_member_info(block)
                if member_data and member_data['company_name']:
                    # Create a unique key to avoid duplicates
                    unique_key = f"{member_data['company_name']}_{member_data['contact_person']}"
                    if unique_key not in members_found:
                        members_found.add(unique_key)
                        self.members_data.append(member_data)
                        print(f"  ✓ {member_data['company_name']} | {member_data['contact_person']}")
        
        # If the above method doesn't work well, try a more targeted approach
        if len(self.members_data) < 10:
            print("Trying alternative parsing method...")
            self.alternative_parsing(soup)
        
        print(f"Successfully scraped {len(self.members_data)} unique BAI members")
        return self.members_data

    def alternative_parsing(self, soup):
        """Alternative parsing method for member data"""
        # Look for specific HTML patterns that might contain member data
        # This is a fallback method
        
        # Find all text that might contain member information
        all_elements = soup.find_all(['div', 'p', 'span', 'td'])
        
        for element in all_elements:
            text = element.get_text(strip=True)
            if (len(text) > 30 and len(text) < 500 and 
                any(keyword in text.upper() for keyword in ['CONSTRUCTION', 'BUILDERS', 'ASSOCIATES']) and
                'COIMBATORE' in text.upper()):
                
                member_data = self.extract_member_info(text)
                if member_data and member_data['company_name']:
                    # Check for duplicates
                    if not any(m['company_name'] == member_data['company_name'] and 
                             m['contact_person'] == member_data['contact_person'] 
                             for m in self.members_data):
                        self.members_data.append(member_data)
                        print(f"  ✓ {member_data['company_name']} | {member_data['contact_person']}")

    def save_to_json(self, filename='bai_members_improved.json'):
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

    def save_to_csv(self, filename='bai_members_improved.csv'):
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
    scraper = ImprovedBAIScraper()
    
    # Scrape the data
    members = scraper.scrape_members()
    
    if members:
        # Save in multiple formats
        scraper.save_to_json()
        scraper.save_to_csv()
        scraper.save_to_database()
        
        print(f"\n✅ Successfully scraped {len(members)} BAI members!")
        print("Files created:")
        print("- bai_members_improved.json")
        print("- bai_members_improved.csv")
        print("- Database table: bai_members")
        
        # Show sample data
        print("\n📋 Sample data:")
        for i, member in enumerate(members[:3]):
            print(f"{i+1}. {member['company_name']}")
            print(f"   Contact: {member['contact_person']}")
            print(f"   Address: {member['address'][:100]}...")
            print(f"   Phone: {member['phone']}")
            print()
    else:
        print("❌ No members data scraped")

if __name__ == "__main__":
    main()
