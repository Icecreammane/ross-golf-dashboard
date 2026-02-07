from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('data/fitness.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS weights
                 (date TEXT, weight REAL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS calories
                 (date TEXT, description TEXT, amount INTEGER)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS workouts
                 (date TEXT, lift TEXT, weight REAL, reps INTEGER, estimated_1rm REAL)''')
    
    conn.commit()
    conn.close()

init_db()

def estimate_1rm(weight, reps):
    """Brzycki formula for 1RM estimation"""
    if reps == 1:
        return weight
    return weight * (36 / (37 - reps))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dashboard')
def dashboard():
    conn = sqlite3.connect('data/fitness.db')
    c = conn.cursor()
    
    # Current weight
    c.execute('SELECT weight FROM weights ORDER BY date DESC LIMIT 1')
    result = c.fetchone()
    current_weight = result[0] if result else 225
    
    # Today's calories
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('SELECT SUM(amount) FROM calories WHERE date = ?', (today,))
    result = c.fetchone()
    today_calories = result[0] if result and result[0] else 0
    
    # Latest lifts (most recent 1RM for each exercise)
    c.execute('''SELECT lift, MAX(estimated_1rm), date 
                 FROM workouts 
                 GROUP BY lift 
                 ORDER BY date DESC''')
    lifts_data = c.fetchall()
    latest_lifts = {lift: {'estimated_1rm': int(rm), 'date': date} 
                    for lift, rm, date in lifts_data}
    
    conn.close()
    
    return jsonify({
        'current_weight': current_weight,
        'target_weight': 210,
        'today_calories': int(today_calories),
        'calorie_target': 2150,
        'latest_lifts': latest_lifts
    })

@app.route('/api/chart-data')
def chart_data():
    conn = sqlite3.connect('data/fitness.db')
    c = conn.cursor()
    
    # Weight data (last 90 days)
    c.execute('''SELECT date, weight FROM weights 
                 ORDER BY date DESC LIMIT 90''')
    weight_data = [{'date': date, 'weight': weight} for date, weight in c.fetchall()]
    weight_data.reverse()  # Oldest first for charts
    
    # Calorie data (last 30 days)
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    c.execute('''SELECT date, SUM(amount) as total 
                 FROM calories 
                 WHERE date >= ? 
                 GROUP BY date 
                 ORDER BY date''', (thirty_days_ago,))
    calorie_data = [{'date': date, 'calories': total} for date, total in c.fetchall()]
    
    # Lift progress (last 90 days per exercise)
    c.execute('''SELECT lift, date, MAX(estimated_1rm) as max_1rm 
                 FROM workouts 
                 GROUP BY lift, date 
                 ORDER BY lift, date''')
    lift_rows = c.fetchall()
    
    lift_progress = {}
    for lift, date, max_1rm in lift_rows:
        if lift not in lift_progress:
            lift_progress[lift] = []
        lift_progress[lift].append({'date': date, '1rm': max_1rm})
    
    conn.close()
    
    return jsonify({
        'weight': weight_data,
        'calories': calorie_data,
        'lifts': lift_progress
    })

@app.route('/api/weekly-summary')
def weekly_summary():
    conn = sqlite3.connect('data/fitness.db')
    c = conn.cursor()
    
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    # Average weight
    c.execute('SELECT AVG(weight) FROM weights WHERE date >= ?', (seven_days_ago,))
    result = c.fetchone()
    avg_weight = round(result[0], 1) if result and result[0] else 0
    
    # Average calories
    c.execute('SELECT AVG(daily_total) FROM (SELECT SUM(amount) as daily_total FROM calories WHERE date >= ? GROUP BY date)', (seven_days_ago,))
    result = c.fetchone()
    avg_calories = int(result[0]) if result and result[0] else 0
    
    # Workout days
    c.execute('SELECT COUNT(DISTINCT date) FROM workouts WHERE date >= ?', (seven_days_ago,))
    result = c.fetchone()
    workout_days = result[0] if result else 0
    
    # Total sets logged
    c.execute('SELECT COUNT(*) FROM workouts WHERE date >= ?', (seven_days_ago,))
    result = c.fetchone()
    total_sets = result[0] if result else 0
    
    conn.close()
    
    return jsonify({
        'avg_weight': avg_weight,
        'avg_calories': avg_calories,
        'workout_days': workout_days,
        'total_sets': total_sets
    })

@app.route('/api/log-workout', methods=['POST'])
def log_workout():
    data = request.json
    lifts = data.get('lifts', [])
    
    conn = sqlite3.connect('data/fitness.db')
    c = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    for lift in lifts:
        name = lift['name']
        weight = lift['weight']
        reps = lift['reps']
        estimated_1rm = estimate_1rm(weight, reps)
        
        c.execute('INSERT INTO workouts VALUES (?, ?, ?, ?, ?)',
                  (today, name, weight, reps, estimated_1rm))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/log-food', methods=['POST'])
def log_food():
    data = request.json
    description = data.get('description', '')
    calories = data.get('calories', 0)
    
    conn = sqlite3.connect('data/fitness.db')
    c = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('INSERT INTO calories VALUES (?, ?, ?)',
              (today, description, calories))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/log-weight', methods=['POST'])
def log_weight():
    data = request.json
    weight = data.get('weight', 0)
    
    conn = sqlite3.connect('data/fitness.db')
    c = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('INSERT INTO weights VALUES (?, ?)', (today, weight))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    import os
    os.makedirs('data', exist_ok=True)
    app.run(host='0.0.0.0', port=3000, debug=True)
