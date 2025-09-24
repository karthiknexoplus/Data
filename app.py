import json
import csv
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
import sqlite3
import hashlib
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from functools import wraps
import time
import io
import re
from urllib.parse import urljoin, parse_qs, urlparse
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Colleges table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS colleges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            s_no TEXT,
            member_code TEXT UNIQUE,
            institution_name TEXT NOT NULL,
            year_established TEXT,
            contact_no TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # NRLM Data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nrlm_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state_code TEXT,
            state_name TEXT,
            district_code TEXT,
            district_name TEXT,
            block_code TEXT,
            block_name TEXT,
            grampanchayat_code TEXT,
            grampanchayat_name TEXT,
            village_code TEXT,
            village_name TEXT,
            shg_name TEXT,
            member_name TEXT,
            member_code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

class NRLMScraper:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://nrlm.gov.in"
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        })
        # Disable SSL verification
        self.session.verify = False
    
    def get_initial_page(self):
        """Get the initial page and establish session"""
        try:
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd=0"
            response = self.session.get(url, timeout=30, verify=False)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error getting initial page: {e}")
            return None
    
    def extract_states(self, html):
        """Extract states from the HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        states = []
        
        # Find state select element
        state_select = soup.find('select', {'name': 'stateCode'})
        if state_select:
            for option in state_select.find_all('option'):
                if option.get('value') and option.get('value') != '':
                    states.append({
                        'code': option.get('value'),
                        'name': option.get_text(strip=True)
                    })
        
        return states
    
    def get_districts(self, state_code):
        """Get districts for a given state"""
        try:
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do"
            data = {
                'methodName': 'getDistrictList',
                'stateCode': state_code
            }
            response = self.session.post(url, data=data, timeout=30, verify=False)
            response.raise_for_status()
            
            # Parse the response
            soup = BeautifulSoup(response.text, 'html.parser')
            districts = []
            
            for option in soup.find_all('option'):
                if option.get('value') and option.get('value') != '':
                    districts.append({
                        'code': option.get('value'),
                        'name': option.get_text(strip=True)
                    })
            
            return districts
        except Exception as e:
            print(f"Error getting districts for state {state_code}: {e}")
            return {}
    
    def get_blocks(self, state_code, district_code):
        """Get blocks for a given state and district"""
        try:
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do"
            data = {
                'methodName': 'getBlockList',
                'stateCode': state_code,
                'districtCode': district_code
            }
            response = self.session.post(url, data=data, timeout=30, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            blocks = []
            
            for option in soup.find_all('option'):
                if option.get('value') and option.get('value') != '':
                    blocks.append({
                        'code': option.get('value'),
                        'name': option.get_text(strip=True)
                    })
            
            return blocks
        except Exception as e:
            print(f"Error getting blocks for state {state_code}, district {district_code}: {e}")
            return {}
    
    def get_grampanchayats(self, state_code, district_code, block_code):
        """Get grampanchayats for given parameters"""
        try:
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do"
            data = {
                'methodName': 'getGrampanchayatList',
                'stateCode': state_code,
                'districtCode': district_code,
                'blockCode': block_code
            }
            response = self.session.post(url, data=data, timeout=30, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            grampanchayats = []
            
            for option in soup.find_all('option'):
                if option.get('value') and option.get('value') != '':
                    grampanchayats.append({
                        'code': option.get('value'),
                        'name': option.get_text(strip=True)
                    })
            
            return grampanchayats
        except Exception as e:
            print(f"Error getting grampanchayats: {e}")
            return {}
    
    def get_villages(self, state_code, district_code, block_code, grampanchayat_code):
        """Get villages for given parameters"""
        try:
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do"
            data = {
                'methodName': 'getVillageList',
                'stateCode': state_code,
                'districtCode': district_code,
                'blockCode': block_code,
                'grampanchayatCode': grampanchayat_code
            }
            response = self.session.post(url, data=data, timeout=30, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            villages = []
            
            for option in soup.find_all('option'):
                if option.get('value') and option.get('value') != '':
                    villages.append({
                        'code': option.get('value'),
                        'name': option.get_text(strip=True)
                    })
            
            return villages
        except Exception as e:
            print(f"Error getting villages: {e}")
            return {}
    
    def get_shg_members(self, state_code, district_code, block_code, grampanchayat_code, village_code):
        """Get SHG members data"""
        try:
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do"
            data = {
                'methodName': 'showShgMembers',
                'stateCode': state_code,
                'districtCode': district_code,
                'blockCode': block_code,
                'grampanchayatCode': grampanchayat_code,
                'villageCode': village_code
            }
            response = self.session.post(url, data=data, timeout=30, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            members = []
            
            # Find the data table
            table = soup.find('table', {'class': 'table'}) or soup.find('table')
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        members.append({
                            'shg_name': cells[0].get_text(strip=True) if len(cells) > 0 else '',
                            'member_name': cells[1].get_text(strip=True) if len(cells) > 1 else '',
                            'member_code': cells[2].get_text(strip=True) if len(cells) > 2 else ''
                        })
            
            return members
        except Exception as e:
            print(f"Error getting SHG members: {e}")
            return {}

def scrape_colleges_data():
    """Scrape colleges data from the website"""
    base_url = "https://www.coimbatoreassociation.com/ajax_listcolleges.php?page="
    data = []
    
    try:
        for page in range(1, 23):
            url = base_url + str(page)
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find table rows (skip header row)
            rows = soup.find_all("tr")[1:]
            
            for row in rows:
                cols = [col.get_text(strip=True) for col in row.find_all("td")]
                if cols and len(cols) >= 5:
                    data.append({
                        's_no': cols[0],
                        'member_code': cols[1],
                        'institution_name': cols[2],
                        'year_established': cols[3],
                        'contact_no': cols[4]
                    })
            
            # Small delay to be respectful to the server
            time.sleep(0.5)
            
    except Exception as e:
        print(f"Error scraping data: {e}")
        return None
    
    return data

def save_colleges_to_db(colleges_data):
    """Save colleges data to database, avoiding duplicates"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    new_count = 0
    updated_count = 0
    
    for college in colleges_data:
        # Check if member_code already exists
        cursor.execute('SELECT id FROM colleges WHERE member_code = ?', (college['member_code'],))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing record
            cursor.execute('''
                UPDATE colleges 
                SET s_no = ?, institution_name = ?, year_established = ?, 
                    contact_no = ?, updated_at = CURRENT_TIMESTAMP
                WHERE member_code = ?
            ''', (college['s_no'], college['institution_name'], 
                  college['year_established'], college['contact_no'], 
                  college['member_code']))
            updated_count += 1
        else:
            # Insert new record
            cursor.execute('''
                INSERT INTO colleges (s_no, member_code, institution_name, year_established, contact_no)
                VALUES (?, ?, ?, ?, ?)
            ''', (college['s_no'], college['member_code'], college['institution_name'],
                  college['year_established'], college['contact_no']))
            new_count += 1
    
    conn.commit()
    conn.close()
    
    return new_count, updated_count

