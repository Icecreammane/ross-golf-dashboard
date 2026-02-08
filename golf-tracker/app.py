#!/usr/bin/env python3
"""
Golf Data Collector - Flask Web Application
Tracks golf rounds, calculates handicap trends, and generates insights.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import List, Dict, Optional

# Configuration
DATA_FILE = Path("/Users/clawdbot/clawd/data/golf-data.json")
LOG_FILE = Path("/Users/clawdbot/clawd/golf-tracker/golf-tracker.log")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


class GolfDataManager:
    """Manages golf round data storage and calculations."""
    
    def __init__(self, data_file: Path):
        self.data_file = data_file
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """Ensure data file exists with proper structure."""
        if not self.data_file.exists():
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            initial_data = {
                "rounds": [],
                "goals": [],
                "courses": {}
            }
            self._save_data(initial_data)
            logger.info(f"Created new data file: {self.data_file}")
    
    def _load_data(self) -> Dict:
        """Load golf data from JSON file."""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return {"rounds": [], "goals": [], "courses": {}}
    
    def _save_data(self, data: Dict):
        """Save golf data to JSON file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Data saved successfully to {self.data_file}")
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            raise
    
    def add_round(self, date: str, course: str, score: int, par: int, 
                  handicap_estimate: Optional[float] = None, notes: str = "") -> Dict:
        """Add a new golf round."""
        # Validation
        if not self._validate_date(date):
            raise ValueError(f"Invalid date format: {date}. Use YYYY-MM-DD")
        if score < 50 or score > 200:
            raise ValueError(f"Invalid score: {score}. Must be between 50 and 200")
        if par < 60 or par > 80:
            raise ValueError(f"Invalid par: {par}. Must be between 60 and 80")
        
        data = self._load_data()
        
        round_data = {
            "id": len(data["rounds"]) + 1,
            "date": date,
            "course": course,
            "score": score,
            "par": par,
            "differential": score - par,
            "handicap_estimate": handicap_estimate,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
        
        data["rounds"].append(round_data)
        
        # Update course statistics
        if course not in data["courses"]:
            data["courses"][course] = {
                "rounds_played": 0,
                "total_score": 0,
                "best_score": score,
                "worst_score": score
            }
        
        course_data = data["courses"][course]
        course_data["rounds_played"] += 1
        course_data["total_score"] += score
        course_data["best_score"] = min(course_data["best_score"], score)
        course_data["worst_score"] = max(course_data["worst_score"], score)
        course_data["average_score"] = course_data["total_score"] / course_data["rounds_played"]
        
        self._save_data(data)
        logger.info(f"Added round: {course} on {date}, score: {score}")
        
        return round_data
    
    def get_all_rounds(self) -> List[Dict]:
        """Get all rounds sorted by date (newest first)."""
        data = self._load_data()
        return sorted(data["rounds"], key=lambda x: x["date"], reverse=True)
    
    def get_recent_rounds(self, count: int = 5) -> List[Dict]:
        """Get the most recent N rounds."""
        return self.get_all_rounds()[:count]
    
    def calculate_handicap_trend(self, rounds_count: int = 10) -> List[float]:
        """Calculate handicap trend over recent rounds."""
        rounds = self.get_all_rounds()[:rounds_count]
        if not rounds:
            return []
        
        # Simple handicap calculation: average of differentials
        handicaps = []
        for i, round_data in enumerate(reversed(rounds)):
            recent = rounds[max(0, len(rounds) - i - 5):len(rounds) - i]
            if recent:
                avg_differential = sum(r["differential"] for r in recent) / len(recent)
                handicaps.append(round(avg_differential * 0.96, 1))  # USGA factor
        
        return handicaps
    
    def get_insights(self) -> Dict:
        """Generate insights about golf performance."""
        data = self._load_data()
        rounds = data["rounds"]
        
        if not rounds:
            return {"message": "No rounds logged yet. Start tracking your game!"}
        
        insights = {}
        
        # Recent performance
        recent_5 = self.get_recent_rounds(5)
        if len(recent_5) >= 5:
            recent_avg = sum(r["score"] for r in recent_5) / len(recent_5)
            insights["recent_average"] = round(recent_avg, 1)
        
        # Monthly comparison
        now = datetime.now()
        this_month = [r for r in rounds if datetime.fromisoformat(r["date"]).month == now.month]
        last_month = [r for r in rounds if datetime.fromisoformat(r["date"]).month == (now.month - 1 or 12)]
        
        if this_month:
            insights["this_month_avg"] = round(sum(r["score"] for r in this_month) / len(this_month), 1)
            insights["this_month_count"] = len(this_month)
        
        if last_month:
            insights["last_month_avg"] = round(sum(r["score"] for r in last_month) / len(last_month), 1)
        
        # Improvement trend
        if "this_month_avg" in insights and "last_month_avg" in insights:
            improvement = insights["last_month_avg"] - insights["this_month_avg"]
            insights["improvement"] = round(improvement, 1)
            if improvement > 0:
                insights["trend"] = "improving"
            elif improvement < 0:
                insights["trend"] = "declining"
            else:
                insights["trend"] = "stable"
        
        # Best and worst
        all_scores = [r["score"] for r in rounds]
        insights["best_score"] = min(all_scores)
        insights["worst_score"] = max(all_scores)
        insights["total_rounds"] = len(rounds)
        
        # Best and worst courses
        if data["courses"]:
            courses_sorted = sorted(data["courses"].items(), key=lambda x: x[1]["average_score"])
            insights["best_course"] = {
                "name": courses_sorted[0][0],
                "avg_score": round(courses_sorted[0][1]["average_score"], 1)
            }
            insights["worst_course"] = {
                "name": courses_sorted[-1][0],
                "avg_score": round(courses_sorted[-1][1]["average_score"], 1)
            }
        
        # Goal tracking
        goals = data.get("goals", [])
        if goals:
            active_goals = [g for g in goals if not g.get("achieved")]
            insights["active_goals"] = active_goals
            
            # Check if any goals were recently achieved
            for goal in active_goals:
                if goal["type"] == "break_score":
                    recent_best = min(r["score"] for r in recent_5) if recent_5 else 999
                    if recent_best < goal["target"]:
                        goal["achieved"] = True
                        goal["achieved_date"] = recent_5[0]["date"]
                        insights["goal_achieved"] = f"Congrats! You broke {goal['target']}!"
        
        return insights
    
    def add_goal(self, goal_type: str, target: int, description: str = "") -> Dict:
        """Add a new goal."""
        data = self._load_data()
        
        goal = {
            "id": len(data["goals"]) + 1,
            "type": goal_type,
            "target": target,
            "description": description,
            "created_date": datetime.now().date().isoformat(),
            "achieved": False
        }
        
        data["goals"].append(goal)
        self._save_data(data)
        logger.info(f"Added goal: {goal_type} - {target}")
        
        return goal
    
    def get_course_stats(self) -> Dict:
        """Get statistics for all courses."""
        data = self._load_data()
        return data.get("courses", {})
    
    @staticmethod
    def _validate_date(date_str: str) -> bool:
        """Validate date format YYYY-MM-DD."""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False


# Initialize data manager
golf_data = GolfDataManager(DATA_FILE)


@app.route('/')
def index():
    """Main dashboard page."""
    rounds = golf_data.get_recent_rounds(10)
    insights = golf_data.get_insights()
    course_stats = golf_data.get_course_stats()
    
    return render_template('index.html', 
                         rounds=rounds, 
                         insights=insights,
                         course_stats=course_stats)


@app.route('/add', methods=['GET', 'POST'])
def add_round():
    """Add a new round."""
    if request.method == 'POST':
        try:
            date = request.form.get('date')
            course = request.form.get('course')
            score = int(request.form.get('score'))
            par = int(request.form.get('par', 72))
            handicap = request.form.get('handicap_estimate')
            notes = request.form.get('notes', '')
            
            handicap_float = float(handicap) if handicap else None
            
            golf_data.add_round(date, course, score, par, handicap_float, notes)
            
            return redirect(url_for('index'))
        
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return render_template('add.html', error=str(e))
        except Exception as e:
            logger.error(f"Error adding round: {e}")
            return render_template('add.html', error="Failed to add round. Check logs.")
    
    # Default date to today
    today = datetime.now().date().isoformat()
    return render_template('add.html', default_date=today)


@app.route('/api/rounds', methods=['GET'])
def api_get_rounds():
    """API endpoint to get all rounds."""
    rounds = golf_data.get_all_rounds()
    return jsonify(rounds)


@app.route('/api/insights', methods=['GET'])
def api_get_insights():
    """API endpoint to get insights."""
    insights = golf_data.get_insights()
    return jsonify(insights)


@app.route('/api/add_round', methods=['POST'])
def api_add_round():
    """API endpoint to add a round."""
    try:
        data = request.get_json()
        round_data = golf_data.add_round(
            date=data['date'],
            course=data['course'],
            score=data['score'],
            par=data.get('par', 72),
            handicap_estimate=data.get('handicap_estimate'),
            notes=data.get('notes', '')
        )
        return jsonify({"success": True, "round": round_data})
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/api/add_goal', methods=['POST'])
def api_add_goal():
    """API endpoint to add a goal."""
    try:
        data = request.get_json()
        goal = golf_data.add_goal(
            goal_type=data['type'],
            target=data['target'],
            description=data.get('description', '')
        )
        return jsonify({"success": True, "goal": goal})
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


if __name__ == '__main__':
    logger.info("Starting Golf Tracker application")
    app.run(host='0.0.0.0', port=5050, debug=False)
