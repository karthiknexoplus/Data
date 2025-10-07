import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import json
import re
from urllib.parse import urljoin, urlparse

class RealCementSupplierScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        self.suppliers_data = []
    
    def scrape_indiamart_search(self, search_term):
        """Scrape IndiaMART search results"""
        print(f"🔍 Searching IndiaMART for: {search_term}")
        
        try:
            # IndiaMART search URL
            search_url = f"https://www.indiamart.com/search.mp?ss={search_term.replace(' ', '+')}"
            
            response = self.session.get(search_url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for supplier listings
                supplier_selectors = [
                    '.lst_cl',
                    '.supplier-item',
                    '.company-item',
                    '.listing-item',
                    '[class*="supplier"]',
                    '[class*="company"]'
                ]
                
                suppliers = []
                for selector in supplier_selectors:
                    elements = soup.select(selector)
                    if elements:
                        suppliers = elements
                        print(f"✅ Found {len(suppliers)} suppliers using selector: {selector}")
                        break
                
                if suppliers:
                    for supplier in suppliers[:10]:  # Limit to first 10
                        try:
                            supplier_data = self.extract_indiamart_supplier(supplier)
                            if supplier_data and supplier_data.get('company_name'):
                                self.suppliers_data.append(supplier_data)
                                print(f"✅ Extracted: {supplier_data['company_name']}")
                        except Exception as e:
                            print(f"❌ Error extracting supplier: {str(e)}")
                            continue
                
                return True
            else:
                print(f"❌ Failed to access IndiaMART: Status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error scraping IndiaMART: {str(e)}")
            return False
    
    def extract_indiamart_supplier(self, supplier_element):
        """Extract data from IndiaMART supplier element"""
        supplier_data = {
            'company_name': '',
            'address': '',
            'phone': '',
            'email': '',
            'website': '',
            'products': [],
            'description': '',
            'source': 'IndiaMART',
            'scraped_at': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            # Company name
            name_selectors = ['.gcnm', '.company-name', 'h2', 'h3', 'h4', '.title']
            for selector in name_selectors:
                element = supplier_element.select_one(selector)
                if element and element.get_text().strip():
                    supplier_data['company_name'] = element.get_text().strip()
                    break
            
            # Address
            address_selectors = ['.clg', '.address', '.location', '.city']
            for selector in address_selectors:
                element = supplier_element.select_one(selector)
                if element and element.get_text().strip():
                    supplier_data['address'] = element.get_text().strip()
                    break
            
            # Phone
            phone_selectors = ['.bo', '.phone', '.contact', 'a[href^="tel:"]']
            for selector in phone_selectors:
                element = supplier_element.select_one(selector)
                if element:
                    phone_text = element.get_text().strip() or element.get('href', '').replace('tel:', '')
                    if phone_text and re.search(r'\d', phone_text):
                        supplier_data['phone'] = phone_text
                        break
            
            # Email
            email_selectors = ['a[href^="mailto:"]', '.email']
            for selector in email_selectors:
                element = supplier_element.select_one(selector)
                if element:
                    email_text = element.get_text().strip() or element.get('href', '').replace('mailto:', '')
                    if email_text and '@' in email_text:
                        supplier_data['email'] = email_text
                        break
            
            # Website
            website_selectors = ['a[href^="http"]', '.website']
            for selector in website_selectors:
                element = supplier_element.select_one(selector)
                if element:
                    href = element.get('href', '')
                    if href and not href.startswith('mailto:') and not href.startswith('tel:'):
                        supplier_data['website'] = href
                        break
            
            # Products
            product_selectors = ['.cp5', '.product', '.item']
            for selector in product_selectors:
                elements = supplier_element.select(selector)
                products = []
                for elem in elements:
                    product_name = elem.select_one('.gpnm, .product-name, .item-name')
                    if product_name and product_name.get_text().strip():
                        products.append(product_name.get_text().strip())
                if products:
                    supplier_data['products'] = products
                    break
            
            # Description
            desc_selectors = ['.description', '.desc', '.summary']
            for selector in desc_selectors:
                element = supplier_element.select_one(selector)
                if element and element.get_text().strip():
                    supplier_data['description'] = element.get_text().strip()[:200]
                    break
            
            return supplier_data
            
        except Exception as e:
            print(f"❌ Error extracting supplier data: {str(e)}")
            return None
    
    def scrape_google_business(self, search_term):
        """Scrape Google Business listings"""
        print(f"🔍 Searching Google Business for: {search_term}")
        
        try:
            # Google search for business listings
            search_url = f"https://www.google.com/search?q={search_term.replace(' ', '+')}+contact+details+phone+address"
            
            response = self.session.get(search_url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for business listings
                business_selectors = [
                    '.g',
                    '.tF2Cxc',
                    '.yuRUbf'
                ]
                
                businesses = []
                for selector in business_selectors:
                    elements = soup.select(selector)
                    if elements:
                        businesses = elements
                        print(f"✅ Found {len(businesses)} businesses using selector: {selector}")
                        break
                
                if businesses:
                    for business in businesses[:5]:  # Limit to first 5
                        try:
                            business_data = self.extract_google_business(business)
                            if business_data and business_data.get('company_name'):
                                self.suppliers_data.append(business_data)
                                print(f"✅ Extracted: {business_data['company_name']}")
                        except Exception as e:
                            print(f"❌ Error extracting business: {str(e)}")
                            continue
                
                return True
            else:
                print(f"❌ Failed to access Google: Status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error scraping Google: {str(e)}")
            return False
    
    def extract_google_business(self, business_element):
        """Extract data from Google business element"""
        business_data = {
            'company_name': '',
            'address': '',
            'phone': '',
            'email': '',
            'website': '',
            'products': [],
            'description': '',
            'source': 'Google Business',
            'scraped_at': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            # Company name
            name_element = business_element.select_one('h3')
            if name_element:
                business_data['company_name'] = name_element.get_text().strip()
            
            # Website
            link_element = business_element.select_one('a[href^="http"]')
            if link_element:
                business_data['website'] = link_element.get('href', '')
            
            # Description
            desc_element = business_element.select_one('.VwiC3b, .s3v9rd')
            if desc_element:
                business_data['description'] = desc_element.get_text().strip()[:200]
            
            # Try to extract phone and address from description
            description = business_data['description']
            if description:
                # Look for phone numbers
                phone_match = re.search(r'(\+?91[\s-]?\d{2,4}[\s-]?\d{6,8})', description)
                if phone_match:
                    business_data['phone'] = phone_match.group(1)
                
                # Look for addresses
                if 'coimbatore' in description.lower():
                    business_data['address'] = 'Coimbatore, Tamil Nadu'
            
            return business_data
            
        except Exception as e:
            print(f"❌ Error extracting business data: {str(e)}")
            return None
    
    def scrape_justdial(self, search_term):
        """Scrape JustDial listings"""
        print(f"🔍 Searching JustDial for: {search_term}")
        
        try:
            # JustDial search URL
            search_url = f"https://www.justdial.com/Coimbatore/{search_term.replace(' ', '-')}"
            
            response = self.session.get(search_url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for business listings
                business_selectors = [
                    '.cntanr',
                    '.cnt-detail',
                    '.store-details'
                ]
                
                businesses = []
                for selector in business_selectors:
                    elements = soup.select(selector)
                    if elements:
                        businesses = elements
                        print(f"✅ Found {len(businesses)} businesses using selector: {selector}")
                        break
                
                if businesses:
                    for business in businesses[:5]:  # Limit to first 5
                        try:
                            business_data = self.extract_justdial_business(business)
                            if business_data and business_data.get('company_name'):
                                self.suppliers_data.append(business_data)
                                print(f"✅ Extracted: {business_data['company_name']}")
                        except Exception as e:
                            print(f"❌ Error extracting business: {str(e)}")
                            continue
                
                return True
            else:
                print(f"❌ Failed to access JustDial: Status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error scraping JustDial: {str(e)}")
            return False
    
    def extract_justdial_business(self, business_element):
        """Extract data from JustDial business element"""
        business_data = {
            'company_name': '',
            'address': '',
            'phone': '',
            'email': '',
            'website': '',
            'products': [],
            'description': '',
            'source': 'JustDial',
            'scraped_at': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            # Company name
            name_element = business_element.select_one('h4, .store-name, .company-name')
            if name_element:
                business_data['company_name'] = name_element.get_text().strip()
            
            # Address
            address_element = business_element.select_one('.address, .location, .addr')
            if address_element:
                business_data['address'] = address_element.get_text().strip()
            
            # Phone
            phone_element = business_element.select_one('.tel, .phone, .contact')
            if phone_element:
                business_data['phone'] = phone_element.get_text().strip()
            
            # Website
            website_element = business_element.select_one('a[href^="http"]')
            if website_element:
                business_data['website'] = website_element.get('href', '')
            
            return business_data
            
        except Exception as e:
            print(f"❌ Error extracting JustDial data: {str(e)}")
            return None
    
    def run_scraping(self):
        """Run the complete scraping process"""
        print("🚀 Starting real cement supplier scraping...")
        print("=" * 60)
        
        # Search terms for cement suppliers in Coimbatore
        search_terms = [
            "cement suppliers coimbatore",
            "cement dealers coimbatore",
            "construction materials coimbatore",
            "ready mix concrete coimbatore",
            "cement manufacturers coimbatore"
        ]
        
        # Try different sources
        sources = [
            {'name': 'IndiaMART', 'method': self.scrape_indiamart_search},
            {'name': 'Google Business', 'method': self.scrape_google_business},
            {'name': 'JustDial', 'method': self.scrape_justdial}
        ]
        
        for search_term in search_terms:
            print(f"\n🔍 Searching for: {search_term}")
            
            for source in sources:
                try:
                    print(f"📡 Trying {source['name']}...")
                    success = source['method'](search_term)
                    
                    if success:
                        print(f"✅ {source['name']} completed successfully")
                    else:
                        print(f"❌ {source['name']} failed")
                    
                    # Delay between requests
                    time.sleep(3)
                    
                except Exception as e:
                    print(f"❌ Error with {source['name']}: {str(e)}")
                    continue
        
        # Remove duplicates
        unique_suppliers = []
        seen_names = set()
        
        for supplier in self.suppliers_data:
            name = supplier.get('company_name', '').lower().strip()
            if name and name not in seen_names:
                seen_names.add(name)
                unique_suppliers.append(supplier)
        
        print(f"\n📊 Scraping completed!")
        print(f"Total suppliers found: {len(self.suppliers_data)}")
        print(f"Unique suppliers: {len(unique_suppliers)}")
        
        return unique_suppliers
    
    def save_data(self, suppliers_data):
        """Save the scraped data"""
        if not suppliers_data:
            print("❌ No data to save")
            return None
        
        # Create DataFrame
        df = pd.DataFrame(suppliers_data)
        
        # Save to CSV
        csv_file = "real_cement_suppliers.csv"
        df.to_csv(csv_file, index=False)
        print(f"✅ Real data saved to: {csv_file}")
        
        # Save to JSON
        json_file = "real_cement_suppliers.json"
        with open(json_file, 'w') as f:
            json.dump(suppliers_data, f, indent=2)
        print(f"✅ Real data saved to: {json_file}")
        
        # Create summary
        summary_file = "real_suppliers_summary.txt"
        with open(summary_file, 'w') as f:
            f.write("REAL CEMENT SUPPLIERS - COIMBATORE\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Total Suppliers: {len(suppliers_data)}\n\n")
            
            # Group by source
            sources = {}
            for supplier in suppliers_data:
                source = supplier.get('source', 'Unknown')
                if source not in sources:
                    sources[source] = []
                sources[source].append(supplier['company_name'])
            
            f.write("SUPPLIERS BY SOURCE:\n")
            f.write("-" * 25 + "\n")
            for source, companies in sources.items():
                f.write(f"\n{source} ({len(companies)}):\n")
                for company in companies:
                    f.write(f"  • {company}\n")
            
            f.write(f"\n\nDETAILED INFORMATION:\n")
            f.write("-" * 25 + "\n")
            for supplier in suppliers_data:
                f.write(f"\n{supplier['company_name']}:\n")
                f.write(f"  Source: {supplier.get('source', 'N/A')}\n")
                f.write(f"  Address: {supplier.get('address', 'N/A')}\n")
                f.write(f"  Phone: {supplier.get('phone', 'N/A')}\n")
                f.write(f"  Email: {supplier.get('email', 'N/A')}\n")
                f.write(f"  Website: {supplier.get('website', 'N/A')}\n")
                if supplier.get('products'):
                    f.write(f"  Products: {', '.join(supplier['products'])}\n")
                if supplier.get('description'):
                    f.write(f"  Description: {supplier['description']}\n")
        
        print(f"✅ Summary saved to: {summary_file}")
        
        return df

def main():
    """Main function"""
    print("🌐 REAL CEMENT SUPPLIER SCRAPER")
    print("=" * 40)
    
    scraper = RealCementSupplierScraper()
    
    # Run scraping
    suppliers_data = scraper.run_scraping()
    
    if suppliers_data:
        # Save data
        df = scraper.save_data(suppliers_data)
        
        print(f"\n📊 FINAL RESULTS:")
        print(f"✅ Successfully scraped {len(suppliers_data)} real suppliers")
        
        # Show sources
        sources = {}
        for supplier in suppliers_data:
            source = supplier.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        print(f"\n📋 DATA SOURCES:")
        for source, count in sources.items():
            print(f"  • {source}: {count} suppliers")
        
        print(f"\n📋 SAMPLE REAL DATA:")
        for i, supplier in enumerate(suppliers_data[:3], 1):
            print(f"\n{i}. {supplier['company_name']}")
            print(f"   Source: {supplier.get('source', 'N/A')}")
            print(f"   Address: {supplier.get('address', 'N/A')}")
            print(f"   Phone: {supplier.get('phone', 'N/A')}")
            print(f"   Website: {supplier.get('website', 'N/A')}")
        
        print(f"\n✅ SUCCESS! Real data saved to CSV and JSON files")
        
    else:
        print("❌ No real data was scraped. Please check your internet connection and try again.")

if __name__ == "__main__":
    main()
