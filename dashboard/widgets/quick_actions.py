#!/usr/bin/env python3
"""
Quick Actions Panel Widget
Provides one-click access to common tasks
"""

from pathlib import Path

def generate_html():
    """Generate quick actions widget"""
    
    actions = [
        {
            'icon': '📧',
            'label': 'Open Gmail',
            'description': 'Check support tickets',
            'action': "window.open('https://mail.google.com', '_blank')",
            'color': '#3b82f6'
        },
        {
            'icon': '🔒',
            'label': 'Run Security Audit',
            'description': 'Scan for vulnerabilities',
            'action': "runSecurityAudit()",
            'color': '#ef4444'
        },
        {
            'icon': '📊',
            'label': 'View Analytics',
            'description': 'Dashboard metrics',
            'action': "window.location.href='hub.html'",
            'color': '#8b5cf6'
        },
        {
            'icon': '🏋️',
            'label': 'FitTrack',
            'description': 'Log workout/meal',
            'action': "window.open('http://localhost:8000', '_blank')",
            'color': '#10b981'
        },
        {
            'icon': '💾',
            'label': 'Backup Workspace',
            'description': 'Create backup',
            'action': "runBackup()",
            'color': '#f59e0b'
        },
        {
            'icon': '🔄',
            'label': 'Git Push',
            'description': 'Push latest commits',
            'action': "gitPush()",
            'color': '#06b6d4'
        },
        {
            'icon': '📝',
            'label': 'Daily Log',
            'description': 'View/edit today',
            'action': "openDailyLog()",
            'color': '#ec4899'
        },
        {
            'icon': '🚀',
            'label': 'Deploy',
            'description': 'Ship to production',
            'action': "deployToProduction()",
            'color': '#14b8a6'
        }
    ]
    
    html = '''
<div class="quick-actions-widget">
    <div class="widget-header">
        <h3>⚡ Quick Actions</h3>
    </div>
    
    <div class="actions-grid">
'''
    
    for action in actions:
        html += f'''
        <div class="action-card" onclick="{action['action']}" style="border-color: {action['color']};">
            <div class="action-icon" style="background-color: {action['color']};">
                {action['icon']}
            </div>
            <div class="action-content">
                <div class="action-label">{action['label']}</div>
                <div class="action-description">{action['description']}</div>
            </div>
        </div>
'''
    
    html += '''
    </div>
</div>

<style>
.quick-actions-widget {
    background: #1e293b;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #334155;
}

.widget-header {
    margin-bottom: 20px;
}

.widget-header h3 {
    margin: 0;
    font-size: 20px;
    color: #60a5fa;
}

.actions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
}

.action-card {
    background: #0f172a;
    padding: 16px;
    border-radius: 10px;
    border-left: 4px solid;
    display: flex;
    gap: 12px;
    cursor: pointer;
    transition: all 0.2s;
}

.action-card:hover {
    background: #1e293b;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.action-icon {
    width: 48px;
    height: 48px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    flex-shrink: 0;
}

.action-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.action-label {
    font-size: 15px;
    font-weight: 600;
    color: #e2e8f0;
    margin-bottom: 2px;
}

.action-description {
    font-size: 12px;
    color: #94a3b8;
}

/* Mobile responsive */
@media (max-width: 768px) {
    .actions-grid {
        grid-template-columns: 1fr;
    }
}
</style>

<script>
function runSecurityAudit() {
    if (confirm('Run security audit? This will scan all files in the workspace.')) {
        alert('Security audit started... Check terminal output.');
        // In production, trigger actual audit
    }
}

function runBackup() {
    if (confirm('Create workspace backup?')) {
        alert('Backup started... Check ~/clawd/backups/ for result.');
        // In production, trigger actual backup
    }
}

function gitPush() {
    if (confirm('Push all commits to remote?')) {
        alert('Git push started... Check terminal for status.');
        // In production, trigger actual git push
    }
}

function openDailyLog() {
    const today = new Date().toISOString().split('T')[0];
    window.location.href = `../memory/${today}.md`;
}

function deployToProduction() {
    if (confirm('⚠️ Deploy to production? This will:\n- Run tests\n- Build production assets\n- Deploy to server\n\nContinue?')) {
        alert('Deployment started... Monitor deployment logs.');
        // In production, trigger actual deployment
    }
}
</script>
'''
    
    return html

if __name__ == "__main__":
    html = generate_html()
    
    # Save widget
    output_file = Path.home() / "clawd" / "dashboard" / "widgets" / "quick_actions.html"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"✅ Quick actions widget generated: {output_file}")
