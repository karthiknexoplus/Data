import fitz  # PyMuPDF
import json
import re
from datetime import datetime

def extract_sub_reg_data():
    """Extract Sub Registrar office data from PDF"""
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
        
        # Process each line for office data
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for P.I.O entries
            if 'P.I.O' in line and 'Appellate' not in line:
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
                
                # Extract designation from the line
                parts = line.split('P.I.O')
                if len(parts) > 1:
                    office_data['designation'] = parts[1].strip()
                
                # Look for office name in previous lines
                for j in range(max(0, i-3), i):
                    prev_line = lines[j].strip()
                    if (prev_line and 
                        not prev_line.startswith('FORMAT') and 
                        not prev_line.startswith('Zone:') and
                        not prev_line.startswith('Department:') and
                        'P.I.O' not in prev_line and
                        'Appellate' not in prev_line and
                        len(prev_line) > 3):
                        office_data['office_name'] = prev_line
                        break
                
                # Extract contact details from current and next lines
                contact_lines = [line]
                for j in range(i+1, min(i+4, len(lines))):
                    if lines[j].strip():
                        contact_lines.append(lines[j].strip())
                
                contact_text = ' '.join(contact_lines)
                
                # Extract phone numbers
                phone_pattern = r'(\d{3})\s+(\d{8})'
                phone_matches = re.findall(phone_pattern, contact_text)
                if phone_matches:
                    office_data['std_code'] = phone_matches[0][0]
                    office_data['office_phone'] = phone_matches[0][1]
                
                # Extract email
                email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
                email_match = re.search(email_pattern, contact_text)
                if email_match:
                    office_data['email'] = email_match.group(1)
                
                # Extract address (look for lines with street/road names)
                for j in range(i+1, min(i+5, len(lines))):
                    addr_line = lines[j].strip()
                    if (addr_line and 
                        ('Road' in addr_line or 'Street' in addr_line or 'Salai' in addr_line or 
                         'Veedhi' in addr_line or 'Nagar' in addr_line or 'Chennai' in addr_line) and
                        not email_pattern in addr_line):
                        office_data['address'] = addr_line
                        break
                
                if office_data['office_name'] or office_data['designation']:
                    all_data.append(office_data)
            
            i += 1
    
    doc.close()
    return all_data

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
    data = extract_sub_reg_data()
    save_to_json(data)
    
    # Print sample data
    print("\nSample data:")
    for i, office in enumerate(data[:10]):
        print(f"\n{i+1}. {office['office_name']} ({office['zone']})")
        print(f"   Designation: {office['designation']}")
        print(f"   Phone: {office['std_code']} {office['office_phone']}")
        print(f"   Email: {office['email']}")
        print(f"   Address: {office['address']}")
    
    # Show zones
    zones = set(office['zone'] for office in data if office['zone'])
    print(f"\nZones found: {sorted(zones)}")
