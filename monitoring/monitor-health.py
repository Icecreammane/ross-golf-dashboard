#!/usr/bin/env python3
"""
System Health Monitor - Check gateway, services, costs, and disk usage
Alerts only when something is genuinely wrong
"""

import json
import subprocess
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

STATE_FILE = Path(__file__).parent / 'state' / 'health-state.json'
COST_THRESHOLD = 10.0  # Alert if costs exceed $10/hour
DISK_THRESHOLD = 90  # Alert if disk usage >90%
DOWN_THRESHOLD = 300  # Alert if down >5 minutes (300 seconds)


def run_command(cmd):
    """Run shell command safely"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip(), result.returncode
    except (subprocess.TimeoutExpired, Exception) as e:
        return str(e), -1


def check_gateway():
    """Check if Clawdbot gateway is running"""
    output, code = run_command('clawdbot gateway status')
    
    if code != 0:
        return {
            'service': 'gateway',
            'status': 'down',
            'details': 'Gateway not responding'
        }
    
    # Check if output indicates running
    if 'running' in output.lower() or 'active' in output.lower():
        return {'service': 'gateway', 'status': 'up'}
    
    return {
        'service': 'gateway',
        'status': 'unknown',
        'details': output[:200]
    }


def check_disk_usage():
    """Check disk usage percentage"""
    usage = shutil.disk_usage('/')
    percent = (usage.used / usage.total) * 100
    
    if percent > DISK_THRESHOLD:
        return {
            'service': 'disk',
            'status': 'warning',
            'details': f'Disk usage at {percent:.1f}%',
            'value': percent
        }
    
    return {'service': 'disk', 'status': 'ok', 'value': percent}


def check_costs():
    """Check API costs from logs (simplified - adjust to actual log format)"""
    # Look for cost tracking in session logs or state files
    # This is a placeholder - implement based on actual cost tracking
    
    try:
        # Check if cost tracking file exists
        cost_file = Path.home() / '.config' / 'clawdbot' / 'costs.json'
        if not cost_file.exists():
            return {'service': 'costs', 'status': 'ok', 'details': 'No cost data'}
        
        with open(cost_file) as f:
            cost_data = json.load(f)
        
        # Calculate hourly rate (last hour)
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        recent_costs = [
            c for c in cost_data.get('entries', [])
            if datetime.fromisoformat(c['timestamp']) > hour_ago
        ]
        
        total_cost = sum(c.get('cost', 0) for c in recent_costs)
        
        if total_cost > COST_THRESHOLD:
            return {
                'service': 'costs',
                'status': 'warning',
                'details': f'Costs at ${total_cost:.2f}/hour',
                'value': total_cost
            }
        
        return {'service': 'costs', 'status': 'ok', 'value': total_cost}
    
    except Exception as e:
        return {
            'service': 'costs',
            'status': 'ok',
            'details': f'Cost check unavailable: {str(e)}'
        }


def check_subagents():
    """Check for running/crashed subagents"""
    # Check session directory for active subagents
    session_dir = Path.home() / '.config' / 'clawdbot' / 'sessions'
    
    if not session_dir.exists():
        return {'service': 'subagents', 'status': 'ok', 'details': 'No sessions'}
    
    # Count active subagent sessions
    try:
        subagent_files = list(session_dir.glob('*subagent*.json'))
        
        if not subagent_files:
            return {'service': 'subagents', 'status': 'ok'}
        
        # Check for stale sessions (>1 hour old, still "running")
        stale_count = 0
        for sf in subagent_files:
            try:
                with open(sf) as f:
                    data = json.load(f)
                    updated = datetime.fromisoformat(data.get('updated', data.get('created', '')))
                    if datetime.now() - updated > timedelta(hours=1):
                        stale_count += 1
            except:
                continue
        
        if stale_count > 0:
            return {
                'service': 'subagents',
                'status': 'warning',
                'details': f'{stale_count} stale subagent sessions'
            }
        
        return {
            'service': 'subagents',
            'status': 'ok',
            'details': f'{len(subagent_files)} active'
        }
    
    except Exception as e:
        return {
            'service': 'subagents',
            'status': 'ok',
            'details': 'Check unavailable'
        }


def load_state():
    """Load previous health state"""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {'down_since': {}}


def save_state(state):
    """Save current health state"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def check_health():
    """Run all health checks"""
    state = load_state()
    now = datetime.now()
    
    checks = [
        check_gateway(),
        check_disk_usage(),
        check_costs(),
        check_subagents()
    ]
    
    alerts = []
    
    for check in checks:
        service = check['service']
        status = check['status']
        
        if status == 'down':
            # Track how long it's been down
            if service not in state['down_since']:
                state['down_since'][service] = now.isoformat()
            
            down_since = datetime.fromisoformat(state['down_since'][service])
            down_seconds = (now - down_since).total_seconds()
            
            # Only alert if down >5 minutes
            if down_seconds > DOWN_THRESHOLD:
                alerts.append({
                    'severity': 'critical',
                    'service': service,
                    'message': f"{service} down for {int(down_seconds/60)} minutes",
                    'details': check.get('details', '')
                })
        
        elif status == 'warning':
            alerts.append({
                'severity': 'warning',
                'service': service,
                'message': check.get('details', f"{service} warning"),
                'value': check.get('value')
            })
            # Clear down_since if service recovered
            state['down_since'].pop(service, None)
        
        else:
            # Service is ok, clear down_since
            state['down_since'].pop(service, None)
    
    save_state(state)
    
    result = {
        'status': 'ok' if not alerts else 'alert',
        'checks': checks,
        'alerts': alerts,
        'timestamp': now.isoformat()
    }
    
    return result


if __name__ == '__main__':
    result = check_health()
    print(json.dumps(result, indent=2))
    
    # Exit code indicates alert level
    sys.exit(1 if result.get('alerts') else 0)
