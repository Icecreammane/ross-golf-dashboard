#!/usr/bin/env python3
"""
Mission Control Dashboard v3 - The Central Hub
Real-time visibility into Jarvis operations + automation control + memory health
"""

from flask import Flask, render_template, jsonify, send_from_directory, request
import json
import os
import subprocess
import glob
from datetime import datetime, timedelta
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mission-control-jarvis-2026'

WORKSPACE = Path('/Users/clawdbot/clawd')
LOGS_DIR = WORKSPACE / 'logs'
MEMORY_DIR = WORKSPACE / 'memory'
ACTION_TRACKER_LOG = LOGS_DIR / 'action-tracker.jsonl'
HEARTBEAT_STATE = MEMORY_DIR / 'heartbeat-state.json'

# Ensure logs directory exists
LOGS_DIR.mkdir(exist_ok=True)

# =============================================================================
# ACTIVITY FEED - Real-time action tracking
# =============================================================================

def get_live_activity(limit=20):
    """Get recent actions from action tracker - LIVE FEED"""
    actions = []
    
    if ACTION_TRACKER_LOG.exists():
        try:
            with open(ACTION_TRACKER_LOG) as f:
                lines = f.readlines()
                for line in reversed(lines[-200:]):  # Last 200 lines
                    try:
                        action = json.loads(line.strip())
                        # Format for display
                        action['display_time'] = format_relative_time(action['timestamp'])
                        action['status_icon'] = get_status_icon(action)
                        actions.append(action)
                        if len(actions) >= limit:
                            break
                    except:
                        continue
        except:
            pass
    
    return actions

def get_status_icon(action):
    """Get emoji icon based on action result"""
    result = action.get('result', 'unknown')
    tool = action.get('tool', '')
    
    if result == 'error':
        return '❌'
    elif result == 'success':
        # Tool-specific icons
        if 'email' in tool.lower():
            return '📧'
        elif 'web' in tool.lower() or 'search' in tool.lower():
            return '🔍'
        elif 'exec' in tool.lower() or 'build' in tool.lower():
            return '⚙️'
        elif 'write' in tool.lower() or 'file' in tool.lower():
            return '📝'
        elif 'cost' in action.get('action', '').lower():
            return '💰'
        elif 'fitness' in action.get('action', '').lower() or 'lean' in action.get('action', '').lower():
            return '💪'
        elif 'job' in action.get('action', '').lower():
            return '💼'
        elif 'flight' in action.get('action', '').lower():
            return '✈️'
        else:
            return '✅'
    else:
        return '🔵'  # In progress

def format_relative_time(timestamp):
    """Format timestamp as relative time (e.g., '2 min ago')"""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        diff = now - dt
        
        seconds = diff.total_seconds()
        if seconds < 60:
            return 'just now'
        elif seconds < 3600:
            mins = int(seconds / 60)
            return f'{mins} min ago'
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f'{hours}h ago'
        else:
            days = int(seconds / 86400)
            return f'{days}d ago'
    except:
        return timestamp

def is_currently_active():
    """Check if Jarvis is currently doing something (activity in last 30 seconds)"""
    if ACTION_TRACKER_LOG.exists():
        try:
            with open(ACTION_TRACKER_LOG) as f:
                lines = f.readlines()
                if lines:
                    last_action = json.loads(lines[-1].strip())
                    dt = datetime.fromisoformat(last_action['timestamp'].replace('Z', '+00:00'))
                    now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
                    diff = (now - dt).total_seconds()
                    return diff < 30
        except:
            pass
    return False

# =============================================================================
# AUTOMATIONS STATUS - What's running automatically
# =============================================================================

