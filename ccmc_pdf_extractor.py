import PyPDF2
import json
import csv
import re
from datetime import datetime

def extract_ccmc_data():
    """Extract CCMC contractor data from PDF"""
    print("🔍 Extracting CCMC contractor data from PDF...")
    
    contractors = []
    
    try:
        with open('ccmc.pdf', 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            print(f"📄 Processing {len(pdf_reader.pages)} pages...")
            
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                lines = text.split('\n')
                
                # Process each line to extract contractor data
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Look for lines that start with a number (contractor entries)
                    if re.match(r'^\d+\s+', line):
                        contractor_data = parse_contractor_line(line)
                        if contractor_data:
                            contractors.append(contractor_data)
            
            print(f"✅ Extracted {len(contractors)} contractors")
            return contractors
            
    except Exception as e:
        print(f"❌ Error extracting PDF: {str(e)}")
        return []

def parse_contractor_line(line):
    """Parse a single contractor line"""
    try:
        # Split by multiple spaces to separate fields
        parts = re.split(r'\s{2,}', line)
        
        if len(parts) < 3:
            return None
        
        # Extract serial number
        serial_match = re.match(r'^(\d+)', parts[0])
        if not serial_match:
            return None
        
        serial_no = serial_match.group(1)
        
        # Extract name (usually the second part)
        name = parts[1] if len(parts) > 1 else ""
        
        # Extract class (usually contains 'I', 'II', 'III', etc.)
        class_info = ""
        for part in parts:
            if re.search(r'[IVX]+', part):
                class_info = part
                break
        
        # Extract address and phone (remaining parts)
        address_parts = []
        phone_parts = []
        
        for part in parts[2:]:
            if re.search(r'\d{10,}', part):  # Phone number pattern
                phone_parts.append(part)
            else:
                address_parts.append(part)
        
        address = ' '.join(address_parts)
        phone = ' '.join(phone_parts)
        
        return {
            'serial_no': serial_no,
            'name': name,
            'class': class_info,
            'address': address,
            'phone': phone,
            'source': 'CCMC PDF',
            'extracted_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error parsing line: {line} - {e}")
        return None

def save_to_json(data, filename="ccmc_contractors.json"):
    """Save data to JSON file"""
    try:
        output_data = {
            "extracted_at": datetime.now().isoformat(),
            "source": "Coimbatore Corporation Contractor List",
            "total_records": len(data),
            "data": {
                "contractors": data
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Data saved to {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving to JSON: {str(e)}")
        return False

def save_to_csv(data, filename="ccmc_contractors.csv"):
    """Save data to CSV file"""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['S.No', 'Name', 'Class', 'Address', 'Phone', 'Source', 'Extracted At'])
            
            for contractor in data:
                writer.writerow([
                    contractor.get('serial_no', ''),
                    contractor.get('name', ''),
                    contractor.get('class', ''),
                    contractor.get('address', ''),
                    contractor.get('phone', ''),
                    contractor.get('source', ''),
                    contractor.get('extracted_at', '')
                ])
        
        print(f"✅ Data saved to {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving to CSV: {str(e)}")
        return False

def main():
    contractors = extract_ccmc_data()
    
    if contractors:
        save_to_json(contractors)
        save_to_csv(contractors)
        
        print(f"\n�� Successfully extracted {len(contractors)} CCMC contractors!")
        print("📁 Files created:")
        print("   - ccmc_contractors.json")
        print("   - ccmc_contractors.csv")
    else:
        print("❌ No contractors found")

if __name__ == "__main__":
    main()
