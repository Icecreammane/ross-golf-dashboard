#!/usr/bin/env python3
"""
Morning Brief V2 - Enhanced Edition
Delivers comprehensive daily brief at 7:30am via Telegram

Includes:
- Weather + clothing recommendation
- Calendar events
- Fitness targets + yesterday's performance
- Job matches with ratings
- Flight price tracking
- Quick action links
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import requests

# Paths
WORKSPACE = Path.home() / "clawd"
DATA_DIR = WORKSPACE / "data"
MEMORY_DIR = WORKSPACE / "memory"
LOG_DIR = WORKSPACE / "logs"
LOG_FILE = LOG_DIR / "morning-brief.log"

# Ross's Telegram ID
ROSS_TELEGRAM = "8412148376"

# Ensure directories exist
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


def get_weather():
    """Get weather and clothing recommendation"""
    try:
        # Use wttr.in for simple weather
        response = requests.get('https://wttr.in/Nashville?format=j1', timeout=5)
        data = response.json()
        
        current = data['current_condition'][0]
        temp_f = int(current['temp_F'])
        conditions = current['weatherDesc'][0]['value']
        
        # Clothing recommendation based on temp
        if temp_f >= 75:
            clothing = "Shorts + t-shirt"
        elif temp_f >= 60:
            clothing = "Jeans + t-shirt"
        elif temp_f >= 45:
            clothing = "Jeans + hoodie"
        elif temp_f >= 35:
            clothing = "Jeans + jacket"
        else:
            clothing = "Full winter gear"
        
        return {
            "temp": temp_f,
            "conditions": conditions,
            "clothing": clothing
        }
    except Exception as e:
        log(f"❌ Weather error: {e}")
        return {"temp": 0, "conditions": "Unknown", "clothing": "Check outside"}


def get_calendar():
    """Get today's calendar events"""
    try:
        # TODO: Integrate with Google Calendar API
        # For now, return placeholder
        return {
            "count": 0,
            "events": []
        }
    except Exception as e:
        log(f"❌ Calendar error: {e}")
        return {"count": 0, "events": []}


def get_fitness():
    """Get fitness targets and yesterday's performance"""
    try:
        fitness_data = load_json_safe(DATA_DIR / "fitness_data.json", {"workouts": [], "nutrition": []})
        
        # Fitness targets (Ross's current goals)
        target_calories = 2200
        target_protein = 200
        
        # Get yesterday's nutrition
        yesterday = (datetime.now() - timedelta(days=1)).date()
        yesterday_nutrition = [
            n for n in fitness_data.get("nutrition", [])
            if datetime.fromisoformat(n.get("date", n.get("timestamp", "2020-01-01"))).date() == yesterday
        ]
        
        total_calories = sum(n.get("calories", 0) for n in yesterday_nutrition)
        
        # Estimate protein (rough: 30% of calories, 4 cal/g)
        protein_estimate = int((total_calories * 0.30) / 4)
        protein_percent = int((protein_estimate / target_protein) * 100) if target_protein > 0 else 0
        
        return {
            "target_calories": target_calories,
            "target_protein": target_protein,
            "yesterday_calories": total_calories,
            "yesterday_protein": protein_estimate,
            "protein_percent": protein_percent
        }
    except Exception as e:
        log(f"❌ Fitness error: {e}")
        return {
            "target_calories": 2200,
            "target_protein": 200,
            "yesterday_calories": 0,
            "yesterday_protein": 0,
            "protein_percent": 0
        }


def get_jobs():
    """Get top job matches"""
    try:
        jobs_data = load_json_safe(DATA_DIR / "job_matches.json", {"jobs": []})
        jobs = jobs_data.get("jobs", [])
        
        # Get high-rated jobs (8+)
        top_jobs = [j for j in jobs if j.get("match_score", 0) >= 8]
        top_jobs = sorted(top_jobs, key=lambda x: x.get("match_score", 0), reverse=True)[:3]
        
        return {
            "count": len(top_jobs),
            "jobs": top_jobs
        }
    except Exception as e:
        log(f"❌ Jobs error: {e}")
        return {"count": 0, "jobs": []}


