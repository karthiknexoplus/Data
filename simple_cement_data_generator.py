import pandas as pd
import time
import requests
from bs4 import BeautifulSoup
import json

def create_cement_suppliers_data():
    """Create realistic cement supplier data for Coimbatore"""
    print("🏗️ Creating cement supplier data for Coimbatore...")
    
    cement_suppliers = [
        {
            'company_name': 'ABC Cement Suppliers',
            'address': '123, Gandhipuram, Coimbatore - 641012',
            'phone': '+91-422-1234567',
            'email': 'info@abccement.com',
            'website': 'https://www.abccement.com',
            'products': ['Portland Cement', 'Ready Mix Concrete', 'Cement Blocks', 'Mortar'],
            'description': 'Leading cement supplier in Coimbatore with 20+ years experience',
            'category': 'Cement Suppliers',
            'location': 'Coimbatore'
        },
        {
            'company_name': 'XYZ Construction Materials',
            'address': '456, Peelamedu, Coimbatore - 641004',
            'phone': '+91-422-9876543',
            'email': 'sales@xyzconstruction.com',
            'website': 'https://www.xyzconstruction.com',
            'products': ['Cement', 'Steel', 'Sand', 'Aggregates', 'Bricks'],
            'description': 'Complete construction materials supplier and dealer',
            'category': 'Construction Materials',
            'location': 'Coimbatore'
        },
        {
            'company_name': 'Coimbatore Cement Works',
            'address': '789, R.S. Puram, Coimbatore - 641002',
            'phone': '+91-422-5555555',
            'email': 'contact@cbecement.com',
            'website': 'https://www.cbecement.com',
            'products': ['OPC Cement', 'PPC Cement', 'Ready Mix Concrete', 'Cement Blocks'],
            'description': 'Manufacturer and supplier of quality cement products',
            'category': 'Cement Manufacturers',
            'location': 'Coimbatore'
        },
        {
            'company_name': 'Tamil Nadu Cement Dealers',
            'address': '321, Saibaba Colony, Coimbatore - 641011',
            'phone': '+91-422-7777777',
            'email': 'info@tncement.com',
            'website': 'https://www.tncement.com',
            'products': ['Cement', 'Concrete Mix', 'Cement Paint', 'Waterproofing'],
            'description': 'Authorized dealer for major cement brands in Tamil Nadu',
            'category': 'Cement Dealers',
            'location': 'Coimbatore'
        },
        {
            'company_name': 'South India Ready Mix',
            'address': '654, Avinashi Road, Coimbatore - 641018',
            'phone': '+91-422-8888888',
            'email': 'sales@southindiamix.com',
            'website': 'https://www.southindiamix.com',
            'products': ['Ready Mix Concrete', 'Cement', 'Sand', 'Aggregates'],
            'description': 'Specialized in ready mix concrete solutions',
            'category': 'Ready Mix Concrete',
            'location': 'Coimbatore'
        },
        {
            'company_name': 'Builders Choice Cement',
            'address': '987, Race Course, Coimbatore - 641018',
            'phone': '+91-422-9999999',
            'email': 'info@builderschoice.com',
            'website': 'https://www.builderschoice.com',
            'products': ['Cement', 'Concrete Blocks', 'Mortar Mix', 'Cement Paint'],
            'description': 'Premium cement and construction materials supplier',
            'category': 'Cement Suppliers',
            'location': 'Coimbatore'
        },
        {
            'company_name': 'Coimbatore Construction Supply',
            'address': '147, Ukkadam, Coimbatore - 641001',
            'phone': '+91-422-1111111',
            'email': 'contact@cbeconstruction.com',
            'website': 'https://www.cbeconstruction.com',
            'products': ['Cement', 'Steel', 'Sand', 'Bricks', 'Tiles'],
            'description': 'One-stop shop for all construction materials',
            'category': 'Construction Materials',
            'location': 'Coimbatore'
        },
        {
            'company_name': 'Modern Cement Solutions',
            'address': '258, Singanallur, Coimbatore - 641005',
            'phone': '+91-422-2222222',
            'email': 'sales@moderncement.com',
            'website': 'https://www.moderncement.com',
            'products': ['Modern Cement', 'Eco-friendly Concrete', 'Cement Blocks'],
            'description': 'Modern and eco-friendly cement solutions',
            'category': 'Cement Manufacturers',
            'location': 'Coimbatore'
        },
        {
            'company_name': 'Reliable Cement Suppliers',
            'address': '369, Podanur, Coimbatore - 641023',
            'phone': '+91-422-3333333',
            'email': 'info@reliablecement.com',
            'website': 'https://www.reliablecement.com',
            'products': ['Cement', 'Concrete Mix', 'Cement Paint', 'Waterproofing'],
            'description': 'Reliable cement supply with timely delivery',
            'category': 'Cement Suppliers',
            'location': 'Coimbatore'
        },
        {
            'company_name': 'Coimbatore Cement Hub',
            'address': '741, Sulur, Coimbatore - 641402',
            'phone': '+91-422-4444444',
            'email': 'contact@cbehub.com',
            'website': 'https://www.cbehub.com',
            'products': ['Cement', 'Ready Mix Concrete', 'Cement Blocks', 'Mortar'],
            'description': 'Central hub for cement and construction materials',
            'category': 'Cement Dealers',
            'location': 'Coimbatore'
        }
    ]
    
    return cement_suppliers

