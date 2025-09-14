import zipfile
import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime

def extract_excel_data():
    """Extract clean data from Excel file"""
    all_data = []
    
    # Zone mapping based on sheet numbers (you can adjust this)
    zone_mapping = {
        1: 'Chennai',
        2: 'Chennai', 
        3: 'Chennai',
        4: 'Chennai',
        5: 'Chennai',
        6: 'Chennai',
        7: 'Chennai',
        8: 'Chennai',
        9: 'Chennai',
        10: 'Chennai',
        11: 'Chennai',
        12: 'Salem',
        13: 'Salem',
        14: 'Salem',
        15: 'Salem',
        16: 'Salem',
        17: 'Salem',
        18: 'Salem',
        19: 'Salem',
        20: 'Salem',
        21: 'Coimbatore',
        22: 'Coimbatore',
        23: 'Coimbatore',
        24: 'Coimbatore',
        25: 'Coimbatore',
        26: 'Coimbatore',
        27: 'Coimbatore',
        28: 'Coimbatore',
        29: 'Coimbatore',
        30: 'Coimbatore',
        31: 'Thanjavur',
        32: 'Thanjavur',
        33: 'Thanjavur',
        34: 'Thanjavur',
        35: 'Thanjavur',
        36: 'Thanjavur',
        37: 'Trichy',
        38: 'Trichy',
        39: 'Trichy',
        40: 'Trichy',
        41: 'Trichy',
        42: 'Trichy',
        43: 'Trichy',
        44: 'Trichy',
        45: 'Trichy',
        46: 'Thirunelveli',
        47: 'Thirunelveli',
        48: 'Thirunelveli',
        49: 'Thirunelveli',
        50: 'Thirunelveli',
        51: 'Thirunelveli',
        52: 'Thirunelveli',
        53: 'Thirunelveli',
        54: 'Thirunelveli',
        55: 'Thirunelveli',
        56: 'Thirunelveli',
        57: 'Thirunelveli',
        58: 'Thirunelveli',
        59: 'Thirunelveli',
        60: 'Thirunelveli',
        61: 'Thirunelveli',
        62: 'Thirunelveli',
        63: 'Thirunelveli',
        64: 'Thirunelveli',
        65: 'Thirunelveli',
        66: 'Thirunelveli',
        67: 'Thirunelveli',
        68: 'Thirunelveli',
        69: 'Thirunelveli',
        70: 'Thirunelveli',
        71: 'Thirunelveli',
        72: 'Thirunelveli',
        73: 'Thirunelveli',
        74: 'Thirunelveli',
        75: 'Thirunelveli',
        76: 'Thirunelveli',
        77: 'Thirunelveli',
        78: 'Vellore',
        79: 'Vellore',
        80: 'Vellore',
        81: 'Vellore',
        82: 'Vellore',
        83: 'Vellore',
        84: 'Vellore',
        85: 'Vellore',
        86: 'Vellore',
        87: 'Vellore',
        88: 'Vellore',
        89: 'Madurai',
        90: 'Madurai',
        91: 'Madurai',
        92: 'Madurai',
        93: 'Madurai',
        94: 'Madurai',
        95: 'Madurai',
        96: 'Madurai',
        97: 'Madurai',
        98: 'Madurai'
    }
    
    print("Extracting data from Excel file...")
    
    with zipfile.ZipFile('sub_reg.xlsx', 'r') as zip_file:
        # Read shared strings
        shared_strings = []
        if 'xl/sharedStrings.xml' in zip_file.namelist():
            with zip_file.open('xl/sharedStrings.xml') as f:
                shared_strings_xml = f.read()
                root = ET.fromstring(shared_strings_xml)
                
                for si in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                    text_elements = si.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
                    text = ''.join([t.text or '' for t in text_elements])
                    shared_strings.append(text)
        
        print(f"Found {len(shared_strings)} shared strings")
        
        # Process each sheet
        for sheet_num in range(1, 99):  # 98 sheets
            sheet_name = f'xl/worksheets/sheet{sheet_num}.xml'
            if sheet_name in zip_file.namelist():
                zone = zone_mapping.get(sheet_num, 'Unknown')
                print(f"Processing sheet {sheet_num} ({zone})...")
                
                with zip_file.open(sheet_name) as f:
                    worksheet_xml = f.read()
                    root = ET.fromstring(worksheet_xml)
                    
                    # Extract data from this sheet
                    sheet_data = extract_sheet_data(root, shared_strings, zone, sheet_num)
                    all_data.extend(sheet_data)
    
    return all_data

