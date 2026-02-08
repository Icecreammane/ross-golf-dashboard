// Revenue Dashboard JavaScript
// Handles data fetching, UI updates, and auto-refresh

class RevenueDashboard {
    constructor() {
        this.refreshInterval = 5 * 60 * 1000; // 5 minutes
        this.currentMetrics = null;
        this.autoRefreshTimer = null;
        
        this.init();
    }

    init() {
        console.log('Revenue Dashboard initializing...');
        
        // Initial data load
        this.fetchMetrics();
        
        // Set up auto-refresh
        this.startAutoRefresh();
        
        // Set up manual refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.manualRefresh();
        });
        
        // Update status
        this.updateStatus('Connected');
    }

    async fetchMetrics() {
        try {
            const response = await fetch('/api/metrics');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const metrics = await response.json();
            this.currentMetrics = metrics;
            this.updateUI(metrics);
            this.updateStatus('Connected');
            
            console.log('Metrics updated:', metrics);
            
        } catch (error) {
            console.error('Error fetching metrics:', error);
            this.updateStatus('Error');
        }
    }

    async manualRefresh() {
        const btn = document.getElementById('refreshBtn');
        btn.classList.add('loading');
        btn.textContent = '⏳ Refreshing...';
        
        try {
            const response = await fetch('/api/refresh', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const metrics = await response.json();
            this.currentMetrics = metrics;
            this.updateUI(metrics);
            this.updateStatus('Connected');
            
            // Celebrate if there's new revenue
            if (metrics.daily_revenue > 0) {
                this.celebrate();
            }
            
            console.log('Manual refresh complete:', metrics);
            
        } catch (error) {
            console.error('Error refreshing:', error);
            this.updateStatus('Error');
        } finally {
            btn.classList.remove('loading');
            btn.textContent = '🔄 Refresh';
        }
    }

    updateUI(metrics) {
        // Update MRR and progress
        this.animateNumber('mrrAmount', metrics.mrr);
        
        const progressPercent = Math.min(100, metrics.progress_percent);
        document.getElementById('progressBar').style.width = `${progressPercent}%`;
        document.getElementById('progressPercent').textContent = `${progressPercent.toFixed(1)}%`;
        
        // Update days to goal
        const daysToGoalEl = document.getElementById('daysToGoal');
        if (metrics.days_to_goal !== null && metrics.days_to_goal > 0) {
            daysToGoalEl.textContent = `${metrics.days_to_goal} days`;
        } else if (metrics.mrr >= 500) {
            daysToGoalEl.textContent = '🎉 Goal Reached!';
            daysToGoalEl.style.color = '#48bb78';
        } else {
            daysToGoalEl.textContent = '—';
        }
        
        // Update projected run rate
        this.animateNumber('runRate', metrics.projected_run_rate);
        
        // Update big metrics
        this.animateNumber('dailyRevenue', metrics.daily_revenue);
        this.animateNumber('totalRevenue', metrics.total_revenue);
        document.getElementById('subscriptionCount').textContent = metrics.subscription_count;
        document.getElementById('coachingCount').textContent = metrics.coaching_inquiries_count;
        
        // Update last updated time
        if (metrics.last_updated) {
            const lastUpdated = new Date(metrics.last_updated);
            document.getElementById('lastUpdated').textContent = 
                `Last updated: ${this.formatTime(lastUpdated)}`;
        }
        
        // Update motivational message
        this.updateMotivation(metrics);
    }

    animateNumber(elementId, targetValue) {
        const element = document.getElementById(elementId);
        const currentValue = parseFloat(element.textContent.replace(/,/g, '')) || 0;
        
        // Only animate if value changed
        if (currentValue === targetValue) {
            return;
        }
        
        const duration = 1000; // 1 second
        const steps = 60;
        const increment = (targetValue - currentValue) / steps;
        let current = currentValue;
        let step = 0;
        
        const timer = setInterval(() => {
            step++;
            current += increment;
            
            if (step >= steps) {
                current = targetValue;
                clearInterval(timer);
            }
            
            element.textContent = this.formatNumber(current);
        }, duration / steps);
    }

    formatNumber(num) {
        return num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    formatTime(date) {
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffMins < 1) {
            return 'just now';
        } else if (diffMins < 60) {
            return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
        } else {
            const diffHours = Math.floor(diffMins / 60);
            if (diffHours < 24) {
                return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
            } else {
                return date.toLocaleString();
            }
        }
    }

    updateMotivation(metrics) {
        const motivationEl = document.getElementById('motivationText');
        let message = '';
        
        const progressPercent = metrics.progress_percent;
        
        if (progressPercent >= 100) {
            message = '🎉 GOAL ACHIEVED! You hit $500 MRR! Time to set a bigger goal! 🚀';
        } else if (progressPercent >= 75) {
            message = '🔥 SO CLOSE! You\'re in the home stretch! Keep pushing! 💪';
        } else if (progressPercent >= 50) {
            message = '💪 Halfway there! Momentum is building! Let\'s go! 🚀';
        } else if (progressPercent >= 25) {
            message = '📈 Great progress! Every sale counts! Stay consistent! 💯';
        } else if (progressPercent > 0) {
            message = '🌱 The journey begins! First dollars are the hardest! Keep building! 🏗️';
        } else {
            message = '🚀 Ready to launch! Your first sale is waiting! Let\'s build! 💡';
        }
        
        // Add daily revenue celebration
        if (metrics.daily_revenue > 0) {
            message += ` +$${metrics.daily_revenue.toFixed(2)} today! 💰`;
        }
        
        motivationEl.textContent = message;
    }

    updateStatus(status) {
        const statusEl = document.querySelector('.status-text');
        const dotEl = document.querySelector('.status-dot');
        
        statusEl.textContent = status;
        
        if (status === 'Connected') {
            dotEl.style.background = '#48bb78';
        } else if (status === 'Error') {
            dotEl.style.background = '#f56565';
        } else {
            dotEl.style.background = '#ed8936';
        }
    }

    celebrate() {
        // Add celebration animation
        const container = document.querySelector('.container');
        container.classList.add('celebrate');
        
        setTimeout(() => {
            container.classList.remove('celebrate');
        }, 500);
        
        console.log('🎉 New revenue!');
    }

    startAutoRefresh() {
        this.autoRefreshTimer = setInterval(() => {
            console.log('Auto-refreshing metrics...');
            this.fetchMetrics();
        }, this.refreshInterval);
        
        console.log(`Auto-refresh enabled (every ${this.refreshInterval / 1000 / 60} minutes)`);
    }

    stopAutoRefresh() {
        if (this.autoRefreshTimer) {
            clearInterval(this.autoRefreshTimer);
            this.autoRefreshTimer = null;
            console.log('Auto-refresh stopped');
        }
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new RevenueDashboard();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.log('Page hidden, stopping auto-refresh');
        window.dashboard.stopAutoRefresh();
    } else {
        console.log('Page visible, resuming auto-refresh');
        window.dashboard.fetchMetrics();
        window.dashboard.startAutoRefresh();
    }
});
