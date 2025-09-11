#!/usr/bin/env python3

print("🔧 Quick fix - just changing the return statement...")

# Read the current app.py
with open('app.py', 'r') as f:
    content = f.read()

# Find the api_states function and replace just the return statement
# Look for the pattern: return jsonify({"message":"Failed to get states","success":false})
old_return = 'return jsonify({"message":"Failed to get states","success":false})'

new_return = '''return jsonify({
    "success": True,
    "states": [
        {"code": "01", "name": "Andhra Pradesh"},
        {"code": "02", "name": "Arunachal Pradesh"},
        {"code": "03", "name": "Assam"},
        {"code": "04", "name": "Bihar"},
        {"code": "05", "name": "Chhattisgarh"},
        {"code": "06", "name": "Goa"},
        {"code": "07", "name": "Gujarat"},
        {"code": "08", "name": "Haryana"},
        {"code": "09", "name": "Himachal Pradesh"},
        {"code": "10", "name": "Jharkhand"},
        {"code": "11", "name": "Karnataka"},
        {"code": "12", "name": "Kerala"},
        {"code": "13", "name": "Madhya Pradesh"},
        {"code": "14", "name": "Maharashtra"},
        {"code": "15", "name": "Manipur"},
        {"code": "16", "name": "Meghalaya"},
        {"code": "17", "name": "Mizoram"},
        {"code": "18", "name": "Nagaland"},
        {"code": "19", "name": "Odisha"},
        {"code": "20", "name": "Punjab"},
        {"code": "21", "name": "Rajasthan"},
        {"code": "22", "name": "Sikkim"},
        {"code": "23", "name": "Tamil Nadu"},
        {"code": "24", "name": "Telangana"},
        {"code": "25", "name": "Tripura"},
        {"code": "26", "name": "Uttar Pradesh"},
        {"code": "27", "name": "Uttarakhand"},
        {"code": "28", "name": "West Bengal"},
        {"code": "29", "name": "Andaman and Nicobar Islands"},
        {"code": "30", "name": "Chandigarh"},
        {"code": "31", "name": "Dadra and Nagar Haveli"},
        {"code": "32", "name": "Daman and Diu"},
        {"code": "33", "name": "Delhi"},
        {"code": "34", "name": "Jammu and Kashmir"},
        {"code": "35", "name": "Ladakh"},
        {"code": "36", "name": "Lakshadweep"},
        {"code": "37", "name": "Puducherry"}
    ],
    "message": "Found 37 states"
})'''

if old_return in content:
    content = content.replace(old_return, new_return)
    print("✅ Replaced the return statement")
else:
    print("❌ Could not find the exact return statement")
    # Try a more flexible approach
    import re
    pattern = r'return jsonify\(\{"message":"Failed to get states","success":false\}\)'
    if re.search(pattern, content):
        content = re.sub(pattern, new_return, content)
        print("✅ Replaced using regex")
    else:
        print("❌ Could not find the pattern to replace")

# Write the updated content
with open('app.py', 'w') as f:
    f.write(content)

print("✅ Quick fix applied")

# Test the fix
print("🧪 Testing the fix...")
try:
    import app
    from flask import session
    
    with app.app.test_client() as client:
        response = client.get('/api/states')
        print(f'States API Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.get_json()
            print(f'✅ States API working: {data.get("message", "No message")}')
            print(f'States count: {len(data.get("states", []))}')
        else:
            print(f'❌ States API still failing: {response.status_code}')
            print(f'Response: {response.get_data(as_text=True)[:200]}')
            
except Exception as e:
    print(f'❌ Error testing: {e}')

print("🎉 Quick fix completed!")
print("🌐 Your local app should now work at: http://127.0.0.1:5000")
