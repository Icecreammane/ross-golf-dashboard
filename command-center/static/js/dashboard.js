// Master Command Center - Dashboard JavaScript

// Configuration
const REFRESH_INTERVAL = 10000; // 10 seconds
const API_BASE = '/api';

// State
let searchTimeout = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Command Center initializing...');
    
    // Initial load
    loadAllData();
    
    // Set up auto-refresh
    setInterval(loadAllData, REFRESH_INTERVAL);
    
    // Set up search
    setupSearch();
    
    console.log('✅ Command Center ready!');
});

// Load all dashboard data
async function loadAllData() {
    updateTimestamp();
    await Promise.all([
        loadServices(),
        loadFiles(),
        loadActivity()
    ]);
}

// Update last updated timestamp
function updateTimestamp() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('last-updated').textContent = timeStr;
}

// Load services status
async function loadServices() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const services = await response.json();
        
        const container = document.getElementById('services-list');
        container.innerHTML = '';
        
        services.forEach(service => {
            const item = createServiceItem(service);
            container.appendChild(item);
        });
    } catch (error) {
        console.error('Error loading services:', error);
        document.getElementById('services-list').innerHTML = 
            '<div class="error">Failed to load services</div>';
    }
}

// Create service item element
function createServiceItem(service) {
    const div = document.createElement('div');
    div.className = 'service-item';
    
    const statusClass = service.status.toLowerCase();
    const statusEmoji = getStatusEmoji(service.status);
    
    let content = `
        <div class="service-name">${service.name}</div>
        <div class="service-status">
            <span class="status-indicator ${statusClass}"></span>
            <span class="status-text">${statusEmoji} ${service.status}</span>
    `;
    
    if (service.type === 'service' && service.url && service.status === 'running') {
        content += `<a href="${service.url}" target="_blank" class="service-link">Open →</a>`;
    } else if (service.type === 'file' && service.time_ago) {
        content += `<span class="service-link">${service.time_ago}</span>`;
    }
    
    content += '</div>';
    div.innerHTML = content;
    
    return div;
}

// Get status emoji
function getStatusEmoji(status) {
    const emojiMap = {
        'running': '✅',
        'down': '❌',
        'available': '✅',
        'missing': '⚠️',
        'building': '🔨'
    };
    return emojiMap[status.toLowerCase()] || '❓';
}

// Load key files
async function loadFiles() {
    try {
        const response = await fetch(`${API_BASE}/files`);
        const files = await response.json();
        
        const container = document.getElementById('files-list');
        container.innerHTML = '';
        
        files.forEach(file => {
            const item = createFileItem(file);
            container.appendChild(item);
        });
    } catch (error) {
        console.error('Error loading files:', error);
        document.getElementById('files-list').innerHTML = 
            '<div class="error">Failed to load files</div>';
    }
}

// Create file item element
function createFileItem(file) {
    const div = document.createElement('div');
    div.className = 'file-item';
    div.onclick = () => openFile(file.path);
    
    div.innerHTML = `
        <div>
            <div class="file-name">${file.name}</div>
            <span class="file-category">${file.category}</span>
        </div>
        <div class="file-meta">
            ${file.exists ? `
                <span>${file.time_ago}</span>
                <span>${file.modified}</span>
            ` : '<span style="color: var(--warning)">Missing</span>'}
        </div>
    `;
    
    return div;
}

