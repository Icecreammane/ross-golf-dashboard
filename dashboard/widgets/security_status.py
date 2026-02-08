#!/usr/bin/env python3
"""
Security Status Dashboard Widget
Shows latest security audit results and credential status
"""

import json
from pathlib import Path
from datetime import datetime
import subprocess

def get_latest_audit():
    """Get latest security audit results"""
    audit_dir = Path.home() / "clawd" / "security-logs"
    if not audit_dir.exists():
        return None
    
    # Find most recent audit file
    audit_files = list(audit_dir.glob("audit_*.md"))
    if not audit_files:
        return None
    
    latest = max(audit_files, key=lambda p: p.stat().st_mtime)
    
    # Parse audit file
    with open(latest) as f:
        content = f.read()
    
    # Extract key metrics
    warnings = 0
    files_scanned = 0
    status = "UNKNOWN"
    
    for line in content.split('\n'):
        if "Warnings Found:" in line:
            warnings = int(line.split(':')[1].strip())
        elif "Files Scanned:" in line:
            files_scanned = int(line.split(':')[1].strip())
        elif "Status:" in line:
            status = line.split(':')[1].strip().replace('✅', '').replace('⚠️', '').strip()
    
    return {
        'warnings': warnings,
        'files_scanned': files_scanned,
        'status': status,
        'timestamp': datetime.fromtimestamp(latest.stat().st_mtime).isoformat(),
        'file': latest.name
    }

def check_credential_files():
    """Check credential storage status"""
    creds_dir = Path.home() / "clawd" / ".credentials"
    
    if not creds_dir.exists():
        return {'status': 'missing', 'count': 0, 'files': []}
    
    cred_files = list(creds_dir.glob("*.json"))
    
    # Check permissions
    issues = []
    for f in cred_files:
        perms = oct(f.stat().st_mode)[-3:]
        if perms != '600':
            issues.append(f"{f.name}: permissions {perms} (should be 600)")
    
    return {
        'status': 'secure' if not issues else 'warning',
        'count': len(cred_files),
        'files': [f.name for f in cred_files],
        'issues': issues
    }

def get_git_status():
    """Check for uncommitted security changes"""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=Path.home() / "clawd",
            capture_output=True,
            text=True
        )
        
        # Check for modified security files
        security_files = []
        for line in result.stdout.split('\n'):
            if any(x in line.lower() for x in ['security', 'credential', '.credentials']):
                security_files.append(line.strip())
        
        return {
            'uncommitted': len(security_files) > 0,
            'files': security_files
        }
    except:
        return {'uncommitted': False, 'files': []}

