#!/usr/bin/env python3
"""
Morning Brief Generator
Aggregates data from multiple sources and generates 3-question brief
Sends to Ross via Telegram at 7:30am CST daily
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

# Paths
WORKSPACE = Path.home() / "clawd"
DATA_DIR = WORKSPACE / "data"
MEMORY_DIR = WORKSPACE / "memory"
LOG_DIR = WORKSPACE / "logs"
LOG_FILE = LOG_DIR / "morning-brief.log"

# Ensure log directory exists
LOG_DIR.mkdir(exist_ok=True)


def log(message):
    """Log to file and stdout"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open(LOG_FILE, "a") as f:
        f.write(log_msg + "\n")


def load_json_safe(filepath, default=None):
    """Safely load JSON file with fallback"""
    try:
        if Path(filepath).exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        else:
            log(f"⚠️  File not found: {filepath}")
            return default
    except Exception as e:
        log(f"❌ Error loading {filepath}: {e}")
        return default


def get_top_tasks():
    """Get top priority tasks from task queue"""
    try:
        task_data = load_json_safe(DATA_DIR / "task-queue.json", {"tasks": []})
        tasks = task_data.get("tasks", [])
        
        # Filter out completed tasks and sort by priority
        active_tasks = [t for t in tasks if not t.get("completed", False)]
        active_tasks.sort(key=lambda x: x.get("priority", 0), reverse=True)
        
        # Get top 3 tasks
        top_3 = active_tasks[:3]
        
        if not top_3:
            return ["No active tasks in queue - time to add some goals!"]
        
        return [f"{t['title']} (Priority: {t.get('priority', 0)})" for t in top_3]
    
    except Exception as e:
        log(f"❌ Error getting tasks: {e}")
        return ["Error loading task queue"]


def get_email_summary():
    """Get flagged emails summary"""
    try:
        email_data = load_json_safe(WORKSPACE / "email_scanner_state.json", {"processed_emails": []})
        emails = email_data.get("processed_emails", [])
        
        # Filter for flagged/important emails
        flagged = [e for e in emails if e.get("flagged", False) or e.get("important", False)]
        
        if not flagged:
            return "No flagged emails - inbox clear"
        
        return f"{len(flagged)} flagged emails requiring attention"
    
    except Exception as e:
        log(f"❌ Error getting emails: {e}")
        return "Email data unavailable"


def get_revenue_status():
    """Get revenue dashboard status"""
    try:
        finance_data = load_json_safe(DATA_DIR / "financial-tracking.json", {})
        
        monthly_revenue = finance_data.get("monthly_revenue", 0)
        snapshots = finance_data.get("snapshots", [])
        goals = finance_data.get("goals", {})
        florida_fund = finance_data.get("florida_fund_balance", 0)
        florida_target = goals.get("florida_fund", 50000)
        
        # Get latest daily revenue
        daily_revenue = 0
        if snapshots:
            latest = snapshots[-1]
            daily_revenue = latest.get("revenue", 0)
        
        # Calculate progress
        florida_progress = (florida_fund / florida_target * 100) if florida_target > 0 else 0
        
        return {
            "mrr": monthly_revenue,
            "daily_revenue": daily_revenue,
            "florida_fund": florida_fund,
            "florida_target": florida_target,
            "florida_progress": florida_progress
        }
    
    except Exception as e:
        log(f"❌ Error getting revenue: {e}")
        return None


def get_weather_conditions():
    """Get weather conditions and activity scores"""
    try:
        weather_data = load_json_safe(DATA_DIR / "weather.json", {})
        locations = weather_data.get("locations", {})
        
        # Get primary location (Nolensville, TN)
        primary = None
        for loc_key, loc_data in locations.items():
            if loc_data.get("primary", False):
                primary = loc_data
                break
        
        if not primary:
            return None
        
        current = primary.get("current", {})
        activities = primary.get("activity_insights", [])
        
        # Get best activity
        best_activity = None
        if activities:
            best = max(activities, key=lambda x: x.get("score", 0))
            best_activity = f"{best['activity']}: {best['verdict']} ({best['score']}/100)"
        
        return {
            "temp": current.get("temperature", 0),
            "conditions": current.get("conditions", "Unknown"),
            "best_activity": best_activity or "No activity scores available"
        }
    
    except Exception as e:
        log(f"❌ Error getting weather: {e}")
        return None


def get_yesterday_summary():
    """Get yesterday's summary from memory files"""
    try:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        yesterday_file = MEMORY_DIR / f"{yesterday}.md"
        
        if not yesterday_file.exists():
            return "No summary from yesterday - first brief of the week!"
        
        # Read file and extract key highlights
        with open(yesterday_file, 'r') as f:
            content = f.read()
        
        # Extract headlines (lines starting with ##)
        headlines = []
        for line in content.split('\n'):
            if line.startswith('## ') and not line.startswith('## '):
                headline = line.replace('##', '').strip()
                if headline and len(headlines) < 5:
                    headlines.append(headline)
        
        if headlines:
            return "\n• ".join([""] + headlines)
        else:
            return "Activity logged yesterday - check memory for details"
    
    except Exception as e:
        log(f"❌ Error getting yesterday's summary: {e}")
        return "Yesterday's summary unavailable"


