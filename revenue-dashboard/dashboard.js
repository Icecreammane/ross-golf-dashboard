// ============================================
// REVENUE DASHBOARD - JAVASCRIPT
// Loads data.json and populates all widgets
// ============================================

let dashboardData = null;
let incomeChart = null;

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', async () => {
    await loadData();
    renderDashboard();
});

// ============================================
// LOAD DATA
// ============================================

async function loadData() {
    try {
        const response = await fetch('data.json');
        dashboardData = await response.json();
        console.log('Dashboard data loaded:', dashboardData);
    } catch (error) {
        console.error('Error loading data:', error);
        // Use default data if file not found
        dashboardData = getDefaultData();
    }
}

function getDefaultData() {
    return {
        mrr: { current: 0, goal: 500 },
        floridaFund: { current: 0, goal: 50000, monthlyContribution: 0 },
        incomeStreams: [],
        thisWeek: { revenue: 0, newCustomers: 0, conversionRate: 0, traffic: 0 },
        recentActivity: [],
        milestones: [],
        pathScenarios: []
    };
}

// ============================================
// RENDER DASHBOARD
// ============================================

function renderDashboard() {
    renderMRRTracker();
    renderIncomeStreams();
    renderThisWeek();
    renderPathToGoal();
    renderFloridaFund();
    renderRecentActivity();
    renderMilestones();
    updateLastUpdated();
}

// ============================================
// MRR TRACKER
// ============================================

function renderMRRTracker() {
    const { current, goal } = dashboardData.mrr;
    const percentage = Math.min((current / goal) * 100, 100);
    
    document.getElementById('currentMRR').textContent = `$${current.toFixed(0)}`;
    document.getElementById('mrrProgress').style.width = `${percentage}%`;
    document.getElementById('mrrPercentage').textContent = `${percentage.toFixed(1)}%`;
    
    // Calculate days to goal (projection)
    const daysToGoal = calculateDaysToGoal(current, goal);
    document.getElementById('daysToGoal').textContent = daysToGoal;
}

function calculateDaysToGoal(current, goal) {
    if (current === 0) return '∞';
    
    // Assume 10% month-over-month growth (conservative)
    const monthlyGrowthRate = 0.10;
    const remaining = goal - current;
    
    if (remaining <= 0) return '0';
    
    // Simple projection: months = log(goal/current) / log(1 + growth_rate)
    const monthsNeeded = Math.log(goal / Math.max(current, 1)) / Math.log(1 + monthlyGrowthRate);
    const daysNeeded = Math.ceil(monthsNeeded * 30);
    
    if (daysNeeded > 365) return '365+';
    return daysNeeded.toString();
}

// ============================================
// INCOME STREAMS
// ============================================

function renderIncomeStreams() {
    const streams = dashboardData.incomeStreams;
    
    // Render chart
    renderIncomeChart(streams);
    
    // Render stream list
    const streamList = document.getElementById('streamList');
    streamList.innerHTML = streams.map(stream => {
        const value = stream.type === 'recurring' 
            ? `$${stream.mrr || 0}/mo` 
            : `$${stream.totalRevenue || 0} total`;
        
        const statusText = stream.status === 'not_launched' 
            ? 'Not launched' 
            : stream.status === 'planned' 
            ? 'Planned' 
            : 'Live';
        
        return `
            <div class="stream-item">
                <div class="stream-info">
                    <div class="stream-color" style="background: ${stream.color};"></div>
                    <div>
                        <div class="stream-name">${stream.name}</div>
                        <div class="stream-status">${statusText}</div>
                    </div>
                </div>
                <div class="stream-value">${value}</div>
            </div>
        `;
    }).join('');
}

