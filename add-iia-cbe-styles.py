import re

def add_iia_cbe_styles():
    """Add comprehensive CSS styles for IIA Cbe page"""
    
    # Read the current template
    with open('templates/iia_cbe.html', 'r') as f:
        content = f.read()
    
    # Replace the existing styles with comprehensive ones
    old_styles = '''<style>
.id-badge {
    background: #e3f2fd;
    color: #1976d2;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.9em;
    font-weight: 500;
}

.type-badge {
    background: #f3e5f5;
    color: #7b1fa2;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.9em;
    font-weight: 500;
}
</style>'''
    
    new_styles = '''<style>
/* Navigation Buttons */
.iia-nav-section {
    margin: 20px 0;
    text-align: center;
}

.nav-buttons {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-bottom: 30px;
}

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
}

.nav-btn:hover {
    background: #6c5ce7;
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(108, 92, 231, 0.3);
}

.nav-btn.active {
    background: #6c5ce7;
    color: white;
    box-shadow: 0 4px 12px rgba(108, 92, 231, 0.3);
}

/* Content Sections */
.content-section {
    background: white;
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    margin-bottom: 30px;
}

.section-header {
    margin-bottom: 30px;
    text-align: center;
}

.section-header h3 {
    color: #2d3436;
    font-size: 24px;
    margin: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
}

/* Office Bearers */
.office-bearers-current h4 {
    color: #6c5ce7;
    font-size: 20px;
    margin-bottom: 20px;
    text-align: center;
    border-bottom: 2px solid #6c5ce7;
    padding-bottom: 10px;
}

.bearers-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.bearer-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
}

.bearer-card:hover {
    transform: translateY(-5px);
}

.bearer-card.chairman {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
}

.bearer-card.vice-chairman {
    background: linear-gradient(135deg, #4834d4 0%, #686de0 100%);
}

.bearer-card.secretary {
    background: linear-gradient(135deg, #00d2d3 0%, #54a0ff 100%);
}

.bearer-card.treasurer {
    background: linear-gradient(135deg, #ff9ff3 0%, #f368e0 100%);
}

.bearer-card.past-chairman {
    background: linear-gradient(135deg, #a55eea 0%, #8b5cf6 100%);
}

.bearer-title {
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 8px;
    opacity: 0.9;
}

.bearer-name {
    font-size: 16px;
    font-weight: 700;
}

/* Executive Members */
.executive-members {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 15px;
    margin-top: 20px;
}

.member-item {
    background: #f8f9fa;
    padding: 12px 16px;
    border-radius: 8px;
    border-left: 4px solid #6c5ce7;
    font-weight: 500;
    color: #2d3436;
    transition: all 0.3s ease;
}

.member-item:hover {
    background: #e9ecef;
    transform: translateX(5px);
}

/* Historical Timeline */
.office-bearers-historical h4 {
    color: #6c5ce7;
    font-size: 20px;
    margin: 30px 0 20px 0;
    text-align: center;
    border-bottom: 2px solid #6c5ce7;
    padding-bottom: 10px;
}

.historical-timeline {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.timeline-item {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 20px;
    border-left: 5px solid #6c5ce7;
    transition: all 0.3s ease;
}

.timeline-item:hover {
    background: #e9ecef;
    transform: translateX(5px);
}

.year {
    font-size: 18px;
    font-weight: 700;
    color: #6c5ce7;
    margin-bottom: 15px;
    text-align: center;
}

.bearers {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 10px;
}

.bearer {
    background: white;
    padding: 10px 15px;
    border-radius: 6px;
    font-weight: 500;
    color: #2d3436;
    border: 1px solid #e9ecef;
}

/* Members Grid */
.members-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 15px;
    margin-top: 20px;
}

.members-grid .member-item {
    background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
    color: white;
    padding: 15px;
    border-radius: 8px;
    text-align: center;
    font-weight: 500;
    transition: all 0.3s ease;
    border: none;
}

.members-grid .member-item:hover {
    background: linear-gradient(135deg, #0984e3 0%, #74b9ff 100%);
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(116, 185, 255, 0.3);
}

/* Responsive Design */
@media (max-width: 768px) {
    .nav-buttons {
        flex-direction: column;
        align-items: center;
    }
    
    .bearers-grid {
        grid-template-columns: 1fr;
    }
    
    .executive-members {
        grid-template-columns: 1fr;
    }
    
    .bearers {
        grid-template-columns: 1fr;
    }
    
    .members-grid {
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    }
}

/* Animation */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.content-section {
    animation: fadeIn 0.6s ease-out;
}
</style>'''
    
    content = content.replace(old_styles, new_styles)
    
    # Write the updated content
    with open('templates/iia_cbe.html', 'w') as f:
        f.write(content)
    
    print("✅ Added comprehensive CSS styles for IIA Cbe page!")

if __name__ == "__main__":
    add_iia_cbe_styles()
