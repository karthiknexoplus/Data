#!/bin/bash

echo "🔍 Checking gunicorn error logs for the latest issue..."

# Check the latest gunicorn error logs
echo "📋 Latest gunicorn error logs:"
if [ -f "/var/log/gunicorn/data-nexoplus-error.log" ]; then
    echo "=== GUNICORN ERROR LOG (last 50 lines) ==="
    sudo tail -50 /var/log/gunicorn/data-nexoplus-error.log
else
    echo "No gunicorn error log found"
fi

echo ""
echo "📋 Latest systemd service logs:"
sudo journalctl -u data-nexoplus --no-pager -l -n 20

echo ""
echo "🧪 Testing gunicorn manually with the fixed config..."
cd /var/www/data.nexoplus.in
source venv/bin/activate

echo "📋 Running gunicorn manually (will show errors)..."
gunicorn --config gunicorn-fixed.conf.py app:app 2>&1 || echo "Gunicorn failed with error above"

echo ""
echo "🧪 Testing Flask app directly to see if there are runtime errors..."
cd /var/www/data.nexoplus.in
source venv/bin/activate

echo "📋 Testing Flask app startup..."
python3 -c "
import app
print('✅ Flask app imported successfully')

# Try to access the app and see if there are any runtime errors
try:
    print('Testing app routes...')
    with app.app.test_client() as client:
        response = client.get('/')
        print(f'Home page status: {response.status_code}')
        
        # Test a few more routes
        response = client.get('/login')
        print(f'Login page status: {response.status_code}')
        
    print('✅ Flask app is working correctly!')
except Exception as e:
    print(f'❌ Flask app runtime error: {e}')
    import traceback
    traceback.print_exc()
"

echo ""
echo "🔧 Checking if there are any database or file access issues..."
cd /var/www/data.nexoplus.in
source venv/bin/activate

python3 -c "
import os
import sqlite3

print('📋 Checking file access...')
files_to_check = ['app.py', 'users.db', 'templates', 'static']
for file in files_to_check:
    path = f'/var/www/data.nexoplus.in/{file}'
    if os.path.exists(path):
        print(f'✅ {file} - exists')
        if os.access(path, os.R_OK):
            print(f'✅ {file} - readable')
        else:
            print(f'❌ {file} - not readable')
    else:
        print(f'❌ {file} - not found')

print('')
print('📋 Testing database access...')
try:
    conn = sqlite3.connect('/var/www/data.nexoplus.in/users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\";')
    tables = cursor.fetchall()
    print(f'✅ Database accessible, tables: {[t[0] for t in tables]}')
    conn.close()
except Exception as e:
    print(f'❌ Database error: {e}')
"

echo ""
echo "🔍 Summary - look for any error messages above"
