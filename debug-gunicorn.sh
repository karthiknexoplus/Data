#!/bin/bash

echo "🔍 Debugging gunicorn startup issues..."

# Stop the service first
sudo systemctl stop data-nexoplus

# Check gunicorn error logs
echo "📋 Checking gunicorn error logs..."
if [ -f "/var/log/gunicorn/data-nexoplus-error.log" ]; then
    echo "=== GUNICORN ERROR LOG ==="
    sudo tail -50 /var/log/gunicorn/data-nexoplus-error.log
else
    echo "No gunicorn error log found"
fi

echo ""
echo "📋 Checking gunicorn access logs..."
if [ -f "/var/log/gunicorn/data-nexoplus-access.log" ]; then
    echo "=== GUNICORN ACCESS LOG ==="
    sudo tail -20 /var/log/gunicorn/data-nexoplus-access.log
else
    echo "No gunicorn access log found"
fi

echo ""
echo "🧪 Testing gunicorn with maximum verbosity..."
cd /var/www/data.nexoplus.in
source venv/bin/activate

# Create a minimal test config
cat > test-gunicorn.conf.py << 'TEST_EOF'
bind = "127.0.0.1:8001"
workers = 1
worker_class = "sync"
timeout = 30
keepalive = 2
preload_app = False
user = "ubuntu"
group = "ubuntu"
loglevel = "debug"
TEST_EOF

echo "📋 Running gunicorn with debug output (will timeout after 15 seconds)..."
timeout 15s gunicorn --config test-gunicorn.conf.py --log-level debug app:app 2>&1 || echo "Gunicorn test completed or timed out"

echo ""
echo "🧪 Testing Flask app directly (not through gunicorn)..."
cd /var/www/data.nexoplus.in
source venv/bin/activate

echo "📋 Testing Flask app.run()..."
python3 -c "
import app
print('Flask app imported successfully')
print('App name:', app.app.name)
print('App debug mode:', app.app.debug)

# Try to access the app object
try:
    print('Testing app object...')
    print('Routes:', [rule.rule for rule in app.app.url_map.iter_rules()])
    print('✅ Flask app is working!')
except Exception as e:
    print(f'❌ Flask app error: {e}')
    import traceback
    traceback.print_exc()
"

echo ""
echo "🧪 Testing if there are any import issues in the app..."
cd /var/www/data.nexoplus.in
source venv/bin/activate

python3 -c "
import sys
print('Python version:', sys.version)
print('Python path:', sys.path)

# Test all imports that might be in app.py
modules_to_test = [
    'flask', 'pandas', 'requests', 'bs4', 'sqlite3', 
    'os', 'json', 'datetime', 'urllib', 'urllib.parse'
]

for module in modules_to_test:
    try:
        __import__(module)
        print(f'✅ {module} - OK')
    except ImportError as ie:
        print(f'❌ {module} - {ie}')
    except Exception as e:
        print(f'⚠️  {module} - {e}')
"

echo ""
echo "🔧 Checking file permissions..."
ls -la /var/www/data.nexoplus.in/
ls -la /var/www/data.nexoplus.in/app.py

echo ""
echo "🔧 Checking if there are any syntax errors in app.py..."
cd /var/www/data.nexoplus.in
source venv/bin/activate
python3 -m py_compile app.py && echo "✅ app.py syntax is valid" || echo "❌ app.py has syntax errors"

echo ""
echo "🧪 Testing a minimal Flask app to see if gunicorn works at all..."
cd /var/www/data.nexoplus.in
source venv/bin/activate

cat > test_app.py << 'TEST_APP_EOF'
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(debug=True)
TEST_APP_EOF

echo "📋 Testing minimal Flask app with gunicorn..."
timeout 10s gunicorn --bind 127.0.0.1:8002 --workers 1 test_app:app 2>&1 || echo "Minimal app test completed or timed out"

echo ""
echo "🔍 Summary of findings above - look for any error messages or issues"
