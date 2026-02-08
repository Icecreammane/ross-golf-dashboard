/**
 * Landing Page JavaScript
 * Email capture, CTA tracking, smooth scrolling
 */

// Smooth scroll to section
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Scroll to CTA section
function scrollToCTA() {
    scrollToSection('cta');
}

// Handle plan selection
function selectPlan(plan) {
    console.log(`Plan selected: ${plan}`);
    
    // Track conversion event
    trackEvent('plan_selected', { plan: plan });
    
    // Redirect to signup/checkout
    if (plan === 'free') {
        window.location.href = '/signup?plan=free';
    } else if (plan === 'pro') {
        window.location.href = '/signup?plan=pro';
    }
}

// Handle contact sales
function contactSales() {
    console.log('Contact sales clicked');
    trackEvent('contact_sales_clicked');
    
    // Open contact form or email
    window.location.href = 'mailto:sales@yourdomain.com?subject=Enterprise Plan Inquiry';
}

// Email signup form handler
document.addEventListener('DOMContentLoaded', () => {
    const signupForm = document.getElementById('signup-form');
    const emailInput = document.getElementById('email-input');
    
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = emailInput.value.trim();
            
            if (!isValidEmail(email)) {
                showNotification('Please enter a valid email address', 'error');
                return;
            }
            
            // Track signup attempt
            trackEvent('signup_started', { email: email });
            
            // Show loading state
            const submitBtn = signupForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Processing...';
            submitBtn.disabled = true;
            
            try {
                // Send email to your backend
                const response = await fetch('/api/signup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email: email })
                });
                
                if (response.ok) {
                    // Success
                    trackEvent('signup_completed', { email: email });
                    showNotification('Success! Check your email to get started.', 'success');
                    emailInput.value = '';
                    
                    // Redirect to welcome page
                    setTimeout(() => {
                        window.location.href = '/welcome?email=' + encodeURIComponent(email);
                    }, 2000);
                } else {
                    throw new Error('Signup failed');
                }
            } catch (error) {
                console.error('Signup error:', error);
                trackEvent('signup_failed', { email: email, error: error.message });
                showNotification('Something went wrong. Please try again.', 'error');
            } finally {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
    }
});

// Email validation
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Show notification
function showNotification(message, type = 'info') {
    // Remove existing notification
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        border-radius: 8px;
        font-weight: 500;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    `;
    
    if (type === 'success') {
        notification.style.background = '#10b981';
        notification.style.color = '#ffffff';
    } else if (type === 'error') {
        notification.style.background = '#ef4444';
        notification.style.color = '#ffffff';
    } else {
        notification.style.background = '#3b82f6';
        notification.style.color = '#ffffff';
    }
    
    // Add animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Analytics / Event Tracking
function trackEvent(eventName, properties = {}) {
    console.log('Event tracked:', eventName, properties);
    
    // Google Analytics (gtag.js)
    if (typeof gtag !== 'undefined') {
        gtag('event', eventName, properties);
    }
    
    // Plausible Analytics
    if (typeof plausible !== 'undefined') {
        plausible(eventName, { props: properties });
    }
    
    // Facebook Pixel
    if (typeof fbq !== 'undefined') {
        fbq('trackCustom', eventName, properties);
    }
    
    // Your custom analytics endpoint
    fetch('/api/track', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            event: eventName,
            properties: properties,
            timestamp: Date.now(),
            url: window.location.href,
            referrer: document.referrer
        })
    }).catch(err => console.error('Tracking error:', err));
}

// Track page view on load
window.addEventListener('load', () => {
    trackEvent('page_view', {
        page: window.location.pathname,
        title: document.title
    });
});

// Track scroll depth
let maxScrollDepth = 0;
window.addEventListener('scroll', () => {
    const scrollPercent = Math.round(
        (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100
    );
    
    if (scrollPercent > maxScrollDepth) {
        maxScrollDepth = scrollPercent;
        
        // Track milestones
        if (maxScrollDepth >= 25 && maxScrollDepth < 50) {
            trackEvent('scroll_depth', { depth: '25%' });
        } else if (maxScrollDepth >= 50 && maxScrollDepth < 75) {
            trackEvent('scroll_depth', { depth: '50%' });
        } else if (maxScrollDepth >= 75 && maxScrollDepth < 100) {
            trackEvent('scroll_depth', { depth: '75%' });
        } else if (maxScrollDepth >= 100) {
            trackEvent('scroll_depth', { depth: '100%' });
        }
    }
});

// Track CTA clicks
document.addEventListener('click', (e) => {
    if (e.target.matches('.btn-primary') || e.target.closest('.btn-primary')) {
        const btnText = e.target.textContent || e.target.closest('.btn-primary').textContent;
        trackEvent('cta_clicked', {
            button_text: btnText.trim(),
            button_location: e.target.closest('section')?.id || 'unknown'
        });
    }
});

// Track time on page
let timeOnPage = 0;
setInterval(() => {
    timeOnPage += 1;
    
    // Track milestones (30s, 1m, 2m, 5m)
    if (timeOnPage === 30 || timeOnPage === 60 || timeOnPage === 120 || timeOnPage === 300) {
        trackEvent('time_on_page', { seconds: timeOnPage });
    }
}, 1000);

// Track exit intent (when user moves mouse to close tab)
document.addEventListener('mouseleave', (e) => {
    if (e.clientY < 0) {
        trackEvent('exit_intent');
        
        // Optional: Show exit intent popup
        // showExitIntentPopup();
    }
});

// Lazy load images (if you add them)
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });
    
    document.querySelectorAll('img.lazy').forEach(img => imageObserver.observe(img));
}

// Add active state to nav links based on scroll position
window.addEventListener('scroll', () => {
    const sections = document.querySelectorAll('section[id]');
    const scrollPos = window.scrollY + 100;
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.offsetHeight;
        const sectionId = section.getAttribute('id');
        
        if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
            document.querySelectorAll('.nav-menu a').forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${sectionId}`) {
                    link.classList.add('active');
                }
            });
        }
    });
});

// Add CSS for active nav link
const style = document.createElement('style');
style.textContent = `
    .nav-menu a.active {
        color: var(--color-primary) !important;
    }
`;
document.head.appendChild(style);

// Console easter egg (optional fun touch)
console.log(
    '%cLooking for a job? 👀',
    'font-size: 20px; font-weight: bold; color: #5469d4;'
);
console.log(
    '%cWe\'re hiring! Email careers@yourdomain.com',
    'font-size: 14px; color: #6b7280;'
);
