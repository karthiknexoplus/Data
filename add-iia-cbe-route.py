import re

def add_iia_cbe_route():
    """Add IIA Cbe route to Flask app"""
    
    # Read the current app.py
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Add the IIA Cbe route before the existing routes
    iia_cbe_route = '''@app.route('/iia-cbe')
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
    return render_template('iia_cbe.html', iia_data=iia_data)

'''
    
    # Insert the new route before the existing routes
    content = content.replace('@app.route(\'/in-data\')', iia_cbe_route + '@app.route(\'/in-data\')')
    
    # Write the updated content
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("✅ Added IIA Cbe route to Flask app!")

if __name__ == "__main__":
    add_iia_cbe_route()
