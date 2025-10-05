// Neo4j Learning Platform - Main JavaScript

// Global utilities
window.LearningPlatform = {
    
    // Show toast notifications
    showToast: function(message, type = 'info') {
        const toastContainer = this.getToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove from DOM after hiding
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },
    
    getToastContainer: function() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        return container;
    },
    
    // Loading states
    setLoading: function(element, loading = true, text = 'Loading...') {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        
        if (!element) return;
        
        if (loading) {
            element.disabled = true;
            element.dataset.originalText = element.innerHTML;
            element.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                ${text}
            `;
        } else {
            element.disabled = false;
            element.innerHTML = element.dataset.originalText || element.innerHTML;
        }
    },
    
    // API helpers
    apiCall: async function(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'API request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API call failed:', error);
            this.showToast(error.message, 'danger');
            throw error;
        }
    },
    
    // Concept completion
    markConceptComplete: async function(conceptId, callback) {
        try {
            const data = await this.apiCall(`/api/concept/${conceptId}/complete`, {
                method: 'POST'
            });
            
            if (data.success) {
                this.showToast('Concept marked as complete!', 'success');
                if (callback) callback();
            }
        } catch (error) {
            // Error already handled in apiCall
        }
    },
    
    // Format helpers
    formatDuration: function(minutes) {
        if (minutes < 60) {
            return `${minutes} min`;
        }
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
    },
    
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },
    
    // Initialize page
    init: function() {
        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Initialize popovers  
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
        
        // Add fade-in animation to cards
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('fade-in-up');
        });
        
        console.log('Neo4j Learning Platform initialized');
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    LearningPlatform.init();
});

// Global functions for backward compatibility
function showToast(message, type) {
    LearningPlatform.showToast(message, type);
}

function markComplete(conceptId) {
    const button = event.target;
    LearningPlatform.setLoading(button, true, 'Updating...');
    
    LearningPlatform.markConceptComplete(conceptId, () => {
        // Refresh page to show updated state
        location.reload();
    }).finally(() => {
        LearningPlatform.setLoading(button, false);
    });
}

// Handle window resize for graph
let resizeTimeout;
window.addEventListener('resize', function() {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(function() {
        if (typeof renderGraph === 'function' && window.graphData) {
            console.log('Resizing graph...');
            renderGraph();
        }
    }, 250);
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Alt + G for graph view
    if (e.altKey && e.key === 'g') {
        e.preventDefault();
        window.location.href = '/graph';
    }
    
    // Alt + D for dashboard
    if (e.altKey && e.key === 'd') {
        e.preventDefault();
        window.location.href = '/';
    }
    
    // Alt + C for concepts list
    if (e.altKey && e.key === 'c') {
        e.preventDefault();
        window.location.href = '/course/list';
    }
});