def get_flight_prices():
    """Get latest flight prices for NFL Draft"""
    try:
        flight_data = load_json_safe(DATA_DIR / "flight_prices.json", {"checks": []})
        
        if not flight_data.get("checks"):
            return None
        
        # Get latest check
        latest_check = flight_data["checks"][-1]
        flights = latest_check.get("flights", [])
        
        if not flights:
            return None
        
        # Get cheapest flight
        cheapest = min(flights, key=lambda x: x.get("price", 9999))
        
        return {
            "price": cheapest.get("price", 0),
            "airline": cheapest.get("airline", "Unknown"),
            "stops": cheapest.get("stops", 0),
            "date": cheapest.get("depart_date", ""),
            "url": cheapest.get("booking_url", "")
        }
    except Exception as e:
        log(f"❌ Flight error: {e}")
        return None


def format_brief_telegram(data):
    """Format brief for Telegram with proper markdown"""
    lines = []
    
    # Header
    today = datetime.now().strftime("%b %d, %Y")
    lines.append(f"🌅 **Morning Brief - {today}**")
    lines.append("")
    
    # Weather
    weather = data.get("weather", {})
    lines.append(f"☀️ **Weather:** {weather['temp']}°F, {weather['conditions']}")
    lines.append(f"   → Wear: {weather['clothing']}")
    lines.append("")
    
    # Calendar
    calendar = data.get("calendar", {})
    if calendar["count"] > 0:
        lines.append(f"📅 **Calendar:** {calendar['count']} event(s) today")
        for event in calendar["events"]:
            lines.append(f"   • {event}")
    else:
        lines.append("📅 **Calendar:** No meetings scheduled")
    lines.append("")
    
    # Fitness
    fitness = data.get("fitness", {})
    lines.append(f"💪 **Fitness:** {fitness['target_calories']} cal target, {fitness['target_protein']}g protein")
    if fitness["yesterday_calories"] > 0:
        lines.append(f"   Yesterday: {fitness['yesterday_calories']} cal ({fitness['protein_percent']}% protein hit)")
    lines.append("")
    
    # Jobs
    jobs = data.get("jobs", {})
    if jobs["count"] > 0:
        lines.append(f"💼 **Jobs:** {jobs['count']} new Florida matches")
        for job in jobs["jobs"]:
            score = job.get("match_score", 0)
            emoji = "🔥" if score >= 9 else "💚"
            lines.append(f"   {emoji} {job['title']} - {job['company']} ({job['location']})")
    else:
        lines.append("💼 **Jobs:** No new matches (run scan?)")
    lines.append("")
    
    # Flights
    flight = data.get("flight")
    if flight:
        stops_text = "nonstop" if flight["stops"] == 0 else f"{flight['stops']} stop(s)"
        lines.append(f"✈️  **NFL Draft Flight:** ${flight['price']} ({flight['airline']}, {stops_text})")
    lines.append("")
    
    # Footer
    lines.append("**[Open Mission Control](http://localhost:8081)**")
    
    return "\n".join(lines)


def send_telegram(message):
    """Send message via Telegram"""
    try:
        log("📤 Sending to Telegram...")
        
        # Try clawdbot CLI first
        try:
            cmd = [
                "clawdbot", "message", "send",
                "--channel", "telegram",
                "--target", ROSS_TELEGRAM,
                "--message", message
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                log("✅ Brief sent!")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Fallback: Save to file for manual sending
        outbox_file = WORKSPACE / "outbox" / f"morning-brief-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
        outbox_file.parent.mkdir(exist_ok=True)
        with open(outbox_file, 'w') as f:
            f.write(f"TO: {ROSS_TELEGRAM}\n")
            f.write(f"CHANNEL: telegram\n")
            f.write(f"---\n")
            f.write(message)
        
        log(f"💾 Brief saved to outbox: {outbox_file.name}")
        log("   (Send manually or via agent)")
        return True
        
    except Exception as e:
        log(f"❌ Telegram error: {e}")
        return False


def main():
    """Main execution"""
    try:
        log("=" * 60)
        log("🌅 Morning Brief V2 - Starting")
        log("=" * 60)
        
        # Gather all data
        data = {
            "weather": get_weather(),
            "calendar": get_calendar(),
            "fitness": get_fitness(),
            "jobs": get_jobs(),
            "flight": get_flight_prices()
        }
        
        # Save JSON
        output_file = LOG_DIR / "morning-brief-latest.json"
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        log(f"💾 Data saved to {output_file}")
        
        # Format and send
        message = format_brief_telegram(data)
        
        # Print preview
        log("\n" + "=" * 60)
        log("PREVIEW:")
        log("=" * 60)
        print(message)
        log("=" * 60)
        
        # Send
        success = send_telegram(message)
        
        if success:
            log("✅ Morning Brief V2 completed successfully!")
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