// Load recent activity
async function loadActivity() {
    try {
        const response = await fetch(`${API_BASE}/activity`);
        const data = await response.json();
        
        // Activity feed
        const activityContainer = document.getElementById('activity-feed');
        activityContainer.innerHTML = '';
        
        // Add builds
        if (data.builds && data.builds.length > 0) {
            data.builds.slice(0, 5).forEach(build => {
                const item = createActivityItem('build', build.date, build.description);
                activityContainer.appendChild(item);
            });
        }
        
        // Add cost summary
        if (data.costs && data.costs.today > 0) {
            const costMsg = `Today's costs: $${data.costs.today.toFixed(2)}`;
            const item = createActivityItem('cost', 'Today', costMsg);
            activityContainer.appendChild(item);
        }
        
        // Add calendar events
        if (data.calendar && data.calendar.length > 0) {
            data.calendar.forEach(event => {
                const msg = `${event.time}: ${event.event}`;
                const item = createActivityItem('calendar', 'Today', msg);
                activityContainer.appendChild(item);
            });
        }
        
        if (activityContainer.children.length === 0) {
            activityContainer.innerHTML = '<div class="loading">No recent activity</div>';
        }
        
        // Health alerts
        const healthContainer = document.getElementById('health-alerts');
        healthContainer.innerHTML = '';
        
        if (data.alerts && data.alerts.length > 0) {
            data.alerts.forEach(alert => {
                const item = createHealthAlert(alert);
                healthContainer.appendChild(item);
            });
        } else {
            healthContainer.innerHTML = `
                <div class="health-alert success">
                    <span>✅</span>
                    <span>All systems operational</span>
                </div>
            `;
        }
        
    } catch (error) {
        console.error('Error loading activity:', error);
        document.getElementById('activity-feed').innerHTML = 
            '<div class="error">Failed to load activity</div>';
    }
}

// Create activity item element
function createActivityItem(type, date, description) {
    const div = document.createElement('div');
    div.className = `activity-item ${type}`;
    
    div.innerHTML = `
        <div class="activity-date">${date}</div>
        <div class="activity-description">${description}</div>
    `;
    
    return div;
}

// Create health alert element
function createHealthAlert(alert) {
    const div = document.createElement('div');
    div.className = `health-alert ${alert.level}`;
    
    const emoji = alert.level === 'warning' ? '⚠️' : 'ℹ️';
    
    div.innerHTML = `
        <span>${emoji}</span>
        <span>${alert.message}</span>
    `;
    
    return div;
}

// Search functionality
function setupSearch() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        
        clearTimeout(searchTimeout);
        
        if (query.length < 2) {
            searchResults.classList.remove('active');
            return;
        }
        
        searchTimeout = setTimeout(() => performSearch(query), 300);
    });
    
    // Close search results when clicking outside
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.remove('active');
        }
    });
}

// Perform search
async function performSearch(query) {
    try {
        const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
        const results = await response.json();
        
        const searchResults = document.getElementById('search-results');
        searchResults.innerHTML = '';
        
        if (results.length === 0) {
            searchResults.innerHTML = '<div class="search-result-item">No results found</div>';
        } else {
            results.forEach(result => {
                const item = createSearchResultItem(result);
                searchResults.appendChild(item);
            });
        }
        
        searchResults.classList.add('active');
    } catch (error) {
        console.error('Search error:', error);
    }
}

// Create search result item
function createSearchResultItem(result) {
    const div = document.createElement('div');
    div.className = 'search-result-item';
    
    const icon = result.type === 'service' ? '🖥️' : '📄';
    div.textContent = `${icon} ${result.name}`;
    
    div.onclick = () => {
        if (result.type === 'service' && result.url.startsWith('http')) {
            window.open(result.url, '_blank');
        } else {
            openFile(result.path || result.url);
        }
        document.getElementById('search-results').classList.remove('active');
        document.getElementById('search-input').value = '';
    };
    
    return div;
}

// Open file (this will be a placeholder - actual implementation depends on system)
function openFile(filepath) {
    // For now, just alert the file path
    // In a real implementation, you might want to:
    // 1. Open in default editor via a backend endpoint
    // 2. Display file contents in a modal
    // 3. Download the file
    
    console.log('Opening file:', filepath);
    alert(`File: ${filepath}\n\nNote: File opening integration pending. For now, navigate to this path manually.`);
    
    // You could also make a backend endpoint to handle this:
    // fetch(`/api/open-file?path=${encodeURIComponent(filepath)}`)
}

// Utility: Format time ago
function formatTimeAgo(timestamp) {
    const now = Date.now();
    const diff = now - timestamp;
    
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (seconds < 60) return 'just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
}

console.log('📊 Dashboard scripts loaded');
