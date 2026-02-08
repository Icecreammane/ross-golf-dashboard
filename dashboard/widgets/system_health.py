#!/usr/bin/env python3
"""
System Health Indicators Widget
Shows system resources, services, and uptime
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

def get_disk_usage():
    """Get disk space usage"""
    try:
        result = subprocess.run(
            ['df', '-h', str(Path.home())],
            capture_output=True,
            text=True
        )
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            return {
                'total': parts[1],
                'used': parts[2],
                'available': parts[3],
                'percent': int(parts[4].replace('%', ''))
            }
    except:
        pass
    return None

def get_memory_usage():
    """Get memory usage (macOS)"""
    try:
        result = subprocess.run(
            ['vm_stat'],
            capture_output=True,
            text=True
        )
        
        # Parse vm_stat output
        lines = result.stdout.strip().split('\n')
        stats = {}
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':')
                stats[key.strip()] = value.strip().rstrip('.')
        
        # Calculate rough memory usage
        page_size = 4096  # macOS page size
        pages_free = int(stats.get('Pages free', '0'))
        pages_active = int(stats.get('Pages active', '0'))
        pages_inactive = int(stats.get('Pages inactive', '0'))
        pages_wired = int(stats.get('Pages wired down', '0'))
        
        total_pages = pages_free + pages_active + pages_inactive + pages_wired
        used_pages = pages_active + pages_wired
        
        used_gb = (used_pages * page_size) / (1024**3)
        total_gb = (total_pages * page_size) / (1024**3)
        percent = int((used_pages / total_pages) * 100) if total_pages > 0 else 0
        
        return {
            'used_gb': f"{used_gb:.1f}",
            'total_gb': f"{total_gb:.1f}",
            'percent': percent
        }
    except:
        pass
    return None

def get_cpu_usage():
    """Get CPU usage"""
    try:
        result = subprocess.run(
            ['top', '-l', '1', '-n', '0'],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        # Parse CPU usage from top output
        for line in result.stdout.split('\n'):
            if 'CPU usage:' in line:
                # Format: "CPU usage: 5.26% user, 3.94% sys, 90.78% idle"
                parts = line.split(',')
                user = float(parts[0].split(':')[1].strip().replace('%', '').split()[0])
                sys = float(parts[1].strip().replace('%', '').split()[0])
                idle = float(parts[2].strip().replace('%', '').split()[0])
                
                used = user + sys
                return {
                    'percent': int(used),
                    'user': user,
                    'sys': sys
                }
    except:
        pass
    return None

def check_services():
    """Check status of key services"""
    services = []
    
    # Check email monitor
    pid_file = Path.home() / "clawd" / "data" / "email_monitor.pid"
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            # Check if process is running
            subprocess.run(['ps', '-p', str(pid)], capture_output=True, check=True)
            services.append({'name': 'Email Monitor', 'status': 'running', 'pid': pid})
        except:
            services.append({'name': 'Email Monitor', 'status': 'stopped', 'pid': None})
    else:
        services.append({'name': 'Email Monitor', 'status': 'not configured', 'pid': None})
    
    # Check FitTrack (if running on port 8000)
    try:
        result = subprocess.run(
            ['lsof', '-i', ':8000'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            services.append({'name': 'FitTrack', 'status': 'running', 'pid': None})
        else:
            services.append({'name': 'FitTrack', 'status': 'stopped', 'pid': None})
    except:
        services.append({'name': 'FitTrack', 'status': 'unknown', 'pid': None})
    
    return services

def get_uptime():
    """Get system uptime"""
    try:
        result = subprocess.run(
            ['uptime'],
            capture_output=True,
            text=True
        )
        
        # Parse uptime output
        output = result.stdout.strip()
        if 'up' in output:
            uptime_part = output.split('up')[1].split(',')[0].strip()
            return uptime_part
    except:
        pass
    return "Unknown"

def generate_html():
    """Generate system health widget"""
    
    disk = get_disk_usage()
    memory = get_memory_usage()
    cpu = get_cpu_usage()
    services = check_services()
    uptime = get_uptime()
    
    html = '''
<div class="health-widget">
    <div class="widget-header">
        <h3>💓 System Health</h3>
        <span class="uptime-badge">🕐 Uptime: {}</span>
    </div>
    
    <div class="health-grid">
'''.format(uptime)
    
    # CPU Card
    if cpu:
        cpu_color = '#10b981' if cpu['percent'] < 70 else '#f59e0b' if cpu['percent'] < 90 else '#ef4444'
        html += f'''
        <div class="health-card">
            <div class="card-header">
                <span class="card-icon">🖥️</span>
                <span class="card-title">CPU</span>
            </div>
            <div class="progress-ring">
                <svg width="80" height="80">
                    <circle cx="40" cy="40" r="30" fill="none" stroke="#0f172a" stroke-width="8"/>
                    <circle cx="40" cy="40" r="30" fill="none" stroke="{cpu_color}" stroke-width="8"
                            stroke-dasharray="{cpu['percent'] * 1.88} 188.4" 
                            stroke-linecap="round" transform="rotate(-90 40 40)"/>
                </svg>
                <div class="ring-text">{cpu['percent']}%</div>
            </div>
            <div class="card-details">
                <div class="detail-row">
                    <span>User:</span>
                    <span>{cpu['user']:.1f}%</span>
                </div>
                <div class="detail-row">
                    <span>System:</span>
                    <span>{cpu['sys']:.1f}%</span>
                </div>
            </div>
        </div>
'''
    
    # Memory Card
    if memory:
        mem_color = '#10b981' if memory['percent'] < 70 else '#f59e0b' if memory['percent'] < 90 else '#ef4444'
        html += f'''
        <div class="health-card">
            <div class="card-header">
                <span class="card-icon">🧠</span>
                <span class="card-title">Memory</span>
            </div>
            <div class="progress-ring">
                <svg width="80" height="80">
                    <circle cx="40" cy="40" r="30" fill="none" stroke="#0f172a" stroke-width="8"/>
                    <circle cx="40" cy="40" r="30" fill="none" stroke="{mem_color}" stroke-width="8"
                            stroke-dasharray="{memory['percent'] * 1.88} 188.4" 
                            stroke-linecap="round" transform="rotate(-90 40 40)"/>
                </svg>
                <div class="ring-text">{memory['percent']}%</div>
            </div>
            <div class="card-details">
                <div class="detail-row">
                    <span>Used:</span>
                    <span>{memory['used_gb']} GB</span>
                </div>
                <div class="detail-row">
                    <span>Total:</span>
                    <span>{memory['total_gb']} GB</span>
                </div>
            </div>
        </div>
'''
    
    # Disk Card
    if disk:
        disk_color = '#10b981' if disk['percent'] < 70 else '#f59e0b' if disk['percent'] < 90 else '#ef4444'
        html += f'''
        <div class="health-card">
            <div class="card-header">
                <span class="card-icon">💾</span>
                <span class="card-title">Disk</span>
            </div>
            <div class="progress-ring">
                <svg width="80" height="80">
                    <circle cx="40" cy="40" r="30" fill="none" stroke="#0f172a" stroke-width="8"/>
                    <circle cx="40" cy="40" r="30" fill="none" stroke="{disk_color}" stroke-width="8"
                            stroke-dasharray="{disk['percent'] * 1.88} 188.4" 
                            stroke-linecap="round" transform="rotate(-90 40 40)"/>
                </svg>
                <div class="ring-text">{disk['percent']}%</div>
            </div>
            <div class="card-details">
                <div class="detail-row">
                    <span>Used:</span>
                    <span>{disk['used']}</span>
                </div>
                <div class="detail-row">
                    <span>Available:</span>
                    <span>{disk['available']}</span>
                </div>
            </div>
        </div>
'''
    
    html += '''
    </div>
    
    <div class="services-section">
        <div class="services-header">🔧 Services</div>
        <div class="services-list">
'''
    
    # Services
    for service in services:
        status_color = {
            'running': '#10b981',
            'stopped': '#ef4444',
            'not configured': '#64748b',
            'unknown': '#f59e0b'
        }.get(service['status'], '#64748b')
        
        status_icon = {
            'running': '✅',
            'stopped': '❌',
            'not configured': '⚙️',
            'unknown': '❓'
        }.get(service['status'], '•')
        
        html += f'''
            <div class="service-item">
                <span class="service-name">{service['name']}</span>
                <span class="service-status" style="color: {status_color};">
                    {status_icon} {service['status'].title()}
                </span>
            </div>
'''
    
    html += '''
        </div>
    </div>
    
    <div class="widget-footer">
        <button onclick="refreshHealth()">
            🔄 Refresh
        </button>
        <button onclick="viewDetailedStats()">
            📊 Details
        </button>
    </div>
</div>

<style>
.health-widget {
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

.uptime-badge {
    font-size: 12px;
    color: #94a3b8;
    background: #0f172a;
    padding: 4px 10px;
    border-radius: 12px;
}

.health-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 20px;
}

.health-card {
    background: #0f172a;
    padding: 20px;
    border-radius: 10px;
}

.card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 15px;
}

.card-icon {
    font-size: 24px;
}

.card-title {
    font-size: 14px;
    font-weight: 600;
    color: #e2e8f0;
}

.progress-ring {
    position: relative;
    width: 80px;
    height: 80px;
    margin: 0 auto 15px;
}

.ring-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 18px;
    font-weight: 600;
    color: #e2e8f0;
}

.card-details {
    font-size: 13px;
}

.detail-row {
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    color: #94a3b8;
}

.detail-row span:last-child {
    color: #e2e8f0;
    font-weight: 600;
}

.services-section {
    background: #0f172a;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 15px;
}

.services-header {
    font-size: 14px;
    font-weight: 600;
    color: #94a3b8;
    margin-bottom: 10px;
}

.services-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.service-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px;
    background: #1e293b;
    border-radius: 6px;
}

.service-name {
    font-size: 13px;
    color: #e2e8f0;
}

.service-status {
    font-size: 12px;
    font-weight: 600;
}

.widget-footer {
    display: flex;
    gap: 10px;
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
function refreshHealth() {
    location.reload();
}

function viewDetailedStats() {
    alert('Detailed system stats:\n\nUse Activity Monitor (macOS) or htop for detailed resource monitoring.');
}
</script>
'''
    
    return html

if __name__ == "__main__":
    html = generate_html()
    
    # Save widget
    output_file = Path.home() / "clawd" / "dashboard" / "widgets" / "system_health.html"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"✅ System health widget generated: {output_file}")
    
    # Print current stats
    cpu = get_cpu_usage()
    memory = get_memory_usage()
    disk = get_disk_usage()
    
    if cpu:
        print(f"   CPU: {cpu['percent']}%")
    if memory:
        print(f"   Memory: {memory['percent']}%")
    if disk:
        print(f"   Disk: {disk['percent']}%")
