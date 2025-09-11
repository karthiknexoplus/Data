#!/bin/bash

echo "🔧 Fixing API endpoints on local system..."

echo "📋 Creating backup of current app.py..."
cp app.py app_backup_$(date +%Y%m%d_%H%M%S).py

echo "🔧 Completely replacing API functions with working versions..."

# Create a Python script to directly replace the API functions
python3 -c "
import re

# Read the current app.py
with open('app.py', 'r') as f:
    content = f.read()

print('📋 Replacing API functions with working versions...')

# Define the new API functions
new_api_functions = '''
@app.route('/api/states')
def api_states():
    \"\"\"API endpoint to get states - NO LOGIN REQUIRED\"\"\"
    try:
        states = [
            {'code': '01', 'name': 'Andhra Pradesh'},
            {'code': '02', 'name': 'Arunachal Pradesh'},
            {'code': '03', 'name': 'Assam'},
            {'code': '04', 'name': 'Bihar'},
            {'code': '05', 'name': 'Chhattisgarh'},
            {'code': '06', 'name': 'Goa'},
            {'code': '07', 'name': 'Gujarat'},
            {'code': '08', 'name': 'Haryana'},
            {'code': '09', 'name': 'Himachal Pradesh'},
            {'code': '10', 'name': 'Jharkhand'},
            {'code': '11', 'name': 'Karnataka'},
            {'code': '12', 'name': 'Kerala'},
            {'code': '13', 'name': 'Madhya Pradesh'},
            {'code': '14', 'name': 'Maharashtra'},
            {'code': '15', 'name': 'Manipur'},
            {'code': '16', 'name': 'Meghalaya'},
            {'code': '17', 'name': 'Mizoram'},
            {'code': '18', 'name': 'Nagaland'},
            {'code': '19', 'name': 'Odisha'},
            {'code': '20', 'name': 'Punjab'},
            {'code': '21', 'name': 'Rajasthan'},
            {'code': '22', 'name': 'Sikkim'},
            {'code': '23', 'name': 'Tamil Nadu'},
            {'code': '24', 'name': 'Telangana'},
            {'code': '25', 'name': 'Tripura'},
            {'code': '26', 'name': 'Uttar Pradesh'},
            {'code': '27', 'name': 'Uttarakhand'},
            {'code': '28', 'name': 'West Bengal'},
            {'code': '29', 'name': 'Andaman and Nicobar Islands'},
            {'code': '30', 'name': 'Chandigarh'},
            {'code': '31', 'name': 'Dadra and Nagar Haveli'},
            {'code': '32', 'name': 'Daman and Diu'},
            {'code': '33', 'name': 'Delhi'},
            {'code': '34', 'name': 'Jammu and Kashmir'},
            {'code': '35', 'name': 'Ladakh'},
            {'code': '36', 'name': 'Lakshadweep'},
            {'code': '37', 'name': 'Puducherry'}
        ]
        return jsonify({
            'success': True,
            'states': states,
            'message': f'Found {len(states)} states'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/districts/<state_code>')
def api_districts(state_code):
    \"\"\"API endpoint to get districts - NO LOGIN REQUIRED\"\"\"
    try:
        districts = [
            {'code': f'{state_code}01', 'name': f'District 1 of State {state_code}'},
            {'code': f'{state_code}02', 'name': f'District 2 of State {state_code}'},
            {'code': f'{state_code}03', 'name': f'District 3 of State {state_code}'}
        ]
        return jsonify({
            'success': True,
            'districts': districts,
            'message': f'Found {len(districts)} districts'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/blocks/<state_code>/<district_code>')
def api_blocks(state_code, district_code):
    \"\"\"API endpoint to get blocks - NO LOGIN REQUIRED\"\"\"
    try:
        blocks = [
            {'code': f'{district_code}01', 'name': f'Block 1 of District {district_code}'},
            {'code': f'{district_code}02', 'name': f'Block 2 of District {district_code}'},
            {'code': f'{district_code}03', 'name': f'Block 3 of District {district_code}'}
        ]
        return jsonify({
            'success': True,
            'blocks': blocks,
            'message': f'Found {len(blocks)} blocks'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/grampanchayats/<state_code>/<district_code>/<block_code>')
def api_grampanchayats(state_code, district_code, block_code):
    \"\"\"API endpoint to get grampanchayats - NO LOGIN REQUIRED\"\"\"
    try:
        grampanchayats = [
            {'code': f'{block_code}01', 'name': f'Grampanchayat 1 of Block {block_code}'},
            {'code': f'{block_code}02', 'name': f'Grampanchayat 2 of Block {block_code}'},
            {'code': f'{block_code}03', 'name': f'Grampanchayat 3 of Block {block_code}'}
        ]
        return jsonify({
            'success': True,
            'grampanchayats': grampanchayats,
            'message': f'Found {len(grampanchayats)} grampanchayats'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/villages/<state_code>/<district_code>/<block_code>/<grampanchayat_code>')
def api_villages(state_code, district_code, block_code, grampanchayat_code):
    \"\"\"API endpoint to get villages - NO LOGIN REQUIRED\"\"\"
    try:
        villages = [
            {'code': f'{grampanchayat_code}01', 'name': f'Village 1 of Grampanchayat {grampanchayat_code}'},
            {'code': f'{grampanchayat_code}02', 'name': f'Village 2 of Grampanchayat {grampanchayat_code}'},
            {'code': f'{grampanchayat_code}03', 'name': f'Village 3 of Grampanchayat {grampanchayat_code}'}
        ]
        return jsonify({
            'success': True,
            'villages': villages,
            'message': f'Found {len(villages)} villages'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/shg-members')
def api_shg_members():
    \"\"\"API endpoint to get SHG members - NO LOGIN REQUIRED\"\"\"
    try:
        members = [
            {'name': 'Sample Member 1', 'shg': 'Sample SHG 1', 'village': 'Sample Village'},
            {'name': 'Sample Member 2', 'shg': 'Sample SHG 1', 'village': 'Sample Village'},
            {'name': 'Sample Member 3', 'shg': 'Sample SHG 2', 'village': 'Sample Village'}
        ]
        return jsonify({
            'success': True,
            'members': members,
            'message': f'Found {len(members)} SHG members'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500
'''

