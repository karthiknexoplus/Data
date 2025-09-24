#!/usr/bin/env python3
"""
Pollachi Ward Map Extractor
Extracts ward information from Pollachi.pdf including ward numbers, boundaries, and geographical data
"""

import fitz  # PyMuPDF
import PyPDF2
import json
import csv
import re
from collections import defaultdict
import os

class PollachiWardExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.ward_data = []
        self.text_content = ""
        self.images = []
        
    def extract_text_content(self):
        """Extract all text content from the PDF"""
        print("Extracting text content from PDF...")
        
        # Using PyMuPDF for better text extraction
        doc = fitz.open(self.pdf_path)
        all_text = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            all_text.append(text)
            print(f"Page {page_num + 1} text length: {len(text)}")
            
        self.text_content = "\n".join(all_text)
        doc.close()
        
        # Also try PyPDF2 for comparison
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pyPDF2_text = ""
                for page in pdf_reader.pages:
                    pyPDF2_text += page.extract_text()
                print(f"PyPDF2 extracted text length: {len(pyPDF2_text)}")
        except Exception as e:
            print(f"PyPDF2 extraction failed: {e}")
    
    def extract_images(self):
        """Extract images from the PDF"""
        print("Extracting images from PDF...")
        
        doc = fitz.open(self.pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                if pix.n - pix.alpha < 4:  # GRAY or RGB
                    img_data = pix.tobytes("png")
                    self.images.append({
                        'page': page_num + 1,
                        'index': img_index,
                        'data': img_data,
                        'width': pix.width,
                        'height': pix.height
                    })
                pix = None
        doc.close()
        print(f"Extracted {len(self.images)} images")
    
    def extract_ward_numbers(self):
        """Extract ward numbers from the text content"""
        print("Extracting ward numbers...")
        
        # Common patterns for ward numbers
        ward_patterns = [
            r'ward\s*(\d+)',  # "ward 1", "ward1"
            r'ward\s*no\.?\s*(\d+)',  # "ward no. 1", "ward no 1"
            r'(\d+)\s*ward',  # "1 ward"
            r'ward\s*number\s*(\d+)',  # "ward number 1"
        ]
        
        ward_numbers = set()
        for pattern in ward_patterns:
            matches = re.findall(pattern, self.text_content, re.IGNORECASE)
            ward_numbers.update([int(match) for match in matches])
        
        # Also look for standalone numbers that might be ward numbers
        number_pattern = r'\b(\d{1,2})\b'
        numbers = re.findall(number_pattern, self.text_content)
        
        # Filter numbers that are likely ward numbers (1-50 range)
        potential_wards = [int(num) for num in numbers if 1 <= int(num) <= 50]
        ward_numbers.update(potential_wards)
        
        print(f"Found ward numbers: {sorted(ward_numbers)}")
        return sorted(ward_numbers)
    
    def extract_geographical_info(self):
        """Extract geographical information like coordinates, boundaries, etc."""
        print("Extracting geographical information...")
        
        geo_info = {
            'coordinates': [],
            'boundaries': [],
            'landmarks': [],
            'roads': [],
            'areas': []
        }
        
        # Look for coordinate patterns
        coord_patterns = [
            r'(\d+\.\d+)\s*,\s*(\d+\.\d+)',  # "12.345, 78.901"
            r'lat[itude]*\s*:?\s*(\d+\.\d+)',  # "lat: 12.345"
            r'lon[gitude]*\s*:?\s*(\d+\.\d+)',  # "lon: 78.901"
        ]
        
        for pattern in coord_patterns:
            matches = re.findall(pattern, self.text_content, re.IGNORECASE)
            geo_info['coordinates'].extend(matches)
        
        # Look for boundary information
        boundary_keywords = ['boundary', 'border', 'limit', 'edge', 'perimeter']
        for keyword in boundary_keywords:
            pattern = rf'{keyword}[:\s]*([^\n]+)'
            matches = re.findall(pattern, self.text_content, re.IGNORECASE)
            geo_info['boundaries'].extend(matches)
        
        # Look for landmark information
        landmark_keywords = ['temple', 'school', 'hospital', 'market', 'station', 'church', 'mosque']
        for keyword in landmark_keywords:
            pattern = rf'{keyword}[:\s]*([^\n]+)'
            matches = re.findall(pattern, self.text_content, re.IGNORECASE)
            geo_info['landmarks'].extend(matches)
        
        # Look for road information
        road_patterns = [
            r'([A-Za-z\s]+)\s*road',
            r'([A-Za-z\s]+)\s*street',
            r'([A-Za-z\s]+)\s*avenue',
        ]
        
        for pattern in road_patterns:
            matches = re.findall(pattern, self.text_content, re.IGNORECASE)
            geo_info['roads'].extend(matches)
        
        return geo_info
    
    def extract_administrative_info(self):
        """Extract administrative information"""
        print("Extracting administrative information...")
        
        admin_info = {
            'municipality': '',
            'district': '',
            'state': '',
            'pincode': '',
            'population': '',
            'area': ''
        }
        
        # Look for municipality/district information
        if 'pollachi' in self.text_content.lower():
            admin_info['municipality'] = 'Pollachi'
        
        # Look for district information
        district_pattern = r'district[:\s]*([^\n]+)'
        district_match = re.search(district_pattern, self.text_content, re.IGNORECASE)
        if district_match:
            admin_info['district'] = district_match.group(1).strip()
        
        # Look for state information
        if 'tamil nadu' in self.text_content.lower() or 'tamilnadu' in self.text_content.lower():
            admin_info['state'] = 'Tamil Nadu'
        
        # Look for pincode
        pincode_pattern = r'pincode[:\s]*(\d{6})'
        pincode_match = re.search(pincode_pattern, self.text_content, re.IGNORECASE)
        if pincode_match:
            admin_info['pincode'] = pincode_match.group(1)
        
        # Look for population
        pop_pattern = r'population[:\s]*([\d,]+)'
        pop_match = re.search(pop_pattern, self.text_content, re.IGNORECASE)
        if pop_match:
            admin_info['population'] = pop_match.group(1)
        
        # Look for area
        area_pattern = r'area[:\s]*([\d,]+\.?\d*)\s*(sq\.?\s*km|hectares?|acres?)'
        area_match = re.search(area_pattern, self.text_content, re.IGNORECASE)
        if area_match:
            admin_info['area'] = f"{area_match.group(1)} {area_match.group(2)}"
        
        return admin_info
    
    def analyze_ward_structure(self):
        """Analyze the ward structure and create comprehensive data"""
        print("Analyzing ward structure...")
        
        ward_numbers = self.extract_ward_numbers()
        geo_info = self.extract_geographical_info()
        admin_info = self.extract_administrative_info()
        
        # Create ward data structure
        for ward_num in ward_numbers:
            ward_data = {
                'ward_number': ward_num,
                'ward_name': f'Ward {ward_num}',
                'boundaries': [],
                'landmarks': [],
                'roads': [],
                'coordinates': [],
                'population': '',
                'area': '',
                'representative': '',
                'contact_info': ''
            }
            
            # Try to find specific information for each ward
            ward_specific_pattern = rf'ward\s*{ward_num}[:\s]*([^\n]+)'
            ward_specific_match = re.search(ward_specific_pattern, self.text_content, re.IGNORECASE)
            if ward_specific_match:
                ward_data['description'] = ward_specific_match.group(1).strip()
            
            self.ward_data.append(ward_data)
        
        # Add general geographical information to all wards
        for ward in self.ward_data:
            ward['general_landmarks'] = geo_info['landmarks']
            ward['general_roads'] = geo_info['roads']
            ward['general_coordinates'] = geo_info['coordinates']
        
        return {
            'wards': self.ward_data,
            'administrative_info': admin_info,
            'geographical_info': geo_info,
            'total_wards': len(ward_numbers),
            'ward_numbers': ward_numbers
        }
    
    def save_to_csv(self, output_file='pollachi_wards.csv'):
        """Save ward data to CSV file"""
        print(f"Saving ward data to {output_file}...")
        
        if not self.ward_data:
            print("No ward data to save")
            return
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['ward_number', 'ward_name', 'description', 'boundaries', 
                         'landmarks', 'roads', 'coordinates', 'population', 'area']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for ward in self.ward_data:
                # Convert lists to strings for CSV
                row = ward.copy()
                for field in ['boundaries', 'landmarks', 'roads', 'coordinates']:
                    if isinstance(row[field], list):
                        row[field] = '; '.join(row[field])
                writer.writerow(row)
        
        print(f"Saved {len(self.ward_data)} wards to {output_file}")
    
    def save_to_json(self, output_file='pollachi_wards.json'):
        """Save complete data to JSON file"""
        print(f"Saving complete data to {output_file}...")
        
        complete_data = self.analyze_ward_structure()
        
        with open(output_file, 'w', encoding='utf-8') as jsonfile:
            json.dump(complete_data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"Saved complete data to {output_file}")
    
    def print_summary(self):
        """Print a summary of extracted information"""
        print("\n" + "="*50)
        print("POLLACHI WARD MAP EXTRACTION SUMMARY")
        print("="*50)
        
        print(f"\nPDF File: {self.pdf_path}")
        print(f"Text Content Length: {len(self.text_content)} characters")
        print(f"Images Extracted: {len(self.images)}")
        
        if self.ward_data:
            print(f"\nTotal Wards Found: {len(self.ward_data)}")
            print("Ward Numbers:", [ward['ward_number'] for ward in self.ward_data])
            
            print("\nSample Ward Data:")
            for i, ward in enumerate(self.ward_data[:3]):  # Show first 3 wards
                print(f"\nWard {ward['ward_number']}:")
                print(f"  Name: {ward['ward_name']}")
                if ward.get('description'):
                    print(f"  Description: {ward['description']}")
                if ward.get('boundaries'):
                    print(f"  Boundaries: {ward['boundaries']}")
        
        print("\nExtraction completed successfully!")

def main():
    pdf_path = 'Pollachi.pdf'
    
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found!")
        return
    
    print("Starting Pollachi Ward Map Extraction...")
    extractor = PollachiWardExtractor(pdf_path)
    
    # Extract all information
    extractor.extract_text_content()
    extractor.extract_images()
    
    # Analyze and save data
    extractor.analyze_ward_structure()
    extractor.save_to_csv()
    extractor.save_to_json()
    extractor.print_summary()

if __name__ == "__main__":
    main()
