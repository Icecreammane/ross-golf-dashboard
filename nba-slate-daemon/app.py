"""
NBA Slate Rankings Dashboard
Flask app with live updates and scheduled tasks
"""
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import json
import os
import pytz
import numpy as np

from scrapers.injury_scraper import InjuryScraper
from scrapers.underdog_scraper import UnderdogScraper
from ranking_engine import RankingEngine

# Custom JSON encoder for numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

app = Flask(__name__)
app.json_encoder = NumpyEncoder
CORS(app)

# Global state
current_data = {
    'players': [],
    'recommendations': {},
    'injuries': {},
    'last_update': None,
    'vegas_lines': {},
    'locked': False
}

DATA_FILE = '/Users/clawdbot/clawd/data/nba-slate-2026-02-09.json'
BRIEF_FILE = '/Users/clawdbot/clawd/data/nba-morning-brief-2026-02-09.md'

# Initialize components
injury_scraper = InjuryScraper()
underdog_scraper = UnderdogScraper()
ranking_engine = RankingEngine()

def update_slate_data():
    """Fetch and update all slate data"""
    global current_data
    
    if current_data['locked']:
        print("Slate is locked. No more updates.")
        return
    
    print(f"[{datetime.now()}] Updating slate data...")
    
    try:
        # Fetch injuries
        injuries = injury_scraper.get_all_injuries()
        current_data['injuries'] = injuries
        
        # Fetch Underdog player data
        players = underdog_scraper.fetch_slate_players()
        
        # Fetch Vegas lines
        vegas = underdog_scraper.fetch_vegas_lines()
        current_data['vegas_lines'] = vegas
        
        # Run ranking algorithm
        ranked_df = ranking_engine.rank_players(players)
        ranked_df = ranking_engine.assign_tiers(ranked_df)
        
        # Generate recommendations
        recommendations = ranking_engine.generate_recommendations(ranked_df)
        
        # Update global state
        current_data['players'] = ranked_df.to_dict('records')
        current_data['recommendations'] = recommendations
        current_data['last_update'] = datetime.now().isoformat()
        
        # Save to JSON
        save_data_to_file()
        
        print(f"Update complete. {len(players)} players ranked.")
        
    except Exception as e:
        print(f"Error updating slate data: {e}")

def save_data_to_file():
    """Save current analysis to JSON file"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    
    with open(DATA_FILE, 'w') as f:
        json.dump(current_data, f, indent=2, cls=NumpyEncoder)

def generate_morning_brief():
    """Generate morning brief summary at 7:30am"""
    print(f"[{datetime.now()}] Generating morning brief...")
    
    recs = current_data['recommendations']
    injuries = current_data['injuries']
    
    brief = f"""# NBA DFS Morning Brief - February 9, 2026
Generated at {datetime.now().strftime('%I:%M %p CT')}

