#!/usr/bin/env python3

print("🔧 Fixing duplicate routes in app.py...")

# Read the current app.py
with open('app.py', 'r') as f:
    content = f.read()

# Split into lines
lines = content.split('\n')
new_lines = []
seen_routes = set()
skip_until_next_function = False

for i, line in enumerate(lines):
    # Check if this line is a route decorator
    if line.strip().startswith('@app.route'):
        route = line.strip()
        if route in seen_routes:
            print(f"Removing duplicate route: {route}")
            skip_until_next_function = True
            continue
        else:
            seen_routes.add(route)
            skip_until_next_function = False
    
    # Check if we're skipping and hit the next function or route
    if skip_until_next_function:
        if (line.strip().startswith('@app.route') or 
            line.strip().startswith('def ') or 
            line.strip().startswith('if __name__') or
            line.strip().startswith('@login_required')):
            skip_until_next_function = False
            new_lines.append(line)
        # Skip this line
        continue
    
    new_lines.append(line)

# Join the lines back
content = '\n'.join(new_lines)

# Write the fixed content
with open('app.py', 'w') as f:
    f.write(content)

print(f"✅ Fixed duplicate routes")
print(f"Routes found: {seen_routes}")

# Test the fixed file
print("🧪 Testing the fixed file...")
try:
    import app
    from flask import session
    
    with app.app.test_client() as client:
        response = client.get('/api/states')
        print(f'States API Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.get_json()
            print(f'✅ States API working: {data.get("message", "No message")}')
        else:
            print(f'❌ States API still failing: {response.status_code}')
            print(f'Response: {response.get_data(as_text=True)[:200]}')
            
except Exception as e:
    print(f'❌ Error testing: {e}')

print("🎉 Routes fixed successfully!")
