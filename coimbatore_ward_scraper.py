import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def scrape_coimbatore_wards():
    """Scrape Coimbatore ward data from the website"""
    print("🔍 Scraping Coimbatore Ward List...")
    
    url = "https://coimbatorejunction.in/coimbatore-ward-list/"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract ward data
        wards_data = []
        
        # Find all ward sections
        ward_sections = soup.find_all(['h3', 'h4'], string=re.compile(r'Coimbatore \d+ Ward List'))
        
        for section in ward_sections:
            ward_info = extract_ward_info(section, soup)
            if ward_info:
                wards_data.append(ward_info)
        
        # If the above method doesn't work, try alternative approach
        if not wards_data:
            wards_data = extract_wards_alternative(soup)
        
        return wards_data
        
    except Exception as e:
        print(f"❌ Error scraping: {str(e)}")
        return []

def extract_ward_info(section, soup):
    """Extract information for a specific ward"""
    try:
        # Extract ward number
        ward_text = section.get_text()
        ward_match = re.search(r'Coimbatore (\d+) Ward List', ward_text)
        if not ward_match:
            return None
        
        ward_number = ward_match.group(1)
        
        # Find the next elements containing ward details
        ward_data = {
            'ward_number': ward_number,
            'ward_name': f"Ward {ward_number}",
            'directions': {}
        }
        
        # Look for North, South, East, West sections
        current = section.find_next()
        while current and current.name in ['h4', 'h5', 'p', 'ul', 'li']:
            text = current.get_text().strip()
            
            if 'North Ward List' in text:
                ward_data['directions']['north'] = extract_direction_details(current)
            elif 'South Ward List' in text:
                ward_data['directions']['south'] = extract_direction_details(current)
            elif 'East Ward List' in text:
                ward_data['directions']['east'] = extract_direction_details(current)
            elif 'West Ward List' in text:
                ward_data['directions']['west'] = extract_direction_details(current)
            
            current = current.find_next()
        
        return ward_data
        
    except Exception as e:
        print(f"Error extracting ward info: {e}")
        return None

def extract_direction_details(element):
    """Extract details for a specific direction (North/South/East/West)"""
    try:
        details = []
        current = element.find_next()
        
        while current and current.name in ['p', 'ul', 'li']:
            text = current.get_text().strip()
            if text and len(text) > 10:  # Filter out very short text
                details.append(text)
            current = current.find_next()
            
            # Stop if we hit another ward section
            if current and current.name in ['h3', 'h4'] and 'Ward List' in current.get_text():
                break
        
        return details
        
    except Exception as e:
        print(f"Error extracting direction details: {e}")
        return []

def extract_wards_alternative(soup):
    """Alternative method to extract ward data"""
    try:
        wards_data = []
        
        # Look for ward numbers in the content
        content = soup.get_text()
        
        # Extract ward numbers 1-100
        for ward_num in range(1, 101):
            ward_pattern = rf'Coimbatore {ward_num} Ward List'
            if ward_pattern in content:
                ward_data = {
                    'ward_number': str(ward_num),
                    'ward_name': f"Ward {ward_num}",
                    'directions': {
                        'north': [],
                        'south': [],
                        'east': [],
                        'west': []
                    }
                }
                wards_data.append(ward_data)
        
        return wards_data
        
    except Exception as e:
        print(f"Error in alternative extraction: {e}")
        return []

def save_to_json(data, filename="coimbatore_wards.json"):
    """Save ward data to JSON file"""
    try:
        output_data = {
            "extracted_at": datetime.now().isoformat(),
            "source": "Coimbatore Junction - Ward List",
            "source_url": "https://coimbatorejunction.in/coimbatore-ward-list/",
            "total_wards": len(data),
            "data": {
                "wards": data
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Data saved to {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving to JSON: {str(e)}")
        return False

def main():
    print("🚀 Starting Coimbatore Ward Scraper...")
    
    wards_data = scrape_coimbatore_wards()
    
    if wards_data:
        save_to_json(wards_data)
        print(f"\n🎉 Successfully scraped {len(wards_data)} wards!")
        print("📁 Files created:")
        print("   - coimbatore_wards.json")
        
        # Show sample data
        print("\n📋 Sample ward data:")
        for ward in wards_data[:3]:
            print(f"Ward {ward['ward_number']}: {len(ward['directions'])} directions")
    else:
        print("❌ No ward data found")

if __name__ == "__main__":
    main()
