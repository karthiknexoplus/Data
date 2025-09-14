import json
import csv

def create_ward_csv():
    """Convert ward JSON data to CSV format"""
    try:
        with open('coimbatore_wards.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        wards = data['data']['wards']
        
        with open('coimbatore_wards.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Ward Number', 'Ward Name', 'Direction', 'Description'])
            
            for ward in wards:
                ward_num = ward['ward_number']
                ward_name = ward['ward_name']
                
                for direction, descriptions in ward['directions'].items():
                    for desc in descriptions:
                        writer.writerow([ward_num, ward_name, direction.title(), desc])
        
        print("✅ CSV file created: coimbatore_wards.csv")
        
    except Exception as e:
        print(f"❌ Error creating CSV: {e}")

if __name__ == "__main__":
    create_ward_csv()