def save_data_to_files(suppliers_data):
    """Save the data to CSV and JSON files"""
    print("💾 Saving data to files...")
    
    # Create DataFrame
    df = pd.DataFrame(suppliers_data)
    
    # Save to CSV
    csv_file = "coimbatore_cement_suppliers.csv"
    df.to_csv(csv_file, index=False)
    print(f"✅ Saved to: {csv_file}")
    
    # Save to JSON
    json_file = "coimbatore_cement_suppliers.json"
    with open(json_file, 'w') as f:
        json.dump(suppliers_data, f, indent=2)
    print(f"✅ Saved to: {json_file}")
    
    # Create a summary file
    summary_file = "cement_suppliers_summary.txt"
    with open(summary_file, 'w') as f:
        f.write("COIMBATORE CEMENT SUPPLIERS SUMMARY\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Total Suppliers: {len(suppliers_data)}\n\n")
        
        # Group by category
        categories = {}
        for supplier in suppliers_data:
            category = supplier['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(supplier['company_name'])
        
        f.write("SUPPLIERS BY CATEGORY:\n")
        f.write("-" * 25 + "\n")
        for category, companies in categories.items():
            f.write(f"\n{category} ({len(companies)}):\n")
            for company in companies:
                f.write(f"  • {company}\n")
        
        f.write(f"\n\nCONTACT INFORMATION:\n")
        f.write("-" * 20 + "\n")
        for supplier in suppliers_data:
            f.write(f"\n{supplier['company_name']}:\n")
            f.write(f"  Address: {supplier['address']}\n")
            f.write(f"  Phone: {supplier['phone']}\n")
            f.write(f"  Email: {supplier['email']}\n")
            f.write(f"  Website: {supplier['website']}\n")
            f.write(f"  Products: {', '.join(supplier['products'])}\n")
    
    print(f"✅ Summary saved to: {summary_file}")
    
    return df

def display_data_preview(df):
    """Display a preview of the data"""
    print("\n📊 DATA PREVIEW:")
    print("=" * 50)
    
    print(f"Total Suppliers: {len(df)}")
    print(f"Categories: {df['category'].nunique()}")
    print(f"Locations: {df['location'].nunique()}")
    
    print(f"\n📋 CATEGORIES:")
    category_counts = df['category'].value_counts()
    for category, count in category_counts.items():
        print(f"  • {category}: {count} suppliers")
    
    print(f"\n📋 SAMPLE SUPPLIERS:")
    for i, row in df.head(3).iterrows():
        print(f"\n{i+1}. {row['company_name']}")
        print(f"   Address: {row['address']}")
        print(f"   Phone: {row['phone']}")
        print(f"   Products: {', '.join(row['products'])}")

def create_search_queries():
    """Create search queries for future web scraping"""
    queries = [
        "cement suppliers coimbatore",
        "cement dealers coimbatore",
        "construction materials coimbatore",
        "ready mix concrete coimbatore",
        "cement manufacturers coimbatore",
        "building materials coimbatore",
        "cement distributors coimbatore",
        "concrete suppliers coimbatore"
    ]
    
    queries_file = "cement_search_queries.txt"
    with open(queries_file, 'w') as f:
        f.write("CEMENT SUPPLIER SEARCH QUERIES FOR COIMBATORE\n")
        f.write("=" * 50 + "\n\n")
        for i, query in enumerate(queries, 1):
            f.write(f"{i}. {query}\n")
    
    print(f"✅ Search queries saved to: {queries_file}")
    return queries

def main():
    """Main function"""
    print("🏗️ COIMBATORE CEMENT SUPPLIERS DATA GENERATOR")
    print("=" * 50)
    
    # Create the data
    suppliers_data = create_cement_suppliers_data()
    
    # Save to files
    df = save_data_to_files(suppliers_data)
    
    # Display preview
    display_data_preview(df)
    
    # Create search queries
    queries = create_search_queries()
    
    print(f"\n✅ SUCCESS!")
    print(f"📊 Generated {len(suppliers_data)} cement suppliers")
    print(f"💾 Data saved in multiple formats")
    print(f"🔍 Created {len(queries)} search queries for future scraping")
    
    print(f"\n📁 FILES CREATED:")
    print(f"  • coimbatore_cement_suppliers.csv")
    print(f"  • coimbatore_cement_suppliers.json")
    print(f"  • cement_suppliers_summary.txt")
    print(f"  • cement_search_queries.txt")

if __name__ == "__main__":
    main()
