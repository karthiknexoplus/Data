#!/usr/bin/env python3
"""
Update all navigation menus to include Pollachi Wards link
"""

import os
import re

def update_navigation_menu(file_path):
    """Update navigation menu in a template file"""
    if not os.path.exists(file_path):
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if Pollachi Wards link already exists
    if 'pollachi_wards' in content:
        print(f"✓ {file_path} already has Pollachi Wards link")
        return True
    
    # Find the navigation menu section
    nav_pattern = r'(<nav class="main-nav">.*?</nav>)'
    nav_match = re.search(nav_pattern, content, re.DOTALL)
    
    if not nav_match:
        print(f"✗ No navigation menu found in {file_path}")
        return False
    
    nav_content = nav_match.group(1)
    
    # Add Pollachi Wards link before Eway Data
    pollachi_link = '''            <li class="nav-item">
                <a href="{{ url_for('pollachi_wards') }}">
                    <i class="fas fa-map-marked-alt"></i>
                    <span>Pollachi Wards</span>
                </a>
            </li>
'''
    
    # Insert before Eway Data link
    if 'Eway Data' in nav_content:
        updated_nav = nav_content.replace(
            '            <li class="nav-item">\n                <a href="#" onclick="alert(\'Eway Data coming soon!\')">\n                    <i class="fas fa-truck"></i>\n                    <span>Eway Data</span>\n                </a>\n            </li>',
            pollachi_link + '            <li class="nav-item">\n                <a href="#" onclick="alert(\'Eway Data coming soon!\')">\n                    <i class="fas fa-truck"></i>\n                    <span>Eway Data</span>\n                </a>\n            </li>'
        )
    else:
        # If no Eway Data link, add at the end before closing </ul>
        updated_nav = nav_content.replace('        </ul>', f'            {pollachi_link}        </ul>')
    
    # Update the content
    updated_content = content.replace(nav_content, updated_nav)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"✓ Updated {file_path}")
    return True

def main():
    """Update all template files"""
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
    
    print("Updating navigation menus to include Pollachi Wards...")
    print("=" * 50)
    
    updated_count = 0
    for template_file in template_files:
        file_path = os.path.join(templates_dir, template_file)
        if update_navigation_menu(file_path):
            updated_count += 1
    
    print("=" * 50)
    print(f"✓ Updated {updated_count} template files")
    print("✓ Pollachi Wards menu added to all navigation menus")

if __name__ == "__main__":
    main()
