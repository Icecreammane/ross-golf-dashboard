#!/usr/bin/env python3
"""
Auto Food Logger - Monitors for new food photos and auto-logs to tracker
Runs during heartbeats to catch any missed food logs
"""

import json
import os
from datetime import datetime
from pathlib import Path

MEDIA_DIR = Path.home() / ".clawdbot" / "media" / "inbound"
TRACKER_FILE = Path.home() / "clawd" / "fitness-tracker" / "fitness_data.json"
STATE_FILE = Path.home() / "clawd" / "memory" / "food_logger_state.json"

def load_state():
    """Load last processed state"""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_check": 0, "processed_files": []}

def save_state(state):
    """Save processed state"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_new_images(state):
    """Find new images since last check"""
    if not MEDIA_DIR.exists():
        return []
    
    new_images = []
    processed = set(state['processed_files'])
    
    for img_path in MEDIA_DIR.glob("*.jpg"):
        if img_path.name not in processed:
            # Get file timestamp
            mtime = img_path.stat().st_mtime
            new_images.append({
                'path': str(img_path),
                'name': img_path.name,
                'timestamp': mtime,
                'datetime': datetime.fromtimestamp(mtime)
            })
    
    return sorted(new_images, key=lambda x: x['timestamp'])

def check_if_logged(img_datetime, tracker_data):
    """Check if a meal exists near this timestamp"""
    date_str = img_datetime.strftime('%Y-%m-%d')
    time_str = img_datetime.strftime('%H:%M')
    
    # Check meals array
    for meal in tracker_data.get('meals', []):
        if meal['date'] == date_str:
            meal_time = meal.get('time', '')
            # If within 30 minutes, consider it logged
            if abs(int(time_str.split(':')[0]) - int(meal_time.split(':')[0])) <= 0:
                if abs(int(time_str.split(':')[1]) - int(meal_time.split(':')[1])) <= 30:
                    return True
    
    return False

def needs_human_analysis(img):
    """Check if image needs human vision analysis"""
    # For now, all unlogged images need analysis
    # Future: could add ML to detect food vs non-food
    return True

def generate_alert(unlogged_images):
    """Generate alert for unlogged food photos"""
    if not unlogged_images:
        return None
    
    alert = {
        "type": "unlogged_food_photos",
        "count": len(unlogged_images),
        "images": []
    }
    
    for img in unlogged_images:
        alert['images'].append({
            'path': img['path'],
            'timestamp': img['datetime'].isoformat(),
            'date': img['datetime'].strftime('%Y-%m-%d'),
            'time': img['datetime'].strftime('%H:%M')
        })
    
    return alert

def main():
    """Main monitoring loop"""
    state = load_state()
    
    # Get new images
    new_images = get_new_images(state)
    
    if not new_images:
        print("✅ No new images to process")
        return
    
    print(f"Found {len(new_images)} new images")
    
    # Load tracker data
    with open(TRACKER_FILE) as f:
        tracker_data = json.load(f)
    
    # Check which images are unlogged
    unlogged = []
    for img in new_images:
        if not check_if_logged(img['datetime'], tracker_data):
            if needs_human_analysis(img):
                unlogged.append(img)
        
        # Mark as processed
        state['processed_files'].append(img['name'])
    
    # Save state
    state['last_check'] = datetime.now().timestamp()
    save_state(state)
    
    # Generate alert if needed
    if unlogged:
        alert = generate_alert(unlogged)
        alert_file = Path.home() / "clawd" / "memory" / "food_alert.json"
        with open(alert_file, 'w') as f:
            json.dump(alert, f, indent=2)
        
        print(f"⚠️  {len(unlogged)} unlogged food photos detected")
        print("Alert saved to memory/food_alert.json")
        for img in unlogged:
            print(f"  - {img['datetime'].strftime('%Y-%m-%d %H:%M')}: {img['name']}")
    else:
        print("✅ All images accounted for in food log")

if __name__ == '__main__':
    main()
