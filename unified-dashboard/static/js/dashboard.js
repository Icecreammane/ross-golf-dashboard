/**
 * Unified Dashboard - Real-time Updates
 * Fast loading with efficient data fetching
 */

// Configuration
const UPDATE_INTERVAL = 30000; // 30 seconds
const API_BASE = window.location.origin;

// State
let currentTab = 'revenue';
let updateTimer = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Dashboard initializing...');
    
    setupTabs();
    setupClock();
    loadAllData();
    
    // Auto-refresh every 30 seconds
    updateTimer = setInterval(loadAllData, UPDATE_INTERVAL);
    
    console.log('✅ Dashboard ready');
});

/**
 * Tab Switching
 */
function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Update buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update content
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');
    
    currentTab = tabName;
}

/**
 * Clock
 */
function setupClock() {
    updateClock();
    setInterval(updateClock, 1000);
}

function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('current-time').textContent = timeString;
}

/**
 * Data Loading
 */
async function loadAllData() {
    try {
        // Use /api/all for fast single-request loading
        const response = await fetch(`${API_BASE}/api/all`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update all tabs
        updateRevenue(data.revenue);
        updateOpportunities(data.opportunities);
        updateMorningBrief(data.morning_brief);
        updateFitness(data.fitness);
        updateGolf(data.golf);
        updateNBA(data.nba);
        
        // Update status
        updateStatus('healthy', data.timestamp);
        
    } catch (error) {
        console.error('❌ Error loading data:', error);
        updateStatus('error');
    }
}

/**
 * Update Revenue Tab
 */
function updateRevenue(data) {
    document.getElementById('mrr-value').textContent = data.mrr.toFixed(2);
    document.getElementById('mrr-goal').textContent = data.goal;
    document.getElementById('mrr-percent').textContent = data.progress;
    document.getElementById('mrr-progress').style.width = `${Math.min(data.progress, 100)}%`;
    
    document.getElementById('daily-revenue').textContent = data.daily_revenue.toFixed(2);
    document.getElementById('weekly-revenue').textContent = data.weekly_revenue.toFixed(2);
    document.getElementById('monthly-revenue').textContent = data.monthly_revenue.toFixed(2);
    
    // Recent sales
    const salesContainer = document.getElementById('recent-sales');
    if (data.recent_sales && data.recent_sales.length > 0) {
        salesContainer.innerHTML = data.recent_sales.map(sale => `
            <div class="list-item">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>${sale.description || 'Sale'}</strong>
                        <div style="font-size: 12px; color: #64748b;">
                            ${new Date(sale.created * 1000).toLocaleDateString()}
                        </div>
                    </div>
                    <div style="font-size: 20px; font-weight: 700; color: #10b981;">
                        $${sale.amount.toFixed(2)}
                    </div>
                </div>
            </div>
        `).join('');
    } else {
        salesContainer.innerHTML = '<p class="empty-state">No recent sales</p>';
    }
}

/**
 * Update Opportunities Tab
 */
function updateOpportunities(data) {
    document.getElementById('total-opps').textContent = data.total_count;
    document.getElementById('high-priority-opps').textContent = data.high_priority;
    document.getElementById('opp-badge').textContent = data.high_priority;
    
    const oppsContainer = document.getElementById('opportunities-list');
    
    if (data.opportunities && data.opportunities.length > 0) {
        oppsContainer.innerHTML = data.opportunities.map((opp, index) => `
            <div class="opportunity-item">
                <div class="opportunity-info">
                    <h4>${index + 1}. ${opp.title}</h4>
                    <div class="opportunity-meta">
                        Source: ${opp.source} | Confidence: ${(opp.confidence * 100).toFixed(0)}%
                    </div>
                </div>
                <div class="opportunity-value">
                    <div class="amount">$${opp.value.toFixed(0)}</div>
                    <div class="confidence">${(opp.confidence * 100).toFixed(0)}% confident</div>
                </div>
            </div>
        `).join('');
    } else {
        oppsContainer.innerHTML = '<p class="empty-state">No opportunities found</p>';
    }
}

/**
 * Update Morning Brief Tab
 */
function updateMorningBrief(data) {
    const statusBadge = document.getElementById('brief-status');
    const contentDiv = document.getElementById('brief-content');
    
    if (data.generated) {
        statusBadge.textContent = '✅ Complete';
        statusBadge.className = 'status-badge complete';
        contentDiv.innerHTML = `<pre>${escapeHtml(data.content)}</pre>`;
    } else {
        statusBadge.textContent = '⏳ Pending';
        statusBadge.className = 'status-badge pending';
        contentDiv.innerHTML = '<p class="empty-state">Morning brief not yet generated (runs at 7:30 AM)</p>';
    }
}

/**
 * Update Fitness Tab
 */
function updateFitness(data) {
    document.getElementById('current-weight').textContent = data.current_weight.toFixed(1);
    document.getElementById('target-weight').textContent = data.target_weight;
    document.getElementById('weight-lost').textContent = data.weight_lost.toFixed(1);
    document.getElementById('weight-percent').textContent = data.progress.toFixed(1);
    document.getElementById('weight-progress').style.width = `${Math.min(data.progress, 100)}%`;
    
    document.getElementById('workouts-week').textContent = data.workouts_this_week;
    
    // Last workout
    const workoutDiv = document.getElementById('last-workout');
    if (data.last_workout) {
        const workout = data.last_workout;
        workoutDiv.innerHTML = `
            <h4>${workout.name || 'Workout'} - ${workout.date}</h4>
            <div class="lift-list">
                ${workout.lifts ? workout.lifts.map(lift => `
                    <div class="lift-item">
                        <span>${lift.name}</span>
                        <span><strong>${lift.weight} lbs</strong> × ${lift.reps} reps</span>
                    </div>
                `).join('') : '<p>No lifts recorded</p>'}
            </div>
        `;
    } else {
        workoutDiv.innerHTML = '<p class="empty-state">No workouts logged</p>';
    }
}

/**
 * Update Golf Tab
 */
function updateGolf(data) {
    document.getElementById('total-rounds').textContent = data.total_rounds;
    document.getElementById('avg-score').textContent = data.average_score.toFixed(1);
    document.getElementById('best-score').textContent = data.best_score || 'N/A';
    document.getElementById('handicap').textContent = data.handicap_estimate.toFixed(1);
    
    // Recent rounds
    const roundsContainer = document.getElementById('recent-rounds');
    if (data.recent_rounds && data.recent_rounds.length > 0) {
        roundsContainer.innerHTML = data.recent_rounds.map(round => `
            <div class="round-item">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>${round.course}</strong>
                        <div style="font-size: 12px; color: #64748b;">
                            ${round.date}${round.notes ? ' - ' + round.notes : ''}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 24px; font-weight: 700;">${round.score}</div>
                        <div style="font-size: 12px; color: #64748b;">
                            ${round.differential > 0 ? '+' : ''}${round.differential} (par ${round.par})
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    } else {
        roundsContainer.innerHTML = '<p class="empty-state">No rounds played</p>';
    }
}

/**
 * Update NBA Tab
 */
function updateNBA(data) {
    const nbaTab = document.getElementById('nba-tab');
    const statusBadge = document.getElementById('nba-status');
    
    if (data.has_slate) {
        // Show NBA tab
        nbaTab.style.display = 'flex';
        
        // Update status
        statusBadge.textContent = data.locked ? '🔒 Locked' : '🔴 Live';
        statusBadge.className = data.locked ? 'status-badge pending' : 'status-badge complete';
        
        // Top stars
        const starsDiv = document.getElementById('nba-stars');
        if (data.top_stars && data.top_stars.length > 0) {
            starsDiv.innerHTML = data.top_stars.map((player, i) => `
                <div class="player-item">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <strong>${i + 1}. ${player.name}</strong> (${player.team})
                            <div style="font-size: 12px; color: #64748b;">
                                Ceiling: ${player.ceiling} | Value: ${player.value.toFixed(2)}
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-weight: 700;">$${player.salary.toLocaleString()}</div>
                            <div style="font-size: 12px; color: #64748b;">${player.ownership_pct}% owned</div>
                        </div>
                    </div>
                </div>
            `).join('');
        } else {
            starsDiv.innerHTML = '<p class="empty-state">No data</p>';
        }
        
        // Value plays
        const valueDiv = document.getElementById('nba-value');
        if (data.top_value && data.top_value.length > 0) {
            valueDiv.innerHTML = data.top_value.map((player, i) => `
                <div class="player-item">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <strong>${i + 1}. ${player.name}</strong> (${player.team})
                            <div style="font-size: 12px; color: #64748b;">
                                Ceiling: ${player.ceiling} | Value: ${player.value.toFixed(2)}
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-weight: 700;">$${player.salary.toLocaleString()}</div>
                            <div style="font-size: 12px; color: #10b981;">💰 Value Play</div>
                        </div>
                    </div>
                </div>
            `).join('');
        } else {
            valueDiv.innerHTML = '<p class="empty-state">No data</p>';
        }
        
        // Stacks
        const stacksDiv = document.getElementById('nba-stacks');
        if (data.stacks && data.stacks.length > 0) {
            stacksDiv.innerHTML = data.stacks.map((stack, i) => `
                <div class="stack-item">
                    <div class="stack-header">
                        <strong>${i + 1}. ${stack.team} Stack</strong>
                        <span style="font-weight: 700;">$${stack.total_salary.toLocaleString()}</span>
                    </div>
                    <div class="stack-players">
                        ${stack.players.join(', ')}
                    </div>
                    <div style="font-size: 12px; color: #64748b; margin-top: 8px;">
                        Ceiling: ${stack.combined_ceiling} | Upside: ${stack.combined_upside}
                    </div>
                </div>
            `).join('');
        } else {
            stacksDiv.innerHTML = '<p class="empty-state">No stacks available</p>';
        }
        
    } else {
        // Hide NBA tab
        nbaTab.style.display = 'none';
    }
}

/**
 * Update Status Indicator
 */
function updateStatus(status, timestamp) {
    const indicator = document.getElementById('status-indicator');
    const lastUpdated = document.getElementById('last-updated');
    const footerTimestamp = document.getElementById('footer-timestamp');
    
    if (status === 'healthy') {
        indicator.style.background = '#10b981';
        lastUpdated.textContent = 'Live';
    } else {
        indicator.style.background = '#ef4444';
        lastUpdated.textContent = 'Error';
    }
    
    if (timestamp) {
        const date = new Date(timestamp);
        footerTimestamp.textContent = date.toLocaleString();
    }
}

/**
 * Utility: Escape HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Cleanup on page unload
 */
window.addEventListener('beforeunload', () => {
    if (updateTimer) {
        clearInterval(updateTimer);
    }
});
