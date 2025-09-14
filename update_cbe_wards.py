# Update the CBE wards route to add search functionality
import re

# Read the current app.py file
with open('app.py', 'r') as f:
    content = f.read()

# Find the cbe_wards function and replace it
old_function = '''@app.route("/cbe-wards")
@login_required
def cbe_wards():
    """Display Coimbatore ward data with pagination"""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = 20
        
        # Load CBE ward data
        ward_data = load_cbe_ward_data()
        
        # Calculate pagination
        total_records = len(ward_data)
        total_pages = (total_records + per_page - 1) // per_page
        
        # Get current page data
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        current_page_data = ward_data[start_idx:end_idx]
        
        return render_template("cbe_wards.html", 
                             ward_data=current_page_data, 
                             username=session.get("username"),
                             current_page=page,
                             total_pages=total_pages,
                             total_records=total_records,
                             per_page=per_page)
    except Exception as e:
        flash(f"Error loading CBE ward data: {str(e)}", "error")
        return render_template("cbe_wards.html", 
                             ward_data=[], 
                             username=session.get("username"),
                             current_page=1,
                             total_pages=1,
                             total_records=0,
                             per_page=20)'''

new_function = '''@app.route("/cbe-wards")
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
                             search_query="")'''

# Replace the function
new_content = content.replace(old_function, new_function)

# Write the updated content
with open('app.py', 'w') as f:
    f.write(new_content)

print("Updated CBE wards route with search functionality!")
