import re

def fix_dashboard_and_add_menu():
    """Fix dashboard to show NRLM data and add IIA Cbe menu"""
    
    # Read the current dashboard template
    with open('templates/dashboard.html', 'r') as f:
        content = f.read()
    
    # Add IIA Cbe menu item
    old_nav = '''            <li class="nav-item">
                <i class="fas fa-truck"></i>
                <span>Eway Data</span>
            </li>'''
    
    new_nav = '''            <li class="nav-item">
                <a href="{{ url_for('iia_cbe') }}" style="text-decoration: none; color: inherit; display: flex; align-items: center;">
                    <i class="fas fa-industry"></i>
                    <span>IIA Cbe</span>
                </a>
            </li>
            <li class="nav-item">
                <i class="fas fa-truck"></i>
                <span>Eway Data</span>
            </li>'''
    
    content = content.replace(old_nav, new_nav)
    
    # Replace the Add Location form with proper NRLM data interface
    old_content = '''        <!-- Add Location Form -->
        <div class="form-section">
            <div class="form-grid">
                <div class="form-column">
                    <div class="input-group">
                        <i class="fas fa-building"></i>
                        <input type="text" placeholder="Name" name="name">
                    </div>
                    <div class="input-group">
                        <i class="fas fa-id-card"></i>
                        <input type="text" placeholder="ORG ID (e.g. PGSH)" name="org_id">
                    </div>
                    <div class="input-group">
                        <i class="fas fa-credit-card"></i>
                        <input type="text" placeholder="Acquirer ID (e.g. 727274)" name="acquirer_id">
                    </div>
                </div>
                <div class="form-column">
                    <div class="input-group">
                        <i class="fas fa-map-marker-alt"></i>
                        <input type="text" placeholder="Address" name="address">
                    </div>
                    <div class="input-group">
                        <i class="fas fa-hashtag"></i>
                        <input type="text" placeholder="Plaza ID (e.g. 712764)" name="plaza_id">
                    </div>
                    <div class="input-group">
                        <i class="fas fa-building"></i>
                        <input type="text" placeholder="Agency ID (e.g. TCABO)" name="agency_id">
                    </div>
                    <div class="input-group">
                        <i class="fas fa-globe"></i>
                        <input type="text" placeholder="Geo Code (e.g. 11.0185,76.9778)" name="geo_code">
                    </div>
                </div>
            </div>
            <button class="add-btn">
                <i class="fas fa-plus"></i>
                Add Location
            </button>
        </div>'''
    
    new_content = '''        <!-- NRLM Data Section -->
        <div class="content-header">
            <div class="header-content">
                <h2><i class="fas fa-database"></i> NRLM Data (IN Data)</h2>
                <div class="header-actions">
                    <div class="download-buttons">
                        <a href="{{ url_for('download_nrlm_csv') }}" class="download-btn csv-btn">
                            <i class="fas fa-file-csv"></i>
                            Download CSV
                        </a>
                        <a href="{{ url_for('download_nrlm_excel') }}" class="download-btn excel-btn">
                            <i class="fas fa-file-excel"></i>
                            Download Excel
                        </a>
                    </div>
                    <div class="stats">
                        <span class="stat-item">
                            <i class="fas fa-users"></i>
                            <span id="totalRecords">{{ nrlm_data|length }}</span> Total Records
                        </span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Location Selection Form -->
        <div class="form-section">
            <h3><i class="fas fa-map-marker-alt"></i> Select Location</h3>
            <div class="location-form">
                <div class="form-row">
                    <div class="form-group">
                        <label><i class="fas fa-map"></i> State</label>
                        <select id="stateSelect" class="form-select">
                            <option value="">Loading states...</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label><i class="fas fa-building"></i> District</label>
                        <select id="districtSelect" class="form-select" disabled>
                            <option value="">Select State First</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label><i class="fas fa-map-marker-alt"></i> Block</label>
                        <select id="blockSelect" class="form-select" disabled>
                            <option value="">Select District First</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label><i class="fas fa-home"></i> Grampanchayat</label>
                        <select id="grampanchayatSelect" class="form-select" disabled>
                            <option value="">Select Block First</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label><i class="fas fa-tree"></i> Village</label>
                        <select id="villageSelect" class="form-select" disabled>
                            <option value="">Select Grampanchayat First</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <button id="fetchDataBtn" class="fetch-btn" disabled>
                            <i class="fas fa-search"></i>
                            Fetch SHG Data
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Results Section -->
        <div id="resultsSection" class="results-section" style="display: none;">
            <h3><i class="fas fa-users"></i> SHG Members</h3>
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>SHG Name</th>
                            <th>Member Name</th>
                            <th>Member Code</th>
                        </tr>
                    </thead>
                    <tbody id="nrlmTableBody">
                        <!-- Data will be populated here -->
                    </tbody>
                </table>
                <div id="noDataMessage" class="no-data-message" style="display: none;">
                    <i class="fas fa-info-circle"></i>
                    No SHG members found for the selected location.
                </div>
            </div>
        </div>

        <!-- Saved NRLM Data Section -->
        <div class="saved-data-section">
            <h3><i class="fas fa-database"></i> Saved NRLM Data</h3>
            <div class="search-container">
                <div class="search-box">
                    <i class="fas fa-search"></i>
                    <input type="text" id="savedSearchInput" placeholder="Search saved data...">
                </div>
            </div>
            <div class="table-container">
                <table class="data-table" id="savedNrlmTable">
                    <thead>
                        <tr>
                            <th>State</th>
                            <th>District</th>
                            <th>Block</th>
                            <th>Grampanchayat</th>
                            <th>Village</th>
                            <th>SHG Name</th>
                            <th>Member Name</th>
                            <th>Member Code</th>
                            <th>Created At</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for record in nrlm_data %}
                        <tr>
                            <td>{{ record[0] or 'N/A' }}</td>
                            <td>{{ record[1] or 'N/A' }}</td>
                            <td>{{ record[2] or 'N/A' }}</td>
                            <td>{{ record[3] or 'N/A' }}</td>
                            <td>{{ record[4] or 'N/A' }}</td>
                            <td>{{ record[5] or 'N/A' }}</td>
                            <td>{{ record[6] or 'N/A' }}</td>
                            <td>{{ record[7] or 'N/A' }}</td>
                            <td>{{ record[8] or 'N/A' }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>'''
    
    content = content.replace(old_content, new_content)
    
    # Write the updated content
    with open('templates/dashboard.html', 'w') as f:
        f.write(content)
    
    print("✅ Fixed dashboard to show NRLM data and added IIA Cbe menu!")

if __name__ == "__main__":
    fix_dashboard_and_add_menu()