## 🌟 Top 5 Stars (Play Everyone)
"""
    
    for i, player in enumerate(recs.get('top_stars', [])[:5], 1):
        brief += f"{i}. **{player['name']}** ({player['team']}) - ${player['salary']:,}\n"
        brief += f"   - Ceiling: {player['ceiling']} | Floor: {player['floor']} | Value: {player['value']}\n"
        brief += f"   - Ownership: {player['ownership_pct']}%\n\n"
    
    brief += "\n## 💰 Top 5 Value Plays\n"
    for i, player in enumerate(recs.get('top_value', [])[:5], 1):
        brief += f"{i}. **{player['name']}** ({player['team']}) - ${player['salary']:,}\n"
        brief += f"   - Ceiling: {player['ceiling']} | Value: {player['value']} | Ownership: {player['ownership_pct']}%\n\n"
    
    brief += "\n## 🔥 2 Recommended Stacks\n"
    for i, stack in enumerate(recs.get('recommended_stacks', [])[:2], 1):
        brief += f"{i}. **{stack['team']} Stack** - ${stack['total_salary']:,}\n"
        brief += f"   - Players: {', '.join(stack['players'])}\n"
        brief += f"   - Combined Ceiling: {stack['combined_ceiling']} | Upside: {stack['combined_upside']}\n\n"
    
    brief += "\n## 🚫 3 Fades (Avoid)\n"
    for i, player in enumerate(recs.get('top_fades', [])[:3], 1):
        brief += f"{i}. **{player['name']}** ({player['team']}) - ${player['salary']:,}\n"
        brief += f"   - Reason: Poor value ({player['value']}) or risky floor ({player['floor']})\n\n"
    
    brief += "\n## 🏥 Injury News Summary\n"
    injury_count = injuries.get('count', 0)
    brief += f"Total injury reports: {injury_count}\n\n"
    
    for injury in injuries.get('injuries', [])[:5]:
        brief += f"- **{injury['headline']}** (ESPN)\n"
        brief += f"  {injury['description'][:150]}...\n\n"
    
    brief += "\n---\n"
    brief += "Dashboard updates live throughout the day at http://localhost:5051\n"
    brief += "Final rankings lock at 11:59pm CT\n"
    
    # Save brief
    os.makedirs(os.path.dirname(BRIEF_FILE), exist_ok=True)
    with open(BRIEF_FILE, 'w') as f:
        f.write(brief)
    
    print(f"Morning brief saved to {BRIEF_FILE}")
    return brief

def lock_final_rankings():
    """Lock rankings at 11:59pm on Feb 9"""
    global current_data
    current_data['locked'] = True
    current_data['locked_at'] = datetime.now().isoformat()
    save_data_to_file()
    print(f"[{datetime.now()}] Final rankings LOCKED. No more updates.")

# Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/players')
def get_players():
    """Get all ranked players"""
    return jsonify({
        'players': current_data['players'],
        'last_update': current_data['last_update'],
        'locked': current_data['locked']
    })

@app.route('/api/recommendations')
def get_recommendations():
    """Get tier recommendations"""
    return jsonify(current_data['recommendations'])

@app.route('/api/injuries')
def get_injuries():
    """Get latest injury updates"""
    return jsonify(current_data['injuries'])

@app.route('/api/vegas')
def get_vegas():
    """Get Vegas betting lines"""
    return jsonify(current_data['vegas_lines'])

@app.route('/api/status')
def get_status():
    """Get system status"""
    return jsonify({
        'last_update': current_data['last_update'],
        'player_count': len(current_data['players']),
        'injury_count': current_data['injuries'].get('count', 0),
        'locked': current_data['locked'],
        'uptime': 'running'
    })

@app.route('/api/refresh')
def manual_refresh():
    """Manually trigger data refresh"""
    if not current_data['locked']:
        update_slate_data()
        return jsonify({'status': 'refreshed', 'timestamp': current_data['last_update']})
    return jsonify({'status': 'locked', 'message': 'Rankings are locked'})

def setup_scheduler():
    """Setup APScheduler for automated tasks"""
    scheduler = BackgroundScheduler()
    central = pytz.timezone('America/Chicago')
    
    # Hourly updates throughout Feb 9, 2026
    scheduler.add_job(
        func=update_slate_data,
        trigger=CronTrigger(
            year=2026, month=2, day=9,
            hour='*',  # Every hour
            timezone=central
        ),
        id='hourly_update',
        name='Hourly slate update'
    )
    
    # Morning brief at 7:30am CT
    scheduler.add_job(
        func=generate_morning_brief,
        trigger=CronTrigger(
            year=2026, month=2, day=9,
            hour=7, minute=30,
            timezone=central
        ),
        id='morning_brief',
        name='Morning brief generation'
    )
    
    # Lock rankings at 11:59pm CT
    scheduler.add_job(
        func=lock_final_rankings,
        trigger=CronTrigger(
            year=2026, month=2, day=9,
            hour=23, minute=59,
            timezone=central
        ),
        id='lock_rankings',
        name='Lock final rankings'
    )
    
    scheduler.start()
    print("Scheduler started. Jobs configured:")
    print("  - Hourly updates throughout Feb 9, 2026")
    print("  - Morning brief at 7:30am CT")
    print("  - Final lock at 11:59pm CT")
    
    return scheduler

if __name__ == '__main__':
    # Initial data load
    print("Initializing NBA Slate Rankings Daemon...")
    update_slate_data()
    
    # Setup scheduler
    scheduler = setup_scheduler()
    
    try:
        # Run Flask app
        print("\n🏀 Dashboard running at http://localhost:5051")
        print("Press Ctrl+C to stop\n")
        app.run(host='0.0.0.0', port=5051, debug=False)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("\nShutdown complete.")