def generate_brief():
    """Generate the 3-question morning brief"""
    log("🌅 Generating morning brief...")
    
    # Gather all data
    tasks = get_top_tasks()
    email_summary = get_email_summary()
    revenue = get_revenue_status()
    weather = get_weather_conditions()
    yesterday = get_yesterday_summary()
    
    # Build the brief
    brief = {
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%A, %B %d, %Y"),
        "questions": []
    }
    
    # Question 1: What's most important today?
    q1_items = []
    if tasks:
        q1_items.extend([f"📋 {task}" for task in tasks[:3]])
    if weather:
        q1_items.append(f"☀️ Weather: {weather['temp']}°F, {weather['conditions']}")
        q1_items.append(f"🏃 {weather['best_activity']}")
    
    brief["questions"].append({
        "question": "What's most important today?",
        "answer": q1_items if q1_items else ["No high-priority items identified"]
    })
    
    # Question 2: What's about to become a problem?
    q2_items = []
    if email_summary and "flagged" in email_summary.lower():
        q2_items.append(f"📧 {email_summary}")
    
    if revenue:
        # Check if revenue is trending down
        if revenue['daily_revenue'] == 0:
            q2_items.append("💰 No revenue logged yesterday - revenue activity needed")
        
        # Check Florida Fund progress
        if revenue['florida_progress'] < 40:
            needed = revenue['florida_target'] - revenue['florida_fund']
            q2_items.append(f"🏖️ Florida Fund: ${revenue['florida_fund']:,.0f}/${revenue['florida_target']:,.0f} ({revenue['florida_progress']:.1f}%) - ${needed:,.0f} to go")
    
    if not q2_items:
        q2_items.append("✅ No critical issues detected - smooth sailing!")
    
    brief["questions"].append({
        "question": "What's about to become a problem?",
        "answer": q2_items
    })
    
    # Question 3: What did you do since last session?
    brief["questions"].append({
        "question": "What did you do since last session?",
        "answer": yesterday if yesterday else "No recent activity logged"
    })
    
    # Add summary stats
    brief["stats"] = {
        "active_tasks": len([t for t in get_top_tasks() if "Error" not in t]),
        "mrr": revenue['mrr'] if revenue else 0,
        "daily_revenue": revenue['daily_revenue'] if revenue else 0,
        "weather_temp": weather['temp'] if weather else 0,
        "weather_conditions": weather['conditions'] if weather else "Unknown"
    }
    
    log(f"✅ Brief generated with {len(brief['questions'])} questions")
    return brief


def format_brief_for_telegram(brief):
    """Format brief as clean, readable Telegram message"""
    lines = []
    lines.append(f"🌅 *Morning Brief*")
    lines.append(f"_{brief['date']}_")
    lines.append("")
    
    for i, q in enumerate(brief['questions'], 1):
        lines.append(f"*{i}. {q['question']}*")
        
        answer = q['answer']
        if isinstance(answer, list):
            for item in answer:
                lines.append(f"  {item}")
        else:
            lines.append(f"  {answer}")
        
        lines.append("")
    
    # Add stats footer
    stats = brief.get('stats', {})
    if stats:
        lines.append("─" * 30)
        lines.append(f"📊 *Quick Stats*")
        lines.append(f"• Active Tasks: {stats.get('active_tasks', 0)}")
        lines.append(f"• MRR: ${stats.get('mrr', 0):,.0f}")
        lines.append(f"• Yesterday Revenue: ${stats.get('daily_revenue', 0):,.0f}")
        lines.append(f"• Weather: {stats.get('weather_temp', 0)}°F, {stats.get('weather_conditions', 'Unknown')}")
    
    # Add Mission Control link
    lines.append("")
    lines.append("─" * 30)
    lines.append("📊 *[Open Mission Control](http://localhost:8081/mission-control)*")
    lines.append("_Your central hub for all automations, live activity, and dashboards_")
    
    return "\n".join(lines)


def send_to_telegram(message):
    """Send brief to Ross via Telegram using Clawdbot message tool"""
    try:
        # Use clawdbot CLI to send message
        cmd = [
            "clawdbot", "message", "send",
            "--channel", "telegram",
            "--target", "8412148376",  # Ross's Telegram ID
            "--message", message
        ]
        
        log(f"📤 Sending brief to Telegram...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            log("✅ Brief sent successfully!")
            return True
        else:
            log(f"❌ Failed to send: {result.stderr}")
            return False
    
    except Exception as e:
        log(f"❌ Error sending to Telegram: {e}")
        return False


def main():
    """Main execution"""
    try:
        log("=" * 60)
        log("🚀 Morning Brief Generator - Starting")
        log("=" * 60)
        
        # Generate brief
        brief = generate_brief()
        
        # Save JSON output
        output_file = LOG_DIR / "morning-brief-latest.json"
        with open(output_file, 'w') as f:
            json.dump(brief, f, indent=2)
        log(f"💾 Brief saved to {output_file}")
        
        # Format for Telegram
        telegram_message = format_brief_for_telegram(brief)
        
        # Send to Telegram
        success = send_to_telegram(telegram_message)
        
        if success:
            log("✅ Morning brief completed successfully!")
            return 0
        else:
            log("⚠️  Brief generated but not sent")
            return 1
    
    except Exception as e:
        log(f"❌ Fatal error: {e}")
        import traceback
        log(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
