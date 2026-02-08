#!/usr/bin/env python3
"""
Email Queue Dashboard Widget
Shows current support ticket queue status
"""

import json
from pathlib import Path
from datetime import datetime, timedelta

def load_support_queue():
    """Load support queue"""
    queue_file = Path.home() / "clawd" / "integrations" / "gmail" / "support-tickets.json"
    if queue_file.exists():
        with open(queue_file) as f:
            return json.load(f)
    return []

def load_monitor_stats():
    """Load monitoring stats"""
    stats_file = Path.home() / "clawd" / "data" / "email_monitor_stats.json"
    if stats_file.exists():
        with open(stats_file) as f:
            return json.load(f)
    return {}

def get_queue_by_priority():
    """Group tickets by priority"""
    queue = load_support_queue()
    
    by_priority = {'P0': [], 'P1': [], 'P2': [], 'P3': []}
    for ticket in queue:
        if ticket['status'] == 'new':
            priority = ticket.get('priority', 'P3')
            by_priority[priority].append(ticket)
    
    return by_priority

def get_recent_tickets(hours=24):
    """Get tickets from last N hours"""
    queue = load_support_queue()
    cutoff = datetime.now() - timedelta(hours=hours)
    
    recent = []
    for ticket in queue:
        received = datetime.fromisoformat(ticket['received_at'])
        if received > cutoff:
            recent.append(ticket)
    
    return recent

