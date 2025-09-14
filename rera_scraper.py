import requests
from bs4 import BeautifulSoup
import json
import csv
import pandas as pd
from datetime import datetime
import time
import re

class RERAScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "https://rera.tn.gov.in"
        self.agents_url = "https://rera.tn.gov.in/registered-agents/tn"
        
    def scrape_agents(self, max_pages=5):
        """Scrape TN RERA registered agents"""
        print("🔍 Starting TN RERA registered agents scraping...")
        
        all_agents = []
        
        try:
            for page in range(1, max_pages + 1):
                print(f"📄 Scraping page {page}...")
                
                # Try different URL patterns for pagination
                page_urls = [
                    f"{self.agents_url}?page={page}",
                    f"{self.agents_url}/page/{page}",
                    f"{self.agents_url}?p={page}",
                    self.agents_url if page == 1 else f"{self.agents_url}?page={page}"
                ]
                
                page_agents = []
                for url in page_urls:
                    try:
                        response = self.session.get(url, timeout=30)
                        response.raise_for_status()
                        
                        soup = BeautifulSoup(response.content, 'html.parser')
                        page_agents = self.parse_agents_page(soup)
                        
                        if page_agents:
                            print(f"✅ Found {len(page_agents)} agents on page {page}")
                            break
                            
                    except Exception as e:
                        print(f"⚠️ Error with URL {url}: {str(e)}")
                        continue
                
                if not page_agents:
                    print(f"❌ No agents found on page {page}, stopping...")
                    break
                    
                all_agents.extend(page_agents)
                time.sleep(1)  # Be respectful to the server
                
        except Exception as e:
            print(f"❌ Error scraping RERA agents: {str(e)}")
            
        print(f"✅ Total agents scraped: {len(all_agents)}")
        return all_agents
    
    def parse_agents_page(self, soup):
        """Parse agents from a single page"""
        agents = []
        
        # Look for table rows or list items containing agent data
        # Try different selectors based on common patterns
        
        # Method 1: Look for table rows
        table_rows = soup.find_all('tr')
        for row in table_rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 4:  # At least 4 columns
                agent_data = self.extract_agent_from_row(cells)
                if agent_data:
                    agents.append(agent_data)
        
        # Method 2: Look for div containers with agent info
        if not agents:
            agent_divs = soup.find_all('div', class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['agent', 'card', 'item', 'row']
            ))
            
            for div in agent_divs:
                text = div.get_text(strip=True)
                if self.is_agent_data(text):
                    agent_data = self.extract_agent_from_text(text)
                    if agent_data:
                        agents.append(agent_data)
        
        # Method 3: Look for any text that matches the pattern
        if not agents:
            all_text = soup.get_text()
            # Look for patterns like "TN/Agent/0241/2020"
            agent_patterns = re.findall(r'TN/Agent/\d+/\d+.*?(?=TN/Agent/\d+/\d+|$)', all_text, re.DOTALL)
            
            for pattern in agent_patterns:
                agent_data = self.extract_agent_from_text(pattern)
                if agent_data:
                    agents.append(agent_data)
        
        return agents
    
    def extract_agent_from_row(self, cells):
        """Extract agent data from table row cells"""
        try:
            if len(cells) < 4:
                return None
                
            # Clean and extract data from cells
            registration_number = cells[0].get_text(strip=True)
            name_address = cells[1].get_text(strip=True)
            type_info = cells[2].get_text(strip=True) if len(cells) > 2 else ""
            date_info = cells[3].get_text(strip=True) if len(cells) > 3 else ""
            
            if not registration_number or not name_address:
                return None
                
            return {
                'registration_number': registration_number,
                'name_address': name_address,
                'type': type_info,
                'date': date_info,
                'source_url': self.agents_url,
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error extracting agent from row: {e}")
            return None
    
    def extract_agent_from_text(self, text):
        """Extract agent data from text block"""
        try:
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if len(lines) < 2:
                return None
                
            # Look for registration number pattern
            reg_match = re.search(r'TN/Agent/\d+/\d+.*?(\d{2}\.\d{2}\.\d{4})', text)
            if not reg_match:
                return None
                
            registration_number = reg_match.group(0)
            
            # Extract name and address (usually the longest line)
            name_address = max(lines, key=len) if lines else ""
            
            # Extract type (look for keywords)
            type_info = ""
            for line in lines:
                if any(keyword in line.lower() for keyword in ['individual', 'firm', 'company', 'partnership']):
                    type_info = line
                    break
            
            # Extract date
            date_match = re.search(r'\d{2}\.\d{2}\.\d{4}', text)
            date_info = date_match.group(0) if date_match else ""
            
            return {
                'registration_number': registration_number,
                'name_address': name_address,
                'type': type_info,
                'date': date_info,
                'source_url': self.agents_url,
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error extracting agent from text: {e}")
            return None
    
    def is_agent_data(self, text):
        """Check if text contains agent data"""
        return bool(re.search(r'TN/Agent/\d+/\d+', text))
    
    def save_to_json(self, data, filename="rera_agents.json"):
        """Save data to JSON file"""
        try:
            output_data = {
                "scraped_at": datetime.now().isoformat(),
                "source": "TN RERA Registered Agents",
                "total_records": len(data),
                "data": {
                    "agents": data
                }
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Data saved to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving to JSON: {str(e)}")
            return False
    
    def save_to_csv(self, data, filename="rera_agents.csv"):
        """Save data to CSV file"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['S.No', 'Registration Number', 'Name & Address', 'Type', 'Date', 'Source URL', 'Scraped At'])
                
                for i, agent in enumerate(data, 1):
                    writer.writerow([
                        i,
                        agent.get('registration_number', ''),
                        agent.get('name_address', ''),
                        agent.get('type', ''),
                        agent.get('date', ''),
                        agent.get('source_url', ''),
                        agent.get('scraped_at', '')
                    ])
            
            print(f"✅ Data saved to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving to CSV: {str(e)}")
            return False

def main():
    scraper = RERAScraper()
    
    # Scrape agents (try 3 pages first)
    agents = scraper.scrape_agents(max_pages=3)
    
    if agents:
        # Save to files
        scraper.save_to_json(agents)
        scraper.save_to_csv(agents)
        
        print(f"\n🎉 Successfully scraped {len(agents)} RERA agents!")
        print("📁 Files created:")
        print("   - rera_agents.json")
        print("   - rera_agents.csv")
    else:
        print("❌ No agents found")

if __name__ == "__main__":
    main()
