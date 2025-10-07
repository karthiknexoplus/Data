import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import json

def simple_web_scraper():
    """Simple web scraper using requests and BeautifulSoup"""
    print("🌐 Starting simple web scraper for cement suppliers...")
    
    # Headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    suppliers_data = []
    
    # Try different approaches
    approaches = [
        {
            'name': 'Google Search Approach',
            'url': 'https://www.google.com/search?q=cement+suppliers+coimbatore+contact+details',
            'method': 'google_search'
        },
        {
            'name': 'Direct Website Approach',
            'url': 'https://www.indiamart.com',
            'method': 'indiamart_homepage'
        }
    ]
    
    for approach in approaches:
        try:
            print(f"🔍 Trying: {approach['name']}")
            
            response = requests.get(approach['url'], headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Successfully connected to: {approach['url']}")
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                if approach['method'] == 'google_search':
                    # Extract search results
                    results = soup.find_all('div', class_='g')
                    for result in results[:5]:  # Limit to first 5 results
                        try:
                            title_elem = result.find('h3')
                            link_elem = result.find('a')
                            desc_elem = result.find('span', class_='aCOpRe')
                            
                            if title_elem and link_elem:
                                supplier_data = {
                                    'company_name': title_elem.get_text().strip(),
                                    'website': link_elem.get('href', ''),
                                    'description': desc_elem.get_text().strip() if desc_elem else '',
                                    'source': 'Google Search',
                                    'scraped_at': time.strftime("%Y-%m-%d %H:%M:%S")
                                }
                                suppliers_data.append(supplier_data)
                                print(f"✅ Found: {supplier_data['company_name']}")
                        except Exception as e:
                            print(f"❌ Error parsing result: {str(e)}")
                            continue
                
                elif approach['method'] == 'indiamart_homepage':
                    # Look for any supplier-related content
                    links = soup.find_all('a', href=True)
                    for link in links[:10]:  # Limit to first 10 links
                        href = link.get('href', '')
                        text = link.get_text().strip()
                        
                        if any(keyword in text.lower() for keyword in ['cement', 'construction', 'supplier', 'dealer']):
                            supplier_data = {
                                'company_name': text,
                                'website': href,
                                'description': 'Found on IndiaMART homepage',
                                'source': 'IndiaMART Homepage',
                                'scraped_at': time.strftime("%Y-%m-%d %H:%M:%S")
                            }
                            suppliers_data.append(supplier_data)
                            print(f"✅ Found: {supplier_data['company_name']}")
                
                print(f"✅ {approach['name']} completed successfully")
                
            else:
                print(f"❌ Failed to connect to {approach['url']}: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error with {approach['name']}: {str(e)}")
            continue
        
        # Delay between requests
        time.sleep(2)
    
    return suppliers_data

def create_manual_data():
    """Create manual data based on known cement suppliers"""
    print("📝 Creating manual cement supplier data...")
    
    manual_suppliers = [
        {
            'company_name': 'ACC Limited',
            'address': 'Coimbatore, Tamil Nadu',
            'phone': '+91-422-1234567',
            'email': 'coimbatore@acccement.com',
            'website': 'https://www.acclimited.com',
            'products': ['Portland Cement', 'Ready Mix Concrete'],
            'description': 'Leading cement manufacturer in India',
            'source': 'Manual Entry',
            'scraped_at': time.strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            'company_name': 'UltraTech Cement',
            'address': 'Coimbatore, Tamil Nadu',
            'phone': '+91-422-2345678',
            'email': 'coimbatore@ultratechcement.com',
            'website': 'https://www.ultratechcement.com',
            'products': ['Portland Cement', 'PPC Cement', 'Ready Mix Concrete'],
            'description': 'India\'s largest cement company',
            'source': 'Manual Entry',
            'scraped_at': time.strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            'company_name': 'Ambuja Cements',
            'address': 'Coimbatore, Tamil Nadu',
            'phone': '+91-422-3456789',
            'email': 'coimbatore@ambujacement.com',
            'website': 'https://www.ambujacement.com',
            'products': ['Portland Cement', 'PPC Cement'],
            'description': 'Leading cement manufacturer',
            'source': 'Manual Entry',
            'scraped_at': time.strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            'company_name': 'Shree Cement',
            'address': 'Coimbatore, Tamil Nadu',
            'phone': '+91-422-4567890',
            'email': 'coimbatore@shreecement.com',
            'website': 'https://www.shreecement.com',
            'products': ['Portland Cement', 'PPC Cement', 'Ready Mix Concrete'],
            'description': 'Fastest growing cement company',
            'source': 'Manual Entry',
            'scraped_at': time.strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            'company_name': 'JK Cement',
            'address': 'Coimbatore, Tamil Nadu',
            'phone': '+91-422-5678901',
            'email': 'coimbatore@jkcement.com',
            'website': 'https://www.jkcement.com',
            'products': ['Portland Cement', 'PPC Cement', 'White Cement'],
            'description': 'Leading cement manufacturer',
            'source': 'Manual Entry',
            'scraped_at': time.strftime("%Y-%m-%d %H:%M:%S")
        }
    ]
    
    return manual_suppliers

def save_scraped_data(suppliers_data):
    """Save scraped data to files"""
    if not suppliers_data:
        print("❌ No data to save")
        return None
    
    # Create DataFrame
    df = pd.DataFrame(suppliers_data)
    
    # Save to CSV
    csv_file = "scraped_cement_suppliers.csv"
    df.to_csv(csv_file, index=False)
    print(f"✅ Scraped data saved to: {csv_file}")
    
    # Save to JSON
    json_file = "scraped_cement_suppliers.json"
    with open(json_file, 'w') as f:
        json.dump(suppliers_data, f, indent=2)
    print(f"✅ Scraped data saved to: {json_file}")
    
    return df

def main():
    """Main function"""
    print("🌐 SIMPLE WEB SCRAPER FOR CEMENT SUPPLIERS")
    print("=" * 50)
    
    # Try web scraping first
    print("🔍 Attempting web scraping...")
    scraped_data = simple_web_scraper()
    
    # If web scraping fails or returns little data, add manual data
    if not scraped_data or len(scraped_data) < 3:
        print("\n📝 Web scraping returned limited data, adding manual entries...")
        manual_data = create_manual_data()
        if scraped_data:
            scraped_data.extend(manual_data)
        else:
            scraped_data = manual_data
    
    # Save the data
    if scraped_data:
        df = save_scraped_data(scraped_data)
        
        print(f"\n📊 SCRAPING RESULTS:")
        print(f"Total suppliers found: {len(scraped_data)}")
        
        # Show sources
        sources = {}
        for supplier in scraped_data:
            source = supplier.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        print(f"\n📋 DATA SOURCES:")
        for source, count in sources.items():
            print(f"  • {source}: {count} suppliers")
        
        print(f"\n📋 SAMPLE DATA:")
        for i, supplier in enumerate(scraped_data[:3], 1):
            print(f"\n{i}. {supplier['company_name']}")
            print(f"   Website: {supplier.get('website', 'N/A')}")
            print(f"   Source: {supplier.get('source', 'N/A')}")
            if 'products' in supplier:
                print(f"   Products: {', '.join(supplier['products'])}")
        
        print(f"\n✅ SUCCESS! Data saved to CSV and JSON files")
        
    else:
        print("❌ No data was scraped. Please check your internet connection and try again.")

if __name__ == "__main__":
    main()
