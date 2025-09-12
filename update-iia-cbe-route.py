import re

def update_iia_cbe_route():
    """Update IIA Cbe route to remove unused data"""
    
    # Read the current app.py
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Find and replace the iia_cbe route
    old_route = '''@app.route('/iia-cbe')
def iia_cbe():
    """IIA Coimbatore data page"""
    # Sample IIA Coimbatore data
    iia_data = [
        (1, 'IIA001', 'Coimbatore Industrial Association', 'Coimbatore', 'Industrial', '1985', '0422-1234567'),
        (2, 'IIA002', 'Tirupur Exporters Association', 'Tirupur', 'Export', '1990', '0421-2345678'),
        (3, 'IIA003', 'Erode Textile Association', 'Erode', 'Textile', '1988', '0424-3456789'),
        (4, 'IIA004', 'Salem Engineering Association', 'Salem', 'Engineering', '1992', '0427-4567890'),
        (5, 'IIA005', 'Namakkal Poultry Association', 'Namakkal', 'Poultry', '1995', '04286-5678901')
    ]
    return render_template('iia_cbe.html', iia_data=iia_data)'''
    
    new_route = '''@app.route('/iia-cbe')
def iia_cbe():
    """IIA Coimbatore data page"""
    return render_template('iia_cbe.html')'''
    
    content = content.replace(old_route, new_route)
    
    # Write the updated content
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("✅ Updated IIA Cbe route!")

if __name__ == "__main__":
    update_iia_cbe_route()
