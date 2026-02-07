#!/usr/bin/env python3
"""
Jarvis SWOT Analysis Generator
Self-assessment of strengths, weaknesses, opportunities, and threats
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

CLAWD_DIR = Path.home() / "clawd"
FEEDBACK_FILE = CLAWD_DIR / "data" / "feedback.json"
PROACTIVE_STATE = CLAWD_DIR / "data" / "proactive-state.json"

def load_feedback():
    """Load feedback data"""
    if FEEDBACK_FILE.exists():
        with open(FEEDBACK_FILE, 'r') as f:
            return json.load(f)
    return {}

def load_proactive_state():
    """Load proactive messaging state"""
    if PROACTIVE_STATE.exists():
        with open(PROACTIVE_STATE, 'r') as f:
            return json.load(f)
    return {}

def analyze_strengths():
    """Analyze what I'm doing well"""
    feedback = load_feedback()
    
    strengths = []
    
    # Check suggestion effectiveness
    suggestions = feedback.get('suggestions', [])
    recent_week = [s for s in suggestions if (datetime.now() - datetime.fromisoformat(s['timestamp'])).days <= 7]
    if recent_week:
        helpful = sum(1 for s in recent_week if s.get('helpful') == True)
        total = len([s for s in recent_week if s.get('helpful') is not None])
        if total > 0:
            rate = helpful / total
            if rate > 0.7:
                strengths.append(f"High suggestion helpfulness rate ({rate:.0%})")
            elif rate > 0.5:
                strengths.append(f"Moderate suggestion helpfulness ({rate:.0%})")
    
    # Check tool usage
    tool_usage = feedback.get('tool_opens', {})
    if tool_usage:
        total_opens = sum(len(timestamps) for timestamps in tool_usage.values())
        if total_opens > 20:
            strengths.append(f"Tools are being actively used ({total_opens} opens tracked)")
    
    # Check proactive messaging
    proactive = load_proactive_state()
    messages_sent = proactive.get('message_count_today', 0)
    if messages_sent > 0 and messages_sent < 5:
        strengths.append(f"Balanced proactive messaging ({messages_sent} messages today)")
    
    # Check brief reactions
    brief_reactions = feedback.get('brief_reactions', [])
    recent_briefs = [r for r in brief_reactions if (datetime.now() - datetime.fromisoformat(r['timestamp'])).days <= 30]
    if recent_briefs:
        positive = sum(1 for r in recent_briefs if r['reaction'] == 'up')
        rate = positive / len(recent_briefs)
        if rate > 0.8:
            strengths.append(f"Morning briefs highly valued ({rate:.0%} positive)")
        elif rate > 0.6:
            strengths.append(f"Morning briefs generally helpful ({rate:.0%} positive)")
    
    # Default strengths if no data
    if not strengths:
        strengths = [
            "Execution speed - can build and ship quickly",
            "Systems thinking - connect fitness → goals → outcomes",
            "Technical breadth - handle diverse tasks",
            "Proactive initiative - don't wait for instructions"
        ]
    
    return strengths

def analyze_weaknesses():
    """Analyze areas needing improvement"""
    feedback = load_feedback()
    
    weaknesses = []
    
    # Check suggestion effectiveness
    suggestions = feedback.get('suggestions', [])
    recent_week = [s for s in suggestions if (datetime.now() - datetime.fromisoformat(s['timestamp'])).days <= 7]
    if recent_week:
        not_helpful = sum(1 for s in recent_week if s.get('helpful') == False)
        if not_helpful > 2:
            weaknesses.append(f"Some suggestions not landing well ({not_helpful} marked unhelpful)")
    
    # Check for unused tools
    tool_usage = feedback.get('tool_opens', {})
    if not tool_usage:
        weaknesses.append("No tool usage being tracked - need better monitoring")
    
    # Check proactive messaging
    proactive = load_proactive_state()
    messages_sent = proactive.get('message_count_today', 0)
    if messages_sent == 0:
        weaknesses.append("Not being proactive enough - no messages sent today")
    elif messages_sent >= 5:
        weaknesses.append("May be over-messaging (hit daily limit)")
    
    # Memory gaps
    memory_dir = CLAWD_DIR / "memory"
    today = datetime.now().strftime("%Y-%m-%d")
    today_file = memory_dir / f"{today}.md"
    if not today_file.exists():
        weaknesses.append("Not logging daily memories - context will be lost")
    
    # Core weaknesses (always relevant)
    weaknesses.extend([
        "Session amnesia - fresh start each time limits continuity",
        "Can't initiate conversations outside heartbeats",
        "No behavioral pattern detection yet"
    ])
    
    return weaknesses