def generate_html():
    """Generate security status widget HTML"""
    audit = get_latest_audit()
    creds = check_credential_files()
    git_status = get_git_status()
    
    # Determine overall status
    if audit and audit['warnings'] == 0 and creds['status'] == 'secure':
        overall_status = 'secure'
        status_color = '#10b981'
        status_icon = '🔒'
        status_text = 'SECURE'
    elif audit and audit['warnings'] > 0:
        overall_status = 'warning'
        status_color = '#f59e0b'
        status_icon = '⚠️'
        status_text = 'WARNINGS'
    else:
        overall_status = 'error'
        status_color = '#ef4444'
        status_icon = '🚨'
        status_text = 'ISSUES'
    
    html = f'''
<div class="security-widget">
    <div class="widget-header">
        <h3>🔒 Security Status</h3>
        <span class="status-badge {overall_status}" style="background-color: {status_color};">
            {status_icon} {status_text}
        </span>
    </div>
    
    <div class="security-grid">
'''
    
    # Audit status
    if audit:
        audit_time = datetime.fromisoformat(audit['timestamp'])
        time_ago = (datetime.now() - audit_time).total_seconds() / 3600
        time_str = f"{int(time_ago)}h ago" if time_ago < 48 else f"{int(time_ago/24)}d ago"
        
        html += f'''
        <div class="security-card">
            <div class="card-icon">🔍</div>
            <div class="card-content">
                <div class="card-label">Last Security Audit</div>
                <div class="card-value {'warning' if audit['warnings'] > 0 else 'good'}">
                    {audit['warnings']} warnings
                </div>
                <div class="card-meta">{audit['files_scanned']} files • {time_str}</div>
            </div>
        </div>
'''
    else:
        html += '''
        <div class="security-card">
            <div class="card-icon">⚠️</div>
            <div class="card-content">
                <div class="card-label">Security Audit</div>
                <div class="card-value warning">No audit found</div>
                <div class="card-meta">Run security audit</div>
            </div>
        </div>
'''
    
    # Credential storage
    html += f'''
        <div class="security-card">
            <div class="card-icon">🔑</div>
            <div class="card-content">
                <div class="card-label">Credential Storage</div>
                <div class="card-value {creds['status']}">
                    {creds['count']} files
                </div>
                <div class="card-meta">{creds['status'].capitalize()}</div>
            </div>
        </div>
'''
    
    # Git status
    git_icon = '⚠️' if git_status['uncommitted'] else '✅'
    git_class = 'warning' if git_status['uncommitted'] else 'good'
    git_text = f"{len(git_status['files'])} uncommitted" if git_status['uncommitted'] else "All committed"
    
    html += f'''
        <div class="security-card">
            <div class="card-icon">{git_icon}</div>
            <div class="card-content">
                <div class="card-label">Git Status</div>
                <div class="card-value {git_class}">
                    {git_text}
                </div>
                <div class="card-meta">Security files</div>
            </div>
        </div>
'''
    
    # API Access
    html += '''
        <div class="security-card">
            <div class="card-icon">🌐</div>
            <div class="card-content">
                <div class="card-label">API Access</div>
                <div class="card-value good">
                    Active
                </div>
                <div class="card-meta">Kill switch ready</div>
            </div>
        </div>
'''
    
    html += '''
    </div>
'''
    
    # Credential details
    if creds['files']:
        html += '''
    <div class="credential-list">
        <div class="list-header">Active Credentials:</div>
'''
        for cred_file in creds['files']:
            html += f'''
        <div class="credential-item">
            <span class="cred-name">{cred_file.replace('.json', '')}</span>
            <span class="cred-status">✓</span>
        </div>
'''
        html += '''
    </div>
'''
    
    # Issues section
    if creds['issues'] or (audit and audit['warnings'] > 0):
        html += '''
    <div class="issues-section">
        <div class="issues-header">⚠️ Issues Found:</div>
'''
        if creds['issues']:
            for issue in creds['issues']:
                html += f'<div class="issue-item">{issue}</div>'
        
        if audit and audit['warnings'] > 0:
            html += f'''
        <div class="issue-item">
            {audit['warnings']} warnings in security audit - review {audit['file']}
        </div>
'''
        html += '''
    </div>
'''
    
    # Actions
    html += '''
    <div class="widget-actions">
        <button onclick="runSecurityAudit()">
            🔍 Run Audit
        </button>
        <button onclick="viewSecurityLog()">
            📄 View Logs
        </button>
        <button onclick="confirmKillSwitch()">
            🚨 Kill Switch
        </button>
    </div>
</div>

<style>
.security-widget {
    background: #1e293b;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #334155;
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

.status-badge {
    padding: 6px 14px;
    border-radius: 16px;
    font-size: 12px;
    font-weight: 600;
    color: white;
}

.security-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-bottom: 20px;
}

.security-card {
    background: #0f172a;
    padding: 15px;
    border-radius: 8px;
    display: flex;
    gap: 12px;
}

.card-icon {
    font-size: 24px;
    line-height: 1;
}

.card-content {
    flex: 1;
}

.card-label {
    font-size: 12px;
    color: #94a3b8;
    margin-bottom: 4px;
}

.card-value {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 2px;
}

.card-value.good {
    color: #10b981;
}

.card-value.warning {
    color: #f59e0b;
}

.card-value.error {
    color: #ef4444;
}

.card-meta {
    font-size: 11px;
    color: #64748b;
}

.credential-list {
    background: #0f172a;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
}

.list-header {
    font-size: 12px;
    color: #94a3b8;
    margin-bottom: 10px;
    font-weight: 600;
}

.credential-item {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #1e293b;
    font-size: 13px;
}

.credential-item:last-child {
    border-bottom: none;
}

.cred-name {
    color: #e2e8f0;
}

.cred-status {
    color: #10b981;
}

.issues-section {
    background: #7f1d1d;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
}

.issues-header {
    font-size: 12px;
    color: #fecaca;
    margin-bottom: 10px;
    font-weight: 600;
}

.issue-item {
    font-size: 13px;
    color: #fecaca;
    padding: 6px 0;
}

.widget-actions {
    display: flex;
    gap: 10px;
}

.widget-actions button {
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

.widget-actions button:hover {
    background: #1e293b;
    border-color: #475569;
}
</style>

<script>
function runSecurityAudit() {
    alert('Running security audit... (Feature not yet implemented in web dashboard)');
}

function viewSecurityLog() {
    window.location.href = '../security-logs/';
}

function confirmKillSwitch() {
    if (confirm('⚠️ WARNING: Kill switch will revoke ALL credentials immediately.\\n\\nThis cannot be undone easily. Are you sure?')) {
        alert('Kill switch activation requires shell access. Run: python3 ~/clawd/scripts/kill_switch.py --execute');
    }
}
</script>
'''
    
    return html

if __name__ == "__main__":
    html = generate_html()
    
    # Save widget
    output_file = Path.home() / "clawd" / "dashboard" / "widgets" / "security_status.html"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"✅ Security status widget generated: {output_file}")
    
    # Print status
    audit = get_latest_audit()
    if audit:
        print(f"   Latest audit: {audit['warnings']} warnings")
    
    creds = check_credential_files()
    print(f"   Credentials: {creds['count']} files ({creds['status']})")