function renderIncomeChart(streams) {
    const ctx = document.getElementById('incomeChart').getContext('2d');
    
    // If chart exists, destroy it first
    if (incomeChart) {
        incomeChart.destroy();
    }
    
    const chartData = streams.map(stream => {
        return stream.type === 'recurring' ? stream.mrr || 0 : 0;
    });
    
    const labels = streams.map(s => s.name);
    const colors = streams.map(s => s.color);
    
    incomeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: chartData.every(v => v === 0) ? [1, 1, 1] : chartData,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: $${context.parsed}/mo`;
                        }
                    }
                }
            }
        }
    });
}

// ============================================
// THIS WEEK
// ============================================

function renderThisWeek() {
    const week = dashboardData.thisWeek;
    
    document.getElementById('weekRevenue').textContent = `$${week.revenue}`;
    document.getElementById('weekCustomers').textContent = week.newCustomers;
    document.getElementById('weekConversion').textContent = `${week.conversionRate}%`;
    document.getElementById('weekTraffic').textContent = week.traffic;
    
    // Update week range
    const weekStart = new Date(week.weekStart);
    const weekEnd = new Date(weekStart);
    weekEnd.setDate(weekEnd.getDate() + 6);
    
    const formatDate = (date) => {
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        return `${months[date.getMonth()]} ${date.getDate()}`;
    };
    
    document.getElementById('weekRange').textContent = 
        `${formatDate(weekStart)}-${formatDate(weekEnd)}`;
}

// ============================================
// PATH TO $500
// ============================================

function renderPathToGoal() {
    const scenarios = dashboardData.pathScenarios;
    const scenariosContainer = document.getElementById('scenarios');
    
    scenariosContainer.innerHTML = scenarios.map(scenario => {
        const realisticClass = scenario.realistic === 'high' 
            ? 'realistic-high' 
            : scenario.realistic === 'medium' 
            ? 'realistic-medium' 
            : '';
        
        return `
            <div class="scenario ${realisticClass}">
                <div class="scenario-name">${scenario.name}</div>
                <div class="scenario-desc">${scenario.description}</div>
                <div class="scenario-meta">
                    <span>⏱️ ${scenario.timeframe}</span>
                    <span>📊 Realistic: ${scenario.realistic}</span>
                </div>
                ${scenario.note ? `<div class="scenario-note">${scenario.note}</div>` : ''}
            </div>
        `;
    }).join('');
}

// ============================================
// FLORIDA FUND
// ============================================

function renderFloridaFund() {
    const fund = dashboardData.floridaFund;
    const percentage = Math.min((fund.current / fund.goal) * 100, 100);
    
    document.getElementById('floridaCurrent').textContent = `$${fund.current.toLocaleString()}`;
    document.getElementById('floridaProgress').style.width = `${percentage}%`;
    
    // Calculate months until move
    const remaining = fund.goal - fund.current;
    const monthsNeeded = fund.monthlyContribution > 0 
        ? Math.ceil(remaining / fund.monthlyContribution)
        : '∞';
    
    document.getElementById('floridaMonths').textContent = monthsNeeded;
    
    // Calculate needed per month (assuming 5-year timeline)
    const monthsInTimeline = 60; // 5 years
    const neededPerMonth = Math.ceil(remaining / monthsInTimeline);
    document.getElementById('floridaNeeded').textContent = `$${neededPerMonth}`;
}

// ============================================
// RECENT ACTIVITY
// ============================================

function renderRecentActivity() {
    const activity = dashboardData.recentActivity;
    const activityList = document.getElementById('activityList');
    
    if (activity.length === 0) {
        activityList.innerHTML = `
            <div class="activity-item">
                <div class="activity-desc">No activity yet. Time to launch! 🚀</div>
            </div>
        `;
        return;
    }
    
    activityList.innerHTML = activity.slice(0, 10).map(item => {
        const date = new Date(item.date);
        const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        
        return `
            <div class="activity-item type-${item.type}">
                <div>
                    <div class="activity-desc">${item.description}</div>
                    <div class="activity-date">${dateStr}</div>
                </div>
                ${item.amount ? `<div class="activity-amount">+$${item.amount}</div>` : ''}
            </div>
        `;
    }).join('');
}

// ============================================
// MILESTONES
// ============================================

function renderMilestones() {
    const milestones = dashboardData.milestones;
    const milestoneList = document.getElementById('milestoneList');
    
    milestoneList.innerHTML = milestones.map(milestone => {
        const date = new Date(milestone.estimatedDate);
        const dateStr = date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
        
        const achievedClass = milestone.achieved ? 'achieved' : '';
        const targetDisplay = milestone.target >= 1000 
            ? `$${(milestone.target / 1000).toFixed(0)}k` 
            : `$${milestone.target}`;
        
        return `
            <div class="milestone-item ${achievedClass}">
                <div class="milestone-name">
                    ${milestone.achieved ? '✅' : '🎯'} ${milestone.name}
                </div>
                <div class="milestone-target">${targetDisplay}</div>
                <div class="milestone-date">
                    ${milestone.achieved ? 'Achieved!' : `Target: ${dateStr}`}
                </div>
                ${!milestone.achieved ? `
                    <span class="milestone-confidence ${milestone.confidence}">
                        ${milestone.confidence} confidence
                    </span>
                ` : ''}
            </div>
        `;
    }).join('');
}

// ============================================
// UTILITIES
// ============================================

function updateLastUpdated() {
    const lastUpdated = dashboardData.mrr.lastUpdated || new Date().toISOString().split('T')[0];
    const date = new Date(lastUpdated);
    const dateStr = date.toLocaleDateString('en-US', { 
        month: 'long', 
        day: 'numeric', 
        year: 'numeric' 
    });
    
    document.getElementById('lastUpdated').textContent = dateStr;
}

function editData() {
    document.getElementById('editModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('editModal').style.display = 'none';
}

// ============================================
// AUTO-REFRESH (Optional)
// ============================================

// Uncomment to auto-refresh data every 5 minutes
// setInterval(async () => {
//     await loadData();
//     renderDashboard();
// }, 5 * 60 * 1000);
