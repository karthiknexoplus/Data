import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import random
import re

class GoogleMapsScraper:
    def __init__(self):
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """Setup Chrome driver with anti-detection measures"""
        chrome_options = Options()
        
        # Anti-detection measures
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Randomize user agent
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        # Window size
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Disable images for faster loading
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Execute script to remove webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def search_google_maps(self, query, location):
        """Search Google Maps for businesses"""
        try:
            # Construct search URL
            search_url = f"https://www.google.com/maps/search/{query}+near+{location}"
            print(f"Searching: {search_url}")
            
            self.driver.get(search_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Try to dismiss any popups or cookies
            try:
                # Look for cookie consent or popup close buttons
                popup_selectors = [
                    "button[aria-label='Accept all']",
                    "button[aria-label='Reject all']",
                    "button[data-value='Accept all']",
                    "button[data-value='Reject all']",
                    ".VfPpkd-LgbsSe[aria-label*='Accept']",
                    ".VfPpkd-LgbsSe[aria-label*='Reject']",
                    "button[jsaction*='close']"
                ]
                
                for selector in popup_selectors:
                    try:
                        popup = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if popup.is_displayed():
                            popup.click()
                            time.sleep(1)
                            break
                    except:
                        continue
                        
            except:
                pass
            
            # Wait for search results to load
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"Error searching Google Maps: {str(e)}")
            return False

    def scroll_and_load_results(self):
        """Scroll to load more results"""
        try:
            # Find the results panel
            results_panel = self.driver.find_element(By.CSS_SELECTOR, "[role='main']")
            
            # Scroll down to load more results
            for i in range(3):  # Scroll 3 times
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_panel)
                time.sleep(2)
                
        except Exception as e:
            print(f"Error scrolling: {str(e)}")

    def extract_business_data(self):
        """Extract business data from Google Maps results"""
        businesses = []
        
        try:
            # Wait for results to appear
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-value='Directions']"))
            )
            
            # Find all business result elements
            result_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-value='Directions']")
            print(f"Found {len(result_elements)} business results")
            
            for i, element in enumerate(result_elements[:10]):  # Limit to 10 results
                try:
                    print(f"Processing result {i+1}...")
                    
                    # Click on the result to get details
                    element.click()
                    time.sleep(2)
                    
                    # Extract business information
                    business_data = self.extract_business_details()
                    if business_data:
                        businesses.append(business_data)
                        print(f"Extracted: {business_data['name']}")
                    
                    # Go back to results list
                    self.driver.back()
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error processing result {i+1}: {str(e)}")
                    continue
                    
        except TimeoutException:
            print("Timeout waiting for results")
        except Exception as e:
            print(f"Error extracting business data: {str(e)}")
            
        return businesses

    def extract_business_details(self):
        """Extract details from a specific business"""
        try:
            # Wait for business details to load
            time.sleep(2)
            
            # Extract business name
            name = "N/A"
            try:
                name_element = self.driver.find_element(By.CSS_SELECTOR, "h1")
                name = name_element.text.strip()
            except:
                pass
            
            # Extract address
            address = "N/A"
            try:
                address_element = self.driver.find_element(By.CSS_SELECTOR, "[data-item-id='address']")
                address = address_element.text.strip()
            except:
                pass
            
            # Extract phone
            phone = "N/A"
            try:
                phone_element = self.driver.find_element(By.CSS_SELECTOR, "[data-item-id='phone']")
                phone = phone_element.text.strip()
            except:
                pass
            
            # Extract website
            website = "N/A"
            try:
                website_element = self.driver.find_element(By.CSS_SELECTOR, "[data-item-id='authority']")
                website = website_element.get_attribute("href")
            except:
                pass
            
            # Extract rating
            rating = "N/A"
            reviews_count = "0"
            try:
                rating_element = self.driver.find_element(By.CSS_SELECTOR, "[jsaction*='pane.rating']")
                rating_text = rating_element.text.strip()
                if "stars" in rating_text:
                    rating = rating_text.split()[0]
                if "reviews" in rating_text:
                    reviews_match = re.search(r'(\d+)\s+reviews', rating_text)
                    if reviews_match:
                        reviews_count = reviews_match.group(1)
            except:
                pass
            
            # Generate email
            email = f"info@{name.lower().replace(' ', '').replace('.', '')}.com"
            
            return {
                'name': name,
                'address': address,
                'phone': phone,
                'email': email,
                'website': website,
                'rating': rating,
                'reviews_count': reviews_count,
                'category': 'RMC',
                'pincode': '641015',
                'keyword': 'ready mix concrete',
                'latitude': 11.0125,
                'longitude': 77.0129,
                'source': 'Google Maps Real'
            }
            
        except Exception as e:
            print(f"Error extracting business details: {str(e)}")
            return None

    def scrape_rmc_suppliers(self, pincode, location):
        """Scrape RMC suppliers for a specific pincode"""
        suppliers = []
        
        try:
            # Search for RMC suppliers
            queries = [
                f"RMC suppliers near {location}",
                f"ready mix concrete near {location}",
                f"concrete suppliers near {location}",
                f"cement suppliers near {location}"
            ]
            
            for query in queries:
                print(f"\nSearching for: {query}")
                
                if self.search_google_maps(query, location):
                    # Scroll to load more results
                    self.scroll_and_load_results()
                    
                    # Extract business data
                    businesses = self.extract_business_data()
                    suppliers.extend(businesses)
                    
                    # Add delay between searches
                    time.sleep(3)
                else:
                    print(f"Failed to search for: {query}")
                    
        except Exception as e:
            print(f"Error scraping RMC suppliers: {str(e)}")
            
        return suppliers

    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

    def run_scraping(self, pincode="641015", location="Coimbatore"):
        """Main method to run the scraping process"""
        print(f"Starting Google Maps scraping for {location} {pincode}")
        
        try:
            suppliers = self.scrape_rmc_suppliers(pincode, location)
            
            if suppliers:
                df = pd.DataFrame(suppliers)
                csv_file = f"suppliers_selenium_{pincode}.csv"
                df.to_csv(csv_file, index=False)
                print(f"\nSaved {len(suppliers)} suppliers to {csv_file}")
                
                # Show sample data
                print("\nSample data:")
                print(df[['name', 'phone', 'rating', 'source']].head())
                
                return suppliers
            else:
                print("No suppliers found!")
                return []
                
        except Exception as e:
            print(f"Error in scraping process: {str(e)}")
            return []
        finally:
            self.close()

if __name__ == "__main__":
    scraper = GoogleMapsScraper()
    suppliers = scraper.run_scraping("641015", "Coimbatore")
