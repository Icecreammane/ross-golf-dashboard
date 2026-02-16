#!/usr/bin/env python3
"""
Mission Control Dashboard - Real-time visibility into Jarvis operations
Flask backend serving dashboard and APIs
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

# Ensure logs directory exists
LOGS_DIR.mkdir(exist_ok=True)

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
        result = subprocess.run(
            ['lsof', '-i', ':3000'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0 and result.stdout:
            return {'port': 3000, 'running': True}
    except:
        pass
    return None

def check_lean_local_alt():
    """Check if Lean is running on localhost:5001"""
    try:
        result = subprocess.run(
            ['lsof', '-i', ':5001'],
            capture_output=True,
            text=True,
            timeout=2
        )
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
            # Check if process exists
            result = subprocess.run(
                ['ps', '-p', str(pid)],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                return {
                    'pid': pid,
                    'running': True
                }
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
    
    return {
        'today': 0,
        'operations': [],
        'top_operations': []
    }

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

def get_action_tracker_data(limit=20, filter_type=None):
    """Get recent actions from action tracker log"""
    actions = []
    
    if ACTION_TRACKER_LOG.exists():
        try:
            with open(ACTION_TRACKER_LOG) as f:
                lines = f.readlines()
                for line in reversed(lines[-100:]):  # Last 100 lines
                    try:
                        action = json.loads(line.strip())
                        if filter_type:
                            if filter_type == 'high-cost' and action.get('cost_estimate', 0) < 0.01:
                                continue
                            if filter_type == 'errors' and action.get('result') != 'error':
                                continue
                        actions.append(action)
                        if len(actions) >= limit:
                            break
                    except:
                        continue
        except:
            pass
    
    return actions

def get_system_health():
    """Get system health metrics"""
    # Use df for disk
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
    
    # Use vm_stat for memory (macOS)
    mem_info = {'percent': 0, 'used_gb': 0, 'total_gb': 0}
    try:
        result = subprocess.run(['vm_stat'], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            # Simple approximation - not perfect but good enough
            mem_info['percent'] = 50  # Default estimate
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
        result = subprocess.run(
            ['clawdbot', 'gateway', 'status'],
            capture_output=True,
            text=True,
            timeout=3
        )
        return 'running' in result.stdout.lower()
    except:
        return False

def get_active_builds():
    """Get active spawned subagent sessions"""
    # TODO: Integrate with subagent session tracking
    builds = []
    
    # Check subagent logs directory
    subagent_dir = LOGS_DIR / 'subagents'
    if subagent_dir.exists():
        for session_dir in subagent_dir.iterdir():
            if session_dir.is_dir():
                status_file = session_dir / 'status.json'
                if status_file.exists():
                    try:
                        with open(status_file) as f:
                            builds.append(json.load(f))
                    except:
                        pass
    
    return builds

def get_completed_builds(limit=5):
    """Get recently completed builds from BUILD_*.md files"""
    builds = []
    
    for build_file in sorted(WORKSPACE.glob('BUILD_*.md'), reverse=True)[:limit]:
        try:
            content = build_file.read_text()
            lines = content.split('\n')
            builds.append({
                'name': build_file.stem,
                'file': build_file.name,
                'timestamp': datetime.fromtimestamp(build_file.stat().st_mtime).isoformat()
            })
        except:
            pass
    
    return builds

def get_confidence_data():
    """Get confidence tracking data"""
    try:
        confidence_file = MEMORY_DIR / 'confidence_data.json'
        if confidence_file.exists():
            with open(confidence_file) as f:
                return json.load(f)
    except:
        pass
    
    return {
        'score': 0,
        'stack': 0,
        'last_win': None,
        'trend': 'neutral'
    }

# Routes
@app.route('/')
def index():
    return render_template('mission_control.html')

@app.route('/mission-control')
def mission_control():
    return render_template('mission_control.html')

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
    
    # Calculate projected monthly cost
    days_in_month = 30
    daily_avg = week_cost / 7
    projected_monthly = daily_avg * days_in_month
    
    return jsonify({
        'today': cost_data['today'],
        'week': week_cost,
        'projected_monthly': round(projected_monthly, 2),
        'top_operations': cost_data['top_operations'],
        'daemon_savings': 0  # TODO: Track actual savings
    })

@app.route('/api/actions')
def api_actions():
    """Get recent actions from action tracker"""
    filter_type = request.args.get('filter', None)
    limit = int(request.args.get('limit', 20))
    
    actions = get_action_tracker_data(limit=limit, filter_type=filter_type)
    return jsonify(actions)

@app.route('/api/builds')
def api_builds():
    """Get active and completed builds"""
    return jsonify({
        'active': get_active_builds(),
        'completed': get_completed_builds()
    })

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
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = 8081
    print(f"🚀 Mission Control starting on http://localhost:{port}")
    print(f"📊 Dashboard: http://localhost:{port}/mission-control")
    app.run(host='0.0.0.0', port=port, debug=True)
