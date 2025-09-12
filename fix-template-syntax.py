import re

def fix_template_syntax():
    """Fix template syntax errors"""
    
    templates = [
        'templates/colleges.html',
        'templates/edu_list_tn.html', 
        'templates/in_data.html',
        'templates/iia_list.html'
    ]
    
    for template_file in templates:
        print(f"Fixing {template_file}...")
        
        with open(template_file, 'r') as f:
            content = f.read()
        
        # Fix the syntax error in href
        content = content.replace('href="{ url_for(\'colleges\') }"', 'href="{{ url_for(\'colleges\') }}"')
        content = content.replace('href="{ url_for(\'edu_list_tn\') }"', 'href="{{ url_for(\'edu_list_tn\') }}"')
        content = content.replace('href="{ url_for(\'in_data\') }"', 'href="{{ url_for(\'in_data\') }}"')
        content = content.replace('href="{ url_for(\'iia_cbe\') }"', 'href="{{ url_for(\'iia_cbe\') }}"')
        
        # Fix the class attribute placement
        content = content.replace('class="nav-item active" style=', 'style=')
        content = re.sub(r'href="\{\{ url_for\(\'(\w+)\'\) \}\}" style=', r'href="{{ url_for(\'\1\') }}" class="nav-item active" style=', content)
        
        with open(template_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Fixed {template_file}")

if __name__ == "__main__":
    fix_template_syntax()
