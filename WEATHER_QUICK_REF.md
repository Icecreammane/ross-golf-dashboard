# Weather Daemon - Quick Reference

## ⚡ Quick Commands

```bash
# View current weather data
cat ~/clawd/data/weather.json | python3 -m json.tool

# Check logs
tail -20 ~/clawd/logs/weather-daemon.log

# Run manually
python3 ~/clawd/scripts/weather_daemon.py

# Check status
launchctl list | grep weather-daemon

# Restart daemon
launchctl unload ~/Library/LaunchAgents/com.clawdbot.weather-daemon.plist
launchctl load ~/Library/LaunchAgents/com.clawdbot.weather-daemon.plist
```

## 📊 Quick Data Queries (with jq)

```bash
# Current temp in Nolensville
jq '.locations.nolensville_tn.current.temperature' ~/clawd/data/weather.json

# Workout conditions today
jq '.locations.nolensville_tn.activity_insights[] | select(.activity=="Outdoor Workout")' ~/clawd/data/weather.json

# 5-day forecast summary
jq '.locations.nolensville_tn.forecast[] | "\(.date): \(.temp_high)°F / \(.temp_low)°F - \(.conditions)"' ~/clawd/data/weather.json

# All locations current temps
jq '.locations | to_entries[] | "\(.value.location): \(.value.current.temperature)°F"' ~/clawd/data/weather.json

# Beach volleyball conditions (Orlando)
jq '.locations.orlando_fl.activity_insights[] | select(.activity=="Beach Volleyball")' ~/clawd/data/weather.json

# Last update time
jq -r '.last_updated' ~/clawd/data/weather.json
```

## 🎯 Activity Scores Quick View

```bash
# All activities for Nolensville
jq '.locations.nolensville_tn.activity_insights[] | {activity: .activity, verdict: .verdict, notes: .notes}' ~/clawd/data/weather.json

# Golf conditions all locations
jq '.locations | to_entries[] | {location: .value.location, golf: (.value.activity_insights[] | select(.activity=="Golf") | .verdict)}' ~/clawd/data/weather.json
```

## 🔧 Management

**Runs**: Every 6 hours (00:00, 06:00, 12:00, 18:00)  
**Data**: `/Users/clawdbot/clawd/data/weather.json`  
**Logs**: `/Users/clawdbot/clawd/logs/weather-daemon.log`  
**Config**: `/Users/clawdbot/Library/LaunchAgents/com.clawdbot.weather-daemon.plist`

## 📍 Locations

- **Nolensville, TN** (primary) - `nolensville_tn`
- **Orlando, FL** - `orlando_fl`  
- **Miami, FL** - `miami_fl`

## 🏃 Activity Types

1. **Outdoor Workout** - All locations
2. **Beach Volleyball** - FL locations only
3. **Golf** - All locations

Each scored 0-100: Excellent (80+), Good (60+), Fair (40+), Poor (<40)

---
📖 Full docs: `~/clawd/WEATHER_DAEMON.md`
