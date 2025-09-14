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

class BAIScraper:
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

    def parse_member_data(self, member_element):
        """Parse individual member data from HTML element"""
        try:
            member_data = {
                'company_name': '',
                'contact_person': '',
                'address': '',
                'phone': '',
                'email': '',
                'source_url': self.members_url,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Extract company name (usually in bold or strong tags)
            company_elem = member_element.find(['strong', 'b'])
            if company_elem:
                member_data['company_name'] = company_elem.get_text(strip=True)
            
            # Extract contact person (usually after company name)
            text_content = member_element.get_text()
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            
            # Look for contact person pattern
            for i, line in enumerate(lines):
                if line == member_data['company_name'] and i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if next_line and next_line != 'NA' and not next_line.startswith('NO.'):
                        member_data['contact_person'] = next_line
                    break
            
            # Extract address (look for lines starting with NO. or containing road/street info)
            address_lines = []
            for line in lines:
                if (line.startswith('NO.') or 
                    any(keyword in line.upper() for keyword in ['ROAD', 'STREET', 'NAGAR', 'COLONY', 'AVENUE', 'LAYOUT', 'POST', 'COIMBATORE'])):
                    address_lines.append(line)
            
            if address_lines:
                member_data['address'] = ' '.join(address_lines)
            
            # Extract phone number
            phone_pattern = r'(\+?91[\s-]?)?[6-9]\d{9}'
            phone_match = re.search(phone_pattern, text_content)
            if phone_match:
                member_data['phone'] = phone_match.group(0).strip()
            
            # Extract email
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_match = re.search(email_pattern, text_content)
            if email_match:
                member_data['email'] = email_match.group(0).strip()
            
            return member_data
            
        except Exception as e:
            print(f"Error parsing member data: {e}")
            return None

    def scrape_members(self):
        """Scrape all BAI members from Coimbatore"""
        print("Starting BAI Coimbatore members scraping...")
        
        html_content = self.get_page_content(self.members_url)
        if not html_content:
            print("Failed to fetch the main page")
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all member elements - they seem to be in divs or similar containers
        # Looking for patterns that contain company names and contact info
        member_elements = []
        
        # Try different selectors to find member data
        selectors = [
            'div[style*="margin"]',
            'div[class*="member"]',
            'div[class*="company"]',
            'p',
            'div'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text(strip=True)
                # Check if this looks like a member entry
                if (len(text) > 50 and 
                    any(keyword in text.upper() for keyword in ['CONSTRUCTION', 'BUILDERS', 'ASSOCIATES', 'INFRASTRUCTURE', 'PROMOTERS']) and
                    'COIMBATORE' in text.upper()):
                    member_elements.append(elem)
        
        print(f"Found {len(member_elements)} potential member elements")
        
        # Parse each member element
        for i, element in enumerate(member_elements):
            print(f"Processing member {i+1}/{len(member_elements)}")
            member_data = self.parse_member_data(element)
            if member_data and member_data['company_name']:
                self.members_data.append(member_data)
                print(f"  - {member_data['company_name']} | {member_data['contact_person']}")
            
            # Be respectful with requests
            time.sleep(0.5)
        
        print(f"Successfully scraped {len(self.members_data)} BAI members")
        return self.members_data

    def save_to_json(self, filename='bai_members.json'):
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

    def save_to_csv(self, filename='bai_members.csv'):
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
    scraper = BAIScraper()
    
    # Scrape the data
    members = scraper.scrape_members()
    
    if members:
        # Save in multiple formats
        scraper.save_to_json()
        scraper.save_to_csv()
        scraper.save_to_database()
        
        print(f"\n✅ Successfully scraped {len(members)} BAI members!")
        print("Files created:")
        print("- bai_members.json")
        print("- bai_members.csv")
        print("- Database table: bai_members")
    else:
        print("❌ No members data scraped")

if __name__ == "__main__":
    main()
