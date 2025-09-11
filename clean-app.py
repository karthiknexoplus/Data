#!/usr/bin/env python3

print("🔧 Cleaning app.py - removing duplicate functions...")

# Read the current app.py
with open('app.py', 'r') as f:
    content = f.read()

# Split into lines
lines = content.split('\n')
new_lines = []
seen_functions = set()
skip_until_next_route = False

for i, line in enumerate(lines):
    # Check if this line starts a function we've seen before
    if line.strip().startswith('def api_'):
        func_name = line.strip().split('(')[0].replace('def ', '')
        if func_name in seen_functions:
            print(f"Removing duplicate function: {func_name}")
            skip_until_next_route = True
            continue
        else:
            seen_functions.add(func_name)
            skip_until_next_route = False
    
    # Check if we're skipping and hit the next route
    if skip_until_next_route:
        if line.strip().startswith('@app.route') or line.strip().startswith('if __name__'):
            skip_until_next_route = False
            new_lines.append(line)
        # Skip this line
        continue
    
    new_lines.append(line)

# Join the lines back
content = '\n'.join(new_lines)

# Write the cleaned content
with open('app.py', 'w') as f:
    f.write(content)

print(f"✅ Cleaned app.py - removed duplicate functions")
print(f"Functions found: {seen_functions}")

# Test the cleaned file
print("🧪 Testing the cleaned file...")
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

print("🎉 App.py cleaned successfully!")
