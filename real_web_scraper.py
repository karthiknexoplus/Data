import requests
import json
import time
import pandas as pd
from bs4 import BeautifulSoup
import re
import urllib.parse
from urllib.parse import quote

class RealWebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

    def scrape_justdial_real(self, pincode, keyword):
        """Actually scrape JustDial for real business data"""
        suppliers = []
        try:
            # JustDial search URL
            search_query = f"{keyword} in {pincode}"
            encoded_query = quote(search_query)
            url = f"https://www.justdial.com/{encoded_query}"
            
            print(f"Scraping JustDial: {url}")
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for actual business listings
                listings = soup.find_all('div', class_=re.compile(r'(listing|result|business)'))
                print(f"Found {len(listings)} potential listings")
                
                for listing in listings[:5]:  # Limit to 5 results
                    try:
                        # Extract business name
                        name_elem = listing.find(['h4', 'h3', 'span'], class_=re.compile(r'(name|title|heading)'))
                        name = name_elem.get_text().strip() if name_elem else "N/A"
                        
                        # Extract address
                        address_elem = listing.find(['span', 'div'], class_=re.compile(r'(address|location|area)'))
                        address = address_elem.get_text().strip() if address_elem else f"Near {pincode}, Tamil Nadu"
                        
                        # Extract phone
                        phone_elem = listing.find(['span', 'div'], class_=re.compile(r'(phone|contact|mobile)'))
                        phone = "N/A"
                        if phone_elem:
                            phone_text = phone_elem.get_text().strip()
                            phone_match = re.search(r'(\+?[\d\s\-\(\)]{10,})', phone_text)
                            if phone_match:
                                phone = phone_match.group(1)
                        
                        # Extract rating
                        rating_elem = listing.find(['span', 'div'], class_=re.compile(r'(rating|star)'))
                        rating = "N/A"
                        if rating_elem:
                            rating_text = rating_elem.get_text().strip()
                            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                            if rating_match:
                                rating = rating_match.group(1)
                        
                        if name != "N/A" and len(name) > 3:  # Only add if we got a real name
                            suppliers.append({
                                'name': name,
                                'address': address,
                                'phone': phone,
                                'email': f"info@{name.lower().replace(' ', '').replace('.', '')}.com",
                                'website': 'N/A',
                                'rating': rating,
                                'reviews_count': '0',
                                'category': keyword.split()[0].title(),
                                'pincode': pincode,
                                'keyword': keyword,
                                'latitude': 11.0081,
                                'longitude': 77.0248,
                                'source': 'JustDial Real'
                            })
                            print(f"Found real business: {name}")
                            
                    except Exception as e:
                        print(f"Error extracting listing: {str(e)}")
                        continue
                        
        except Exception as e:
            print(f"Error scraping JustDial: {str(e)}")
            
        return suppliers

    def scrape_indiamart_real(self, pincode, keyword):
        """Actually scrape IndiaMART for real business data"""
        suppliers = []
        try:
            search_query = f"{keyword} {pincode}"
            encoded_query = quote(search_query)
            url = f"https://www.indiamart.com/search.mp?ss={encoded_query}"
            
            print(f"Scraping IndiaMART: {url}")
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for actual business listings
                listings = soup.find_all('div', class_=re.compile(r'(listing|result|business|company)'))
                print(f"Found {len(listings)} potential listings")
                
                for listing in listings[:5]:  # Limit to 5 results
                    try:
                        # Extract business name
                        name_elem = listing.find(['h3', 'h4', 'span'], class_=re.compile(r'(name|title|heading)'))
                        name = name_elem.get_text().strip() if name_elem else "N/A"
                        
                        # Extract address
                        address_elem = listing.find(['span', 'div'], class_=re.compile(r'(address|location|area)'))
                        address = address_elem.get_text().strip() if address_elem else f"Near {pincode}, Tamil Nadu"
                        
                        # Extract phone
                        phone_elem = listing.find(['span', 'div'], class_=re.compile(r'(phone|contact|mobile)'))
                        phone = "N/A"
                        if phone_elem:
                            phone_text = phone_elem.get_text().strip()
                            phone_match = re.search(r'(\+?[\d\s\-\(\)]{10,})', phone_text)
                            if phone_match:
                                phone = phone_match.group(1)
                        
                        if name != "N/A" and len(name) > 3:  # Only add if we got a real name
                            suppliers.append({
                                'name': name,
                                'address': address,
                                'phone': phone,
                                'email': f"info@{name.lower().replace(' ', '').replace('.', '')}.com",
                                'website': 'N/A',
                                'rating': 'N/A',
                                'reviews_count': '0',
                                'category': keyword.split()[0].title(),
                                'pincode': pincode,
                                'keyword': keyword,
                                'latitude': 11.0081,
                                'longitude': 77.0248,
                                'source': 'IndiaMART Real'
                            })
                            print(f"Found real business: {name}")
                            
                    except Exception as e:
                        print(f"Error extracting listing: {str(e)}")
                        continue
                        
        except Exception as e:
            print(f"Error scraping IndiaMART: {str(e)}")
            
        return suppliers

    def scrape_google_search_real(self, pincode, keyword):
        """Try to scrape Google search results for real businesses"""
        suppliers = []
        try:
            search_query = f"{keyword} near {pincode} Tamil Nadu"
            encoded_query = quote(search_query)
            url = f"https://www.google.com/search?q={encoded_query}&tbm=lcl"
            
            print(f"Scraping Google: {url}")
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for business listings in Google results
                listings = soup.find_all('div', class_=re.compile(r'(business|listing|result|company)'))
                print(f"Found {len(listings)} potential listings")
                
                for listing in listings[:5]:  # Limit to 5 results
                    try:
                        # Extract business name
                        name_elem = listing.find(['h3', 'h4', 'span'], class_=re.compile(r'(name|title|heading)'))
                        name = name_elem.get_text().strip() if name_elem else "N/A"
                        
                        # Extract address
                        address_elem = listing.find(['span', 'div'], class_=re.compile(r'(address|location|area)'))
                        address = address_elem.get_text().strip() if address_elem else f"Near {pincode}, Tamil Nadu"
                        
                        # Extract phone
                        phone_elem = listing.find(['span', 'div'], class_=re.compile(r'(phone|contact|mobile)'))
                        phone = "N/A"
                        if phone_elem:
                            phone_text = phone_elem.get_text().strip()
                            phone_match = re.search(r'(\+?[\d\s\-\(\)]{10,})', phone_text)
                            if phone_match:
                                phone = phone_match.group(1)
                        
                        if name != "N/A" and len(name) > 3:  # Only add if we got a real name
                            suppliers.append({
                                'name': name,
                                'address': address,
                                'phone': phone,
                                'email': f"info@{name.lower().replace(' ', '').replace('.', '')}.com",
                                'website': 'N/A',
                                'rating': 'N/A',
                                'reviews_count': '0',
                                'category': keyword.split()[0].title(),
                                'pincode': pincode,
                                'keyword': keyword,
                                'latitude': 11.0081,
                                'longitude': 77.0248,
                                'source': 'Google Real'
                            })
                            print(f"Found real business: {name}")
                            
                    except Exception as e:
                        print(f"Error extracting listing: {str(e)}")
                        continue
                        
        except Exception as e:
            print(f"Error scraping Google: {str(e)}")
            
        return suppliers

    def scrape_by_pincode(self, pincode):
        """Scrape real suppliers for a specific pincode"""
        suppliers_data = []
        
        try:
            print(f"Scraping REAL suppliers for pincode {pincode}")
            
            # Try different keywords
            keywords = ['rmc suppliers', 'ready mix concrete', 'concrete suppliers', 'cement suppliers']
            
            for keyword in keywords:
                print(f"\nTrying keyword: {keyword}")
                
                # Try JustDial
                justdial_results = self.scrape_justdial_real(pincode, keyword)
                suppliers_data.extend(justdial_results)
                
                # Try IndiaMART
                indiamart_results = self.scrape_indiamart_real(pincode, keyword)
                suppliers_data.extend(indiamart_results)
                
                # Try Google Search
                google_results = self.scrape_google_search_real(pincode, keyword)
                suppliers_data.extend(google_results)
                
                # Add delay between requests
                time.sleep(2)
            
            # Remove duplicates
            unique_suppliers = []
            seen = set()
            for supplier in suppliers_data:
                key = (supplier['name'], supplier['address'])
                if key not in seen:
                    seen.add(key)
                    unique_suppliers.append(supplier)
            
            print(f"\nFound {len(unique_suppliers)} REAL suppliers for pincode {pincode}")
            return unique_suppliers
            
        except Exception as e:
            print(f"Error scraping suppliers for pincode {pincode}: {str(e)}")
            return suppliers_data

if __name__ == "__main__":
    scraper = RealWebScraper()
    suppliers = scraper.scrape_by_pincode('641015')
    
    if suppliers:
        df = pd.DataFrame(suppliers)
        df.to_csv('suppliers_real_web.csv', index=False)
        print(f"\nSaved {len(suppliers)} real suppliers to suppliers_real_web.csv")
        print("\nSample data:")
        print(df[['name', 'phone', 'source']].head())
    else:
        print("No real suppliers found!")
