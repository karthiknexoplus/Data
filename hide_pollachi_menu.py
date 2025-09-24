#!/usr/bin/env python3
"""
Temporarily hide Pollachi Wards menu from all navigation menus
"""

import os
import re

def hide_pollachi_menu(file_path):
    """Remove Pollachi Wards menu item from a template file"""
    if not os.path.exists(file_path):
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if Pollachi Wards link exists
    if 'pollachi_wards' not in content:
        print(f"✓ {file_path} - No Pollachi Wards link found")
        return True
    
    # Remove the Pollachi Wards menu item
    pollachi_pattern = r'            <li class="nav-item">\n                <a href="{{ url_for\(\'pollachi_wards\'\) }}">\n                    <i class="fas fa-map-marked-alt"></i>\n                    <span>Pollachi Wards</span>\n                </a>\n            </li>\n'
    
    # Remove the menu item
    updated_content = re.sub(pollachi_pattern, '', content)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"✓ Hidden Pollachi Wards menu in {file_path}")
    return True

def main():
    """Hide Pollachi Wards menu from all template files"""
    templates_dir = 'templates'
    template_files = [
        'dashboard.html',
        'bai_members.html',
        'colleges.html',
        'edu_list_tn.html',
        'iia_cbe.html',
        'cozcena.html',
        'sr_office.html',
        'tcea_members.html',
        'credai_members.html',
        'rera_agents.html',
        'ccmc_contractors.html',
        'cbe_wards.html',
        'in_data.html'
    ]
    
    print("Hiding Pollachi Wards menu from all templates...")
    print("=" * 50)
    
    hidden_count = 0
    for template_file in template_files:
        file_path = os.path.join(templates_dir, template_file)
        if hide_pollachi_menu(file_path):
            hidden_count += 1
    
    print("=" * 50)
    print(f"✓ Hidden Pollachi Wards menu from {hidden_count} template files")
    print("✓ Pollachi Wards menu is now temporarily hidden")

if __name__ == "__main__":
    main()
