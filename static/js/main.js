// Main JavaScript for Arlo GOC Onboarding Site

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Highlight active navigation link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.style.color = 'var(--arlo-primary)';
            link.style.borderBottomColor = 'var(--arlo-primary)';
        }
    });

    // Add fade-in animation to cards
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '0';
                entry.target.style.transform = 'translateY(20px)';
                entry.target.style.transition = 'opacity 0.5s, transform 0.5s';
                
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, 100);
                
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });

    document.querySelectorAll('.card, .quick-link-card, .training-card').forEach(card => {
        observer.observe(card);
    });

    // Print functionality
    const printButton = document.querySelector('[data-print]');
    if (printButton) {
        printButton.addEventListener('click', () => {
            window.print();
        });
    }

    // Tool access status tracking (could be extended with backend)
    const toolLinks = document.querySelectorAll('.tool-section .btn-primary');
    toolLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Track tool access (could send to analytics)
            console.log('Tool accessed:', this.textContent);
        });
    });

    // Training module progress tracking
    const trainingCards = document.querySelectorAll('.training-card');
    trainingCards.forEach(card => {
        card.addEventListener('click', function() {
            // Could track which training modules are being viewed
            console.log('Training module accessed');
        });
    });

    // Add tooltip functionality
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.getAttribute('data-tooltip');
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.position = 'absolute';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        });
        
        element.addEventListener('mouseleave', function() {
            const tooltip = document.querySelector('.tooltip');
            if (tooltip) {
                tooltip.remove();
            }
        });
    });

    // Mobile menu toggle (if needed)
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }

    // Session timer for onboarding progress
    if (!sessionStorage.getItem('onboarding_start_time')) {
        sessionStorage.setItem('onboarding_start_time', new Date().toISOString());
    }

    // Add keyboard navigation
    document.addEventListener('keydown', function(e) {
        // Escape key to close modals/overlays
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.active');
            modals.forEach(modal => modal.classList.remove('active'));
        }
    });

    // Copy code snippets
    const codeBlocks = document.querySelectorAll('code');
    codeBlocks.forEach(block => {
        block.addEventListener('click', function() {
            navigator.clipboard.writeText(this.textContent).then(() => {
                const tooltip = document.createElement('span');
                tooltip.textContent = 'Copied!';
                tooltip.className = 'copy-tooltip';
                this.appendChild(tooltip);
                setTimeout(() => tooltip.remove(), 2000);
            });
        });
    });
});

// Utility function to format dates
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Utility function to calculate days since start
function getDaysSinceOnboardingStart() {
    const startTime = sessionStorage.getItem('onboarding_start_time');
    if (!startTime) return 0;
    
    const start = new Date(startTime);
    const now = new Date();
    const diffTime = Math.abs(now - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
}

// Export functions for use in other scripts
window.ArloOnboarding = {
    formatDate,
    getDaysSinceOnboardingStart
};
