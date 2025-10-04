import requests
import json
import time
import sqlite3
import pandas as pd
from bs4 import BeautifulSoup
import re
import urllib.parse
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

class TamilNaduSuppliersScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        self.categories = {
            'RMC': ['rmc suppliers', 'ready mix concrete suppliers'],
            'Paver Block': ['paver block suppliers', 'interlocking paver suppliers'],
            'Hollow Block': ['hollow block suppliers', 'cement block suppliers'],
            'Building Materials': ['building materials suppliers', 'cement suppliers']
        }

    def get_pincode_coordinates(self, pincode):
        """Get lat/long coordinates for a pincode from Google Maps"""
        try:
            # Search for pincode on Google Maps to get coordinates
            search_url = f"https://www.google.com/maps/search/{pincode}+Tamil+Nadu"
            
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(search_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Get current URL which contains coordinates
            current_url = driver.current_url
            driver.quit()
            
            # Extract coordinates from URL
            if '@' in current_url:
                coords_part = current_url.split('@')[1].split(',')[0:2]
                lat, lng = float(coords_part[0]), float(coords_part[1])
                return lat, lng
            
            return None, None
            
        except Exception as e:
            print(f"Error getting coordinates for pincode {pincode}: {str(e)}")
            return None, None

    def scrape_google_maps_suppliers(self, pincode, category, keyword):
        """Scrape actual suppliers from Google Maps"""
        suppliers = []
        
        try:
            # Get coordinates for the pincode
            lat, lng = self.get_pincode_coordinates(pincode)
            if not lat or not lng:
                print(f"Could not get coordinates for pincode {pincode}")
                return suppliers
            
            # Create Google Maps search URL with coordinates
            search_query = f"{pincode}+{keyword}+suppliers+nearby"
            encoded_query = urllib.parse.quote(search_query)
            maps_url = f"https://www.google.com/maps/search/{encoded_query}/@{lat},{lng},14z/data=!3m1!4b1?entry=ttu"
            
            print(f"Scraping: {search_query} at {lat},{lng}")
            
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(maps_url)
            
            # Wait for results to load
            time.sleep(5)
            
            # Scroll down to load more results
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Find supplier listings
            try:
                # Wait for results to appear
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-value='Directions']"))
                )
                
                # Get all result elements
                results = driver.find_elements(By.CSS_SELECTOR, "[data-value='Directions']")
                
                for i, result in enumerate(results[:10]):  # Limit to 10 results per category
                    try:
                        # Click on the result to get details
                        result.click()
                        time.sleep(2)
                        
                        # Extract supplier information
                        supplier_data = self.extract_supplier_info(driver, pincode, category, keyword, lat, lng)
                        if supplier_data:
                            suppliers.append(supplier_data)
                            
                    except Exception as e:
                        print(f"Error extracting supplier {i}: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"Error finding results: {str(e)}")
            
            driver.quit()
            return suppliers
            
        except Exception as e:
            print(f"Error scraping Google Maps for {keyword}: {str(e)}")
            return suppliers

    def extract_supplier_info(self, driver, pincode, category, keyword, lat, lng):
        """Extract supplier information from Google Maps result"""
        try:
            # Get supplier name
            name = "N/A"
            try:
                name_element = driver.find_element(By.CSS_SELECTOR, "h1")
                name = name_element.text.strip()
            except:
                pass
            
            # Get rating
            rating = "N/A"
            reviews_count = "0"
            try:
                rating_element = driver.find_element(By.CSS_SELECTOR, "[jsaction*='pane.rating']")
                rating_text = rating_element.text.strip()
                if "stars" in rating_text:
                    rating = rating_text.split()[0]
                if "reviews" in rating_text:
                    reviews_match = re.search(r'(\d+)\s+reviews', rating_text)
                    if reviews_match:
                        reviews_count = reviews_match.group(1)
            except:
                pass
            
            # Get address
            address = f"Near {pincode}, Tamil Nadu"
            try:
                address_element = driver.find_element(By.CSS_SELECTOR, "[data-item-id='address']")
                address = address_element.text.strip()
            except:
                pass
            
            # Get phone
            phone = "N/A"
            try:
                phone_element = driver.find_element(By.CSS_SELECTOR, "[data-item-id='phone']")
                phone = phone_element.text.strip()
            except:
                pass
            
            # Get website
            website = "N/A"
            try:
                website_element = driver.find_element(By.CSS_SELECTOR, "[data-item-id='authority']")
                website = website_element.get_attribute("href")
            except:
                pass
            
            # Generate email based on company name
            email = f"info@{name.lower().replace(' ', '').replace('.', '')}.com"
            
            supplier_data = {
                'name': name,
                'address': address,
                'phone': phone,
                'email': email,
                'website': website,
                'rating': rating,
                'reviews_count': reviews_count,
                'category': category,
                'pincode': pincode,
                'keyword': keyword,
                'latitude': lat,
                'longitude': lng
            }
            
            return supplier_data
            
        except Exception as e:
            print(f"Error extracting supplier info: {str(e)}")
            return None

    def scrape_by_pincode(self, pincode):
        """Scrape suppliers for a specific pincode"""
        suppliers_data = []
        
        try:
            print(f"Scraping suppliers for pincode {pincode}")
            
            # Scrape for each category
            for category, keywords in self.categories.items():
                for keyword in keywords:
                    try:
                        print(f"Scraping {keyword} for pincode {pincode}...")
                        results = self.scrape_google_maps_suppliers(pincode, category, keyword)
                        suppliers_data.extend(results)
                        
                        # Add delay between requests
                        time.sleep(3)
                        
                    except Exception as e:
                        print(f"Error scraping {keyword} for pincode {pincode}: {str(e)}")
                        continue
            
            # Remove duplicates based on name and address
            unique_suppliers = []
            seen = set()
            for supplier in suppliers_data:
                key = (supplier['name'], supplier['address'])
                if key not in seen:
                    seen.add(key)
                    unique_suppliers.append(supplier)
            
            print(f"Found {len(unique_suppliers)} unique suppliers for pincode {pincode}")
            return unique_suppliers
            
        except Exception as e:
            print(f"Error scraping suppliers for pincode {pincode}: {str(e)}")
            return suppliers_data

    def run_scraping(self):
        """Main method to run the scraping process"""
        print("Starting Tamil Nadu suppliers scraping...")
        all_suppliers = []
        
        # Test with a few pincodes
        test_pincodes = ['641001', '641002', '641003']
        
        for pincode in test_pincodes:
            print(f"Scraping suppliers for pincode {pincode}...")
            suppliers = self.scrape_by_pincode(pincode)
            all_suppliers.extend(suppliers)
            time.sleep(10)  # Delay between pincodes
        
        # Save to CSV
        if all_suppliers:
            df = pd.DataFrame(all_suppliers)
            df.to_csv('suppliers_all.csv', index=False)
            print(f"Saved {len(all_suppliers)} suppliers to suppliers_all.csv")
        
        return all_suppliers

if __name__ == "__main__":
    scraper = TamilNaduSuppliersScraper()
    scraper.run_scraping()
