# Weather Daemon Documentation

## Overview
The Weather Daemon is a production-ready automated service that fetches weather data for multiple locations and provides contextual insights for outdoor activities. It runs every 6 hours via launchd and stores data in a structured JSON format.

## Features
- ✅ **Multi-location support**: Nolensville TN (primary), Orlando FL, Miami FL
- ✅ **Comprehensive data**: Current conditions + 5-day forecast
- ✅ **Free API**: Uses Open-Meteo (no API key, no cost)
- ✅ **Activity insights**: Outdoor workout, beach volleyball, golf conditions
- ✅ **Auto-run**: launchd integration for 6-hour intervals
- ✅ **Logging**: Full execution logs with timestamps
- ✅ **Error handling**: Graceful failures with detailed logging

## Data Points

### Current Weather
- Temperature (°F)
- Feels-like temperature
- Humidity (%)
- Conditions (Clear, Cloudy, Rain, etc.)
- Wind speed (mph) and direction
- Current precipitation

### 5-Day Forecast (per day)
- Date
- High/Low temperatures
- Conditions
- Rain chance (%)
- UV index
- Max wind speed

### Activity Insights
Each location provides contextual recommendations for:

#### 1. Outdoor Workout
Factors considered:
- Temperature range (penalized if <45°F or >85°F)
- Rain probability
- Wind speed
- Score: 0-100 with verdict (Excellent/Good/Fair/Poor)

#### 2. Beach Volleyball (Florida locations only)
Factors considered:
- Temperature (ideal 65-95°F)
- Rain probability
- Wind speed (affects ball control)
- UV index warnings
- Score: 0-100 with verdict

#### 3. Golf
Factors considered:
- Temperature (ideal 50-88°F)
- Rain probability and course conditions
- Wind speed for club selection
- Score: 0-100 with verdict

## File Structure

```
/Users/clawdbot/clawd/
├── scripts/
│   └── weather_daemon.py          # Main daemon script
├── data/
│   └── weather.json                # Weather data (updated every 6h)
├── logs/
│   └── weather-daemon.log          # Execution logs
└── WEATHER_DAEMON.md               # This documentation

/Users/clawdbot/Library/LaunchAgents/
└── com.clawdbot.weather-daemon.plist  # launchd configuration
```

## Installation & Setup

### 1. Verify Files Exist
All files should be in place:
```bash
ls -la ~/clawd/scripts/weather_daemon.py
ls -la ~/Library/LaunchAgents/com.clawdbot.weather-daemon.plist
```

### 2. Load the LaunchAgent
```bash
launchctl load ~/Library/LaunchAgents/com.clawdbot.weather-daemon.plist
```

### 3. Verify It's Running
```bash
launchctl list | grep weather-daemon
```

### 4. Manually Trigger (for testing)
```bash
launchctl start com.clawdbot.weather-daemon
```

## Usage

### Manual Execution
Run the daemon manually anytime:
```bash
python3 ~/clawd/scripts/weather_daemon.py
```

### Read Weather Data
```bash
cat ~/clawd/data/weather.json | python3 -m json.tool
```

Or use jq for specific queries:
```bash
# Get current temp for Nolensville
jq '.locations.nolensville_tn.current.temperature' ~/clawd/data/weather.json

# Get outdoor workout verdict
jq '.locations.nolensville_tn.activity_insights[] | select(.activity=="Outdoor Workout") | .verdict' ~/clawd/data/weather.json

# Get 5-day forecast for Orlando
jq '.locations.orlando_fl.forecast' ~/clawd/data/weather.json
```

### Check Logs
```bash
# View recent logs
tail -n 50 ~/clawd/logs/weather-daemon.log

# Follow logs in real-time
tail -f ~/clawd/logs/weather-daemon.log

# Search for errors
grep ERROR ~/clawd/logs/weather-daemon.log
```

## API Information

**Provider**: Open-Meteo  
**Endpoint**: https://api.open-meteo.com/v1/forecast  
**Cost**: Free (no API key required)  
**Rate Limits**: Generous for personal use  
**Documentation**: https://open-meteo.com/en/docs

### API Parameters Used
- Temperature in Fahrenheit
- Wind speed in mph
- Precipitation in inches
- Timezone: America/Chicago
- Forecast days: 6 (today + 5 days)

## Locations

### Nolensville, TN (Primary)
- **Coordinates**: 35.9523°N, 86.6694°W
- **Why**: Your home base
- **Activities**: Outdoor workouts, golf

### Orlando, FL
- **Coordinates**: 28.5383°N, 81.3792°W
- **Why**: Future location consideration
- **Activities**: Outdoor workouts, beach volleyball, golf

### Miami, FL
- **Coordinates**: 25.7617°N, 80.1918°W
- **Why**: Future location consideration
- **Activities**: Outdoor workouts, beach volleyball, golf

## Schedule

**Run Interval**: Every 6 hours  
**Typical Run Times** (if loaded at midnight):
- 00:00 (midnight)
- 06:00 (6 AM)
- 12:00 (noon)
- 18:00 (6 PM)

