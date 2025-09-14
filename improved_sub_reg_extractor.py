import fitz  # PyMuPDF
import json
import re
from datetime import datetime

def extract_sub_reg_data():
    """Extract Sub Registrar office data from PDF with better parsing"""
    doc = fitz.open('sub_reg.pdf')
    all_data = []
    current_zone = ""
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        lines = text.split('\n')
        
        # Find zone information
        for line in lines:
            if 'Zone:' in line:
                current_zone = line.split('Zone:')[1].strip()
                break
        
        # Process the page text as a whole for better pattern matching
        page_text = ' '.join(lines)
        
        # Split by office entries (look for P.I.O patterns)
        office_entries = re.split(r'(?=P\.I\.O)', page_text)
        
        for entry in office_entries[1:]:  # Skip first empty entry
            if 'P.I.O' not in entry:
                continue
                
            office_data = {
                'zone': current_zone,
                'office_name': '',
                'designation_under_act': 'P.I.O',
                'designation': '',
                'std_code': '',
                'office_phone': '',
                'home_phone': '',
                'fax': '',
                'email': '',
                'address': ''
            }
            
            # Extract designation
            designation_match = re.search(r'P\.I\.O\s+(.+?)(?:\s+\d{3}|\s+[A-Z]|$)', entry)
            if designation_match:
                office_data['designation'] = designation_match.group(1).strip()
            
            # Extract phone numbers
            phone_matches = re.findall(r'(\d{3})\s+(\d{8})', entry)
            if phone_matches:
                office_data['std_code'] = phone_matches[0][0]
                office_data['office_phone'] = phone_matches[0][1]
            
            # Extract email
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', entry)
            if email_match:
                office_data['email'] = email_match.group(1)
            
            # Extract office name (look for location names before P.I.O)
            # This is tricky, let's look for common patterns
            name_patterns = [
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+P\.I\.O',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Sub\s+Registrar',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+District\s+Registrar'
            ]
            
            for pattern in name_patterns:
                name_match = re.search(pattern, entry)
                if name_match:
                    office_data['office_name'] = name_match.group(1).strip()
                    break
            
            # Extract address (look for lines with common address keywords)
            address_keywords = ['Road', 'Street', 'Salai', 'Veedhi', 'Nagar', 'Chennai', 'Madurai', 'Coimbatore']
            address_lines = re.findall(r'([^.\n]*(?:' + '|'.join(address_keywords) + r')[^.\n]*)', entry)
            if address_lines:
                office_data['address'] = address_lines[0].strip()
            
            # Only add if we have meaningful data
            if (office_data['office_name'] or office_data['designation'] or 
                office_data['office_phone'] or office_data['email']):
                all_data.append(office_data)
    
    doc.close()
    return all_data

def clean_data(data):
    """Clean and standardize the extracted data"""
    cleaned_data = []
    
    for office in data:
        # Clean office name
        if office['office_name']:
            office['office_name'] = re.sub(r'\s+', ' ', office['office_name']).strip()
        
        # Clean designation
        if office['designation']:
            office['designation'] = re.sub(r'\s+', ' ', office['designation']).strip()
        
        # Clean address
        if office['address']:
            office['address'] = re.sub(r'\s+', ' ', office['address']).strip()
        
        # Only keep entries with meaningful data
        if (office['office_name'] or office['designation'] or 
            office['office_phone'] or office['email']):
            cleaned_data.append(office)
    
    return cleaned_data

def save_to_json(data, filename='sub_reg_offices.json'):
    """Save extracted data to JSON file"""
    output_data = {
        'metadata': {
            'extracted_on': datetime.now().isoformat(),
            'total_offices': len(data),
            'source': 'sub_reg.pdf'
        },
        'data': data
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Data saved to {filename}")
    print(f"Total offices extracted: {len(data)}")

if __name__ == '__main__':
    print("Extracting Sub Registrar office data...")
    raw_data = extract_sub_reg_data()
    cleaned_data = clean_data(raw_data)
    save_to_json(cleaned_data)
    
    # Print sample data
    print("\nSample data:")
    for i, office in enumerate(cleaned_data[:10]):
        print(f"\n{i+1}. {office['office_name']} ({office['zone']})")
        print(f"   Designation: {office['designation']}")
        print(f"   Phone: {office['std_code']} {office['office_phone']}")
        print(f"   Email: {office['email']}")
        print(f"   Address: {office['address']}")
    
    # Show zones
    zones = set(office['zone'] for office in cleaned_data if office['zone'])
    print(f"\nZones found: {sorted(zones)}")
    
    # Show zone-wise counts
    zone_counts = {}
    for office in cleaned_data:
        zone = office['zone']
        zone_counts[zone] = zone_counts.get(zone, 0) + 1
    
    print("\nZone-wise office counts:")
    for zone, count in sorted(zone_counts.items()):
        print(f"  {zone}: {count} offices")
