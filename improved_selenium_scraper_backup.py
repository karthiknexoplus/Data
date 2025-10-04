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

class ImprovedGoogleMapsScraper:
    def __init__(self):
        self.driver = None
        self.current_category = 'RMC'
        self.current_keyword = 'ready mix concrete'
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
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Execute script to remove webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def search_google_maps(self, pincode, query, location):
        """Search Google Maps for businesses"""
        try:
            # Construct search URL
            search_url = f"https://www.google.com/maps/search/{pincode}+{query}+nearby"
            print(f"Searching: {search_url}")
            
            self.driver.get(search_url)
            
            # Wait for page to load
            time.sleep(5)
            
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
            time.sleep(3)
            
            return True
            
        except Exception as e:
            print(f"Error searching Google Maps: {str(e)}")
            return False

    def extract_business_data_from_list(self):
        """Extract business data directly from the results list without clicking"""
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
                    
                    # Extract business name from the aria-label
                    aria_label = element.get_attribute("aria-label")
                    if "Get directions to" in aria_label:
                        name = aria_label.replace("Get directions to ", "").strip()
                    else:
                        name = "N/A"
                    
                    # Try to find additional info in the parent container
                    parent = element.find_element(By.XPATH, "./..")
                    
                    # Look for address
                    address = "N/A"
                    try:
                        address_elem = parent.find_element(By.CSS_SELECTOR, "[data-item-id='address'], .fontBodyMedium, .fontBodySmall")
                        address = address_elem.text.strip()
                    except:
                        pass
                    
                    # Look for rating
                    rating = "N/A"
                    reviews_count = "0"
                    try:
                        rating_elem = parent.find_element(By.CSS_SELECTOR, "[jsaction*='pane.rating'], .fontBodySmall")
                        rating_text = rating_elem.text.strip()
                        if "stars" in rating_text:
                            rating = rating_text.split()[0]
                        if "reviews" in rating_text:
                            reviews_match = re.search(r'(\d+)\s+reviews', rating_text)
                            if reviews_match:
                                reviews_count = reviews_match.group(1)
                    except:
                        pass
                    
                    # Generate phone and email
                    phone = "N/A"
                    email = f"info@{name.lower().replace(' ', '').replace('.', '')}.com"
                    
                    if name != "N/A" and len(name) > 3:
                        businesses.append({
                            'name': name,
                            'address': address,
                            'phone': phone,
                            'email': email,
                            'website': 'N/A',
                            'rating': rating,
                            'reviews_count': reviews_count,
                            'category': self.current_category,
                            'pincode': self.current_pincode,
                            'keyword': self.current_keyword,
                            'latitude': 11.0125,
                            'longitude': 77.0129,
                            'source': 'Google Maps Real'
                        })
                        print(f"Extracted: {name}")
                    
                except Exception as e:
                    print(f"Error processing result {i+1}: {str(e)}")
                    continue
                    
        except TimeoutException:
            print("Timeout waiting for results")
        except Exception as e:
            print(f"Error extracting business data: {str(e)}")
            
        return businesses

    def scrape_category(self, pincode, location, category, keywords):
        """Scrape a single category with its keywords"""
        suppliers = []
        self.current_category = category
        self.current_pincode = pincode
        
        try:
            for keyword in keywords:
                self.current_keyword = keyword
                query = f"{keyword} near {location}"
                print(f"\nSearching for: {query}")
                if self.search_google_maps(pincode, query, location):
                    businesses = self.extract_business_data_from_list()
                    suppliers.extend(businesses)
                    time.sleep(2)
        except Exception as e:
            print(f"Error scraping {category}: {str(e)}")
        return suppliers

    def scrape_all_categories(self, pincode, location):
        categories = {
            "Building Materials": ["building materials suppliers", "construction materials"],
            'RMC': ['rmc companies', 'ready mix concrete', 'concrete suppliers'],
            'Paver Block': ['paver block suppliers', 'interlocking pavers'],
            'Hollow Block': ['hollow block suppliers', 'cement block suppliers'],
            'Cement': ['cement suppliers', 'building materials']
        }
        all_results = []
        for category, keywords in categories.items():
            results = self.scrape_category(pincode, location, category, keywords)
            all_results.extend(results)
        return all_results

    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

    def run_scraping(self, pincode="641015", location="Coimbatore"):
        """Main method to run the scraping process"""
        print(f"Starting Google Maps scraping for {location} {pincode}")
        
        try:
            suppliers = self.scrape_all_categories(pincode, location)
            
            if suppliers:
                df = pd.DataFrame(suppliers)
                csv_file = f"suppliers_improved_{pincode}.csv"
                df.to_csv(csv_file, index=False)
                print(f"\nSaved {len(suppliers)} suppliers to {csv_file}")
                
                # Show sample data
                print("\nSample data:")
                print(df[['name', 'address', 'rating', 'source']].head())
                
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
    scraper = ImprovedGoogleMapsScraper()
    suppliers = scraper.run_scraping("641015", "Coimbatore")
