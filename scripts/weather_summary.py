#!/usr/bin/env python3
"""
Quick weather summary script - Example usage of weather daemon data
"""

import json
from pathlib import Path
from datetime import datetime

DATA_FILE = Path.home() / "clawd/data/weather.json"

def format_verdict_emoji(verdict):
    """Add emoji to verdict"""
    emojis = {
        "Excellent": "🟢",
        "Good": "🟡",
        "Fair": "🟠",
        "Poor": "🔴"
    }
    return f"{emojis.get(verdict, '⚪')} {verdict}"

def main():
    if not DATA_FILE.exists():
        print("❌ Weather data not found. Run: python3 ~/clawd/scripts/weather_daemon.py")
        return
    
    with open(DATA_FILE) as f:
        data = json.load(f)
    
    last_updated = datetime.fromisoformat(data['last_updated'])
    print(f"🌤️  Weather Report")
    print(f"📅 Last updated: {last_updated.strftime('%Y-%m-%d %I:%M %p')}")
    print("=" * 60)
    print()
    
    for loc_id, loc_data in data['locations'].items():
        is_primary = "⭐" if loc_data['primary'] else "  "
        print(f"{is_primary} {loc_data['location']}")
        print("-" * 60)
        
        curr = loc_data['current']
        print(f"🌡️  {curr['temperature']}°F (feels like {curr['feels_like']}°F)")
        print(f"☁️  {curr['conditions']}")
        print(f"💧 Humidity: {curr['humidity']}%")
        print(f"💨 Wind: {curr['wind_speed']} mph")
        print()
        
        print("📊 Activity Conditions:")
        for insight in loc_data['activity_insights']:
            verdict_str = format_verdict_emoji(insight['verdict'])
            print(f"   {insight['activity']}: {verdict_str}")
            if insight['notes']:
                for note in insight['notes']:
                    print(f"      • {note}")
        print()
        
        print("📅 5-Day Forecast:")
        for day in loc_data['forecast']:
            date_obj = datetime.fromisoformat(day['date'])
            day_name = date_obj.strftime('%a %m/%d')
            print(f"   {day_name}: {day['temp_high']:.0f}°/{day['temp_low']:.0f}°F - "
                  f"{day['conditions']} (Rain: {day['rain_chance']}%, UV: {day['uv_index']:.1f})")
        print()
        print()

if __name__ == "__main__":
    main()
