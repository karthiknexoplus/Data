# Read the dashboard template
with open('templates/dashboard.html', 'r') as f:
    content = f.read()

# Find the COZCENA menu item and add SR Office after it
sr_menu_item = '''            <li class="nav-item">
                <a href="{{ url_for('sr_office') }}">
                    <i class="fas fa-landmark"></i>
                    <span>SR Office</span>
                </a>
            </li>'''

# Insert after COZCENA
cozcena_pattern = '''            <li class="nav-item">
                <a href="{{ url_for('cozcena') }}">
                    <i class="fas fa-building"></i>
                    <span>COZCENA</span>
                </a>
            </li>'''

if cozcena_pattern in content:
    new_content = content.replace(cozcena_pattern, cozcena_pattern + '\n' + sr_menu_item)
    
    with open('templates/dashboard.html', 'w') as f:
        f.write(new_content)
    
    print("SR Office menu item added successfully!")
else:
    print("COZCENA pattern not found")
