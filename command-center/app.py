#!/usr/bin/env python3
"""
Master Command Center - Ross's Single Dashboard Hub
Central hub showing all services, dashboards, files, and activity
"""

from flask import Flask, render_template, jsonify, request
import os
import json
import socket
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import glob

app = Flask(__name__)

# Base paths
CLAWD_PATH = Path.home() / 'clawd'
MEMORY_PATH = CLAWD_PATH / 'memory'
REPORTS_PATH = CLAWD_PATH / 'reports'

# Service configurations
SERVICES = [
    {'name': 'Fitness Tracker', 'port': 3001, 'url': 'http://localhost:3001'},
    {'name': 'Org Chart Dashboard', 'port': 8080, 'url': 'http://localhost:8080'},
    {'name': 'Command Center', 'port': 5000, 'url': 'http://localhost:5000'},
]

# File-based services
FILE_SERVICES = [
    {'name': 'NBA Rankings', 'path': REPORTS_PATH / 'nba_rankings.md'},
]

# Important files
KEY_FILES = [
    {'name': 'GOALS.md', 'path': CLAWD_PATH / 'GOALS.md', 'category': 'Planning'},
    {'name': 'MEMORY.md', 'path': CLAWD_PATH / 'MEMORY.md', 'category': 'Memory'},
    {'name': 'BUILD_QUEUE.md', 'path': CLAWD_PATH / 'BUILD_QUEUE.md', 'category': 'Development'},
    {'name': 'WEEKEND_BUILD.md', 'path': CLAWD_PATH / 'WEEKEND_BUILD.md', 'category': 'Development'},
    {'name': 'NBA Rankings', 'path': REPORTS_PATH / 'nba_rankings.md', 'category': 'Reports'},
    {'name': 'Cost Summary', 'path': MEMORY_PATH / 'cost_summary.json', 'category': 'Finance'},
]

def check_port(port):
    """Check if a port is open/service is running"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def get_file_status(filepath):
    """Get file modification time and status"""
    if filepath.exists():
        mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
        time_ago = datetime.now() - mtime
        if time_ago < timedelta(hours=1):
            status = 'recent'
        elif time_ago < timedelta(days=1):
            status = 'today'
        else:
            status = 'older'
        return {
            'exists': True,
            'modified': mtime.strftime('%Y-%m-%d %H:%M'),
            'time_ago': format_time_ago(time_ago),
            'status': status
        }
    return {'exists': False}

def format_time_ago(delta):
    """Format timedelta to human-readable string"""
    if delta < timedelta(minutes=1):
        return 'just now'
    elif delta < timedelta(hours=1):
        mins = int(delta.total_seconds() / 60)
        return f'{mins}m ago'
    elif delta < timedelta(days=1):
        hours = int(delta.total_seconds() / 3600)
        return f'{hours}h ago'
    else:
        days = delta.days
        return f'{days}d ago'

def get_recent_builds():
    """Get recent builds from memory files"""
    builds = []
    try:
        # Check last 7 days of memory files
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            memory_file = MEMORY_PATH / f'{date}.md'
            if memory_file.exists():
                content = memory_file.read_text()
                # Look for build mentions (simple pattern matching)
                for line in content.split('\n'):
                    if 'build' in line.lower() or 'completed' in line.lower():
                        builds.append({
                            'date': date,
                            'description': line.strip()[:100]
                        })
    except Exception as e:
        print(f"Error reading builds: {e}")
    return builds[:10]  # Last 10 builds

def get_cost_summary():
    """Get today's cost summary"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        cost_file = MEMORY_PATH / f'cost-log-{today}.json'
        if cost_file.exists():
            data = json.loads(cost_file.read_text())
            return {
                'today': data.get('total_cost', 0),
                'breakdown': data.get('breakdown', {})
            }
    except Exception as e:
        print(f"Error reading costs: {e}")
    return {'today': 0, 'breakdown': {}}

def get_calendar_events():
    """Get today's calendar events (placeholder for now)"""
    # This would integrate with Google Calendar API
    return [
        {'time': 'No calendar integration yet', 'event': 'Configure Google Calendar API'}
    ]

def get_system_health():
    """Check system health indicators"""
    alerts = []
    
    # Check disk space
    try:
        result = subprocess.run(['df', '-h', str(Path.home())], 
                              capture_output=True, text=True, timeout=5)
        # Simple check - if usage > 90%, alert
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) > 4:
                    usage = parts[4].rstrip('%')
                    if int(usage) > 90:
                        alerts.append({'level': 'warning', 'message': f'Disk usage at {usage}%'})
    except Exception as e:
        print(f"Disk check error: {e}")
    
    # Check if key services are down
    for service in SERVICES:
        if service['port'] != 5000 and not check_port(service['port']):
            alerts.append({'level': 'info', 'message': f'{service["name"]} is not running'})
    
    return alerts

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """Get all service statuses"""
    services_status = []
    
    # Check port-based services
    for service in SERVICES:
        is_running = check_port(service['port'])
        services_status.append({
            'name': service['name'],
            'url': service['url'],
            'status': 'running' if is_running else 'down',
            'type': 'service'
        })
    
    # Check file-based services
    for service in FILE_SERVICES:
        file_status = get_file_status(service['path'])
        services_status.append({
            'name': service['name'],
            'status': 'available' if file_status['exists'] else 'missing',
            'modified': file_status.get('modified', 'N/A'),
            'time_ago': file_status.get('time_ago', 'N/A'),
            'type': 'file',
            'path': str(service['path'])
        })
    
    return jsonify(services_status)

@app.route('/api/files')
def api_files():
    """Get key files status"""
    files_status = []
    
    for file_info in KEY_FILES:
        file_status = get_file_status(file_info['path'])
        files_status.append({
            'name': file_info['name'],
            'category': file_info['category'],
            'path': str(file_info['path']),
            'exists': file_status['exists'],
            'modified': file_status.get('modified', 'N/A'),
            'time_ago': file_status.get('time_ago', 'N/A'),
            'status': file_status.get('status', 'missing')
        })
    
    return jsonify(files_status)

@app.route('/api/activity')
def api_activity():
    """Get recent activity"""
    return jsonify({
        'builds': get_recent_builds(),
        'costs': get_cost_summary(),
        'calendar': get_calendar_events(),
        'alerts': get_system_health()
    })

@app.route('/api/search')
def api_search():
    """Search for files and services"""
    query = request.args.get('q', '').lower()
    results = []
    
    # Search services
    for service in SERVICES + FILE_SERVICES:
        if query in service['name'].lower():
            results.append({
                'type': 'service',
                'name': service['name'],
                'url': service.get('url', service.get('path', ''))
            })
    
    # Search files
    for file_info in KEY_FILES:
        if query in file_info['name'].lower():
            results.append({
                'type': 'file',
                'name': file_info['name'],
                'path': str(file_info['path'])
            })
    
    return jsonify(results)

if __name__ == '__main__':
    print("🚀 Master Command Center starting on http://localhost:5000")
    print("📊 Dashboard ready - your central hub for everything!")
    app.run(host='0.0.0.0', port=5000, debug=True)