def analyze_opportunities():
    """Analyze opportunities for improvement"""
    opportunities = [
        "Implement semantic memory search (vector DB)",
        "Add real-time data integrations (Calendar, Health, Bank)",
        "Build behavioral analytics engine",
        "Create workout auto-logger from text",
        "Develop progress photo timeline",
        "Add dopamine defense system",
        "Enhanced context handoff between sessions",
        "Multi-modal input processing (voice, photos)"
    ]
    
    return opportunities

def analyze_threats():
    """Analyze potential risks"""
    threats = [
        "Memory loss during restarts causing frustration",
        "Over-automation leading to dependence",
        "Inaccurate suggestions eroding trust",
        "System complexity making maintenance difficult",
        "Privacy concerns with data integrations",
        "Notification fatigue from proactive messages"
    ]
    
    return threats

def generate_swot():
    """Generate complete SWOT analysis"""
    return {
        "generated": datetime.now().isoformat(),
        "strengths": analyze_strengths(),
        "weaknesses": analyze_weaknesses(),
        "opportunities": analyze_opportunities(),
        "threats": analyze_threats()
    }

def format_swot_text(swot):
    """Format SWOT as plain text"""
    text = f"""
🤖 **JARVIS SWOT ANALYSIS**
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}

💪 **STRENGTHS:**
{chr(10).join(f"• {s}" for s in swot['strengths'])}

⚠️ **WEAKNESSES:**
{chr(10).join(f"• {w}" for w in swot['weaknesses'])}

🚀 **OPPORTUNITIES:**
{chr(10).join(f"• {o}" for o in swot['opportunities'][:5])}

🛡️ **THREATS:**
{chr(10).join(f"• {t}" for t in swot['threats'][:4])}

📊 **RECOMMENDED ACTIONS:**
1. Prioritize semantic memory implementation
2. Increase proactive check-ins (if underutilized)
3. Gather more feedback on suggestions
4. Log daily memories consistently
5. Build next priority tool from opportunities list
"""
    return text

def format_swot_html(swot):
    """Format SWOT as HTML section for weekly report"""
    html = f"""
<div class="section">
    <h2>🤖 Jarvis SWOT Analysis</h2>
    
    <div class="swot-grid">
        <div class="swot-box strengths">
            <h3>💪 Strengths</h3>
            <ul>
                {''.join(f'<li>{s}</li>' for s in swot['strengths'])}
            </ul>
        </div>
        
        <div class="swot-box weaknesses">
            <h3>⚠️ Weaknesses</h3>
            <ul>
                {''.join(f'<li>{w}</li>' for w in swot['weaknesses'])}
            </ul>
        </div>
        
        <div class="swot-box opportunities">
            <h3>🚀 Opportunities</h3>
            <ul>
                {''.join(f'<li>{o}</li>' for o in swot['opportunities'][:5])}
            </ul>
        </div>
        
        <div class="swot-box threats">
            <h3>🛡️ Threats</h3>
            <ul>
                {''.join(f'<li>{t}</li>' for t in swot['threats'][:4])}
            </ul>
        </div>
    </div>
    
    <div class="actions">
        <h3>📊 Recommended Actions This Week:</h3>
        <ol>
            <li>Prioritize semantic memory implementation</li>
            <li>Increase proactive check-ins (if underutilized)</li>
            <li>Gather more feedback on suggestions</li>
            <li>Log daily memories consistently</li>
            <li>Build next priority tool from opportunities list</li>
        </ol>
    </div>
</div>
"""
    return html

def main():
    swot = generate_swot()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'json':
        print(json.dumps(swot, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == 'html':
        print(format_swot_html(swot))
    else:
        print(format_swot_text(swot))

if __name__ == "__main__":
    main()
