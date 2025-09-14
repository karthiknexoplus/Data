import requests
from bs4 import BeautifulSoup
import json
import csv
import pandas as pd
from datetime import datetime
import time

class CREDAIScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "https://www.credaicoimbatore.com"
        self.members_url = "https://www.credaicoimbatore.com/about/members-of-credai"
        
    def scrape_members(self):
        """Scrape CREDAI Coimbatore members"""
        print("🔍 Starting CREDAI Coimbatore members scraping...")
        
        try:
            response = self.session.get(self.members_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all member entries
            members = []
            
            # Look for member names in various possible structures
            # The page shows company names as headings
            member_headings = soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6'])
            
            for heading in member_headings:
                text = heading.get_text(strip=True)
                # Filter out navigation and other non-member headings
                if (text and 
                    len(text) > 5 and 
                    not any(skip in text.lower() for skip in [
                        'home', 'about', 'contact', 'news', 'events', 'insights',
                        'credai', 'portal', 'fairpro', 'members of', 'committee',
                        'quick links', 'copyright', 'tree plantation'
                    ]) and
                    any(keyword in text.lower() for keyword in [
                        'pvt', 'ltd', 'llp', 'foundation', 'developers', 'builders',
                        'properties', 'housing', 'constructions', 'estates', 'realtors'
                    ])):
                    
                    member = {
                        'name': text,
                        'type': 'Member',
                        'source_url': self.members_url,
                        'scraped_at': datetime.now().isoformat()
                    }
                    members.append(member)
            
            # Also look for any divs or sections that might contain member info
            member_sections = soup.find_all('div', class_=lambda x: x and 'member' in x.lower())
            for section in member_sections:
                text = section.get_text(strip=True)
                if text and len(text) > 10 and 'pvt' in text.lower():
                    member = {
                        'name': text,
                        'type': 'Member',
                        'source_url': self.members_url,
                        'scraped_at': datetime.now().isoformat()
                    }
                    if member not in members:  # Avoid duplicates
                        members.append(member)
            
            print(f"✅ Found {len(members)} CREDAI members")
            return members
            
        except Exception as e:
            print(f"❌ Error scraping CREDAI members: {str(e)}")
            return []
    
    def save_to_json(self, data, filename="credai_members.json"):
        """Save data to JSON file"""
        try:
            output_data = {
                "scraped_at": datetime.now().isoformat(),
                "source": "CREDAI Coimbatore",
                "total_records": len(data),
                "data": {
                    "members": data
                }
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Data saved to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving to JSON: {str(e)}")
            return False
    
    def save_to_csv(self, data, filename="credai_members.csv"):
        """Save data to CSV file"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['S.No', 'Name', 'Type', 'Source URL', 'Scraped At'])
                
                for i, member in enumerate(data, 1):
                    writer.writerow([
                        i,
                        member.get('name', ''),
                        member.get('type', ''),
                        member.get('source_url', ''),
                        member.get('scraped_at', '')
                    ])
            
            print(f"✅ Data saved to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving to CSV: {str(e)}")
            return False

def main():
    scraper = CREDAIScraper()
    
    # Scrape members
    members = scraper.scrape_members()
    
    if members:
        # Save to files
        scraper.save_to_json(members)
        scraper.save_to_csv(members)
        
        print(f"\n🎉 Successfully scraped {len(members)} CREDAI members!")
        print("📁 Files created:")
        print("   - credai_members.json")
        print("   - credai_members.csv")
    else:
        print("❌ No members found")

if __name__ == "__main__":
    main()
