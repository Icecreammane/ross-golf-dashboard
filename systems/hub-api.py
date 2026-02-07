#!/usr/bin/env python3
"""
Hub API - Unified data layer for Integration Hub
Serves data from all systems: fitness, NBA, deal flow, builds, memory
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime, date
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for local development

# Base paths
BASE_DIR = Path.home() / 'clawd'
FITNESS_DATA = BASE_DIR / 'fitness-tracker' / 'fitness_data.json'
NBA_RANKINGS = BASE_DIR / 'nba' / 'rankings.json'
DEAL_FLOW_DATA = BASE_DIR / 'revenue' / 'deal-flow' / 'opportunities.json'
BUILD_STATUS = BASE_DIR / 'logs' / 'build-status.json'
MEMORY_DIR = BASE_DIR / 'memory'
CONTEXT_STATE = MEMORY_DIR / 'context-state.json'


def load_json(filepath, default=None):
    """Safely load JSON file"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return default or {}
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return default or {}


def get_today_date():
    """Get today's date in YYYY-MM-DD format"""
    return date.today().isoformat()


@app.route('/api/hub/status')
def hub_status():
    """Overall system status"""
    try:
        # Check if key services are accessible
        fitness_ok = os.path.exists(FITNESS_DATA)
        nba_ok = os.path.exists(NBA_RANKINGS)
        dealflow_ok = os.path.exists(DEAL_FLOW_DATA)
        builds_ok = os.path.exists(BUILD_STATUS)
        
        # Get memory stats
        memory_files = list(MEMORY_DIR.glob('*.md'))
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'fitness_tracker': fitness_ok,
                'nba_rankings': nba_ok,
                'deal_flow_pipeline': dealflow_ok,
                'build_system': builds_ok,
                'memory_system': len(memory_files) > 0
            },
            'uptime': {
                'fitness_port': 3000,
                'hub_port': 8080,
                'gateway': 'running'
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500


@app.route('/api/hub/revenue')
def revenue_summary():
    """Deal Flow + Escape Velocity summary"""
    try:
        opportunities = load_json(DEAL_FLOW_DATA, {'opportunities': []})
        
        opps = opportunities.get('opportunities', [])
        
        # Calculate stats
        active_opps = [o for o in opps if o.get('status') == 'active']
        total_potential = sum(o.get('returnPotential', 0) for o in active_opps)
        avg_effort = sum(o.get('effortScore', 0) for o in active_opps) / len(active_opps) if active_opps else 0
        high_viral = [o for o in active_opps if o.get('viralPotential', 0) >= 7]
        
        # Get top opportunities by return potential
        top_opps = sorted(active_opps, key=lambda x: x.get('returnPotential', 0), reverse=True)[:5]
        
        return jsonify({
            'summary': {
                'total_opportunities': len(opps),
                'active_opportunities': len(active_opps),
                'total_potential_revenue': total_potential,
                'avg_effort_score': round(avg_effort, 1),
                'high_viral_count': len(high_viral)
            },
            'top_opportunities': [
                {
                    'title': o.get('title'),
                    'type': o.get('type'),
                    'return_potential': o.get('returnPotential'),
                    'effort_score': o.get('effortScore'),
                    'viral_potential': o.get('viralPotential')
                }
                for o in top_opps
            ],
            'escape_velocity': {
                'calculator_available': os.path.exists(BASE_DIR / 'revenue' / 'escape-velocity' / 'calculator.html'),
                'monthly_target': 5000,  # From context
                'current_runway': 'tracking'
            },
            'last_updated': opportunities.get('lastUpdated', datetime.now().isoformat())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/hub/nba')
def nba_preview():
    """Latest NBA rankings preview (Top 5)"""
    try:
        rankings = load_json(NBA_RANKINGS, {'rankings': []})
        
        top_5 = rankings.get('rankings', [])[:5]
        
        return jsonify({
            'slate_date': rankings.get('slate_date'),
            'num_games': rankings.get('num_games', 0),
            'generated_at': rankings.get('generated_at'),
            'top_5': [
                {
                    'rank': p.get('rank'),
                    'name': p.get('name'),
                    'team': p.get('team'),
                    'opponent': p.get('opponent'),
                    'projected_points': p.get('projected_fantasy_points'),
                    'ppg': round(p.get('ppg', 0), 1),
                    'rpg': round(p.get('rpg', 0), 1),
                    'apg': round(p.get('apg', 0), 1)
                }
                for p in top_5
            ],
            'dashboard_url': 'http://10.0.0.18:8000'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/hub/builds')
def builds_summary():
    """Active builds from build-status.json"""
    try:
        builds = load_json(BUILD_STATUS, {})
        
        active = builds.get('active_builds', [])
        completed = builds.get('completed_builds', [])
        queued = builds.get('queued_builds', [])
        
        return jsonify({
            'active_count': len(active),
            'completed_count': len(completed),
            'queued_count': len(queued),
            'active_builds': [
                {
                    'id': b.get('id'),
                    'title': b.get('title'),
                    'status': b.get('status'),
                    'priority': b.get('priority'),
                    'progress': b.get('progress', 0),
                    'eta': b.get('eta')
                }
                for b in active
            ],
            'last_completed': completed[0] if completed else None,
            'last_updated': builds.get('last_updated'),
            'dashboard_url': '/dashboard/builds.html'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/hub/fitness')
def fitness_summary():
    """Daily fitness progress"""
    try:
        fitness = load_json(FITNESS_DATA, {})
        
        today = get_today_date()
        
        # Get today's food logs
        today_food = [f for f in fitness.get('food_logs', []) 
                      if f.get('date') == today]
        
        # Calculate daily totals
        total_cals = sum(f.get('calories', 0) for f in today_food)
        total_protein = sum(f.get('protein', 0) for f in today_food)
        total_carbs = sum(f.get('carbs', 0) for f in today_food)
        total_fat = sum(f.get('fat', 0) for f in today_food)
        
        # Get targets
        settings = fitness.get('settings', {})
        target_cals = settings.get('daily_calories', 2650)
        target_protein = settings.get('daily_protein', 200)
        
        # Get latest workout
        workouts = fitness.get('workouts', [])
        last_workout = workouts[-1] if workouts else None
        
        return jsonify({
            'today': {
                'date': today,
                'calories': total_cals,
                'protein': total_protein,
                'carbs': total_carbs,
                'fat': total_fat,
                'meals_logged': len(today_food)
            },
            'targets': {
                'calories': target_cals,
                'protein': target_protein,
                'calories_remaining': target_cals - total_cals,
                'protein_remaining': target_protein - total_protein
            },
            'progress': {
                'calories_percent': round((total_cals / target_cals) * 100, 1) if target_cals > 0 else 0,
                'protein_percent': round((total_protein / target_protein) * 100, 1) if target_protein > 0 else 0
            },
            'last_workout': {
                'date': last_workout.get('date') if last_workout else None,
                'exercises': len(last_workout.get('lifts', [])) if last_workout else 0
            },
            'settings': {
                'current_weight': settings.get('current_weight'),
                'target_weight': settings.get('target_weight')
            },
            'dashboard_url': 'http://10.0.0.18:3000'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/hub/memory')
def memory_stats():
    """Memory system stats"""
    try:
        context_state = load_json(CONTEXT_STATE, {})
        
        # Get memory file count
        memory_files = list(MEMORY_DIR.glob('2026-*.md'))
        
        # Get context stats
        stats = context_state.get('stats', {})
        
        return jsonify({
            'daily_logs': len(memory_files),
            'last_search': stats.get('last_search_time'),
            'search_performance': {
                'avg_time_ms': stats.get('avg_search_time_ms', 0),
                'total_searches': stats.get('total_searches', 0)
            },
            'auto_context_enabled': context_state.get('auto_context_enabled', True),
            'recent_context_count': len(context_state.get('recent_contexts', [])),
            'system_version': '2.0'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/hub/health')
def health_check():
    """Quick health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'service': 'hub-api'
    })


# Serve static files (dashboards)
@app.route('/dashboard/<path:filename>')
def serve_dashboard(filename):
    """Serve dashboard HTML files"""
    return send_from_directory(BASE_DIR / 'dashboard', filename)


if __name__ == '__main__':
    print("🚀 Hub API starting on http://10.0.0.18:8080")
    print(f"📊 Serving data from: {BASE_DIR}")
    app.run(host='0.0.0.0', port=8080, debug=True)
