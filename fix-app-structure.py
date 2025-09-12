import re

def fix_app_structure():
    """Fix the Flask app structure by moving app.run() to the end"""
    
    # Read the current app.py
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Remove the app.run() line from the middle
    content = re.sub(r'    app\.run\(debug=True\)\n', '', content)
    
    # Add app.run() at the very end
    content += '\nif __name__ == "__main__":\n    app.run(debug=True)\n'
    
    # Write the fixed content
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed Flask app structure - moved app.run() to the end")

if __name__ == "__main__":
    fix_app_structure()
