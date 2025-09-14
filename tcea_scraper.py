#!/usr/bin/env python3
"""
TCEA (Tirupur Civil Engineers Association) Members Scraper
Scrapes member data from all 15 pages of the TCEA website
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import csv
from datetime import datetime
import re

class TCEAScraper:
    def __init__(self):
        self.base_url = "https://tcea.in/"
        self.members_data = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_members_page(self, page_num=None):
        """Scrape members from a specific page"""
        if page_num is None:
            url = f"{self.base_url}members.html"
        else:
            url = f"{self.base_url}members{page_num}.html"
        
        try:
            print(f"Scraping: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all member names (they appear to be in h5 tags or similar)
            members = []
            
            # Look for member names in various possible selectors
            selectors = [
                'h5',
                'h4', 
                'h3',
                '.member-name',
                '[class*="member"]',
                'p'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    # Check if it looks like a member name (starts with "Er.")
                    if text.startswith('Er.') and len(text) > 5:
                        # Clean up the name
                        name = text.replace('#####', '').strip()
                        if name and name not in [m['name'] for m in members]:
                            members.append({
                                'name': name,
                                'page': page_num if page_num is not None else 0,
                                'url': url
                            })
            
            # If no members found with above selectors, try a more general approach
            if not members:
                # Look for any text that starts with "Er."
                all_text = soup.get_text()
                lines = all_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('Er.') and len(line) > 5:
                        # Clean up the name
                        name = re.sub(r'^#+\s*', '', line).strip()
                        if name and name not in [m['name'] for m in members]:
                            members.append({
                                'name': name,
                                'page': page_num if page_num is not None else 0,
                                'url': url
                            })
            
            print(f"Found {len(members)} members on page {page_num if page_num is not None else 0}")
            return members
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return []
    
    def scrape_all_members(self):
        """Scrape members from all pages"""
        print("Starting TCEA Members scraping...")
        
        # Scrape main members page (page 0)
        members = self.scrape_members_page()
        self.members_data.extend(members)
        
        # Scrape pages 1-14
        for page_num in range(1, 15):
            members = self.scrape_members_page(page_num)
            self.members_data.extend(members)
            time.sleep(1)  # Be respectful to the server
        
        print(f"Total members scraped: {len(self.members_data)}")
        return self.members_data
    
    def save_to_json(self, filename="tcea_members.json"):
        """Save members data to JSON file"""
        data = {
            'scraped_at': datetime.now().isoformat(),
            'total_members': len(self.members_data),
            'source': 'TCEA (Tirupur Civil Engineers Association)',
            'members': self.members_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Data saved to {filename}")
    
    def save_to_csv(self, filename="tcea_members.csv"):
        """Save members data to CSV file"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Page', 'Source URL'])
            
            for member in self.members_data:
                writer.writerow([
                    member['name'],
                    member['page'],
                    member['url']
                ])
        
        print(f"Data saved to {filename}")
    
    def get_members_list(self):
        """Get just the list of member names"""
        return [member['name'] for member in self.members_data]

def main():
    scraper = TCEAScraper()
    
    # Scrape all members
    members = scraper.scrape_all_members()
    
    if members:
        # Save to files
        scraper.save_to_json()
        scraper.save_to_csv()
        
        # Print summary
        print("\n" + "="*50)
        print("SCRAPING COMPLETE")
        print("="*50)
        print(f"Total members found: {len(members)}")
        print(f"Pages scraped: 15 (members.html + members1.html to members14.html)")
        print("\nFirst 10 members:")
        for i, member in enumerate(members[:10]):
            print(f"{i+1}. {member['name']}")
        
        if len(members) > 10:
            print(f"... and {len(members) - 10} more members")
    else:
        print("No members found. Please check the website structure.")

if __name__ == "__main__":
    main()
