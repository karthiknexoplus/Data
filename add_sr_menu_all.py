import os
import re

# SR Office menu item
sr_menu_item = '''            <li class="nav-item">
                <a href="{{ url_for('sr_office') }}">
                    <i class="fas fa-landmark"></i>
                    <span>SR Office</span>
                </a>
            </li>'''

# Find all HTML template files
template_files = []
for root, dirs, files in os.walk('templates'):
    for file in files:
        if file.endswith('.html'):
            template_files.append(os.path.join(root, file))

print(f"Found {len(template_files)} template files")

for template_file in template_files:
    print(f"Processing {template_file}...")
    
    with open(template_file, 'r') as f:
        content = f.read()
    
    # Check if SR Office menu already exists
    if 'sr_office' in content:
        print(f"  - SR Office menu already exists in {template_file}")
        continue
    
    # Look for COZCENA menu item to add SR Office after it
    cozcena_pattern = r'(<li class="nav-item">\s*<a href="\{\{ url_for\(\'cozcena\'\) \}\}">\s*<i class="fas fa-building"></i>\s*<span>COZCENA</span>\s*</a>\s*</li>)'
    
    if re.search(cozcena_pattern, content, re.DOTALL):
        # Add SR Office after COZCENA
        new_content = re.sub(cozcena_pattern, r'\1\n' + sr_menu_item, content, flags=re.DOTALL)
        
        with open(template_file, 'w') as f:
            f.write(new_content)
        
        print(f"  - Added SR Office menu to {template_file}")
    else:
        # Look for any nav-item to add after
        nav_pattern = r'(<li class="nav-item">\s*<a href="\{\{ url_for\(\'[^\']+\'\) \}\}">\s*<i class="fas fa-[^"]+"></i>\s*<span>[^<]+</span>\s*</a>\s*</li>)'
        
        matches = list(re.finditer(nav_pattern, content, re.DOTALL))
        if matches:
            # Add after the last nav item
            last_match = matches[-1]
            new_content = content[:last_match.end()] + '\n' + sr_menu_item + content[last_match.end():]
            
            with open(template_file, 'w') as f:
                f.write(new_content)
            
            print(f"  - Added SR Office menu to {template_file} (after last nav item)")
        else:
            print(f"  - No suitable location found in {template_file}")

print("Done!")