def get_automations_status():
    """Get status of all automated tasks"""
    state = {}
    if HEARTBEAT_STATE.exists():
        try:
            with open(HEARTBEAT_STATE) as f:
                state = json.load(f)
        except:
            pass
    
    automations = [
        {
            'name': 'Morning Brief',
            'icon': '🌅',
            'status': 'active',
            'last_run': state.get('morning_brief_sent'),
            'next_run': 'Tomorrow 7:30am',
            'result': 'Delivered to Telegram',
            'enabled': True
        },
        {
            'name': 'Cost Tracking',
            'icon': '💰',
            'status': 'active',
            'last_run': state.get('daily_cost_check_done'),
            'next_run': 'End of day',
            'result': 'Monitoring spend',
            'enabled': True
        },
        {
            'name': 'Proactive Monitor',
            'icon': '🔍',
            'status': check_daemon_status(),
            'last_run': state.get('lastChecks', {}).get('email'),
            'next_run': 'Every 5 minutes',
            'result': 'Checking email/calendar/fitness',
            'enabled': True
        },
        {
            'name': 'Memory Indexing',
            'icon': '🧠',
            'status': 'active',
            'last_run': get_memory_last_update(),
            'next_run': 'Continuous',
            'result': 'Building search index',
            'enabled': True
        },
        {
            'name': 'Job Scanner',
            'icon': '💼',
            'status': 'paused',
            'last_run': None,
            'next_run': 'On demand',
            'result': 'Florida R&D roles',
            'enabled': False
        },
        {
            'name': 'Flight Monitor',
            'icon': '✈️',
            'status': 'paused',
            'last_run': None,
            'next_run': 'On demand',
            'result': 'NFL Draft Nashville → Pittsburgh',
            'enabled': False
        }
    ]
    
    return automations

def check_daemon_status():
    """Check if proactive daemon is running"""
    try:
        pid_file = LOGS_DIR / 'monitor-daemon.pid'
        if pid_file.exists():
            pid = int(pid_file.read_text().strip())
            result = subprocess.run(['ps', '-p', str(pid)], capture_output=True, timeout=2)
            return 'active' if result.returncode == 0 else 'stopped'
    except:
        pass
    return 'stopped'

def get_memory_last_update():
    """Get last memory update timestamp"""
    try:
        memory_index = MEMORY_DIR / 'memory_index.json'
        if memory_index.exists():
            return datetime.fromtimestamp(memory_index.stat().st_mtime).isoformat()
    except:
        pass
    return None

# =============================================================================
# MEMORY HEALTH - Verify persistence is working
# =============================================================================

def get_memory_health():
    """Get memory system health metrics"""
    health = {
        'status': 'healthy',
        'session_summary_updated': None,
        'files_tracked': 0,
        'topics_indexed': 0,
        'decision_logs': 0,
        'last_index_update': None,
        'index_size_mb': 0
    }
    
    # Check SESSION_SUMMARY.md
    session_summary = WORKSPACE / 'SESSION_SUMMARY.md'
    if session_summary.exists():
        health['session_summary_updated'] = datetime.fromtimestamp(
            session_summary.stat().st_mtime
        ).strftime('%b %d, %H:%M')
    
    # Check memory index
    memory_index = MEMORY_DIR / 'memory_index.json'
    if memory_index.exists():
        try:
            with open(memory_index) as f:
                index = json.load(f)
                health['files_tracked'] = len(index.get('files', {}))
                health['topics_indexed'] = len(index.get('topics', {}))
            
            health['last_index_update'] = datetime.fromtimestamp(
                memory_index.stat().st_mtime
            ).strftime('%b %d, %H:%M')
            health['index_size_mb'] = round(memory_index.stat().st_size / 1024 / 1024, 2)
        except:
            health['status'] = 'degraded'
    
    # Count decision logs
    try:
        decision_logs = list(MEMORY_DIR.glob('decision-log-*.json'))
        health['decision_logs'] = len(decision_logs)
    except:
        pass
    
    # Count daily memory files
    try:
        daily_logs = list(MEMORY_DIR.glob('20*.md'))
        health['daily_logs_count'] = len(daily_logs)
    except:
        pass
    
    return health

# =============================================================================
# QUICK LINKS - One-click access to everything
# =============================================================================

