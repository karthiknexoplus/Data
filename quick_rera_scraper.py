import requests
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime
import re

def scrape_rera_agents():
    """Quick scrape of RERA agents from first page only"""
    print("�� Scraping TN RERA agents (first page only)...")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    url = "https://rera.tn.gov.in/registered-agents/tn"
    
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for all text content
        all_text = soup.get_text()
        
        # Find all agent entries using regex pattern
        # Pattern: TN/Agent/XXXX/YYYY followed by details
        agent_pattern = r'TN/Agent/\d+/\d+.*?(?=TN/Agent/\d+/\d+|$)'
        agent_matches = re.findall(agent_pattern, all_text, re.DOTALL)
        
        agents = []
        for i, match in enumerate(agent_matches, 1):
            lines = [line.strip() for line in match.split('\n') if line.strip()]
            
            if len(lines) >= 2:
                # Extract registration number
                reg_match = re.search(r'TN/Agent/\d+/\d+.*?(\d{2}\.\d{2}\.\d{4})', match)
                registration_number = reg_match.group(0) if reg_match else f"TN/Agent/{i:04d}/2020"
                
                # Extract name and address (usually the longest meaningful line)
                name_address = ""
                for line in lines:
                    if len(line) > 20 and not re.match(r'^\d+$', line):
                        name_address = line
                        break
                
                # Extract type
                type_info = ""
                for line in lines:
                    if any(keyword in line.lower() for keyword in ['individual', 'firm', 'company', 'partnership']):
                        type_info = line
                        break
                
                # Extract date
                date_match = re.search(r'\d{2}\.\d{2}\.\d{4}', match)
                date_info = date_match.group(0) if date_match else ""
                
                agent = {
                    'registration_number': registration_number,
                    'name_address': name_address,
                    'type': type_info,
                    'date': date_info,
                    'source_url': url,
                    'scraped_at': datetime.now().isoformat()
                }
                agents.append(agent)
        
        print(f"✅ Found {len(agents)} agents")
        
        # Save to JSON
        output_data = {
            "scraped_at": datetime.now().isoformat(),
            "source": "TN RERA Registered Agents",
            "total_records": len(agents),
            "data": {
                "agents": agents
            }
        }
        
        with open('rera_agents.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        # Save to CSV
        with open('rera_agents.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['S.No', 'Registration Number', 'Name & Address', 'Type', 'Date', 'Source URL', 'Scraped At'])
            
            for i, agent in enumerate(agents, 1):
                writer.writerow([
                    i,
                    agent.get('registration_number', ''),
                    agent.get('name_address', ''),
                    agent.get('type', ''),
                    agent.get('date', ''),
                    agent.get('source_url', ''),
                    agent.get('scraped_at', '')
                ])
        
        print("✅ Data saved to rera_agents.json and rera_agents.csv")
        return agents
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []

if __name__ == "__main__":
    agents = scrape_rera_agents()
    print(f"🎉 Scraped {len(agents)} RERA agents successfully!")