def save_nrlm_data_to_db(nrlm_data):
    """Save NRLM data to database"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    new_count = 0
    
    for data in nrlm_data:
        # Check if record already exists
        cursor.execute('''
            SELECT id FROM nrlm_data 
            WHERE state_code = ? AND district_code = ? AND block_code = ? 
            AND grampanchayat_code = ? AND village_code = ? AND member_code = ?
        ''', (data['state_code'], data['district_code'], data['block_code'],
              data['grampanchayat_code'], data['village_code'], data['member_code']))
        
        existing = cursor.fetchone()
        
        if not existing:
            # Insert new record
            cursor.execute('''
                INSERT INTO nrlm_data (state_code, state_name, district_code, district_name,
                                     block_code, block_name, grampanchayat_code, grampanchayat_name,
                                     village_code, village_name, shg_name, member_name, member_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data['state_code'], data['state_name'], data['district_code'], data['district_name'],
                  data['block_code'], data['block_name'], data['grampanchayat_code'], data['grampanchayat_name'],
                  data['village_code'], data['village_name'], data['shg_name'], data['member_name'], data['member_code']))
            new_count += 1
    
    conn.commit()
    conn.close()
    
    return new_count

def get_colleges_data():
    """Get all colleges data from database"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT s_no, member_code, institution_name, year_established, contact_no, created_at FROM colleges ORDER BY institution_name')
    colleges_data = cursor.fetchall()
    conn.close()
    
    return colleges_data

