import re
import os

def fix_all_menus_and_members():
    """Fix all menu templates to include IIA Cbe and fix Members section"""
    
    # List of templates to update
    templates = [
        'templates/colleges.html',
        'templates/edu_list_tn.html', 
        'templates/in_data.html',
        'templates/iia_list.html'
    ]
    
    # The complete navigation structure
    complete_nav = '''            <li class="nav-item">
                <a href="{{ url_for('in_data') }}" style="text-decoration: none; color: inherit; display: flex; align-items: center;">
                    <i class="fas fa-database"></i>
                    <span>IN Data</span>
                </a>
            </li>
            <li class="nav-item">
                <i class="fas fa-chart-bar"></i>
                <span>BAI Data</span>
            </li>
            <li class="nav-item">
                <a href="{{ url_for('colleges') }}" style="text-decoration: none; color: inherit; display: flex; align-items: center;">
                    <i class="fas fa-graduation-cap"></i>
                    <span>Colleges</span>
                </a>
            </li>
            <li class="nav-item">
                <a href="{{ url_for('edu_list_tn') }}" style="text-decoration: none; color: inherit; display: flex; align-items: center;">
                    <i class="fas fa-university"></i>
                    <span>EDU list TN</span>
                </a>
            </li>
            <li class="nav-item">
                <a href="{{ url_for('iia_cbe') }}" style="text-decoration: none; color: inherit; display: flex; align-items: center;">
                    <i class="fas fa-industry"></i>
                    <span>IIA Cbe</span>
                </a>
            </li>
            <li class="nav-item">
                <i class="fas fa-truck"></i>
                <span>Eway Data</span>
            </li>'''
    
    for template_file in templates:
        if os.path.exists(template_file):
            print(f"Updating {template_file}...")
            
            # Read the template
            with open(template_file, 'r') as f:
                content = f.read()
            
            # Find and replace the nav-list section
            nav_pattern = r'<ul class="nav-list">.*?</ul>'
            nav_match = re.search(nav_pattern, content, re.DOTALL)
            
            if nav_match:
                # Determine which item should be active
                active_class = ""
                if "colleges" in template_file:
                    active_class = 'class="nav-item active"'
                elif "edu_list_tn" in template_file:
                    active_class = 'class="nav-item active"'
                elif "in_data" in template_file:
                    active_class = 'class="nav-item active"'
                elif "iia_list" in template_file:
                    active_class = 'class="nav-item active"'
                
                # Create the new nav with proper active class
                new_nav = complete_nav
                if active_class:
                    # Replace the appropriate nav-item with active class
                    if "colleges" in template_file:
                        new_nav = new_nav.replace('href="{{ url_for(\'colleges\') }}"', f'href="{{ url_for(\'colleges\') }}" {active_class}')
                    elif "edu_list_tn" in template_file:
                        new_nav = new_nav.replace('href="{{ url_for(\'edu_list_tn\') }}"', f'href="{{ url_for(\'edu_list_tn\') }}" {active_class}')
                    elif "in_data" in template_file:
                        new_nav = new_nav.replace('href="{{ url_for(\'in_data\') }}"', f'href="{{ url_for(\'in_data\') }}" {active_class}')
                    elif "iia_list" in template_file:
                        new_nav = new_nav.replace('href="{{ url_for(\'iia_list\') }}"', f'href="{{ url_for(\'iia_list\') }}" {active_class}')
                
                # Replace the old nav with new nav
                content = content.replace(nav_match.group(0), f'<ul class="nav-list">\n{new_nav}\n        </ul>')
                
                # Write the updated content
                with open(template_file, 'w') as f:
                    f.write(content)
                
                print(f"✅ Updated {template_file}")
            else:
                print(f"❌ Could not find nav-list in {template_file}")
    
    # Fix the Members section issue in iia_cbe.html
    print("Fixing Members section in iia_cbe.html...")
    
    with open('templates/iia_cbe.html', 'r') as f:
        content = f.read()
    
    # Check if the JavaScript is properly placed
    if 'function showMembers()' not in content:
        print("❌ Members JavaScript function not found")
    else:
        print("✅ Members JavaScript function found")
    
    # Check if the Members section has proper display style
    if 'id="membersSection"' in content:
        print("✅ Members section found")
    else:
        print("❌ Members section not found")
    
    print("✅ All menu updates completed!")

if __name__ == "__main__":
    fix_all_menus_and_members()
