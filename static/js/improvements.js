// Enhanced JavaScript for IN Data page
document.addEventListener('DOMContentLoaded', function() {
    // Add loading states to dropdowns
    function addLoadingState(selectElement) {
        selectElement.classList.add('loading');
        selectElement.disabled = true;
    }
    
    function removeLoadingState(selectElement) {
        selectElement.classList.remove('loading');
        selectElement.disabled = false;
    }
    
    // Add success/error states
    function addSuccessState(selectElement) {
        selectElement.classList.add('success');
        setTimeout(() => selectElement.classList.remove('success'), 2000);
    }
    
    function addErrorState(selectElement) {
        selectElement.classList.add('error');
        setTimeout(() => selectElement.classList.remove('error'), 3000);
    }
    
    // Enhanced form validation
    function validateForm() {
        const stateSelect = document.getElementById('stateSelect');
        const districtSelect = document.getElementById('districtSelect');
        const blockSelect = document.getElementById('blockSelect');
        const grampanchayatSelect = document.getElementById('grampanchayatSelect');
        const villageSelect = document.getElementById('villageSelect');
        const fetchBtn = document.getElementById('fetchDataBtn');
        
        const isComplete = stateSelect.value && districtSelect.value && 
                          blockSelect.value && grampanchayatSelect.value && 
                          villageSelect.value;
        
        fetchBtn.disabled = !isComplete;
        
        if (isComplete) {
            fetchBtn.style.background = 'linear-gradient(135deg, #764ba2, #667eea)';
        } else {
            fetchBtn.style.background = '#ccc';
        }
    }
    
    // Add validation to all selects
    const allSelects = document.querySelectorAll('.form-select');
    allSelects.forEach(select => {
        select.addEventListener('change', validateForm);
    });
    
    // Enhanced error handling
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : type === 'success' ? 'check-circle' : 'info-circle'}"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">&times;</button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    // Add notification styles
    const notificationStyles = document.createElement('style');
    notificationStyles.textContent = `
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            z-index: 10000;
            display: flex;
            align-items: center;
            gap: 10px;
            min-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideIn 0.3s ease;
        }
        
        .notification-success {
            background: #4caf50;
        }
        
        .notification-error {
            background: #f44336;
        }
        
        .notification-info {
            background: #2196f3;
        }
        
        .notification button {
            background: none;
            border: none;
            color: white;
            font-size: 18px;
            cursor: pointer;
            margin-left: auto;
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(notificationStyles);
    
    // Enhanced API calls with better error handling
    window.enhancedFetch = async function(url, options = {}) {
        try {
            const response = await fetch(url, options);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.message || 'Unknown error occurred');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            showNotification(error.message, 'error');
            throw error;
        }
    };
    
    // Add tooltips for better UX
    function addTooltips() {
        const tooltips = {
            'stateSelect': 'Select your state to begin',
            'districtSelect': 'Choose a district from the selected state',
            'blockSelect': 'Select a block within the district',
            'grampanchayatSelect': 'Pick a grampanchayat from the block',
            'villageSelect': 'Choose a village to fetch SHG data',
            'fetchDataBtn': 'Click to fetch SHG member data from NRLM website'
        };
        
        Object.entries(tooltips).forEach(([id, text]) => {
            const element = document.getElementById(id);
            if (element) {
                element.title = text;
            }
        });
    }
    
    addTooltips();
    
    // Add keyboard navigation support
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.target.classList.contains('form-select')) {
            e.target.blur();
        }
    });
    
    // Add auto-save functionality for form state
    function saveFormState() {
        const formData = {
            state: document.getElementById('stateSelect').value,
            district: document.getElementById('districtSelect').value,
            block: document.getElementById('blockSelect').value,
            grampanchayat: document.getElementById('grampanchayatSelect').value,
            village: document.getElementById('villageSelect').value
        };
        
        localStorage.setItem('nrlmFormState', JSON.stringify(formData));
    }
    
    function loadFormState() {
        const savedState = localStorage.getItem('nrlmFormState');
        if (savedState) {
            try {
                const formData = JSON.parse(savedState);
                // Restore form state if needed
                console.log('Form state loaded:', formData);
            } catch (e) {
                console.error('Error loading form state:', e);
            }
        }
    }
    
    // Save form state on changes
    allSelects.forEach(select => {
        select.addEventListener('change', saveFormState);
    });
    
    loadFormState();
    
    // Add progress indicator
    function updateProgress() {
        const selects = document.querySelectorAll('.form-select');
        const completed = Array.from(selects).filter(select => select.value).length;
        const progress = (completed / selects.length) * 100;
        
        // You can add a progress bar here if needed
        console.log(`Form completion: ${progress.toFixed(0)}%`);
    }
    
    allSelects.forEach(select => {
        select.addEventListener('change', updateProgress);
    });
});