def get_quick_links():
    """Get organized quick links for dashboards and tools"""
    return {
        'daily_use': [
            {'name': '📊 Lean Tracker', 'url': 'http://localhost:5001', 'status': check_port(5001)},
            {'name': '💰 Tax Helper', 'url': 'http://localhost:5002', 'status': check_port(5002)},
            {'name': '📈 Performance Analytics', 'url': 'http://localhost:5001/analytics', 'status': check_port(5001)},
            {'name': '💼 Job Matches', 'url': '/jobs', 'status': 'paused'},
            {'name': '✈️ Flight Monitor', 'url': '/flights', 'status': 'paused'}
        ],
        'production': [
            {'name': '🏋️ Lean (Production)', 'url': 'https://lean-fitness-tracker-production.up.railway.app/', 'status': 'live'},
            {'name': '🌐 Landing Page', 'url': 'https://relaxed-malasada-fe5aa1.netlify.app/', 'status': 'live'}
        ],
        'admin': [
            {'name': '⚙️ Settings', 'url': '/settings', 'status': 'active'},
            {'name': '📝 Memory Files', 'url': f'file://{MEMORY_DIR}', 'status': 'active'},
            {'name': '🔍 Logs', 'url': f'file://{LOGS_DIR}', 'status': 'active'},
            {'name': '💸 Cost Dashboard', 'url': '/api/costs', 'status': 'active'}
        ]
    }

def check_port(port):
    """Check if service is running on port"""
    try:
        result = subprocess.run(
            ['lsof', '-i', f':{port}'],
            capture_output=True,
            text=True,
            timeout=2
        )
        return 'running' if result.returncode == 0 and result.stdout else 'stopped'
    except:
        return 'unknown'

# =============================================================================
# LEGACY ENDPOINTS (Keep for backward compatibility)
# =============================================================================

def get_service_status(name, check_func):
    """Generic service status checker"""
    try:
        status = check_func()
        return {
            'name': name,
            'status': 'running' if status else 'stopped',
            'healthy': bool(status),
            'details': status
        }
    except Exception as e:
        return {
            'name': name,
            'status': 'error',
            'healthy': False,
            'details': str(e)
        }

def check_lean_local():
    """Check if Lean is running on localhost:3000"""
    try:
        result = subprocess.run(['lsof', '-i', ':3000'], capture_output=True, text=True, timeout=2)
        if result.returncode == 0 and result.stdout:
            return {'port': 3000, 'running': True}
    except:
        pass
    return None

def check_lean_local_alt():
    """Check if Lean is running on localhost:5001"""
    try:
        result = subprocess.run(['lsof', '-i', ':5001'], capture_output=True, text=True, timeout=2)
        if result.returncode == 0 and result.stdout:
            return {'port': 5001, 'running': True}
    except:
        pass
    return None

