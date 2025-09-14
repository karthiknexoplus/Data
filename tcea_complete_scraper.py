#!/usr/bin/env python3
"""
Complete TCEA Scraper - All Pages
Scrapes: Members, Office Bearers, EC Members, Past Leaders
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import csv
from datetime import datetime
import re

class TCEACompleteScraper:
    def __init__(self):
        self.base_url = "https://tcea.in/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.all_data = {
            'members': [],
            'office_bearers': [],
            'ec_members': [],
            'past_leaders': []
        }
    
    def scrape_members(self):
        """Scrape all members from 15 pages"""
        print("Scraping TCEA Members...")
        for page_num in range(15):
            if page_num == 0:
                url = f"{self.base_url}members.html"
            else:
                url = f"{self.base_url}members{page_num}.html"
            
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract member names
                all_text = soup.get_text()
                lines = all_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('Er.') and len(line) > 5:
                        name = re.sub(r'^#+\s*', '', line).strip()
                        if name and name not in [m['name'] for m in self.all_data['members']]:
                            self.all_data['members'].append({
                                'name': name,
                                'page': page_num,
                                'url': url,
                                'type': 'Member'
                            })
                
                print(f"  Page {page_num}: Found members")
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  Error scraping page {page_num}: {str(e)}")
    
    def scrape_office_bearers(self):
        """Scrape office bearers"""
        print("Scraping Office Bearers...")
        try:
            url = f"{self.base_url}officebearers.html"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract office bearers
            all_text = soup.get_text()
            lines = all_text.split('\n')
            
            current_position = None
            for line in lines:
                line = line.strip()
                if line.startswith('Er.') and len(line) > 5:
                    name = re.sub(r'^#+\s*', '', line).strip()
                    if name:
                        self.all_data['office_bearers'].append({
                            'name': name,
                            'position': current_position or 'Office Bearer',
                            'url': url,
                            'type': 'Office Bearer'
                        })
                elif any(pos in line.upper() for pos in ['PRESIDENT', 'SECRETARY', 'TREASURER', 'VICE PRESIDENT', 'JOINT SECRETARY']):
                    current_position = line.strip()
            
            print(f"  Found {len(self.all_data['office_bearers'])} office bearers")
            
        except Exception as e:
            print(f"  Error scraping office bearers: {str(e)}")
    
    def scrape_ec_members(self):
        """Scrape EC members"""
        print("Scraping EC Members...")
        try:
            url = f"{self.base_url}ecmembers.html"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract EC members
            all_text = soup.get_text()
            lines = all_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('Er.') and len(line) > 5:
                    name = re.sub(r'^#+\s*', '', line).strip()
                    if name:
                        self.all_data['ec_members'].append({
                            'name': name,
                            'position': 'EC Member',
                            'url': url,
                            'type': 'EC Member'
                        })
            
            print(f"  Found {len(self.all_data['ec_members'])} EC members")
            
        except Exception as e:
            print(f"  Error scraping EC members: {str(e)}")
    
    def scrape_past_leaders(self):
        """Scrape past leaders"""
        print("Scraping Past Leaders...")
        try:
            url = f"{self.base_url}pastleaders.html"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract past leaders
            all_text = soup.get_text()
            lines = all_text.split('\n')
            
            current_period = None
            current_position = None
            
            for line in lines:
                line = line.strip()
                
                # Check for period (e.g., "2000 - 2003")
                if re.match(r'\d{4}\s*-\s*\d{4}', line):
                    current_period = line
                    continue
                
                # Check for position
                if any(pos in line.upper() for pos in ['PRESIDENT', 'SECRETARY', 'TREASURER']):
                    current_position = line.strip()
                    continue
                
                # Check for member name
                if line.startswith('Er.') and len(line) > 5:
                    name = re.sub(r'^#+\s*', '', line).strip()
                    if name:
                        self.all_data['past_leaders'].append({
                            'name': name,
                            'position': current_position or 'Past Leader',
                            'period': current_period or 'Unknown Period',
                            'url': url,
                            'type': 'Past Leader'
                        })
            
            print(f"  Found {len(self.all_data['past_leaders'])} past leaders")
            
        except Exception as e:
            print(f"  Error scraping past leaders: {str(e)}")
    
    def scrape_all(self):
        """Scrape all TCEA data"""
        print("Starting Complete TCEA Scraping...")
        print("="*50)
        
        self.scrape_members()
        self.scrape_office_bearers()
        self.scrape_ec_members()
        self.scrape_past_leaders()
        
        print("="*50)
        print("SCRAPING COMPLETE!")
        print("="*50)
        
        total = sum(len(data) for data in self.all_data.values())
        print(f"Total records: {total}")
        print(f"  - Members: {len(self.all_data['members'])}")
        print(f"  - Office Bearers: {len(self.all_data['office_bearers'])}")
        print(f"  - EC Members: {len(self.all_data['ec_members'])}")
        print(f"  - Past Leaders: {len(self.all_data['past_leaders'])}")
        
        return self.all_data
    
    def save_to_json(self, filename="tcea_complete_data.json"):
        """Save all data to JSON"""
        data = {
            'scraped_at': datetime.now().isoformat(),
            'source': 'TCEA (Tirupur Civil Engineers Association)',
            'total_records': sum(len(data) for data in self.all_data.values()),
            'data': self.all_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Complete data saved to {filename}")
    
    def save_to_csv(self, filename="tcea_complete_data.csv"):
        """Save all data to CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Type', 'Name', 'Position', 'Period', 'Page', 'Source URL'])
            
            # Write all data
            for data_type, records in self.all_data.items():
                for record in records:
                    writer.writerow([
                        record.get('type', ''),
                        record.get('name', ''),
                        record.get('position', ''),
                        record.get('period', ''),
                        record.get('page', ''),
                        record.get('url', '')
                    ])
        
        print(f"Complete data saved to {filename}")

def main():
    scraper = TCEACompleteScraper()
    data = scraper.scrape_all()
    
    if any(data.values()):
        scraper.save_to_json()
        scraper.save_to_csv()
        print("\n✅ All TCEA data successfully scraped and saved!")
    else:
        print("\n❌ No data found. Please check the website structure.")

if __name__ == "__main__":
    main()
