# Fix the clickable functionality by updating the template
import re

# Read the current template
with open('templates/cbe_wards.html', 'r') as f:
    content = f.read()

# Find the direction section and fix the onclick
old_section = '''<div class="direction-section clickable-direction" 
                                 style="background: white; padding: 15px; border-radius: 6px; border-left: 4px solid #764ba2; cursor: pointer; transition: all 0.3s ease;"
                                 onclick="showMapModal('{{ direction }}', '{{ ward.ward_name }}', '{{ ward.ward_number }}', {{ descriptions|tojson }})">'''

new_section = '''<div class="direction-section clickable-direction" 
                                 style="background: white; padding: 15px; border-radius: 6px; border-left: 4px solid #764ba2; cursor: pointer; transition: all 0.3s ease;"
                                 data-direction="{{ direction }}"
                                 data-ward="{{ ward.ward_name }}"
                                 data-ward-number="{{ ward.ward_number }}"
                                 data-descriptions="{{ descriptions|join('|') }}">'''

# Replace the section
new_content = content.replace(old_section, new_section)

# Write the updated content
with open('templates/cbe_wards.html', 'w') as f:
    f.write(new_content)

print("Fixed clickable functionality!")
