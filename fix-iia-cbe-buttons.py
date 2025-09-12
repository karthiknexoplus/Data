import re

def fix_iia_cbe_buttons():
    """Remove industrial associations text and fix button functionality"""
    
    # Read the current template
    with open('templates/iia_cbe.html', 'r') as f:
        content = f.read()
    
    # Remove the "5 Industrial Associations" text
    old_stats = '''                    <div class="stats">
                        <span class="stat-item">
                            <i class="fas fa-building"></i>
                            <span>{{ iia_data|length }}</span> Industrial Associations
                        </span>
                    </div>'''
    
    content = content.replace(old_stats, '')
    
    # Update the JavaScript to make buttons more responsive
    old_js = '''    <script>
    function showOfficeBearers() {
        document.getElementById('officeBearersSection').style.display = 'block';
        document.getElementById('membersSection').style.display = 'none';
        document.getElementById('officeBearersBtn').classList.add('active');
        document.getElementById('membersBtn').classList.remove('active');
    }
    
    function showMembers() {
        document.getElementById('officeBearersSection').style.display = 'none';
        document.getElementById('membersSection').style.display = 'block';
        document.getElementById('membersBtn').classList.add('active');
        document.getElementById('officeBearersBtn').classList.remove('active');
    }
    </script>'''
    
    new_js = '''    <script>
    function showOfficeBearers() {
        console.log('Showing Office Bearers...');
        document.getElementById('officeBearersSection').style.display = 'block';
        document.getElementById('membersSection').style.display = 'none';
        document.getElementById('officeBearersBtn').classList.add('active');
        document.getElementById('membersBtn').classList.remove('active');
        
        // Scroll to the content
        document.getElementById('officeBearersSection').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }
    
    function showMembers() {
        console.log('Showing Members...');
        document.getElementById('officeBearersSection').style.display = 'none';
        document.getElementById('membersSection').style.display = 'block';
        document.getElementById('membersBtn').classList.add('active');
        document.getElementById('officeBearersBtn').classList.remove('active');
        
        // Scroll to the content
        document.getElementById('membersSection').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }
    
    // Add click event listeners for better responsiveness
    document.addEventListener('DOMContentLoaded', function() {
        const officeBearersBtn = document.getElementById('officeBearersBtn');
        const membersBtn = document.getElementById('membersBtn');
        
        if (officeBearersBtn) {
            officeBearersBtn.addEventListener('click', showOfficeBearers);
        }
        
        if (membersBtn) {
            membersBtn.addEventListener('click', showMembers);
        }
        
        // Initialize with Office Bearers shown
        showOfficeBearers();
    });
    </script>'''
    
    content = content.replace(old_js, new_js)
    
    # Add better button styling for clickability
    button_styles = '''
/* Enhanced Button Styles */
.nav-btn {
    padding: 12px 24px;
    border: 2px solid #6c5ce7;
    background: white;
    color: #6c5ce7;
    border-radius: 8px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 600;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 8px;
    user-select: none;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
}

.nav-btn:hover {
    background: #6c5ce7;
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(108, 92, 231, 0.3);
}

.nav-btn:active {
    transform: translateY(0);
    box-shadow: 0 2px 6px rgba(108, 92, 231, 0.3);
}

.nav-btn.active {
    background: #6c5ce7;
    color: white;
    box-shadow: 0 4px 12px rgba(108, 92, 231, 0.3);
}

.nav-btn:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.2);
}'''
    
    # Add the enhanced button styles to the existing styles
    content = content.replace('/* Navigation Buttons */', '/* Navigation Buttons */' + button_styles)
    
    # Write the updated content
    with open('templates/iia_cbe.html', 'w') as f:
        f.write(content)
    
    print("✅ Fixed IIA Cbe buttons and removed industrial associations text!")

if __name__ == "__main__":
    fix_iia_cbe_buttons()
