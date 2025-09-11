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
            return []
    
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
            return []
    
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
            return []
    
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
            return []
    
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
            return []

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
@login_required
def dashboard():
    return render_template('dashboard.html', username=session['username'])

@app.route('/colleges')
@login_required
def colleges():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM colleges ORDER BY institution_name')
    colleges_data = cursor.fetchall()
    conn.close()
    
    return render_template('colleges.html', colleges=colleges_data)

@app.route('/in-data')
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

@app.route('/edu-list-tn')
@login_required
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
@login_required
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
@login_required
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
@login_required
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
            return []
    
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
            return []
    
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
            return []
    
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
            return []
    
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
            return []

@app.route('/iia-list')
@login_required
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
@login_required
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
@login_required
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
