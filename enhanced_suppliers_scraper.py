import time
import pandas as pd
from improved_selenium_scraper import ImprovedGoogleMapsScraper

class EnhancedSuppliersScraper:
    def __init__(self):
        self.selenium_scraper = ImprovedGoogleMapsScraper()
        
    def scrape_by_pincode(self, pincode, force_refresh=False, category=None, state=None, district=None):
        """Scrape suppliers for a specific pincode without caching"""
        print(f"Scraping suppliers for pincode {pincode}")
        
        # Determine location for search
        if state and district:
            location = f"{district}, {state}"
        elif state:
            location = state
        else:
            location = "Coimbatore"  # Fallback to Coimbatore if no location provided
        
        print(f"Using location: {location}")
        
        # Always scrape fresh data - no caching
        print(f"Scraping fresh data for pincode {pincode}...")
        try:
            if category:
                # Scrape only specific category
                print(f"Scraping only {category} category...")
                suppliers = self.selenium_scraper.scrape_category(pincode, location, category, self._get_category_keywords(category))
            else:
                # Scrape all categories
                suppliers = self.selenium_scraper.scrape_all_categories(pincode, location)
            
            # Remove duplicates based on name
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
    
    def _get_category_keywords(self, category):
        """Get keywords for a specific category"""
        categories = {
            "Building Materials": ["building materials suppliers", "construction materials"],
            'RMC': ['rmc companies', 'ready mix concrete', 'concrete suppliers'],
            'Paver Block': ['paver block suppliers', 'interlocking pavers'],
            'Hollow Block': ['hollow block suppliers', 'cement block suppliers'],
            'Cement': ['cement suppliers', 'building materials']
        }
        return categories.get(category, [])
    
    def get_available_categories(self):
        """Get list of available categories"""
        return ["Building Materials", "RMC", "Paver Block", "Hollow Block", "Cement"]
    
    def get_cache_status(self, pincode):
        """Return cache status - always returns no cache since we removed caching"""
        return {
            "exists": False,
            "age_hours": None,
            "count": 0
        }
    
    def close(self):
        """Close the selenium scraper"""
        if self.selenium_scraper:
            self.selenium_scraper.close()
