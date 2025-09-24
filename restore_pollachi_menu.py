#!/usr/bin/env python3
"""
Restore Pollachi Wards menu to all navigation menus
"""

import os
import re

def restore_pollachi_menu(file_path):
    """Add Pollachi Wards menu item to a template file"""
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
    
    print(f"✓ Restored Pollachi Wards menu in {file_path}")
    return True

def main():
    """Restore Pollachi Wards menu to all template files"""
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
    
    print("Restoring Pollachi Wards menu to all templates...")
    print("=" * 50)
    
    restored_count = 0
    for template_file in template_files:
        file_path = os.path.join(templates_dir, template_file)
        if restore_pollachi_menu(file_path):
            restored_count += 1
    
    print("=" * 50)
    print(f"✓ Restored Pollachi Wards menu to {restored_count} template files")
    print("✓ Pollachi Wards menu is now visible again")

if __name__ == "__main__":
    main()
