// Network Automation Platform - Main Application JavaScript

class NetworkApp {
    constructor() {
        this.initializeApp();
    }

    initializeApp() {
        this.setupAuthenticationCheck();
        this.setupNavigationHighlighting();
        this.setupToastSystem();
        this.initializeLucideIcons();
    }

    setupAuthenticationCheck() {
        // Check if user is authenticated for protected pages
        const token = localStorage.getItem('access_token');
        const publicPages = ['/login'];
        const currentPath = window.location.pathname;

        if (!token && !publicPages.includes(currentPath)) {  
            // Redirect to login if not authenticated
            // window.location.href = '/login';
        }
    }

    setupNavigationHighlighting() {
        // Highlight active navigation item
        const navLinks = document.querySelectorAll('.nav-link');
        const currentPath = window.location.pathname;

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    }

    setupToastSystem() {
        // Create toast container if it doesn't exist
        if (!document.getElementById('toast-container')) {
            const toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
    }

    initializeLucideIcons() {
        // Initialize Lucide icons if available
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    // Utility method to show toast notifications
    static showToast(message, type = 'info', duration = 5000) {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) return;

        const toastId = 'toast-' + Date.now();
        const iconMap = {
            success: 'check-circle',
            error: 'x-circle',
            warning: 'alert-triangle',
            info: 'info'
        };

        const colorMap = {
            success: 'text-bg-success',
            error: 'text-bg-danger',
            warning: 'text-bg-warning',
            info: 'text-bg-primary'
        };

        const toastHtml = `
            <div id="${toastId}" class="toast ${colorMap[type]}" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header ${colorMap[type]}">
                    <i data-lucide="${iconMap[type]}" class="me-2"></i>
                    <strong class="me-auto">${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHtml);

        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: duration
        });

        toast.show();

        // Initialize Lucide icons for the new toast
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }

        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    // API helper methods
    static async apiCall(endpoint, options = {}) {
        const token = localStorage.getItem('access_token');
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` })
            }
        };

        const finalOptions = { ...defaultOptions, ...options };

        try {
            const response = await fetch(endpoint, finalOptions);
            
            if (response.status === 401) {
                localStorage.removeItem('access_token');
                window.location.href = '/login';
                return null;
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API call error:', error);
            NetworkApp.showToast('Network error occurred', 'error');
            throw error;
        }
    }

    // Authentication helpers
    static async logout() {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
    }

    static isAuthenticated() {
        return !!localStorage.getItem('access_token');
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.NetworkApp = new NetworkApp();
    
    // Make static methods available globally
    window.showToast = NetworkApp.showToast;
    window.apiCall = NetworkApp.apiCall;
    
    console.log('Network Automation Platform initialized');
});

// Global error handler for unhandled promise rejections
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    NetworkApp.showToast('An unexpected error occurred', 'error');
});

// Global error handler for JavaScript errors
window.addEventListener('error', function(event) {
    console.error('JavaScript error:', event.error);
    // Don't show toast for every JS error to avoid spam
});

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NetworkApp;
}
