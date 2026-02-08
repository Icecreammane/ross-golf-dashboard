#!/usr/bin/env python3
"""
Daily Macro Tracker Automation
Sends reminders and daily summaries for protein/calorie tracking
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import subprocess

# Add parent directory to path for imports
sys.path.insert(0, str(Path.home() / "clawd"))

def load_todays_data():
    """Load today's macro data from fitness tracker"""
    # Check common data locations
    data_locations = [
        Path.home() / "clawd" / "fitness-tracker" / "data" / f"{datetime.now().strftime('%Y-%m-%d')}.json",
        Path.home() / "clawd" / "data" / "fitness" / f"{datetime.now().strftime('%Y-%m-%d')}.json",
    ]
    
    for location in data_locations:
        if location.exists():
            with open(location) as f:
                return json.load(f)
    
    # Return empty data if not found
    return {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "protein_g": 0,
        "protein_goal": 180,
        "calories": 0,
        "calories_goal": 2400,
        "meals_logged": [],
        "water_oz": 0
    }

def calculate_progress(current, goal):
    """Calculate progress percentage"""
    if goal == 0:
        return 0
    return min(int((current / goal) * 100), 100)

def get_progress_bar(percent, length=20):
    """Generate ASCII progress bar"""
    filled = int((percent / 100) * length)
    bar = '█' * filled + '░' * (length - filled)
    return bar

def send_telegram_notification(message):
    """Send notification via Telegram"""
    try:
        from security_logger import send_telegram_alert
        send_telegram_alert(message)
        return True
    except Exception as e:
        print(f"Could not send Telegram: {e}")
        return False

def generate_morning_reminder():
    """Generate morning check-in reminder"""
    data = load_todays_data()
    
    message = f"""☀️ *Good Morning!*

Time to fuel up for a great day 💪

🎯 *Today's Goals:*
• Protein: {data['protein_goal']}g
• Calories: {data['calories_goal']}
• Water: 100oz

*Quick tip:* Start with a high-protein breakfast (30g+) to stay ahead!

[Log Your Breakfast →](http://localhost:8000/quick-log)
"""
    
    return message

def generate_midday_reminder():
    """Generate midday progress check"""
    data = load_todays_data()
    
    protein_progress = calculate_progress(data['protein_g'], data['protein_goal'])
    protein_bar = get_progress_bar(protein_progress)
    
    # Determine encouragement message
    if protein_progress < 30:
        encouragement = "⚠️ *Behind pace!* Grab a protein shake or chicken."
    elif protein_progress < 50:
        encouragement = "📊 *On track!* Keep it up."
    else:
        encouragement = "🔥 *Crushing it!* You're ahead of schedule."
    
    message = f"""🕐 *Midday Check-In*

🍗 *Protein Progress:*
{protein_bar} {protein_progress}%
{data['protein_g']}g / {data['protein_goal']}g

{encouragement}

*Need a boost?*
• Protein shake: +30g
• Greek yogurt: +15g
• Chicken breast: +40g

[Log a Meal →](http://localhost:8000/quick-log)
"""
    
    return message

def generate_evening_summary():
    """Generate end-of-day summary"""
    data = load_todays_data()
    
    protein_progress = calculate_progress(data['protein_g'], data['protein_goal'])
    calorie_progress = calculate_progress(data['calories'], data['calories_goal'])
    
    protein_bar = get_progress_bar(protein_progress)
    calorie_bar = get_progress_bar(calorie_progress)
    
    # Determine status emoji
    if protein_progress >= 90:
        status = "✅ *GOAL CRUSHED!*"
    elif protein_progress >= 80:
        status = "💪 *Great Day!*"
    elif protein_progress >= 60:
        status = "👍 *Solid Effort*"
    else:
        status = "⚠️ *Tomorrow's a New Day*"
    
    message = f"""🌙 *Daily Summary*

{status}

📊 *Today's Numbers:*

🍗 Protein: {protein_bar} {protein_progress}%
{data['protein_g']}g / {data['protein_goal']}g

🔥 Calories: {calorie_bar} {calorie_progress}%
{data['calories']} / {data['calories_goal']}

🍽️ *Meals Logged:* {len(data['meals_logged'])}

💧 *Water:* {data.get('water_oz', 0)}oz

---

*Tomorrow's goal:* Hit {data['protein_goal']}g protein again! 🎯

[View Full Stats →](http://localhost:8000/dashboard)
"""
    
    return message

