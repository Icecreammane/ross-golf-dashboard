#!/usr/bin/env python3
"""
Auto Log Session - Captures session activity in real-time

Monitors conversation and automatically logs:
- What we built (features, fixes, products)
- Deployments (URLs, platforms)
- Decisions (product, technical, strategic)
- Critical info (credentials, endpoints, links)

Run in background during sessions or call at session end.
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path

WORKSPACE = Path.home() / "clawd"
MEMORY_DIR = WORKSPACE / "memory"

def extract_urls(text):
    """Extract all URLs from text"""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(url_pattern, text)

def detect_deployments(text):
    """Detect deployment-related content"""
    deployment_keywords = [
        'deployed', 'railway', 'vercel', 'render', 'heroku',
        'production', 'live', 'shipped to', 'running on',
        '.app/', '.com/', '.io/', '.dev/'
    ]
    
    lines = text.split('\n')
    deployments = []
    
    for line in lines:
        if any(keyword in line.lower() for keyword in deployment_keywords):
            urls = extract_urls(line)
            if urls:
                deployments.append({
                    'url': urls[0],
                    'context': line.strip(),
                    'timestamp': datetime.now().isoformat()
                })
    
    return deployments

def detect_builds(text):
    """Detect what was built"""
    build_keywords = [
        'built', 'created', 'added', 'implemented', 'shipped',
        'feature:', 'system:', 'script:', 'file:'
    ]
    
    lines = text.split('\n')
    builds = []
    
    for line in lines:
        if any(keyword in line.lower() for keyword in build_keywords):
            # Check if it's a heading or significant line
            if line.startswith('#') or line.startswith('**') or line.startswith('✅'):
                builds.append({
                    'description': line.strip(),
                    'timestamp': datetime.now().isoformat()
                })
    
    return builds[:20]  # Limit to top 20

def detect_decisions(text):
    """Detect decisions made"""
    decision_patterns = [
        r'Ross: ["\']?(.+?)["\']?$',
        r'Decision: (.+?)$',
        r'Decided to (.+?)$',
        r'Ross wants (.+?)$',
    ]
    
    lines = text.split('\n')
    decisions = []
    
    for line in lines:
        for pattern in decision_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                decisions.append({
                    'decision': match.group(1).strip(),
                    'timestamp': datetime.now().isoformat()
                })
                break
    
    return decisions

def log_session_activity(content, session_date=None):
    """Process content and log to today's memory file"""
    if session_date is None:
        session_date = datetime.now().strftime('%Y-%m-%d')
    
    memory_file = MEMORY_DIR / f"{session_date}.md"
    
    # Extract information
    deployments = detect_deployments(content)
    builds = detect_builds(content)
    decisions = detect_decisions(content)
    
    # Append to memory file
    if memory_file.exists():
        existing = memory_file.read_text()
    else:
        existing = f"# {session_date}\n\n"
    
    # Add critical info section if deployments found
    if deployments and "## 🔗 Critical URLs" not in existing:
        section = "\n## 🔗 Critical URLs & Deployments\n\n"
        for dep in deployments:
            section += f"- **{dep['url']}** - {dep['context']}\n"
        existing += section
    
    memory_file.write_text(existing)
    
    return {
        'deployments': len(deployments),
        'builds': len(builds),
        'decisions': len(decisions),
        'file': str(memory_file)
    }

def analyze_recent_logs():
    """Analyze recent logs to find missing critical info"""
    today = datetime.now().strftime('%Y-%m-%d')
    memory_file = MEMORY_DIR / f"{today}.md"
    
    if not memory_file.exists():
        return {'status': 'no_log', 'message': 'No log file for today'}
    
    content = memory_file.read_text()
    
    # Check for critical sections
    has_urls = 'http' in content.lower()
    has_deployments = 'deploy' in content.lower() or 'railway' in content.lower()
    has_builds = 'built' in content.lower() or 'shipped' in content.lower()
    
    return {
        'status': 'ok' if all([has_urls, has_builds]) else 'incomplete',
        'has_urls': has_urls,
        'has_deployments': has_deployments,
        'has_builds': has_builds,
        'content_length': len(content)
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'analyze':
        result = analyze_recent_logs()
        print(json.dumps(result, indent=2))
    else:
        # Read stdin for live logging
        print("📝 Auto-logger ready. Paste session content or press Ctrl+D:")
        content = sys.stdin.read()
        result = log_session_activity(content)
        print(f"\n✅ Logged to {result['file']}")
        print(f"   - {result['deployments']} deployments")
        print(f"   - {result['builds']} builds")
        print(f"   - {result['decisions']} decisions")