def generate_html():
    """Generate HTML widget"""
    queue = load_support_queue()
    stats = load_monitor_stats()
    by_priority = get_queue_by_priority()
    recent = get_recent_tickets(24)
    
    # Count new vs drafted
    new_count = sum(1 for t in queue if t['status'] == 'new')
    drafted_count = sum(1 for t in queue if t['status'] == 'drafted')
    
    html = f'''
<div class="email-queue-widget">
    <div class="widget-header">
        <h3>📧 Email Support Queue</h3>
        <span class="status-badge {'active' if stats.get('last_scan') else 'inactive'}">
            {'ACTIVE' if stats.get('last_scan') else 'INACTIVE'}
        </span>
    </div>
    
    <div class="queue-summary">
        <div class="metric">
            <div class="metric-value">{new_count}</div>
            <div class="metric-label">New Tickets</div>
        </div>
        <div class="metric">
            <div class="metric-value">{drafted_count}</div>
            <div class="metric-label">Drafts Ready</div>
        </div>
        <div class="metric">
            <div class="metric-value">{len(recent)}</div>
            <div class="metric-label">Last 24h</div>
        </div>
    </div>
    
    <div class="priority-breakdown">
        <h4>Priority Breakdown</h4>
'''
    
    # Priority badges
    priority_colors = {
        'P0': '#dc2626',  # Red
        'P1': '#ea580c',  # Orange
        'P2': '#f59e0b',  # Yellow
        'P3': '#10b981'   # Green
    }
    
    for priority, tickets in by_priority.items():
        count = len(tickets)
        color = priority_colors[priority]
        
        html += f'''
        <div class="priority-row">
            <span class="priority-badge" style="background-color: {color};">{priority}</span>
            <span class="priority-count">{count} tickets</span>
        </div>
'''
    
    html += '''
    </div>
'''
    
    # Recent tickets
    if new_count > 0:
        html += '''
    <div class="recent-tickets">
        <h4>New Tickets</h4>
        <div class="ticket-list">
'''
        
        new_tickets = [t for t in queue if t['status'] == 'new'][:5]  # Show max 5
        for ticket in new_tickets:
            priority_color = priority_colors[ticket.get('priority', 'P3')]
            
            html += f'''
            <div class="ticket-item">
                <span class="ticket-priority" style="background-color: {priority_color};">
                    {ticket.get('priority', 'P3')}
                </span>
                <div class="ticket-info">
                    <div class="ticket-subject">{ticket['subject'][:50]}...</div>
                    <div class="ticket-meta">{ticket['from']}</div>
                </div>
            </div>
'''
        
        html += '''
        </div>
    </div>
'''
    
    # Monitor stats
    if stats:
        last_scan = stats.get('last_scan')
        if last_scan:
            last_scan_dt = datetime.fromisoformat(last_scan)
            time_ago = (datetime.now() - last_scan_dt).total_seconds() / 60
            last_scan_str = f"{int(time_ago)} min ago" if time_ago < 60 else f"{int(time_ago/60)} hr ago"
        else:
            last_scan_str = "Never"
        
        html += f'''
    <div class="monitor-stats">
        <div class="stat-row">
            <span class="stat-label">Last Scan:</span>
            <span class="stat-value">{last_scan_str}</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Total Scans:</span>
            <span class="stat-value">{stats.get('total_scans', 0)}</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Emails Processed:</span>
            <span class="stat-value">{stats.get('total_emails_processed', 0)}</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Drafts Created:</span>
            <span class="stat-value">{stats.get('total_drafts_created', 0)}</span>
        </div>
    </div>
'''
    
    html += '''
    <div class="widget-actions">
        <button onclick="window.location.href='mailto:bigmeatyclawd@gmail.com'">
            Open Gmail
        </button>
        <button onclick="refreshWidget('email-queue')">
            Refresh
        </button>
    </div>
</div>

<style>
.email-queue-widget {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    max-width: 500px;
}

.widget-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.widget-header h3 {
    margin: 0;
    font-size: 20px;
}

.status-badge {
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
}

.status-badge.active {
    background: #dcfce7;
    color: #166534;
}

.status-badge.inactive {
    background: #fee2e2;
    color: #991b1b;
}

.queue-summary {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin-bottom: 20px;
}

.metric {
    text-align: center;
    padding: 15px;
    background: #f9fafb;
    border-radius: 8px;
}

.metric-value {
    font-size: 32px;
    font-weight: 700;
    color: #1f2937;
}

.metric-label {
    font-size: 12px;
    color: #6b7280;
    margin-top: 5px;
}

.priority-breakdown {
    margin-bottom: 20px;
}

.priority-breakdown h4 {
    font-size: 14px;
    color: #6b7280;
    margin-bottom: 10px;
}

.priority-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #f3f4f6;
}

.priority-badge {
    padding: 2px 8px;
    border-radius: 4px;
    color: white;
    font-size: 12px;
    font-weight: 600;
}

.priority-count {
    font-size: 14px;
    color: #6b7280;
}

.recent-tickets {
    margin-bottom: 20px;
}

.recent-tickets h4 {
    font-size: 14px;
    color: #6b7280;
    margin-bottom: 10px;
}

.ticket-list {
    max-height: 200px;
    overflow-y: auto;
}

.ticket-item {
    display: flex;
    gap: 10px;
    padding: 10px;
    border-radius: 6px;
    margin-bottom: 8px;
    background: #f9fafb;
}

.ticket-priority {
    padding: 2px 6px;
    border-radius: 4px;
    color: white;
    font-size: 10px;
    font-weight: 600;
    height: fit-content;
}

.ticket-info {
    flex: 1;
}

.ticket-subject {
    font-size: 13px;
    color: #1f2937;
    margin-bottom: 2px;
}

.ticket-meta {
    font-size: 11px;
    color: #9ca3af;
}

.monitor-stats {
    background: #f9fafb;
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 15px;
}

.stat-row {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    font-size: 13px;
}

.stat-label {
    color: #6b7280;
}

.stat-value {
    font-weight: 600;
    color: #1f2937;
}

.widget-actions {
    display: flex;
    gap: 10px;
}

.widget-actions button {
    flex: 1;
    padding: 10px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    background: white;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s;
}

.widget-actions button:hover {
    background: #f9fafb;
    border-color: #9ca3af;
}
</style>
'''
    
    return html

if __name__ == "__main__":
    html = generate_html()
    
    # Save to file
    output_file = Path.home() / "clawd" / "dashboard" / "widgets" / "email_queue.html"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"✅ Email queue widget generated: {output_file}")
    print(f"📊 Current queue status:")
    
    queue = load_support_queue()
    by_priority = get_queue_by_priority()
    
    for priority, tickets in by_priority.items():
        if tickets:
            print(f"   {priority}: {len(tickets)} tickets")
