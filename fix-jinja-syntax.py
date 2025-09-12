import re

def fix_jinja_syntax():
    """Fix Jinja2 template syntax errors"""
    
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
        
        # Fix the escaped quotes in url_for
        content = content.replace("url_for(\\'", "url_for('")
        content = content.replace("\\')", "')")
        
        # Fix any other escaped quotes
        content = content.replace("\\'", "'")
        
        with open(template_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Fixed {template_file}")

if __name__ == "__main__":
    fix_jinja_syntax()
