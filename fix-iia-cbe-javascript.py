import re

def fix_iia_cbe_javascript():
    """Add missing JavaScript functions to iia_cbe.html"""
    
    # Read the current template
    with open('templates/iia_cbe.html', 'r') as f:
        content = f.read()
    
    # Add the JavaScript before the closing body tag
    javascript = '''
    <script>
    function showOfficeBearers() {
        document.getElementById('officeBearersSection').style.display = 'block';
        document.getElementById('membersSection').style.display = 'none';
        document.getElementById('officeBearersBtn').classList.add('active');
        document.getElementById('membersBtn').classList.remove('active');
    }
    
    function showMembers() {
        document.getElementById('officeBearersSection').style.display = 'none';
        document.getElementById('membersSection').style.display = 'block';
        document.getElementById('membersBtn').classList.add('active');
        document.getElementById('officeBearersBtn').classList.remove('active');
    }
    </script>'''
    
    # Add the JavaScript before the closing body tag
    if '</body>' in content:
        content = content.replace('</body>', javascript + '</body>')
    else:
        # If no body tag, add before the last closing tag
        content = content + javascript
    
    # Write the updated content
    with open('templates/iia_cbe.html', 'w') as f:
        f.write(content)
    
    print("✅ Added JavaScript functions to iia_cbe.html!")

if __name__ == "__main__":
    fix_iia_cbe_javascript()