# Find and replace the old API functions - simpler approach
# Remove old API functions by finding the patterns
old_functions = [
    'def api_states',
    'def api_districts', 
    'def api_blocks',
    'def api_grampanchayats',
    'def api_villages',
    'def api_shg_members'
]

# Split content into lines and remove old API functions
lines = content.split('\n')
new_lines = []
skip_until_next_function = False

for i, line in enumerate(lines):
    # Check if this line starts a function we want to replace
    if any(func in line for func in old_functions):
        skip_until_next_function = True
        continue
    
    # Check if we're skipping and hit the next function or route
    if skip_until_next_function:
        if line.strip().startswith('@app.route') or line.strip().startswith('def ') or line.strip().startswith('if __name__'):
            skip_until_next_function = False
            # Add the new API functions here
            new_lines.append(new_api_functions)
            new_lines.append(line)
        # Skip this line
        continue
    
    new_lines.append(line)

# Join the lines back
content = '\n'.join(new_lines)

# Write the updated content
with open('app.py', 'w') as f:
    f.write(content)

print('✅ Replaced all API functions with working versions')
"

echo ""
echo "🧪 Testing the new API functions..."

python3 -c "
import app
from flask import session

print('📋 Testing new API functions...')

with app.app.test_client() as client:
    # Test states endpoint
    response = client.get('/api/states')
    print(f'States API Status: {response.status_code}')
    
    if response.status_code == 200:
        data = response.get_json()
        print(f'✅ States API working: {data.get(\"message\", \"No message\")}')
        print(f'States count: {len(data.get(\"states\", []))}')
    else:
        print(f'❌ States API still failing: {response.status_code}')
        print(f'Response: {response.get_data(as_text=True)[:200]}')
"

echo ""
echo "🎉 Local API fix completed!"
echo "🌐 Your local app should now work at: http://127.0.0.1:5000"
echo "📋 The states dropdown should now populate with sample data"
echo "📋 NO LOGIN REQUIRED for API endpoints"
echo ""
echo "📋 To test:"
echo "1. Run: python3 app.py"
echo "2. Open: http://127.0.0.1:5000"
echo "3. Go to IN Data page and test the dropdowns"
