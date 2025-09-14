import fitz
import json
import re
from datetime import datetime

def extract_clean_sr_data():
    """Extract clean Sub Registrar data with manual zone mapping"""
    doc = fitz.open('sub_reg.pdf')
    all_data = []
    
    # Manual zone mapping based on page analysis
    zone_mapping = {
        2: 'Chennai',
        12: 'Salem', 
        21: 'Coimbatore',
        31: 'Thanjavur',
        37: 'Trichy',
        46: 'Thirunelveli',
        78: 'Vellore',
        89: 'Madurai'
    }
    
    print("Extracting clean SR office data...")
    
    for page_num in range(1, len(doc) + 1):
        page = doc[page_num - 1]
        text = page.get_text()
        
        # Determine zone for this page
        zone = None
        for start_page, zone_name in zone_mapping.items():
            if page_num >= start_page:
                zone = zone_name
        
        if not zone:
            continue
            
        # Extract office data from this page
        offices = extract_offices_from_text(text, zone, page_num)
        all_data.extend(offices)
    
    doc.close()
    return all_data

def extract_offices_from_text(text, zone, page_num):
    """Extract office data from text"""
    offices = []
    lines = text.split('\n')
    
    # Look for office entries
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines and headers
        if not line or 'FORMAT' in line or 'Zone:' in line or 'Department:' in line:
            i += 1
            continue
        
        # Look for potential office names (location names)
        if (len(line) > 3 and 
            not line.isdigit() and 
            not line.startswith('044') and 
            not line.startswith('042') and
            not line.startswith('043') and
            not line.startswith('045') and
            '@' not in line and
            'P.I.O' not in line and
            'Appellate' not in line):
            
            office = {
                'zone': zone,
                'office_name': line,
                'designation_under_act': 'P.I.O',
                'designation': '',
                'std_code': '',
                'office_phone': '',
                'home_phone': '',
                'fax': '',
                'email': '',
                'address': '',
                'page': page_num
            }
            
            # Look for contact details in next few lines
            for j in range(i + 1, min(i + 8, len(lines))):
                next_line = lines[j].strip()
                
                # Extract phone numbers
                phone_match = re.search(r'(\d{3})\s+(\d{7,8})', next_line)
                if phone_match:
                    office['std_code'] = phone_match.group(1)
                    office['office_phone'] = phone_match.group(2)
                
                # Extract email
                email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', next_line)
                if email_match:
                    office['email'] = email_match.group(1)
                
                # Extract address (lines with location keywords)
                if (len(next_line) > 10 and 
                    any(keyword in next_line for keyword in ['Road', 'Street', 'Salai', 'Veedhi', 'Nagar', 'Office', 'Chennai', 'Madurai', 'Coimbatore', 'Salem', 'Thanjavur', 'Trichy', 'Vellore', 'Thirunelveli']) and
                    '@' not in next_line and
                    not next_line.isdigit()):
                    office['address'] = next_line
            
            # Only add if we have meaningful data
            if office['office_name'] and (office['office_phone'] or office['email'] or office['address']):
                offices.append(office)
        
        i += 1
    
    return offices

def clean_and_deduplicate(offices):
    """Clean data and remove duplicates"""
    cleaned = []
    seen = set()
    
    for office in offices:
        # Create a key for deduplication
        key = f"{office['office_name']}_{office['zone']}_{office['office_phone']}"
        if key in seen:
            continue
        seen.add(key)
        
        # Clean office name
        office['office_name'] = office['office_name'].strip()
        
        # Clean address
        if office['address']:
            office['address'] = office['address'].strip()
        
        # Only keep if we have meaningful data
        if office['office_name'] and len(office['office_name']) > 2:
            cleaned.append(office)
    
    return cleaned

def save_data(offices, filename='sub_reg_offices.json'):
    """Save data to JSON"""
    output_data = {
        'metadata': {
            'extracted_on': datetime.now().isoformat(),
            'total_offices': len(offices),
            'source': 'sub_reg.pdf',
            'zones': sorted(list(set(office['zone'] for office in offices)))
        },
        'data': offices
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Data saved to {filename}")
    print(f"Total offices extracted: {len(offices)}")

if __name__ == '__main__':
    print("Extracting clean Sub Registrar office data...")
    raw_data = extract_clean_sr_data()
    cleaned_data = clean_and_deduplicate(raw_data)
    save_data(cleaned_data)
    
    # Show zone distribution
    zones = {}
    for office in cleaned_data:
        zone = office['zone']
        zones[zone] = zones.get(zone, 0) + 1
    
    print("\nZone distribution:")
    for zone, count in sorted(zones.items()):
        print(f"  {zone}: {count} offices")
    
    # Show sample data
    print("\nSample offices:")
    for i, office in enumerate(cleaned_data[:10]):
        print(f"{i+1}. {office['office_name']} ({office['zone']})")
        if office['office_phone']:
            print(f"   Phone: {office['std_code']} {office['office_phone']}")
        if office['email']:
            print(f"   Email: {office['email']}")
        if office['address']:
            print(f"   Address: {office['address']}")
        print()
