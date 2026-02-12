# Fitness Dashboard - API Documentation

## Overview
RESTful API for fitness tracking. All endpoints return JSON.

Base URL: `http://localhost:3001`

---

## Endpoints

### GET /
**Description:** Main dashboard page  
**Returns:** HTML page

---

### GET /api/summary
**Description:** Get summary statistics  
**Returns:**
```json
{
  "today_calories": 1850,
  "calorie_goal": 2200,
  "week_workouts": 3,
  "latest_weight": 225,
  "today_protein": 175,
  "protein_goal": 200
}
```

---

### GET /api/calories
**Description:** Get all calorie entries  
**Returns:**
```json
[
  {
    "date": "2025-02-11",
    "calories": 650,
    "meal": "Chicken and rice",
    "timestamp": "2025-02-11T12:30:00"
  }
]
```

---

### POST /api/calories
**Description:** Log calorie entry  
**Body:**
```json
{
  "date": "2025-02-11",
  "calories": 650,
  "meal": "Chicken and rice"
}
```
**Returns:**
```json
{
  "status": "success",
  "entry": {
    "date": "2025-02-11",
    "calories": 650,
    "meal": "Chicken and rice",
    "timestamp": "2025-02-11T12:30:45.123456"
  }
}
```

---

### GET /api/workouts
**Description:** Get all workout entries  
**Returns:**
```json
[
  {
    "date": "2025-02-11",
    "type": "Chest",
    "notes": "Great pump!"
  }
]
```

---

### POST /api/workouts
**Description:** Log workout  
**Body:**
```json
{
  "date": "2025-02-11",
  "type": "Chest",
  "notes": "Great pump!"
}
```
**Returns:**
```json
{
  "status": "success",
  "entry": {
    "date": "2025-02-11",
    "type": "Chest",
    "notes": "Great pump!"
  }
}
```

---

### GET /api/weight
**Description:** Get all weight entries  
**Returns:**
```json
[
  {
    "date": "2025-02-08",
    "weight": 225
  }
]
```

---

### POST /api/weight
**Description:** Log weight measurement  
**Body:**
```json
{
  "date": "2025-02-08",
  "weight": 225
}
```
**Returns:**
```json
{
  "status": "success",
  "entry": {
    "date": "2025-02-08",
    "weight": 225
  }
}
```

---

### GET /api/macros
**Description:** Get all macro entries  
**Returns:**
```json
[
  {
    "date": "2025-02-11",
    "protein": 45,
    "meal": "Chicken breast",
    "timestamp": "2025-02-11T12:30:00"
  }
]
```

---

### POST /api/macros
**Description:** Log macro entry  
**Body:**
```json
{
  "date": "2025-02-11",
  "protein": 45,
  "meal": "Chicken breast"
}
```
**Returns:**
```json
{
  "status": "success",
  "entry": {
    "date": "2025-02-11",
    "protein": 45,
    "meal": "Chicken breast",
    "timestamp": "2025-02-11T12:30:45.123456"
  }
}
```

---

## Example Usage

### Using curl

**Get summary:**
```bash
curl http://localhost:3001/api/summary
```

**Log a meal:**
```bash
curl -X POST http://localhost:3001/api/calories \
  -H "Content-Type: application/json" \
  -d '{"date":"2025-02-11","calories":650,"meal":"Chicken and rice"}'
```

**Log a workout:**
```bash
curl -X POST http://localhost:3001/api/workouts \
  -H "Content-Type: application/json" \
  -d '{"date":"2025-02-11","type":"Chest","notes":"Great session"}'
```

**Log weight:**
```bash
curl -X POST http://localhost:3001/api/weight \
  -H "Content-Type: application/json" \
  -d '{"date":"2025-02-11","weight":224.5}'
```

### Using Python

```python
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:3001"

# Get summary
response = requests.get(f"{BASE_URL}/api/summary")
summary = response.json()
print(f"Today's calories: {summary['today_calories']}")

# Log a meal
meal_data = {
    "date": datetime.now().strftime("%Y-%m-%d"),
    "calories": 650,
    "meal": "Chicken and rice"
}
response = requests.post(f"{BASE_URL}/api/calories", json=meal_data)
print(response.json())

# Log a workout
workout_data = {
    "date": datetime.now().strftime("%Y-%m-%d"),
    "type": "Chest",
    "notes": "Bench press PR!"
}
response = requests.post(f"{BASE_URL}/api/workouts", json=workout_data)
print(response.json())
```

### Using JavaScript (fetch)

```javascript
// Get summary
fetch('http://localhost:3001/api/summary')
  .then(response => response.json())
  .then(data => console.log(data));

// Log a meal
fetch('http://localhost:3001/api/calories', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    date: new Date().toISOString().split('T')[0],
    calories: 650,
    meal: 'Chicken and rice'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## Data Format

### Date Format
All dates use ISO 8601 format: `YYYY-MM-DD`  
Example: `"2025-02-11"`

### Timestamp Format
Auto-generated timestamps use ISO 8601: `YYYY-MM-DDTHH:MM:SS`  
Example: `"2025-02-11T12:30:45.123456"`

### Weight Format
Numeric value in pounds (can include decimals)  
Example: `224.5`

### Workout Types
Predefined types (can be extended):
- `Legs`
- `Chest`
- `Back`
- `Arms`
- `Shoulders`
- `Cardio`

---

## Integration Ideas

### Siri Shortcuts
Create iOS shortcuts to POST data via API from your phone

### Automation
Write scripts to auto-import from MyFitnessPal, Apple Health, etc.

### Voice Commands
Integrate with voice assistant to log meals hands-free

### Wearables
Pull workout data from Apple Watch or Fitbit

---

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200` - Success
- `400` - Bad request (invalid data)
- `404` - Endpoint not found
- `500` - Server error

Error response format:
```json
{
  "status": "error",
  "message": "Description of error"
}
```

---

## Future Enhancements

Potential API additions:
- `DELETE` endpoints to remove entries
- `PUT` endpoints to update existing entries
- Filter by date range: `/api/calories?start=2025-02-01&end=2025-02-11`
- Aggregate stats: `/api/stats/weekly`, `/api/stats/monthly`
- Export data: `/api/export?format=csv`
- Goal tracking: `/api/goals`
- Photo uploads for meals
- Exercise details (sets, reps, weight)

---

## Database Migration Path

When ready to migrate from JSON to database:

1. Keep API interface identical
2. Replace JSON file I/O with SQLAlchemy/SQLite
3. Run migration script to import existing JSON data
4. No frontend changes needed!

Example migration script structure:
```python
from app import init_db
import json

def migrate():
    # Read JSON files
    with open('data/calories.json') as f:
        calories = json.load(f)
    
    # Insert into database
    for entry in calories:
        db.session.add(CalorieEntry(**entry))
    
    db.session.commit()
```

---

For questions or feature requests, ask Jarvis! 🤖