def generate_weekly_report():
    """Generate weekly progress report"""
    # Calculate last 7 days data
    week_data = []
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        data_file = Path.home() / "clawd" / "data" / "fitness" / f"{date.strftime('%Y-%m-%d')}.json"
        
        if data_file.exists():
            with open(data_file) as f:
                week_data.append(json.load(f))
    
    if not week_data:
        return "No weekly data available yet. Keep logging!"
    
    # Calculate averages
    avg_protein = sum(d.get('protein_g', 0) for d in week_data) / len(week_data)
    avg_calories = sum(d.get('calories', 0) for d in week_data) / len(week_data)
    days_hit_goal = sum(1 for d in week_data if d.get('protein_g', 0) >= d.get('protein_goal', 180))
    
    streak = days_hit_goal
    
    message = f"""📈 *Weekly Report*

🔥 *{streak}-Day Streak!*

📊 *7-Day Averages:*
• Protein: {avg_protein:.0f}g/day
• Calories: {avg_calories:.0f}/day
• Goal Hit Rate: {days_hit_goal}/7 days ({int(days_hit_goal/7*100)}%)

💪 *Insights:*
"""
    
    if days_hit_goal >= 6:
        message += "• 🌟 *Exceptional!* You're consistent.\n"
    elif days_hit_goal >= 4:
        message += "• 💪 *Strong week!* Keep it up.\n"
    else:
        message += "• 📊 *Room to improve.* Focus on consistency.\n"
    
    if avg_protein >= 170:
        message += "• ✅ Protein intake is solid.\n"
    else:
        message += "• ⚠️ Boost protein 20-30g/day.\n"
    
    message += "\n*Next week goal:* 7/7 days hitting protein! 🎯"
    
    return message

def send_reminder(reminder_type):
    """Send appropriate reminder based on type"""
    if reminder_type == "morning":
        message = generate_morning_reminder()
    elif reminder_type == "midday":
        message = generate_midday_reminder()
    elif reminder_type == "evening":
        message = generate_evening_summary()
    elif reminder_type == "weekly":
        message = generate_weekly_report()
    else:
        print(f"Unknown reminder type: {reminder_type}")
        return False
    
    print(f"\n{'='*60}")
    print(f"Macro Tracker - {reminder_type.title()} Reminder")
    print(f"{'='*60}")
    print(message)
    print(f"{'='*60}\n")
    
    # Send via Telegram
    if send_telegram_notification(message):
        print("✅ Sent via Telegram")
    else:
        print("📧 Telegram unavailable - printed to console")
    
    return True

def setup_cron_jobs():
    """Print cron job setup instructions"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║           MACRO TRACKER AUTOMATION SETUP                      ║
╚═══════════════════════════════════════════════════════════════╝

To automate daily reminders, add these to your crontab:

┌─ Run: crontab -e

# Morning reminder (8:00 AM)
0 8 * * * python3 ~/clawd/scripts/daily_macro_reminder.py morning

# Midday check-in (12:30 PM)
30 12 * * * python3 ~/clawd/scripts/daily_macro_reminder.py midday

# Evening summary (8:00 PM)
0 20 * * * python3 ~/clawd/scripts/daily_macro_reminder.py evening

# Weekly report (Sunday 9:00 AM)
0 9 * * 0 python3 ~/clawd/scripts/daily_macro_reminder.py weekly

└─────────────────────────────────────────────────────────────┘

Or use the quick setup script:
  bash ~/clawd/scripts/setup_macro_reminders.sh

""")

def main():
    if len(sys.argv) < 2:
        print("Usage: daily_macro_reminder.py {morning|midday|evening|weekly|setup}")
        print("\nExamples:")
        print("  python3 daily_macro_reminder.py morning   # Send morning reminder")
        print("  python3 daily_macro_reminder.py evening   # Send evening summary")
        print("  python3 daily_macro_reminder.py setup     # Show cron setup")
        return 1
    
    command = sys.argv[1]
    
    if command == "setup":
        setup_cron_jobs()
        return 0
    
    if command in ["morning", "midday", "evening", "weekly"]:
        success = send_reminder(command)
        return 0 if success else 1
    
    print(f"Unknown command: {command}")
    return 1

if __name__ == "__main__":
    exit(main())