def extract_sheet_data(root, shared_strings, zone, sheet_num):
    """Extract data from a single sheet"""
    offices = []
    
    # Find all cells
    cells = root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c')
    
    # Group cells by row
    rows = {}
    for cell in cells:
        cell_ref = cell.get('r', '')
        if cell_ref:
            # Extract row number
            row_num = int(re.sub(r'[A-Z]', '', cell_ref))
            
            if row_num not in rows:
                rows[row_num] = {}
            
            # Get cell value
            cell_type = cell.get('t', '')
            value_elem = cell.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
            value = value_elem.text if value_elem is not None else ''
            
            # Convert shared string reference
            if cell_type == 's' and value.isdigit():
                try:
                    value = shared_strings[int(value)]
                except (ValueError, IndexError):
                    pass
            
            # Extract column letter
            col_letter = re.sub(r'\d', '', cell_ref)
            rows[row_num][col_letter] = value
    
    # Process rows to find office data
    for row_num in sorted(rows.keys()):
        row_data = rows[row_num]
        
        # Skip header rows
        if row_num <= 3:
            continue
        
        # Look for office data
        office = extract_office_from_row(row_data, zone, sheet_num, row_num)
        if office:
            offices.append(office)
    
    return offices

def extract_office_from_row(row_data, zone, sheet_num, row_num):
    """Extract office data from a row"""
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
        'sheet': sheet_num,
        'row': row_num
    }
    
    # Map columns to data fields (adjust based on actual structure)
    # A: Office Name, B: Designation, C: STD Code, D: Phone, E: Email, F: Address
    office['office_name'] = row_data.get('A', '').strip()
    office['designation'] = row_data.get('B', '').strip()
    office['std_code'] = row_data.get('C', '').strip()
    office['office_phone'] = row_data.get('D', '').strip()
    office['email'] = row_data.get('E', '').strip()
    office['address'] = row_data.get('F', '').strip()
    
    # Only return if we have meaningful data
    if (office['office_name'] or office['designation'] or 
        office['office_phone'] or office['email']):
        return office
    
    return None

def clean_data(offices):
    """Clean and standardize the data"""
    cleaned = []
    seen = set()
    
    for office in offices:
        # Create a key for deduplication
        key = f"{office['office_name']}_{office['zone']}_{office['office_phone']}"
        if key in seen:
            continue
        seen.add(key)
        
        # Clean office name
        if office['office_name']:
            office['office_name'] = office['office_name'].strip()
            # Remove common junk
            if office['office_name'] in ['FORMAT – I', 'Name of the office/ Unit', 'Designation', 'STD code', 'Phone No.', 'Fax', 'Email', 'Address']:
                continue
        
        # Clean designation
        if office['designation']:
            office['designation'] = office['designation'].strip()
        
        # Clean phone
        if office['office_phone']:
            office['office_phone'] = str(office['office_phone']).strip()
        
        # Clean email
        if office['email']:
            office['email'] = office['email'].strip()
        
        # Clean address
        if office['address']:
            office['address'] = office['address'].strip()
        
        # Only keep meaningful entries
        if (office['office_name'] and len(office['office_name']) > 2) or office['office_phone'] or office['email']:
            cleaned.append(office)
    
    return cleaned

def save_data(offices, filename='sub_reg_offices.json'):
    """Save data to JSON"""
    output_data = {
        'metadata': {
            'extracted_on': datetime.now().isoformat(),
            'total_offices': len(offices),
            'source': 'sub_reg.xlsx',
            'zones': sorted(list(set(office['zone'] for office in offices)))
        },
        'data': offices
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Data saved to {filename}")
    print(f"Total offices extracted: {len(offices)}")

if __name__ == '__main__':
    print("Extracting clean data from Excel file...")
    raw_data = extract_excel_data()
    cleaned_data = clean_data(raw_data)
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
        if office['designation']:
            print(f"   Designation: {office['designation']}")
        if office['office_phone']:
            print(f"   Phone: {office['std_code']} {office['office_phone']}")
        if office['email']:
            print(f"   Email: {office['email']}")
        if office['address']:
            print(f"   Address: {office['address']}")
        print()
