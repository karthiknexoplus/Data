import time
import pandas as pd
from improved_selenium_scraper import ImprovedGoogleMapsScraper

class FinalSuppliersScraper:
    def __init__(self):
        self.selenium_scraper = ImprovedGoogleMapsScraper()

    def scrape_by_pincode(self, pincode):
        """Scrape suppliers for a specific pincode using Selenium"""
        try:
            print(f"Scraping real suppliers for pincode {pincode}")
            
            # Use the improved Selenium scraper for all categories
            suppliers = self.selenium_scraper.scrape_all_categories(pincode, "Coimbatore")
            
            # Remove duplicates
            unique_suppliers = []
            seen = set()
            for supplier in suppliers:
                key = supplier['name']
                if key not in seen:
                    seen.add(key)
                    unique_suppliers.append(supplier)
            
            print(f"Found {len(unique_suppliers)} unique suppliers for pincode {pincode}")
            return unique_suppliers
            
        except Exception as e:
            print(f"Error scraping suppliers for pincode {pincode}: {str(e)}")
            return []

    def run_scraping(self, pincodes=None):
        """Main method to run the scraping process"""
        print("Starting final suppliers scraping...")
        all_suppliers = []
        
        if not pincodes:
            pincodes = ['641001', '641002', '641015', '641016']
        
        for pincode in pincodes:
            print(f"Scraping suppliers for pincode {pincode}...")
            suppliers = self.scrape_by_pincode(pincode)
            all_suppliers.extend(suppliers)
            time.sleep(2)  # Delay between pincodes
        
        # Save to CSV
        if all_suppliers:
            df = pd.DataFrame(all_suppliers)
            df.to_csv('suppliers_final.csv', index=False)
            print(f"Saved {len(all_suppliers)} suppliers to suppliers_final.csv")
        
        return all_suppliers

if __name__ == "__main__":
    scraper = FinalSuppliersScraper()
    scraper.run_scraping()