def get_nrlm_data():
    """Get all NRLM data from database"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT state_name, district_name, block_name, grampanchayat_name, 
               village_name, shg_name, member_name, member_code, created_at 
        FROM nrlm_data ORDER BY state_name, district_name, block_name
    ''')
    nrlm_data = cursor.fetchall()
    conn.close()
    
    return nrlm_data

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, password FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and user[1] == hash_password(password):
            session['user_id'] = user[0]
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('signup.html')
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                         (username, hash_password(password)))
            conn.commit()
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists', 'error')
        finally:
            conn.close()
    
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/colleges')
def colleges():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, s_no, member_code, institution_name, year_established, contact_no, created_at FROM colleges ORDER BY institution_name')
    colleges_data = cursor.fetchall()
    conn.close()
    
    # Convert tuples to dictionaries for easier template access
    colleges_list = []
    for row in colleges_data:
        college_dict = {
            'id': row[0],
            's_no': row[1],
            'member_code': row[2],
            'institution_name': row[3],
            'year_established': row[4],
            'contact_no': row[5],
            'created_at': row[6]
        }
        colleges_list.append(college_dict)
    
    return render_template('colleges.html', colleges=colleges_list)

@app.route('/iia-cbe')
def iia_cbe():
    """IIA Coimbatore data page"""
    return render_template('iia_cbe.html')

@app.route('/cozcena')
def cozcena():
    """COZCENA - Covai Zone Civil Engineers Association data page"""
    return render_template('cozcena.html')

@app.route('/in-data')
def in_data():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT state_name, district_name, block_name, grampanchayat_name, 
               village_name, shg_name, member_name, member_code, created_at 
        FROM nrlm_data ORDER BY state_name, district_name, block_name
    ''')
    nrlm_data = cursor.fetchall()
    conn.close()
    
    return render_template('in_data.html', nrlm_data=nrlm_data)

# API endpoints for dropdowns
@app.route('/api/states')
def api_states():
    try:
        scraper = WorkingNRLMScraper()
        html = scraper.get_initial_page()
        if html:
            states = scraper.extract_states(html)
            return jsonify({'success': True, 'states': states})
        else:
            return jsonify({'success': False, 'message': 'Failed to get states'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/districts/<state_code>')
def api_districts(state_code):
    try:
        scraper = WorkingNRLMScraper()
        html = scraper.get_initial_page()
        if html:
            districts = scraper.get_districts(state_code)
        else:
            districts = []
        return jsonify({'success': True, 'districts': districts})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
@app.route('/api/blocks/<state_code>/<district_code>')
def api_blocks(state_code, district_code):
    try:
        scraper = WorkingNRLMScraper()
        html = scraper.get_initial_page()
        if html:
            blocks = scraper.get_blocks(state_code, district_code)
        else:
            blocks = []
        return jsonify({'success': True, 'blocks': blocks})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/grampanchayats/<state_code>/<district_code>/<block_code>')
def api_grampanchayats(state_code, district_code, block_code):
    try:
        scraper = WorkingNRLMScraper()
        html = scraper.get_initial_page()
        if html:
            grampanchayats = scraper.get_grampanchayats(state_code, district_code, block_code)
        else:
            grampanchayats = []
        return jsonify({'success': True, 'grampanchayats': grampanchayats})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/villages/<state_code>/<district_code>/<block_code>/<grampanchayat_code>')
def api_villages(state_code, district_code, block_code, grampanchayat_code):
    try:
        scraper = WorkingNRLMScraper()
        html = scraper.get_initial_page()
        if html:
            villages = scraper.get_villages(state_code, district_code, block_code, grampanchayat_code)
        else:
            villages = []
        return jsonify({'success': True, 'villages': villages})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/shg-members', methods=['POST'])
def api_shg_members():
    try:
        data = request.get_json()
        state_code = data.get('state_code')
        district_code = data.get('district_code')
        block_code = data.get('block_code')
        grampanchayat_code = data.get('grampanchayat_code')
        village_code = data.get('village_code')
        
        scraper = WorkingNRLMScraper()
        members = scraper.get_shg_members(state_code, district_code, block_code, grampanchayat_code, village_code)
        
        # Save to database
        if members:
            nrlm_data = []
            for member in members:
                nrlm_data.append({
                    'state_code': state_code,
                    'state_name': data.get('state_name', ''),
                    'district_code': district_code,
                    'district_name': data.get('district_name', ''),
                    'block_code': block_code,
                    'block_name': data.get('block_name', ''),
                    'grampanchayat_code': grampanchayat_code,
                    'grampanchayat_name': data.get('grampanchayat_name', ''),
                    'village_code': village_code,
                    'village_name': data.get('village_name', ''),
                    'shg_name': member['shg_name'],
                    'member_name': member['member_name'],
                    'member_code': member['member_code']
                })
            
            new_count = save_nrlm_data_to_db(nrlm_data)
            
            return jsonify({
                'success': True, 
                'members': members,
                'new_records_saved': new_count
            })
        else:
            return jsonify({'success': True, 'members': [], 'message': 'No SHG members found'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/import-colleges', methods=['POST'])
def import_colleges():
    try:
        # Scrape data from website
        colleges_data = scrape_colleges_data()
        
        if not colleges_data:
            return jsonify({'success': False, 'message': 'Failed to scrape data from website'})
        
        # Save to database
        new_count, updated_count = save_colleges_to_db(colleges_data)
        
        return jsonify({
            'success': True, 
            'message': f'Import completed! {new_count} new colleges added, {updated_count} updated.',
            'total_scraped': len(colleges_data),
            'new_count': new_count,
            'updated_count': updated_count
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/download-colleges-csv')
def download_colleges_csv():
    """Download colleges data as CSV"""
    colleges_data = get_colleges_data()
    
    # Create DataFrame
    df = pd.DataFrame(colleges_data, columns=[
        'S.No', 'Member Code', 'Institution Name', 'Year Established', 'Contact No', 'Created At'
    ])
    
    # Create CSV in memory
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=colleges_data_{time.strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response

@app.route('/download-colleges-excel')
def download_colleges_excel():
    """Download colleges data as Excel"""
    colleges_data = get_colleges_data()
    
    # Create DataFrame
    df = pd.DataFrame(colleges_data, columns=[
        'S.No', 'Member Code', 'Institution Name', 'Year Established', 'Contact No', 'Created At'
    ])
    
    # Create Excel in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Colleges Data', index=False)
    
    output.seek(0)
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename=colleges_data_{time.strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    return response

@app.route('/download-nrlm-csv')
def download_nrlm_csv():
    """Download NRLM data as CSV"""
    nrlm_data = get_nrlm_data()
    
    # Create DataFrame
    df = pd.DataFrame(nrlm_data, columns=[
        'State', 'District', 'Block', 'Grampanchayat', 'Village', 'SHG Name', 'Member Name', 'Member Code', 'Created At'
    ])
    
    # Create CSV in memory
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=nrlm_data_{time.strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response

@app.route('/download-nrlm-excel')
def download_nrlm_excel():
    """Download NRLM data as Excel"""
    nrlm_data = get_nrlm_data()
    
    # Create DataFrame
    df = pd.DataFrame(nrlm_data, columns=[
        'State', 'District', 'Block', 'Grampanchayat', 'Village', 'SHG Name', 'Member Name', 'Member Code', 'Created At'
    ])
    
    # Create Excel in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='NRLM Data', index=False)
    
    output.seek(0)
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename=nrlm_data_{time.strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    return response

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# CBE Ward Routes
@app.route("/cbe-wards")
@login_required
def cbe_wards():
    """Display Coimbatore ward data with pagination and search"""
    try:
        page = request.args.get("page", 1, type=int)
        search_query = request.args.get("search", "")
        per_page = 20
        
        # Load CBE ward data
        ward_data = load_cbe_ward_data()
        
        # Apply search filter
        filtered_data = ward_data
        if search_query:
            search_lower = search_query.lower()
            filtered_data = []
            for ward in ward_data:
                # Search in ward name, ward number, and directions
                if (search_lower in ward.get('ward_name', '').lower() or
                    search_lower in str(ward.get('ward_number', '')).lower() or
                    any(search_lower in str(directions).lower() for directions in ward.get('directions', {}).values())):
                    filtered_data.append(ward)
        
        # Calculate pagination
        total_records = len(filtered_data)
        total_pages = (total_records + per_page - 1) // per_page
        
        # Get current page data
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        current_page_data = filtered_data[start_idx:end_idx]
        
        return render_template("cbe_wards.html", 
                             ward_data=current_page_data, 
                             username=session.get("username"),
                             current_page=page,
                             total_pages=total_pages,
                             total_records=total_records,
                             per_page=per_page,
                             search_query=search_query)
    except Exception as e:
        flash(f"Error loading CBE ward data: {str(e)}", "error")
        return render_template("cbe_wards.html", 
                             ward_data=[], 
                             username=session.get("username"),
                             current_page=1,
                             total_pages=1,
                             total_records=0,
                             per_page=20,
                             search_query="")

@app.route("/download-cbe-wards-csv")
@login_required
def download_cbe_wards_csv():
    """Download CBE ward data as CSV"""
    try:
        ward_data = load_cbe_ward_data()
        
        # Create CSV response
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["Ward Number", "Ward Name", "Direction", "Description"])
        
        # Write data
        for ward in ward_data:
            for direction, descriptions in ward["directions"].items():
                for desc in descriptions:
                    writer.writerow([
                        ward["ward_number"],
                        ward["ward_name"],
                        direction.title(),
                        desc
                    ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers["Content-Type"] = "text/csv"
        response.headers["Content-Disposition"] = "attachment; filename=cbe_wards.csv"
        
        return response
    except Exception as e:
        flash(f"Error generating CSV: {str(e)}", "error")
        return redirect(url_for("cbe_wards"))

def load_cbe_ward_data():
    """Load CBE ward data from JSON file"""
    try:
        if os.path.exists("coimbatore_wards.json"):
            with open("coimbatore_wards.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("data", {}).get("wards", [])
        else:
            return []
    except Exception as e:
        print(f"Error loading CBE ward data: {str(e)}")
        return []
@app.route('/edu-list-tn')
def edu_list_tn():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s_no, name, district, region, college_type, category, contact, website, established, affiliation
        FROM dce_colleges 
        ORDER BY district, name
    ''')
    edu_data = cursor.fetchall()
    conn.close()
    
    return render_template('edu_list_tn.html', edu_data=edu_data)

@app.route('/refresh-dce-data')
def refresh_dce_data():
    try:
        from dce_scraper_improved import DCEScraperImproved
        scraper = DCEScraperImproved()
        colleges = scraper.get_all_colleges()
        if colleges:
            scraper.save_to_database(colleges)
            flash(f'Successfully updated {len(colleges)} colleges from DCE website!', 'success')
        else:
            flash('No colleges found or error occurred during scraping.', 'error')
    except Exception as e:
        flash(f'Error refreshing DCE data: {str(e)}', 'error')
    
    return redirect(url_for('edu_list_tn'))

@app.route('/download-dce-csv')
def download_dce_csv():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s_no, name, district, region, college_type, category, contact, website, established, affiliation
        FROM dce_colleges 
        ORDER BY district, name
    ''')
    data = cursor.fetchall()
    conn.close()
    
    # Create CSV content
    csv_content = "S.No,College Name,District,Region,College Type,Category,Contact,Website,Established,Affiliation\n"
    for row in data:
        csv_content += f"{row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]},{row[7]},{row[8]},{row[9]}\n"
    
    response = make_response(csv_content)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=dce_colleges.csv'
    return response

@app.route('/download-dce-excel')
def download_dce_excel():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s_no, name, district, region, college_type, category, contact, website, established, affiliation
        FROM dce_colleges 
        ORDER BY district, name
    ''')
    data = cursor.fetchall()
    conn.close()
    
    # Create Excel content (simplified as CSV with .xlsx extension)
    excel_content = "S.No,College Name,District,Region,College Type,Category,Contact,Website,Established,Affiliation\n"
    for row in data:
        excel_content += f"{row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]},{row[7]},{row[8]},{row[9]}\n"
    
    response = make_response(excel_content)
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = 'attachment; filename=dce_colleges.xlsx'
    return response
import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WorkingNRLMScraper:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://nrlm.gov.in"
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Origin': 'https://nrlm.gov.in',
            'Cache-Control': 'max-age=0'
        })
        self.session.verify = False
        self.token = None
    
    def get_initial_page(self):
        """Get the initial page and establish session"""
        try:
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd=0"
            response = self.session.get(url, timeout=30, verify=False)
            response.raise_for_status()
            
            # Extract token from the page
            soup = BeautifulSoup(response.text, 'html.parser')
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'tokenValue' in script.string:
                    import re
                    match = re.search(r"tokenValue\s*=\s*'([^']+)'", script.string)
                    if match:
                        self.token = match.group(1)
                        break
            
            return response.text
        except Exception as e:
            print(f"Error getting initial page: {e}")
            return None
    
    def extract_states(self, html):
        """Extract states from the HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        states = []
        
        # Find state select element
        state_select = soup.find('select', {'name': 'stateCode'})
        if state_select:
            for option in state_select.find_all('option'):
                if option.get('value') and option.get('value') != '':
                    states.append({
                        'code': option.get('value'),
                        'name': option.get_text(strip=True)
                    })
        
        return states
    
    def get_districts(self, state_code):
        """Get districts for a given state"""
        try:
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd={state_code}&reqtrack={self.token}"
            form_data = {
                'methodName': 'showShgMembers',
                'encd': state_code,
                'reqtrack': self.token,
                'stateCode': state_code
            }
            self.session.headers['Referer'] = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&reqtrack={self.token}&encd=0"
            
            response = self.session.post(url, data=form_data, timeout=30, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            districts = []
            
            district_select = soup.find('select', {'name': 'districtCode'})
            if district_select:
                for option in district_select.find_all('option'):
                    if option.get('value') and option.get('value') != '':
                        districts.append({
                            'code': option.get('value'),
                            'name': option.get_text(strip=True)
                        })
            
            return districts
        except Exception as e:
            print(f"Error getting districts for state {state_code}: {e}")
            return {}
    
    def get_blocks(self, state_code, district_code):
        """Get blocks for a given state and district"""
        try:
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd={district_code}&reqtrack={self.token}"
            form_data = {
                'methodName': 'showShgMembers',
                'encd': district_code,
                'reqtrack': self.token,
                'stateCode': state_code,
                'districtCode': district_code
            }
            self.session.headers['Referer'] = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&reqtrack={self.token}&encd={state_code}"
            
            response = self.session.post(url, data=form_data, timeout=30, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            blocks = []
            
            block_select = soup.find('select', {'name': 'blockCode'})
            if block_select:
                for option in block_select.find_all('option'):
                    if option.get('value') and option.get('value') != '':
                        blocks.append({
                            'code': option.get('value'),
                            'name': option.get_text(strip=True)
                        })
            
            return blocks
        except Exception as e:
            print(f"Error getting blocks for state {state_code}, district {district_code}: {e}")
            return {}
    
    def get_grampanchayats(self, state_code, district_code, block_code):
        """Get grampanchayats for given parameters"""
        try:
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd={block_code}&reqtrack={self.token}"
            form_data = {
                'methodName': 'showShgMembers',
                'encd': block_code,
                'reqtrack': self.token,
                'stateCode': state_code,
                'districtCode': district_code,
                'blockCode': block_code
            }
            self.session.headers['Referer'] = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&reqtrack={self.token}&encd={district_code}"
            
            response = self.session.post(url, data=form_data, timeout=30, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            grampanchayats = []
            
            grampanchayat_select = soup.find('select', {'name': 'grampanchayatCode'})
            if grampanchayat_select:
                for option in grampanchayat_select.find_all('option'):
                    if option.get('value') and option.get('value') != '':
                        grampanchayats.append({
                            'code': option.get('value'),
                            'name': option.get_text(strip=True)
                        })
            
            return grampanchayats
        except Exception as e:
            print(f"Error getting grampanchayats: {e}")
            return {}
    
    def get_villages(self, state_code, district_code, block_code, grampanchayat_code):
        """Get villages for given parameters"""
        try:
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd={grampanchayat_code}&reqtrack={self.token}"
            form_data = {
                'methodName': 'showShgMembers',
                'encd': grampanchayat_code,
                'reqtrack': self.token,
                'stateCode': state_code,
                'districtCode': district_code,
                'blockCode': block_code,
                'grampanchayatCode': grampanchayat_code
            }
            self.session.headers['Referer'] = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&reqtrack={self.token}&encd={block_code}"
            
            response = self.session.post(url, data=form_data, timeout=30, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            villages = []
            
            village_select = soup.find('select', {'name': 'villageCode'})
            if village_select:
                for option in village_select.find_all('option'):
                    if option.get('value') and option.get('value') != '':
                        villages.append({
                            'code': option.get('value'),
                            'name': option.get_text(strip=True)
                        })
            
            return villages
        except Exception as e:
            print(f"Error getting villages: {e}")
            return {}
    
    def get_shg_members(self, state_code, district_code, block_code, grampanchayat_code, village_code):
        """Get SHG members data"""
        try:
            url = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&encd={village_code}&reqtrack={self.token}"
            form_data = {
                'methodName': 'showShgMembers',
                'encd': village_code,
                'reqtrack': self.token,
                'stateCode': state_code,
                'districtCode': district_code,
                'blockCode': block_code,
                'grampanchayatCode': grampanchayat_code,
                'villageCode': village_code
            }
            self.session.headers['Referer'] = f"{self.base_url}/BlockWiseSHGMemebrsAction.do?methodName=showShgMembers&reqtrack={self.token}&encd={grampanchayat_code}"
            
            response = self.session.post(url, data=form_data, timeout=30, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            members = []
            
            # Find the data table
            table = soup.find('table', {'class': 'table'}) or soup.find('table')
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        members.append({
                            'shg_name': cells[0].get_text(strip=True) if len(cells) > 0 else '',
                            'member_name': cells[1].get_text(strip=True) if len(cells) > 1 else '',
                            'member_code': cells[2].get_text(strip=True) if len(cells) > 2 else ''
                        })
            
            return members
        except Exception as e:
            print(f"Error getting SHG members: {e}")
            return {}

@app.route('/iia-list')
def iia_list():
    # Sample IIA data
    iia_data = [
        (1, 'IIA001', 'Indian Institute of Architecture - Chennai', 'Chennai', 'Architecture', '1955', '044-2491 1234'),
        (2, 'IIA002', 'Indian Institute of Architecture - Mumbai', 'Mumbai', 'Architecture', '1960', '022-2204 5678'),
        (3, 'IIA003', 'Indian Institute of Architecture - Delhi', 'Delhi', 'Architecture', '1965', '011-2467 9012'),
        (4, 'IIA004', 'Indian Institute of Architecture - Bangalore', 'Bangalore', 'Architecture', '1970', '080-2556 3456'),
        (5, 'IIA005', 'Indian Institute of Architecture - Kolkata', 'Kolkata', 'Architecture', '1975', '033-2245 7890')
    ]
    return render_template('iia_list.html', iia_data=iia_data)

@app.route('/creda-list')
def creda_list():
    # Sample CREDAI data
    creda_data = [
        (1, 'CRD001', 'CREDAI Chennai', 'Chennai', 'Real Estate', '1999', '044-2833 1234'),
        (2, 'CRD002', 'CREDAI Mumbai', 'Mumbai', 'Real Estate', '2000', '022-2204 5678'),
        (3, 'CRD003', 'CREDAI Delhi', 'Delhi', 'Real Estate', '2001', '011-2467 9012'),
        (4, 'CRD004', 'CREDAI Bangalore', 'Bangalore', 'Real Estate', '2002', '080-2556 3456'),
        (5, 'CRD005', 'CREDAI Pune', 'Pune', 'Real Estate', '2003', '020-2556 7890')
    ]
    return render_template('creda_list.html', creda_data=creda_data)

@app.route('/ccmc-con')
def ccmc_con():
    # Sample CCMC data
    ccmc_data = [
        (1, 'CCM001', 'Chennai Corporation', 'Chennai', 'Municipal', '1688', '044-2538 1234'),
        (2, 'CCM002', 'Mumbai Corporation', 'Mumbai', 'Municipal', '1888', '022-2204 5678'),
        (3, 'CCM003', 'Delhi Corporation', 'Delhi', 'Municipal', '1957', '011-2467 9012'),
        (4, 'CCM004', 'Bangalore Corporation', 'Bangalore', 'Municipal', '1949', '080-2556 3456'),
        (5, 'CCM005', 'Kolkata Corporation', 'Kolkata', 'Municipal', '1876', '033-2245 7890')
    ]
    return render_template('ccmc_con.html', ccmc_data=ccmc_data)


# TCEA Members Routes
@app.route('/tcea-members')
@login_required
def tcea_members():
    """Display TCEA members page with search and pagination"""
    try:
        page = request.args.get("page", 1, type=int)
        search_query = request.args.get("search", "")
        category = request.args.get("category", "")
        per_page = 20
        
        # Load TCEA members data
        tcea_data = load_complete_tcea_data()
        
        # Combine all data for filtering
        all_data = []
        if tcea_data:
            # Add members
            for member in tcea_data.get('members', []):
                all_data.append({
                    'name': member.get('name', ''),
                    'position': 'Member',
                    'category': 'members',
                    'page': member.get('page', 0),
                    'url': member.get('url', ''),
                    'type': 'member'
                })
            
            # Add office bearers
            for bearer in tcea_data.get('office_bearers', []):
                all_data.append({
                    'name': bearer.get('name', ''),
                    'position': bearer.get('position', ''),
                    'category': 'office_bearers',
                    'page': 0,
                    'url': bearer.get('url', ''),
                    'type': 'office_bearer'
                })
            
            # Add EC members
            for ec in tcea_data.get('ec_members', []):
                all_data.append({
                    'name': ec.get('name', ''),
                    'position': ec.get('position', ''),
                    'category': 'ec_members',
                    'page': 0,
                    'url': ec.get('url', ''),
                    'type': 'ec_member'
                })
            
            # Add past leaders
            for leader in tcea_data.get('past_leaders', []):
                all_data.append({
                    'name': leader.get('name', ''),
                    'position': leader.get('position', ''),
                    'category': 'past_leaders',
                    'page': 0,
                    'url': leader.get('url', ''),
                    'type': 'past_leader'
                })
        
        # Apply filters
        filtered_data = all_data
        if search_query:
            search_lower = search_query.lower()
            filtered_data = [item for item in filtered_data 
                           if search_lower in item.get('name', '').lower() or 
                              search_lower in item.get('position', '').lower()]
        
        if category:
            filtered_data = [item for item in filtered_data 
                           if item.get('category') == category]
        
        # Calculate pagination
        total_records = len(filtered_data)
        total_pages = (total_records + per_page - 1) // per_page
        
        # Get current page data
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        current_page_data = filtered_data[start_idx:end_idx]
        
        return render_template('tcea_members.html', 
                             tcea_data=tcea_data,
                             filtered_data=current_page_data,
                             username=session.get('username'),
                             current_page=page,
                             total_pages=total_pages,
                             total_records=total_records,
                             per_page=per_page,
                             search_query=search_query,
                             category=category)
    except Exception as e:
        flash(f'Error loading TCEA data: {str(e)}', 'error')
        return render_template('tcea_members.html', 
                             tcea_data={},
                             filtered_data=[],
                             username=session.get('username'),
                             current_page=1,
                             total_pages=1,
                             total_records=0,
                             per_page=20,
                             search_query="",
                             category="")

@app.route('/download-tcea-csv')
@login_required
def download_tcea_csv():
    """Download TCEA members as CSV"""
    try:
        tcea_data = load_complete_tcea_data()
        
        # Create CSV response
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['S.No', 'Name', 'Page', 'Source URL'])
        
        # Write data
        for i, member in enumerate(tcea_data, 1):
            writer.writerow([
                i,
                member.get('name', ''),
                member.get('page', ''),
                member.get('url', '')
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=tcea_members.csv'
        
        return response
    except Exception as e:
        flash(f'Error generating CSV: {str(e)}', 'error')
        return redirect(url_for('tcea_members'))

@app.route('/download-tcea-excel')
@login_required
def download_tcea_excel():
    """Download TCEA members as Excel"""
    try:
        tcea_data = load_complete_tcea_data()
        
        # Create DataFrame
        df_data = []
        for i, member in enumerate(tcea_data, 1):
            df_data.append({
                'S.No': i,
                'Name': member.get('name', ''),
                'Page': member.get('page', ''),
                'Source URL': member.get('url', '')
            })
        
        df = pd.DataFrame(df_data)
        
        # Create Excel response
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='TCEA Members', index=False)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = 'attachment; filename=tcea_members.xlsx'
        
        return response
    except Exception as e:
        flash(f'Error generating Excel: {str(e)}', 'error')
        return redirect(url_for('tcea_members'))

def load_complete_tcea_data():
    """Load TCEA members data from JSON file"""
    try:
        if os.path.exists('tcea_complete_data.json'):
            with open('tcea_complete_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('data', {})
        else:
            # If no JSON file exists, return empty list
            return {}
    except Exception as e:
        print(f"Error loading TCEA data: {str(e)}")
        return {}




# CREDAI Members Routes
@app.route('/credai-members')
@login_required
def credai_members():
    """Display CREDAI members page"""
    try:
        # Load CREDAI members data
        credai_data = load_credai_data()
        return render_template('credai_members.html', credai_data=credai_data, username=session.get('username'))
    except Exception as e:
        flash(f'Error loading CREDAI data: {str(e)}', 'error')
        return render_template('credai_members.html', credai_data=[], username=session.get('username'))

@app.route('/download-credai-csv')
@login_required
def download_credai_csv():
    """Download CREDAI members as CSV"""
    try:
        credai_data = load_credai_data()
        
        # Create CSV response
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['S.No', 'Name', 'Type', 'Source URL', 'Scraped At'])
        
        # Write data
        for i, member in enumerate(credai_data, 1):
            writer.writerow([
                i,
                member.get('name', ''),
                member.get('type', ''),
                member.get('source_url', ''),
                member.get('scraped_at', '')
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=credai_members.csv'
        
        return response
    except Exception as e:
        flash(f'Error generating CSV: {str(e)}', 'error')
        return redirect(url_for('credai_members'))

@app.route('/download-credai-excel')
@login_required
def download_credai_excel():
    """Download CREDAI members as Excel"""
    try:
        credai_data = load_credai_data()
        
        # Create DataFrame
        df_data = []
        for i, member in enumerate(credai_data, 1):
            df_data.append({
                'S.No': i,
                'Name': member.get('name', ''),
                'Type': member.get('type', ''),
                'Source URL': member.get('source_url', ''),
                'Scraped At': member.get('scraped_at', '')
            })
        
        df = pd.DataFrame(df_data)
        
        # Create Excel response
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='CREDAI Members', index=False)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = 'attachment; filename=credai_members.xlsx'
        
        return response
    except Exception as e:
        flash(f'Error generating Excel: {str(e)}', 'error')
        return redirect(url_for('credai_members'))

def load_credai_data():
    """Load CREDAI members data from JSON file"""
    try:
        if os.path.exists('credai_members.json'):
            with open('credai_members.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('data', {}).get('members', [])
        else:
            # If no JSON file exists, return empty list
            return []
    except Exception as e:
        print(f"Error loading CREDAI data: {str(e)}")
        return []




# RERA Agents Routes
@app.route('/rera-agents')
@login_required
def rera_agents():
    """Display RERA agents page with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 200
        
        # Load RERA agents data
        rera_data = load_rera_data()
        
        # Calculate pagination
        total_records = len(rera_data)
        total_pages = (total_records + per_page - 1) // per_page
        
        # Get current page data
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        current_page_data = rera_data[start_idx:end_idx]
        
        return render_template('rera_agents.html', 
                             rera_data=current_page_data, 
                             username=session.get('username'),
                             current_page=page,
                             total_pages=total_pages,
                             total_records=total_records,
                             per_page=per_page)
    except Exception as e:
        flash(f'Error loading RERA data: {str(e)}', 'error')
        return render_template('rera_agents.html', 
                             rera_data=[], 
                             username=session.get('username'),
                             current_page=1,
                             total_pages=1,
                             total_records=0,
                             per_page=200)

@app.route('/download-rera-csv')
@login_required
def download_rera_csv():
    """Download RERA agents as CSV"""
    try:
        rera_data = load_rera_data()
        
        # Create CSV response
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['S.No', 'Registration Number', 'Name & Address', 'Type', 'Date', 'Source URL', 'Scraped At'])
        
        # Write data
        for i, agent in enumerate(rera_data, 1):
            writer.writerow([
                i,
                agent.get('registration_number', ''),
                agent.get('name_address', ''),
                agent.get('type', ''),
                agent.get('date', ''),
                agent.get('source_url', ''),
                agent.get('scraped_at', '')
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=rera_agents.csv'
        
        return response
    except Exception as e:
        flash(f'Error generating CSV: {str(e)}', 'error')
        return redirect(url_for('rera_agents'))

@app.route('/download-rera-excel')
@login_required
def download_rera_excel():
    """Download RERA agents as Excel"""
    try:
        rera_data = load_rera_data()
        
        # Create DataFrame
        df_data = []
        for i, agent in enumerate(rera_data, 1):
            df_data.append({
                'S.No': i,
                'Registration Number': agent.get('registration_number', ''),
                'Name & Address': agent.get('name_address', ''),
                'Type': agent.get('type', ''),
                'Date': agent.get('date', ''),
                'Source URL': agent.get('source_url', ''),
                'Scraped At': agent.get('scraped_at', '')
            })
        
        df = pd.DataFrame(df_data)
        
        # Create Excel response
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='RERA Agents', index=False)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = 'attachment; filename=rera_agents.xlsx'
        
        return response
    except Exception as e:
        flash(f'Error generating Excel: {str(e)}', 'error')
        return redirect(url_for('rera_agents'))

def load_rera_data():
    """Load RERA agents data from JSON file"""
    try:
        if os.path.exists('rera_agents.json'):
            with open('rera_agents.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('data', {}).get('agents', [])
        else:
            return []
    except Exception as e:
        print(f"Error loading RERA data: {str(e)}")

# CCMC Contractors Routes
@app.route('/ccmc-contractors')
@login_required
def ccmc_contractors():
    """Display CCMC contractors page with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 200
        
        # Load CCMC contractors data
        ccmc_data = load_ccmc_data()
        
        # Calculate pagination
        total_records = len(ccmc_data)
        total_pages = (total_records + per_page - 1) // per_page
        
        # Get current page data
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        current_page_data = ccmc_data[start_idx:end_idx]
        
        return render_template('ccmc_contractors.html', 
                             ccmc_data=current_page_data, 
                             username=session.get('username'),
                             current_page=page,
                             total_pages=total_pages,
                             total_records=total_records,
                             per_page=per_page)
    except Exception as e:
        flash(f'Error loading CCMC data: {str(e)}', 'error')
        return render_template('ccmc_contractors.html', 
                             ccmc_data=[], 
                             username=session.get('username'),
                             current_page=1,
                             total_pages=1,
                             total_records=0,
                             per_page=200)

@app.route('/download-ccmc-csv')
@login_required
def download_ccmc_csv():
    """Download CCMC contractors as CSV"""
    try:
        ccmc_data = load_ccmc_data()
        
        # Create CSV response
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['S.No', 'Name', 'Class', 'Address', 'Phone', 'Source', 'Extracted At'])
        
        # Write data
        for i, contractor in enumerate(ccmc_data, 1):
            writer.writerow([
                i,
                contractor.get('name', ''),
                contractor.get('class', ''),
                contractor.get('address', ''),
                contractor.get('phone', ''),
                contractor.get('source', ''),
                contractor.get('extracted_at', '')
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=ccmc_contractors.csv'
        
        return response
    except Exception as e:
        flash(f'Error generating CSV: {str(e)}', 'error')
        return redirect(url_for('ccmc_contractors'))

@app.route('/download-ccmc-excel')
@login_required
def download_ccmc_excel():
    """Download CCMC contractors as Excel"""
    try:
        ccmc_data = load_ccmc_data()
        
        # Create DataFrame
        df_data = []
        for i, contractor in enumerate(ccmc_data, 1):
            df_data.append({
                'S.No': i,
                'Name': contractor.get('name', ''),
                'Class': contractor.get('class', ''),
                'Address': contractor.get('address', ''),
                'Phone': contractor.get('phone', ''),
                'Source': contractor.get('source', ''),
                'Extracted At': contractor.get('extracted_at', '')
            })
        
        df = pd.DataFrame(df_data)
        
        # Create Excel response
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='CCMC Contractors', index=False)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = 'attachment; filename=ccmc_contractors.xlsx'
        
        return response
    except Exception as e:
        flash(f'Error generating Excel: {str(e)}', 'error')
        return redirect(url_for('ccmc_contractors'))

def load_ccmc_data():
    """Load CCMC contractors data from JSON file"""
    try:
        if os.path.exists('ccmc_contractors.json'):
            with open('ccmc_contractors.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('data', {}).get('contractors', [])
        else:
            return []
    except Exception as e:
        print(f"Error loading CCMC data: {str(e)}")
        return []

        return []

def load_sub_reg_data():
    """Load Sub Registrar office data from JSON file"""
    try:
        if os.path.exists('sub_reg_offices.json'):
            with open('sub_reg_offices.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('data', [])
        else:
            return []
    except Exception as e:
        print(f"Error loading Sub Registrar data: {str(e)}")
        return []

@app.route('/sr-office')
@login_required
def sr_office():
    """Display Sub Registrar offices with filtering"""
    try:
        sub_reg_data = load_sub_reg_data()
        
        # Get filter parameters
        zone_filter = request.args.get('zone', '')
        search_query = request.args.get('search', '')
        
        # Apply filters
        filtered_data = sub_reg_data
        
        if zone_filter:
            filtered_data = [office for office in filtered_data if office.get('zone', '').lower() == zone_filter.lower()]
        
        if search_query:
            search_lower = search_query.lower()
            filtered_data = [office for office in filtered_data if 
                           search_lower in office.get('office_name', '').lower() or
                           search_lower in office.get('designation', '').lower() or
                           search_lower in office.get('address', '').lower()]
        
        # Get unique zones for filter dropdown
        zones = sorted(set(office.get('zone', '') for office in sub_reg_data if office.get('zone')))
        
        # Pagination
        page = int(request.args.get('page', 1))
        per_page = 50
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_data = filtered_data[start_idx:end_idx]
        
        total_pages = (len(filtered_data) + per_page - 1) // per_page
        
        return render_template('sr_office.html', 
                             sub_reg_data=paginated_data,
                             zones=zones,
                             current_zone=zone_filter,
                             search_query=search_query,
                             username=session.get('username'),
                             current_page=page,
                             total_pages=total_pages,
                             total_records=len(filtered_data),
                             per_page=per_page)
    except Exception as e:
        flash(f'Error loading Sub Registrar data: {str(e)}', 'error')
        return render_template('sr_office.html', 
                             sub_reg_data=[], 
                             zones=[],
                             username=session.get('username'),
                             current_page=1,
                             total_pages=1,
                             total_records=0,
                             per_page=50)

@app.route('/download-sr-office-csv')
@login_required
def download_sr_office_csv():
    """Download Sub Registrar offices as CSV"""
    try:
        sub_reg_data = load_sub_reg_data()
        
        # Get filter parameters
        zone_filter = request.args.get('zone', '')
        search_query = request.args.get('search', '')
        
        # Apply same filters as main page
        filtered_data = sub_reg_data
        
        if zone_filter:
            filtered_data = [office for office in filtered_data if office.get('zone', '').lower() == zone_filter.lower()]
        
        if search_query:
            search_lower = search_query.lower()
            filtered_data = [office for office in filtered_data if 
                           search_lower in office.get('office_name', '').lower() or
                           search_lower in office.get('designation', '').lower() or
                           search_lower in office.get('address', '').lower()]
        
        # Create CSV response
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Zone', 'Office Name', 'Designation', 'STD Code', 'Office Phone', 'Email', 'Address'])
        
        # Write data
        for office in filtered_data:
            writer.writerow([
                office.get('zone', ''),
                office.get('office_name', ''),
                office.get('designation', ''),
                office.get('std_code', ''),
                office.get('office_phone', ''),
                office.get('email', ''),
                office.get('address', '')
            ])
        
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=sub_registrar_offices_{zone_filter or "all"}.csv'
        
        return response
    except Exception as e:
        flash(f'Error generating CSV: {str(e)}', 'error')
        return redirect(url_for('sr_office'))


@app.route('/api/ward-map-url')
@login_required
def ward_map_url():
    """API endpoint to generate Google Maps URL for ward boundaries"""
    try:
        from google_maps_helper import create_ward_boundary_map_url
        
        ward_name = request.args.get('ward_name', '')
        direction = request.args.get('direction', '')
        descriptions = request.args.getlist('descriptions')
        
        if not descriptions:
            descriptions_str = request.args.get('descriptions_str', '')
            descriptions = descriptions_str.split('|') if descriptions_str else []
        
        if ward_name and direction and descriptions:
            map_url = create_ward_boundary_map_url(ward_name, direction, descriptions)
            return jsonify({
                'success': True,
                'map_url': map_url,
                'ward_name': ward_name,
                'direction': direction
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Missing required parameters: ward_name, direction, descriptions'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# BAI Members route
@app.route('/bai-members')
@login_required
def bai_members():
    """Display BAI members data"""
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search_query = request.args.get('search', '').strip()
        
        # Build query
        query = "SELECT * FROM bai_members WHERE 1=1"
        params = []
        
        if search_query:
            query += " AND (company_name LIKE ? OR contact_person LIKE ? OR address LIKE ?)"
            search_param = f"%{search_query}%"
            params.extend([search_param, search_param, search_param])
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM ({query})"
        cursor.execute(count_query, params)
        total_records = cursor.fetchone()[0]
        
        # Calculate pagination
        total_pages = (total_records + per_page - 1) // per_page
        offset = (page - 1) * per_page
        
        # Get paginated data
        query += " ORDER BY company_name LIMIT ? OFFSET ?"
        params.extend([per_page, offset])
        
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        bai_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        
        return render_template('bai_members.html', 
                             bai_data=bai_data,
                             username=session.get('username'),
                             current_page=page,
                             total_pages=total_pages,
                             total_records=total_records,
                             per_page=per_page,
                             search_query=search_query)
    except Exception as e:
        flash(f'Error loading BAI data: {str(e)}', 'error')
        return render_template('bai_members.html', 
                             bai_data=[],
                             username=session.get('username'),
                             current_page=1,
                             total_pages=1,
                             total_records=0,
                             per_page=50,
                             search_query='')

@app.route('/download-bai-csv')
@login_required
def download_bai_csv():
    """Download BAI members as CSV"""
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Get filter parameters
        search_query = request.args.get('search', '')
        
        # Build query
        query = "SELECT company_name, contact_person, address, phone, email, source_url, scraped_at FROM bai_members WHERE 1=1"
        params = []
        
        if search_query:
            query += " AND (company_name LIKE ? OR contact_person LIKE ? OR address LIKE ?)"
            search_param = f"%{search_query}%"
            params.extend([search_param, search_param, search_param])
        
        query += " ORDER BY company_name"
        
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        bai_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        
        # Create CSV response
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Company Name', 'Contact Person', 'Address', 'Phone', 'Email', 'Source URL', 'Scraped At'])
        
        # Write data
        for member in bai_data:
            writer.writerow([
                member.get('company_name', ''),
                member.get('contact_person', ''),
                member.get('address', ''),
                member.get('phone', ''),
                member.get('email', ''),
                member.get('source_url', ''),
                member.get('scraped_at', '')
            ])
        
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=bai_members_{search_query or "all"}.csv'
        
        return response
    except Exception as e:
        flash(f'Error generating CSV: {str(e)}', 'error')
        return redirect(url_for('bai_members'))



# Pollachi Wards functionality
def load_pollachi_wards_data():
    """Load Pollachi wards data from JSON file"""
    try:
        if os.path.exists('pollachi_wards.json'):
            with open('pollachi_wards.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('wards', [])
        else:
            return []
    except Exception as e:
        print(f"Error loading Pollachi wards data: {str(e)}")
        return []

@app.route('/pollachi-wards')
@login_required
def pollachi_wards():
    """Display Pollachi wards with filtering"""
    try:
        wards_data = load_pollachi_wards_data()
        
        # Get filter parameters
        search_query = request.args.get('search', '')
        
        # Apply filters
        filtered_data = wards_data
        
        if search_query:
            search_lower = search_query.lower()
            filtered_data = [ward for ward in filtered_data if 
                           search_lower in str(ward.get('ward_number', '')).lower() or
                           search_lower in ward.get('ward_name', '').lower() or
                           search_lower in str(ward.get('description', '')).lower()]
        
        # Pagination
        page = int(request.args.get('page', 1))
        per_page = 50
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_data = filtered_data[start_idx:end_idx]
        
        total_pages = (len(filtered_data) + per_page - 1) // per_page
        
        return render_template('pollachi_wards.html', 
                             wards_data=paginated_data,
                             search_query=search_query,
                             username=session.get('username'),
                             current_page=page,
                             total_pages=total_pages,
                             total_wards=len(filtered_data))
    except Exception as e:
        flash(f'Error loading Pollachi wards data: {str(e)}', 'error')
        return render_template('pollachi_wards.html', 
                             wards_data=[],
                             search_query='',
                             username=session.get('username'),
                             current_page=1,
                             total_pages=1,
                             total_wards=0)

@app.route('/download-pollachi-wards-csv')
@login_required
def download_pollachi_wards_csv():
    """Download Pollachi wards data as CSV"""
    try:
        wards_data = load_pollachi_wards_data()
        
        # Get search query for filename
        search_query = request.args.get('search', '')
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Ward Number', 'Ward Name', 'Description', 'Landmarks', 
            'Roads', 'Boundaries', 'Population', 'Area'
        ])
        
        # Write data
        for ward in wards_data:
            landmarks = '; '.join(ward.get('general_landmarks', [])) if ward.get('general_landmarks') else ''
            roads = '; '.join(ward.get('general_roads', [])) if ward.get('general_roads') else ''
            boundaries = '; '.join(ward.get('boundaries', [])) if ward.get('boundaries') else ''
            
            writer.writerow([
                ward.get('ward_number', ''),
                ward.get('ward_name', ''),
                ward.get('description', ''),
                landmarks,
                roads,
                boundaries,
                ward.get('population', ''),
                ward.get('area', '')
            ])
        
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=pollachi_wards_{search_query or "all"}.csv'
        
        return response
    except Exception as e:
        flash(f'Error generating CSV: {str(e)}', 'error')
        return redirect(url_for('pollachi_wards'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
