import fitz
import json
import re
from datetime import datetime

def extract_all_zones_and_offices():
    """Extract all zones and offices with proper parsing"""
    doc = fitz.open('sub_reg.pdf')
    all_data = []
    current_zone = ""
    
    # All known zones from manual inspection
    all_zones = ['Chennai', 'Coimbatore', 'Madurai', 'Salem', 'Thanjavur', 'Thirunelveli', 'Trichy', 'Vellore']
    
    print("Extracting data from PDF...")
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        lines = text.split('\n')
        
        # Find zone information
        for line in lines:
            line_clean = line.strip()
            if 'Zone:' in line_clean:
                zone_text = line_clean.split('Zone:')[1].strip()
                # Clean up zone name
                for zone in all_zones:
                    if zone.upper() in zone_text.upper():
                        current_zone = zone
                        print(f"Page {page_num + 1}: Found zone - {current_zone}")
                        break
        
        # If no zone found, check if it's a continuation of previous zone
        if not current_zone:
            for zone in all_zones:
                if zone.upper() in text.upper() and 'FORMAT' not in text.upper():
                    current_zone = zone
                    break
        
        # Extract office data from this page
        page_offices = extract_offices_from_page(text, current_zone, page_num + 1)
        all_data.extend(page_offices)
    
    doc.close()
    return all_data

def extract_offices_from_page(text, zone, page_num):
    """Extract office data from a single page"""
    offices = []
    
    # Split text into potential office entries
    # Look for patterns that indicate office entries
    office_patterns = [
        r'P\.I\.O[^.]*?(?=P\.I\.O|Appellate Authority|$)',
        r'Appellate Authority[^.]*?(?=P\.I\.O|Appellate Authority|$)'
    ]
    
    for pattern in office_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            office = parse_office_entry(match, zone, page_num)
            if office and (office['office_name'] or office['designation'] or office['office_phone']):
                offices.append(office)
    
    return offices

def parse_office_entry(text, zone, page_num):
    """Parse a single office entry"""
    office = {
        'zone': zone,
        'office_name': '',
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
    
    # Extract designation
    designation_match = re.search(r'P\.I\.O\s+(.+?)(?:\s+\d{3}|\s+[A-Z]|$)', text)
    if designation_match:
        office['designation'] = designation_match.group(1).strip()
    
    # Extract phone numbers
    phone_matches = re.findall(r'(\d{3})\s+(\d{8})', text)
    if phone_matches:
        office['std_code'] = phone_matches[0][0]
        office['office_phone'] = phone_matches[0][1]
    
    # Extract email
    email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
    if email_match:
        office['email'] = email_match.group(1)
    
    # Extract office name - look for location names
    name_patterns = [
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+P\.I\.O',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Sub\s+Registrar',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+District\s+Registrar',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Joint\s+Sub\s+Registrar'
    ]
    
    for pattern in name_patterns:
        name_match = re.search(pattern, text)
        if name_match:
            office['office_name'] = name_match.group(1).strip()
            break
    
    # If no office name found, try to extract from context
    if not office['office_name']:
        # Look for common office name patterns
        context_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Office|Registrar)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Sub|Joint)'
        ]
        for pattern in context_patterns:
            context_match = re.search(pattern, text)
            if context_match:
                office['office_name'] = context_match.group(1).strip()
                break
    
    # Extract address
    address_keywords = ['Road', 'Street', 'Salai', 'Veedhi', 'Nagar', 'Chennai', 'Madurai', 'Coimbatore', 'Salem', 'Thanjavur', 'Trichy', 'Vellore', 'Thirunelveli']
    address_lines = re.findall(r'([^.\n]*(?:' + '|'.join(address_keywords) + r')[^.\n]*)', text)
    if address_lines:
        # Take the longest address line
        office['address'] = max(address_lines, key=len).strip()
    
    return office

def clean_office_data(offices):
    """Clean and standardize office data"""
    cleaned = []
    
    for office in offices:
        # Clean office name
        if office['office_name']:
            office['office_name'] = re.sub(r'\s+', ' ', office['office_name']).strip()
            # Remove common junk words
            junk_words = ['Appellate', 'Authority', 'Joint', 'Sub', 'Registrar', 'Office']
            for word in junk_words:
                if office['office_name'] == word:
                    office['office_name'] = ''
                    break
        
        # Clean designation
        if office['designation']:
            office['designation'] = re.sub(r'\s+', ' ', office['designation']).strip()
        
        # Clean address
        if office['address']:
            office['address'] = re.sub(r'\s+', ' ', office['address']).strip()
            # Remove email addresses from address
            office['address'] = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', office['address']).strip()
        
        # Only keep meaningful entries
        if (office['office_name'] or office['designation'] or office['office_phone'] or office['email']):
            cleaned.append(office)
    
    return cleaned

def save_clean_data(offices, filename='sub_reg_offices.json'):
    """Save cleaned data to JSON"""
    output_data = {
        'metadata': {
            'extracted_on': datetime.now().isoformat(),
            'total_offices': len(offices),
            'source': 'sub_reg.pdf',
            'zones': list(set(office['zone'] for office in offices if office['zone']))
        },
        'data': offices
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Data saved to {filename}")
    print(f"Total offices extracted: {len(offices)}")

if __name__ == '__main__':
    print("Extracting Sub Registrar office data with proper zone detection...")
    raw_data = extract_all_zones_and_offices()
    cleaned_data = clean_office_data(raw_data)
    save_clean_data(cleaned_data)
    
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
    for i, office in enumerate(cleaned_data[:5]):
        print(f"{i+1}. {office['office_name']} ({office['zone']})")
        print(f"   Designation: {office['designation']}")
        print(f"   Phone: {office['std_code']} {office['office_phone']}")
        print(f"   Email: {office['email']}")
        print(f"   Address: {office['address']}")
        print()
