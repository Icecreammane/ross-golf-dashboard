#!/usr/bin/env python3
"""
Recent Activity Timeline Widget
Shows recent actions, commits, and system events
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import subprocess

def get_recent_commits(limit=10):
    """Get recent git commits"""
    try:
        result = subprocess.run(
            ['git', 'log', f'--max-count={limit}', '--pretty=format:%H|%an|%s|%ct'],
            cwd=Path.home() / "clawd",
            capture_output=True,
            text=True
        )
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            hash_val, author, message, timestamp = line.split('|')
            commits.append({
                'type': 'commit',
                'hash': hash_val[:8],
                'author': author,
                'message': message,
                'timestamp': datetime.fromtimestamp(int(timestamp))
            })
        
        return commits
    except:
        return []

def get_recent_logs(hours=24):
    """Get recent activity from memory logs"""
    memory_dir = Path.home() / "clawd" / "memory"
    if not memory_dir.exists():
        return []
    
    cutoff = datetime.now() - timedelta(hours=hours)
    activities = []
    
    # Check today and yesterday's memory files
    for day_offset in [0, 1]:
        date = datetime.now() - timedelta(days=day_offset)
        log_file = memory_dir / f"{date.strftime('%Y-%m-%d')}.md"
        
        if not log_file.exists():
            continue
        
        try:
            with open(log_file) as f:
                content = f.read()
            
            # Look for time-stamped entries
            for line in content.split('\n'):
                if line.startswith('###') or line.startswith('##'):
                    # Extract timestamp if present
                    if any(x in line for x in ['[', ']', '-']):
                        activities.append({
                            'type': 'log',
                            'message': line.strip('#').strip(),
                            'timestamp': date  # Approximate
                        })
        except:
            continue
    
    return activities[:10]  # Return most recent

def get_email_activity():
    """Get email monitoring activity"""
    stats_file = Path.home() / "clawd" / "data" / "email_monitor_stats.json"
    if not stats_file.exists():
        return []
    
    try:
        with open(stats_file) as f:
            stats = json.load(f)
        
        activities = []
        
        if stats.get('last_scan'):
            last_scan = datetime.fromisoformat(stats['last_scan'])
            if (datetime.now() - last_scan).total_seconds() < 3600:  # Last hour
                activities.append({
                    'type': 'email',
                    'icon': '📧',
                    'message': f"Email scan completed - {stats.get('total_emails_processed', 0)} total processed",
                    'timestamp': last_scan
                })
        
        return activities
    except:
        return []

def get_security_activity():
    """Get security audit activity"""
    audit_dir = Path.home() / "clawd" / "security-logs"
    if not audit_dir.exists():
        return []
    
    try:
        audit_files = list(audit_dir.glob("audit_*.md"))
        if not audit_files:
            return []
        
        latest = max(audit_files, key=lambda p: p.stat().st_mtime)
        timestamp = datetime.fromtimestamp(latest.stat().st_mtime)
        
        # Only show if recent (last 24h)
        if (datetime.now() - timestamp).total_seconds() < 86400:
            return [{
                'type': 'security',
                'icon': '🔒',
                'message': "Security audit completed",
                'timestamp': timestamp
            }]
        
        return []
    except:
        return []

def combine_and_sort_activities():
    """Combine all activities and sort by time"""
    all_activities = []
    
    # Get all sources
    commits = get_recent_commits(5)
    logs = get_recent_logs(24)
    email = get_email_activity()
    security = get_security_activity()
    
    all_activities.extend(commits)
    all_activities.extend(logs)
    all_activities.extend(email)
    all_activities.extend(security)
    
    # Sort by timestamp (most recent first)
    all_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return all_activities[:15]  # Show top 15

def generate_html():
    """Generate activity timeline widget"""
    activities = combine_and_sort_activities()
    
    html = '''
<div class="activity-widget">
    <div class="widget-header">
        <h3>📊 Recent Activity</h3>
        <span class="activity-count">{} events</span>
    </div>
    
    <div class="timeline">
'''.format(len(activities))
    
    if not activities:
        html += '''
        <div class="no-activity">
            <div class="no-activity-icon">🤷</div>
            <div class="no-activity-text">No recent activity</div>
        </div>
'''
    else:
        for activity in activities:
            # Format timestamp
            timestamp = activity['timestamp']
            now = datetime.now()
            delta = now - timestamp
            
            if delta.total_seconds() < 60:
                time_str = "Just now"
            elif delta.total_seconds() < 3600:
                mins = int(delta.total_seconds() / 60)
                time_str = f"{mins}m ago"
            elif delta.total_seconds() < 86400:
                hours = int(delta.total_seconds() / 3600)
                time_str = f"{hours}h ago"
            else:
                days = int(delta.total_seconds() / 86400)
                time_str = f"{days}d ago"
            
            # Get icon and style based on type
            if activity['type'] == 'commit':
                icon = '🔨'
                style_class = 'commit'
                message = f"{activity['message'][:60]}..."
            elif activity['type'] == 'email':
                icon = activity.get('icon', '📧')
                style_class = 'email'
                message = activity['message']
            elif activity['type'] == 'security':
                icon = activity.get('icon', '🔒')
                style_class = 'security'
                message = activity['message']
            elif activity['type'] == 'log':
                icon = '📝'
                style_class = 'log'
                message = activity['message'][:60]
            else:
                icon = '•'
                style_class = 'other'
                message = str(activity.get('message', 'Activity'))
            
            html += f'''
        <div class="timeline-item {style_class}">
            <div class="timeline-icon">{icon}</div>
            <div class="timeline-content">
                <div class="timeline-message">{message}</div>
                <div class="timeline-time">{time_str}</div>
            </div>
        </div>
'''
    
    html += '''
    </div>
    
    <div class="widget-footer">
        <button onclick="refreshTimeline()">
            🔄 Refresh
        </button>
        <button onclick="viewFullLog()">
            📜 Full Log
        </button>
    </div>
</div>

<style>
.activity-widget {
    background: #1e293b;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #334155;
    max-height: 600px;
    display: flex;
    flex-direction: column;
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
    color: #60a5fa;
}

.activity-count {
    font-size: 12px;
    color: #94a3b8;
    background: #0f172a;
    padding: 4px 10px;
    border-radius: 12px;
}

.timeline {
    flex: 1;
    overflow-y: auto;
    padding-right: 10px;
}

.timeline::-webkit-scrollbar {
    width: 6px;
}

.timeline::-webkit-scrollbar-track {
    background: #0f172a;
    border-radius: 3px;
}

.timeline::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 3px;
}

.timeline::-webkit-scrollbar-thumb:hover {
    background: #475569;
}

.timeline-item {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
    padding-bottom: 16px;
    border-bottom: 1px solid #0f172a;
}

.timeline-item:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
}

.timeline-icon {
    font-size: 20px;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #0f172a;
    border-radius: 8px;
    flex-shrink: 0;
}

.timeline-item.commit .timeline-icon {
    background: #1e40af;
}

.timeline-item.email .timeline-icon {
    background: #15803d;
}

.timeline-item.security .timeline-icon {
    background: #b91c1c;
}

.timeline-content {
    flex: 1;
    min-width: 0;
}

.timeline-message {
    font-size: 14px;
    color: #e2e8f0;
    margin-bottom: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.timeline-time {
    font-size: 12px;
    color: #64748b;
}

.no-activity {
    text-align: center;
    padding: 40px 20px;
}

.no-activity-icon {
    font-size: 48px;
    margin-bottom: 10px;
}

.no-activity-text {
    font-size: 14px;
    color: #64748b;
}

.widget-footer {
    margin-top: 20px;
    display: flex;
    gap: 10px;
    border-top: 1px solid #0f172a;
    padding-top: 15px;
}

.widget-footer button {
    flex: 1;
    padding: 10px;
    border: 1px solid #334155;
    border-radius: 6px;
    background: #0f172a;
    color: #e2e8f0;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.2s;
}

.widget-footer button:hover {
    background: #1e293b;
    border-color: #475569;
}
</style>

<script>
function refreshTimeline() {
    location.reload();
}

function viewFullLog() {
    window.location.href = '../memory/';
}
</script>
'''
    
    return html

if __name__ == "__main__":
    html = generate_html()
    
    # Save widget
    output_file = Path.home() / "clawd" / "dashboard" / "widgets" / "recent_activity.html"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"✅ Recent activity widget generated: {output_file}")
    
    activities = combine_and_sort_activities()
    print(f"   {len(activities)} recent activities tracked")
