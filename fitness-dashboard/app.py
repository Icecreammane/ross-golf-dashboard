#!/usr/bin/env python3
"""
Fitness Progress Dashboard - Flask Backend
Tracks calories, workouts, weight, and macros for Ross
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)

# Data file paths
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CALORIES_FILE = os.path.join(DATA_DIR, 'calories.json')
WORKOUTS_FILE = os.path.join(DATA_DIR, 'workouts.json')
WEIGHT_FILE = os.path.join(DATA_DIR, 'weight.json')
MACROS_FILE = os.path.join(DATA_DIR, 'macros.json')

# Initialize data files if they don't exist
def init_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if not os.path.exists(CALORIES_FILE):
        with open(CALORIES_FILE, 'w') as f:
            json.dump([], f)
    
    if not os.path.exists(WORKOUTS_FILE):
        # Pre-populate with initial workouts
        workouts = [
            {"date": "2025-02-08", "type": "Legs", "notes": "Previous week"},
            {"date": "2025-02-10", "type": "Legs", "notes": ""},
            {"date": "2025-02-11", "type": "Chest", "notes": ""}
        ]
        with open(WORKOUTS_FILE, 'w') as f:
            json.dump(workouts, f, indent=2)
    
    if not os.path.exists(WEIGHT_FILE):
        # Pre-populate with initial weight
        weights = [
            {"date": "2025-02-08", "weight": 225}
        ]
        with open(WEIGHT_FILE, 'w') as f:
            json.dump(weights, f, indent=2)
    
    if not os.path.exists(MACROS_FILE):
        with open(MACROS_FILE, 'w') as f:
            json.dump([], f)

init_data_files()

# Helper functions
def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/calories', methods=['GET', 'POST'])
def calories():
    if request.method == 'GET':
        data = load_json(CALORIES_FILE)
        return jsonify(data)
    
    if request.method == 'POST':
        data = load_json(CALORIES_FILE)
        new_entry = request.json
        new_entry['timestamp'] = datetime.now().isoformat()
        data.append(new_entry)
        save_json(CALORIES_FILE, data)
        return jsonify({"status": "success", "entry": new_entry})

@app.route('/api/workouts', methods=['GET', 'POST'])
def workouts():
    if request.method == 'GET':
        data = load_json(WORKOUTS_FILE)
        return jsonify(data)
    
    if request.method == 'POST':
        data = load_json(WORKOUTS_FILE)
        new_entry = request.json
        data.append(new_entry)
        save_json(WORKOUTS_FILE, data)
        return jsonify({"status": "success", "entry": new_entry})

@app.route('/api/weight', methods=['GET', 'POST'])
def weight():
    if request.method == 'GET':
        data = load_json(WEIGHT_FILE)
        return jsonify(data)
    
    if request.method == 'POST':
        data = load_json(WEIGHT_FILE)
        new_entry = request.json
        data.append(new_entry)
        save_json(WEIGHT_FILE, data)
        return jsonify({"status": "success", "entry": new_entry})

@app.route('/api/macros', methods=['GET', 'POST'])
def macros():
    if request.method == 'GET':
        data = load_json(MACROS_FILE)
        return jsonify(data)
    
    if request.method == 'POST':
        data = load_json(MACROS_FILE)
        new_entry = request.json
        new_entry['timestamp'] = datetime.now().isoformat()
        data.append(new_entry)
        save_json(MACROS_FILE, data)
        return jsonify({"status": "success", "entry": new_entry})

@app.route('/api/summary')
def summary():
    """Get summary stats for the dashboard"""
    calories = load_json(CALORIES_FILE)
    workouts = load_json(WORKOUTS_FILE)
    weights = load_json(WEIGHT_FILE)
    macros = load_json(MACROS_FILE)
    
    today = datetime.now().date().isoformat()
    
    # Today's calories
    today_calories = sum(
        entry.get('calories', 0) 
        for entry in calories 
        if entry.get('date', '').startswith(today)
    )
    
    # This week's workouts
    week_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
    week_workouts = [w for w in workouts if w.get('date', '') >= week_ago]
    
    # Latest weight
    latest_weight = weights[-1].get('weight') if weights else None
    
    # Today's protein
    today_protein = sum(
        entry.get('protein', 0)
        for entry in macros
        if entry.get('date', '').startswith(today)
    )
    
    return jsonify({
        "today_calories": today_calories,
        "calorie_goal": 2200,
        "week_workouts": len(week_workouts),
        "latest_weight": latest_weight,
        "today_protein": today_protein,
        "protein_goal": 200
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=True)
