#!/usr/bin/env python3
"""
Weather Daemon - Fetches weather data for multiple locations
Uses Open-Meteo API (free, no API key required)
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.error

# Configuration
LOCATIONS = {
    "nolensville_tn": {
        "name": "Nolensville, TN",
        "lat": 35.9523,
        "lon": -86.6694,
        "primary": True
    },
    "orlando_fl": {
        "name": "Orlando, FL",
        "lat": 28.5383,
        "lon": -81.3792,
        "primary": False
    },
    "miami_fl": {
        "name": "Miami, FL",
        "lat": 25.7617,
        "lon": -80.1918,
        "primary": False
    }
}

DATA_FILE = Path("/Users/clawdbot/clawd/data/weather.json")
LOG_FILE = Path("/Users/clawdbot/clawd/logs/weather-daemon.log")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def fetch_weather(lat, lon):
    """Fetch weather data from Open-Meteo API"""
    # API endpoint with all required parameters
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
        f"precipitation,weather_code,wind_speed_10m,wind_direction_10m"
        f"&daily=weather_code,temperature_2m_max,temperature_2m_min,"
        f"precipitation_probability_max,uv_index_max,wind_speed_10m_max"
        f"&temperature_unit=fahrenheit&wind_speed_unit=mph"
        f"&precipitation_unit=inch&timezone=America%2FChicago"
        f"&forecast_days=6"
    )
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data
    except urllib.error.URLError as e:
        logger.error(f"Failed to fetch weather data: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse weather data: {e}")
        return None


def interpret_weather_code(code):
    """Convert WMO weather code to human-readable condition"""
    conditions = {
        0: "Clear",
        1: "Mostly Clear",
        2: "Partly Cloudy",
        3: "Cloudy",
        45: "Foggy",
        48: "Foggy",
        51: "Light Drizzle",
        53: "Drizzle",
        55: "Heavy Drizzle",
        61: "Light Rain",
        63: "Rain",
        65: "Heavy Rain",
        71: "Light Snow",
        73: "Snow",
        75: "Heavy Snow",
        77: "Snow Grains",
        80: "Light Showers",
        81: "Showers",
        82: "Heavy Showers",
        85: "Light Snow Showers",
        86: "Snow Showers",
        95: "Thunderstorm",
        96: "Thunderstorm with Hail",
        99: "Severe Thunderstorm"
    }
    return conditions.get(code, "Unknown")


def analyze_conditions(location_name, current, daily):
    """Provide contextual insights for outdoor activities"""
    insights = []
    
    temp = current.get('temperature_2m', 0)
    precip_prob = daily.get('precipitation_probability_max', [0])[0]
    uv_index = daily.get('uv_index_max', [0])[0]
    wind_speed = daily.get('wind_speed_10m_max', [0])[0]
    
    # Outdoor Workout Assessment
    workout_score = 100
    workout_notes = []
    
    if temp < 32:
        workout_score -= 40
        workout_notes.append("freezing temps - dress warm")
    elif temp < 45:
        workout_score -= 20
        workout_notes.append("cold - layer up")
    elif temp > 90:
        workout_score -= 30
        workout_notes.append("very hot - hydrate well")
    elif temp > 85:
        workout_score -= 15
        workout_notes.append("hot - stay hydrated")
    
    if precip_prob > 70:
        workout_score -= 40
        workout_notes.append("high rain chance")
    elif precip_prob > 40:
        workout_score -= 20
        workout_notes.append("possible rain")
    
    if wind_speed > 20:
        workout_score -= 15
        workout_notes.append("windy conditions")
    
    if workout_score >= 80:
        workout_verdict = "Excellent"
    elif workout_score >= 60:
        workout_verdict = "Good"
    elif workout_score >= 40:
        workout_verdict = "Fair"
    else:
        workout_verdict = "Poor"
    
    insights.append({
        "activity": "Outdoor Workout",
        "verdict": workout_verdict,
        "score": workout_score,
        "notes": workout_notes if workout_notes else ["ideal conditions"]
    })
    
    # Beach Volleyball (Florida locations)
    if "FL" in location_name:
        beach_score = 100
        beach_notes = []
        
        if temp < 65:
            beach_score -= 30
            beach_notes.append("cool for beach sports")
        elif temp > 95:
            beach_score -= 25
            beach_notes.append("very hot - seek shade between games")
        
        if precip_prob > 60:
            beach_score -= 50
            beach_notes.append("rain likely - check radar")
        elif precip_prob > 30:
            beach_score -= 20
            beach_notes.append("rain possible")
        
        if wind_speed > 25:
            beach_score -= 30
            beach_notes.append("very windy - ball control difficult")
        elif wind_speed > 15:
            beach_score -= 10
            beach_notes.append("breezy - adjust serves")
        
        if uv_index > 8:
            beach_notes.append("high UV - use sunscreen")
        
        if beach_score >= 80:
            beach_verdict = "Excellent"
        elif beach_score >= 60:
            beach_verdict = "Good"
        elif beach_score >= 40:
            beach_verdict = "Fair"
        else:
            beach_verdict = "Poor"
        
        insights.append({
            "activity": "Beach Volleyball",
            "verdict": beach_verdict,
            "score": beach_score,
            "notes": beach_notes if beach_notes else ["perfect beach conditions"]
        })
    
    # Golf Assessment
    golf_score = 100
    golf_notes = []
    
    if temp < 40:
        golf_score -= 35
        golf_notes.append("cold - layers recommended")
    elif temp < 50:
        golf_score -= 15
        golf_notes.append("chilly - bring a jacket")
    elif temp > 95:
        golf_score -= 30
        golf_notes.append("very hot - early tee time advised")
    elif temp > 88:
        golf_score -= 15
        golf_notes.append("hot - stay hydrated")
    
    if precip_prob > 60:
        golf_score -= 50
        golf_notes.append("rain likely - course may be wet")
    elif precip_prob > 30:
        golf_score -= 25
        golf_notes.append("rain possible - bring rain gear")
    
    if wind_speed > 20:
        golf_score -= 20
        golf_notes.append("windy - club selection critical")
    elif wind_speed > 12:
        golf_score -= 10
        golf_notes.append("breezy - factor in wind")
    
    if golf_score >= 80:
        golf_verdict = "Excellent"
    elif golf_score >= 60:
        golf_verdict = "Good"
    elif golf_score >= 40:
        golf_verdict = "Fair"
    else:
        golf_verdict = "Poor"
    
    insights.append({
        "activity": "Golf",
        "verdict": golf_verdict,
        "score": golf_score,
        "notes": golf_notes if golf_notes else ["great conditions for golf"]
    })
    
    return insights


def process_location(location_id, location_data):
    """Fetch and process weather for a single location"""
    logger.info(f"Fetching weather for {location_data['name']}")
    
    raw_data = fetch_weather(location_data['lat'], location_data['lon'])
    if not raw_data:
        return None
    
    current = raw_data.get('current', {})
    daily = raw_data.get('daily', {})
    
    # Process current conditions
    current_processed = {
        "temperature": current.get('temperature_2m'),
        "feels_like": current.get('apparent_temperature'),
        "humidity": current.get('relative_humidity_2m'),
        "conditions": interpret_weather_code(current.get('weather_code', 0)),
        "wind_speed": current.get('wind_speed_10m'),
        "wind_direction": current.get('wind_direction_10m'),
        "precipitation": current.get('precipitation', 0)
    }
    
    # Process 5-day forecast
    forecast = []
    for i in range(1, 6):  # Skip today (index 0), get next 5 days
        forecast.append({
            "date": daily.get('time', [])[i] if i < len(daily.get('time', [])) else None,
            "temp_high": daily.get('temperature_2m_max', [])[i] if i < len(daily.get('temperature_2m_max', [])) else None,
            "temp_low": daily.get('temperature_2m_min', [])[i] if i < len(daily.get('temperature_2m_min', [])) else None,
            "conditions": interpret_weather_code(daily.get('weather_code', [])[i]) if i < len(daily.get('weather_code', [])) else "Unknown",
            "rain_chance": daily.get('precipitation_probability_max', [])[i] if i < len(daily.get('precipitation_probability_max', [])) else 0,
            "uv_index": daily.get('uv_index_max', [])[i] if i < len(daily.get('uv_index_max', [])) else 0,
            "wind_speed": daily.get('wind_speed_10m_max', [])[i] if i < len(daily.get('wind_speed_10m_max', [])) else 0
        })
    
    # Get today's daily data for activity analysis
    today_daily = {
        "precipitation_probability_max": [daily.get('precipitation_probability_max', [0])[0]],
        "uv_index_max": [daily.get('uv_index_max', [0])[0]],
        "wind_speed_10m_max": [daily.get('wind_speed_10m_max', [0])[0]]
    }
    
    insights = analyze_conditions(location_data['name'], current, today_daily)
    
    return {
        "location": location_data['name'],
        "coordinates": {
            "lat": location_data['lat'],
            "lon": location_data['lon']
        },
        "primary": location_data['primary'],
        "current": current_processed,
        "forecast": forecast,
        "activity_insights": insights
    }


def main():
    """Main execution function"""
    logger.info("=" * 60)
    logger.info("Weather daemon started")
    
    weather_data = {
        "last_updated": datetime.now().isoformat(),
        "locations": {}
    }
    
    # Fetch weather for all locations
    for location_id, location_info in LOCATIONS.items():
        try:
            processed = process_location(location_id, location_info)
            if processed:
                weather_data["locations"][location_id] = processed
                logger.info(f"✓ {location_info['name']}: {processed['current']['temperature']}°F, {processed['current']['conditions']}")
            else:
                logger.warning(f"✗ Failed to fetch data for {location_info['name']}")
        except Exception as e:
            logger.error(f"Error processing {location_info['name']}: {e}")
    
    # Save to file
    try:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE, 'w') as f:
            json.dump(weather_data, f, indent=2)
        logger.info(f"Weather data saved to {DATA_FILE}")
    except Exception as e:
        logger.error(f"Failed to save weather data: {e}")
        return 1
    
    logger.info("Weather daemon completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
