import PyPDF2
import json
import csv
import re
from datetime import datetime

def extract_ccmc_data():
    """Extract CCMC contractor data from PDF with improved parsing"""
    print("🔍 Extracting CCMC contractor data from PDF...")
    
    contractors = []
    
    try:
        with open('ccmc.pdf', 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            print(f"📄 Processing {len(pdf_reader.pages)} pages...")
            
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                
                # Split text into lines and process
                lines = text.split('\n')
                
                # Look for contractor entries
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    
                    # Check if line starts with a number (contractor entry)
                    if re.match(r'^\d+\s+', line):
                        contractor_data = parse_contractor_entry(lines, i)
                        if contractor_data:
                            contractors.append(contractor_data)
                            # Skip lines that were processed
                            i += contractor_data.get('lines_processed', 1)
                        else:
                            i += 1
                    else:
                        i += 1
            
            print(f"✅ Extracted {len(contractors)} contractors")
            return contractors
            
    except Exception as e:
        print(f"❌ Error extracting PDF: {str(e)}")
        return []

def parse_contractor_entry(lines, start_idx):
    """Parse contractor entry starting from given line index"""
    try:
        # Get the main line
        main_line = lines[start_idx].strip()
        
        # Extract serial number
        serial_match = re.match(r'^(\d+)', main_line)
        if not serial_match:
            return None
        
        serial_no = serial_match.group(1)
        
        # Remove serial number from the line
        remaining_text = main_line[len(serial_no):].strip()
        
        # Look for class indicators (I, II, III, etc.)
        class_match = re.search(r'\b([IVX]+)\b', remaining_text)
        class_info = class_match.group(1) if class_match else ""
        
        # Extract name (text before class)
        if class_match:
            name = remaining_text[:class_match.start()].strip()
        else:
            name = remaining_text
        
        # Look for phone numbers in the text
        phone_pattern = r'\b\d{10,}\b'
        phone_matches = re.findall(phone_pattern, remaining_text)
        phone = ', '.join(phone_matches) if phone_matches else ""
        
        # Extract address (remove name, class, and phone from remaining text)
        address = remaining_text
        if class_match:
            address = address[class_match.end():].strip()
        
        # Remove phone numbers from address
        for phone_num in phone_matches:
            address = address.replace(phone_num, '').strip()
        
        # Clean up address
        address = re.sub(r'\s+', ' ', address).strip()
        address = address.rstrip(',').strip()
        
        return {
            'serial_no': serial_no,
            'name': name,
            'class': class_info,
            'address': address,
            'phone': phone,
            'source': 'CCMC PDF',
            'extracted_at': datetime.now().isoformat(),
            'lines_processed': 1
        }
        
    except Exception as e:
        print(f"Error parsing contractor entry: {e}")
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
        
        print(f"\n🎉 Successfully extracted {len(contractors)} CCMC contractors!")
        print("📁 Files created:")
        print("   - ccmc_contractors.json")
        print("   - ccmc_contractors.csv")
        
        # Show first few entries
        print("\n📋 Sample entries:")
        for i, contractor in enumerate(contractors[:5]):
            print(f"{i+1}. {contractor['name']} (Class: {contractor['class']})")
    else:
        print("❌ No contractors found")

if __name__ == "__main__":
    main()