def check_proactive_daemon():
    """Check if proactive daemon is running"""
    try:
        pid_file = LOGS_DIR / 'monitor-daemon.pid'
        if pid_file.exists():
            pid = int(pid_file.read_text().strip())
            result = subprocess.run(['ps', '-p', str(pid)], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return {'pid': pid, 'running': True}
    except:
        pass
    return None

def get_cost_data():
    """Get cost data from cost logs"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        cost_log_path = MEMORY_DIR / f'cost-log-{today}.json'
        
        if cost_log_path.exists():
            with open(cost_log_path) as f:
                data = json.load(f)
                return {
                    'today': data.get('total_cost', 0),
                    'operations': data.get('operations', []),
                    'top_operations': sorted(
                        data.get('operations', []),
                        key=lambda x: x.get('cost', 0),
                        reverse=True
                    )[:3]
                }
    except:
        pass
    
    return {'today': 0, 'operations': [], 'top_operations': []}

def get_week_cost():
    """Calculate this week's costs"""
    total = 0
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        cost_log = MEMORY_DIR / f'cost-log-{date}.json'
        if cost_log.exists():
            try:
                with open(cost_log) as f:
                    data = json.load(f)
                    total += data.get('total_cost', 0)
            except:
                pass
    return round(total, 2)

def get_system_health():
    """Get system health metrics"""
    disk_info = {'percent': 0, 'used_gb': 0, 'total_gb': 0}
    try:
        result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 5:
                    disk_info['percent'] = int(parts[4].rstrip('%'))
                    disk_info['used_gb'] = parts[2]
                    disk_info['total_gb'] = parts[1]
    except:
        pass
    
    mem_info = {'percent': 0, 'used_gb': 0, 'total_gb': 0}
    try:
        result = subprocess.run(['vm_stat'], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            mem_info['percent'] = 50
            mem_info['used_gb'] = '?'
            mem_info['total_gb'] = '?'
    except:
        pass
    
    return {
        'disk': disk_info,
        'memory': mem_info,
        'gateway': check_gateway_status()
    }

def check_gateway_status():
    """Check Clawdbot gateway status"""
    try:
        result = subprocess.run(['clawdbot', 'gateway', 'status'], capture_output=True, text=True, timeout=3)
        return 'running' in result.stdout.lower()
    except:
        return False

def get_confidence_data():
    """Get confidence tracking data"""
    try:
        confidence_file = MEMORY_DIR / 'confidence_data.json'
        if confidence_file.exists():
            with open(confidence_file) as f:
                return json.load(f)
    except:
        pass
    
    return {'score': 0, 'stack': 0, 'last_win': None, 'trend': 'neutral'}

# =============================================================================
# API ROUTES
# =============================================================================

@app.route('/')
def index():
    return render_template('mission_control.html')

@app.route('/mission-control')
def mission_control():
    return render_template('mission_control.html')

@app.route('/api/activity/live')
def api_activity_live():
    """LIVE ACTIVITY FEED - Real-time action tracking"""
    limit = int(request.args.get('limit', 20))
    actions = get_live_activity(limit=limit)
    is_active = is_currently_active()
    
    return jsonify({
        'actions': actions,
        'is_active': is_active,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/automations')
def api_automations():
    """AUTOMATIONS STATUS - What's running automatically"""
    return jsonify({
        'automations': get_automations_status(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/memory/health')
def api_memory_health():
    """MEMORY HEALTH - Verify persistence is working"""
    return jsonify(get_memory_health())

@app.route('/api/quick-links')
def api_quick_links():
    """QUICK LINKS - One-click access to everything"""
    return jsonify(get_quick_links())

# Legacy endpoints
@app.route('/api/services')
def api_services():
    """Get status of all services"""
    services = [
        get_service_status('Lean Local (3000)', check_lean_local),
        get_service_status('Lean Local (5001)', check_lean_local_alt),
        get_service_status('Proactive Daemon', check_proactive_daemon),
        {
            'name': 'Lean Production',
            'status': 'deployed',
            'healthy': True,
            'details': {'url': 'https://lean-fitness-tracker-production.up.railway.app/'}
        },
        {
            'name': 'Landing Page',
            'status': 'deployed',
            'healthy': True,
            'details': {'url': 'https://relaxed-malasada-fe5aa1.netlify.app/'}
        }
    ]
    return jsonify(services)

@app.route('/api/costs')
def api_costs():
    """Get cost data"""
    cost_data = get_cost_data()
    week_cost = get_week_cost()
    
    days_in_month = 30
    daily_avg = week_cost / 7
    projected_monthly = daily_avg * days_in_month
    
    return jsonify({
        'today': cost_data['today'],
        'week': week_cost,
        'projected_monthly': round(projected_monthly, 2),
        'top_operations': cost_data['top_operations'],
        'daemon_savings': 0
    })

@app.route('/api/actions')
def api_actions():
    """Get recent actions from action tracker (legacy)"""
    actions = get_live_activity(limit=20)
    return jsonify([a for a in actions])

@app.route('/api/health')
def api_health():
    """Get system health metrics"""
    return jsonify(get_system_health())

@app.route('/api/confidence')
def api_confidence():
    """Get confidence tracking data"""
    return jsonify(get_confidence_data())

@app.route('/api/status')
def api_status():
    """Get complete dashboard status in one call"""
    return jsonify({
        'services': api_services().get_json(),
        'costs': api_costs().get_json(),
        'health': api_health().get_json(),
        'confidence': api_confidence().get_json(),
        'memory': get_memory_health(),
        'automations': get_automations_status(),
        'activity': get_live_activity(limit=10),
        'is_active': is_currently_active(),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = 8081
    print(f"🚀 Mission Control v3 starting on http://localhost:{port}")
    print(f"📊 Dashboard: http://localhost:{port}/mission-control")
    print(f"\n✨ NEW FEATURES:")
    print(f"   • Live Activity Feed - See what Jarvis is doing right now")
    print(f"   • Automations Status - All scheduled tasks in one place")
    print(f"   • Memory Health - Verify persistence is working")
    print(f"   • Quick Links - One-click access to everything")
    print(f"\n🔴 LIVE indicator shows when Jarvis is actively working\n")
    app.run(host='0.0.0.0', port=port, debug=True)