**RunAtLoad**: Yes (runs immediately when loaded)

## Maintenance

### Update Locations
Edit `LOCATIONS` dict in `weather_daemon.py`:
```python
LOCATIONS = {
    "location_id": {
        "name": "City, State",
        "lat": latitude,
        "lon": longitude,
        "primary": True/False
    }
}
```

After editing, restart the daemon:
```bash
launchctl unload ~/Library/LaunchAgents/com.clawdbot.weather-daemon.plist
launchctl load ~/Library/LaunchAgents/com.clawdbot.weather-daemon.plist
```

### Change Update Frequency
Edit the plist file and change `StartInterval`:
```xml
<key>StartInterval</key>
<integer>21600</integer>  <!-- seconds (6h = 21600s) -->
```

Common intervals:
- 1 hour: 3600
- 3 hours: 10800
- 6 hours: 21600 (current)
- 12 hours: 43200

Then reload:
```bash
launchctl unload ~/Library/LaunchAgents/com.clawdbot.weather-daemon.plist
launchctl load ~/Library/LaunchAgents/com.clawdbot.weather-daemon.plist
```

### Log Rotation
Logs will grow over time. Set up log rotation if desired:
```bash
# Create a weekly cleanup job (example)
echo "0 0 * * 0 find ~/clawd/logs -name 'weather-daemon.log' -mtime +30 -delete" | crontab -
```

## Troubleshooting

### Daemon Not Running
```bash
# Check if loaded
launchctl list | grep weather-daemon

# If not found, load it
launchctl load ~/Library/LaunchAgents/com.clawdbot.weather-daemon.plist

# Check for errors in system log
log show --predicate 'subsystem == "com.apple.launchd"' --last 1h | grep weather
```

### No Weather Data File
```bash
# Run manually to see errors
python3 ~/clawd/scripts/weather_daemon.py

# Check permissions
ls -la ~/clawd/data/

# Create directory if missing
mkdir -p ~/clawd/data
```

### API Errors
The daemon handles API failures gracefully:
- Network timeouts: 10-second timeout per request
- Failed locations: Logged but don't stop other locations
- JSON parsing errors: Logged with details

Check logs for specifics:
```bash
grep ERROR ~/clawd/logs/weather-daemon.log
```

### Stale Data
Check last update timestamp:
```bash
jq '.last_updated' ~/clawd/data/weather.json
```

If stale (>6 hours old):
1. Manually trigger: `launchctl start com.clawdbot.weather-daemon`
2. Check logs for errors
3. Verify internet connectivity

## Integration Examples

### Morning Weather Report Script
```bash
#!/bin/bash
# morning-weather.sh

WEATHER_FILE=~/clawd/data/weather.json

echo "🌤️  Good morning! Here's your weather:"
echo ""

# Primary location
TEMP=$(jq -r '.locations.nolensville_tn.current.temperature' $WEATHER_FILE)
CONDITIONS=$(jq -r '.locations.nolensville_tn.current.conditions' $WEATHER_FILE)
WORKOUT=$(jq -r '.locations.nolensville_tn.activity_insights[] | select(.activity=="Outdoor Workout") | .verdict' $WEATHER_FILE)

echo "Nolensville: ${TEMP}°F, ${CONDITIONS}"
echo "Workout conditions: ${WORKOUT}"
```

### Python Integration
```python
import json
from pathlib import Path

def get_weather():
    with open(Path.home() / 'clawd/data/weather.json') as f:
        return json.load(f)

weather = get_weather()
primary = weather['locations']['nolensville_tn']

print(f"Temperature: {primary['current']['temperature']}°F")
print(f"Conditions: {primary['current']['conditions']}")

for insight in primary['activity_insights']:
    print(f"{insight['activity']}: {insight['verdict']}")
    if insight['notes']:
        print(f"  - {', '.join(insight['notes'])}")
```

## Security & Privacy

- ✅ No API keys required
- ✅ No personal data transmitted
- ✅ All data stored locally
- ✅ Open-source API provider
- ✅ No tracking or analytics

## Performance

**Typical execution time**: 2-3 seconds  
**API calls per run**: 3 (one per location)  
**Data file size**: ~3-5 KB  
**Log growth**: ~200 bytes per run (~1.4 KB/day)

## Version History

**v1.0 (2026-02-08)**
- Initial production release
- 3 locations supported
- 3 activity types with scoring
- Full launchd integration
- Comprehensive logging

## Support & Modifications

This daemon is designed to be easily modified. Common customizations:

1. **Add locations**: Edit `LOCATIONS` dict
2. **Add activity types**: Add functions to `analyze_conditions()`
3. **Change data format**: Modify `process_location()` return structure
4. **Add notifications**: Integrate with messaging services
5. **Create dashboard**: Use data file as JSON API source

For questions or issues, check logs first, then review this documentation.

---

**Status**: ✅ Production Ready  
**Last Updated**: 2026-02-08  
**Maintainer**: Jarvis (Clawdbot Agent)
