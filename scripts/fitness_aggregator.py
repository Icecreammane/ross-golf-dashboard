#!/usr/bin/env python3
"""
Fitness Aggregator - Daily Summary Generator
Pulls data from FitTrack Pro API, generates insights, and stores summaries.
Runs daily at 11pm to analyze yesterday's data.
"""

import sys
import json
import logging
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from statistics import mean, stdev

# Configuration
API_URL = "http://localhost:3000/api/stats"
DATA_DIR = Path("/Users/clawdbot/clawd/data")
SUMMARY_FILE = DATA_DIR / "fitness-summary.json"
LOG_DIR = Path("/Users/clawdbot/clawd/logs")
LOG_FILE = LOG_DIR / "fitness-aggregator.log"

# Setup logging
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class FitnessAggregator:
    """Analyzes fitness tracking data and generates insights."""
    
    def __init__(self, api_url: str = API_URL):
        self.api_url = api_url
        self.data = None
        self.goals = {}
        
    def fetch_data(self) -> Dict:
        """Fetch data from FitTrack Pro API."""
        logger.info(f"Fetching data from {self.api_url}")
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            self.data = response.json()
            self.goals = self.data.get('goals', {})
            logger.info("Data fetched successfully")
            return self.data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch data: {e}")
            raise
    
    def get_date_range_data(self, days: int) -> List[Dict]:
        """Get data for the last N days, excluding entries with no data."""
        if not self.data or 'history' not in self.data:
            return []
        
        history = self.data['history']
        # Filter out empty days (all zeros)
        active_days = [
            day for day in history 
            if day.get('calories', 0) > 0 or day.get('protein', 0) > 0
        ]
        return active_days[-days:] if len(active_days) > days else active_days
    
    def calculate_daily_summary(self, date: str = None) -> Dict:
        """Calculate summary for a specific date (defaults to yesterday)."""
        if date is None:
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        history = self.data.get('history', [])
        day_data = next((d for d in history if d['date'] == date), None)
        
        if not day_data:
            logger.warning(f"No data found for {date}")
            return None
        
        # Calculate compliance percentages
        cal_target = self.goals.get('calories', 2200)
        protein_target = self.goals.get('protein', 200)
        carb_target = self.goals.get('carbs', 250)
        fat_target = self.goals.get('fat', 70)
        
        calories = day_data.get('calories', 0)
        protein = day_data.get('protein', 0)
        carbs = day_data.get('carbs', 0)
        fat = day_data.get('fat', 0)
        
        summary = {
            'date': date,
            'calories': calories,
            'protein': protein,
            'carbs': carbs,
            'fat': fat,
            'weight': day_data.get('weight'),
            'compliance': {
                'calories': round((calories / cal_target * 100) if cal_target else 0, 1),
                'protein': round((protein / protein_target * 100) if protein_target else 0, 1),
                'carbs': round((carbs / carb_target * 100) if carb_target else 0, 1),
                'fat': round((fat / fat_target * 100) if fat_target else 0, 1),
            },
            'goals_met': {
                'calories': abs(calories - cal_target) <= cal_target * 0.1,  # Within 10%
                'protein': protein >= protein_target,
                'carbs': abs(carbs - carb_target) <= carb_target * 0.15,
                'fat': abs(fat - fat_target) <= fat_target * 0.15,
            }
        }
        
        return summary
    
    def calculate_weekly_summary(self, weeks_ago: int = 0) -> Dict:
        """Calculate summary for a week (0 = current week, 1 = last week, etc)."""
        week_data = self.get_date_range_data(14)  # Get 2 weeks
        
        if not week_data:
            logger.warning("No data available for weekly summary")
            return None
        
        # Split into current and previous week
        split_point = 7 if len(week_data) >= 14 else len(week_data) // 2
        
        if weeks_ago == 0:
            data = week_data[-split_point:] if len(week_data) > split_point else week_data
        else:
            data = week_data[:split_point] if len(week_data) > split_point else []
        
        if not data:
            return None
        
        # Calculate averages
        avg_calories = mean([d.get('calories', 0) for d in data])
        avg_protein = mean([d.get('protein', 0) for d in data])
        avg_carbs = mean([d.get('carbs', 0) for d in data])
        avg_fat = mean([d.get('fat', 0) for d in data])
        
        # Count goal hits
        protein_target = self.goals.get('protein', 200)
        protein_hits = sum(1 for d in data if d.get('protein', 0) >= protein_target)
        
        cal_target = self.goals.get('calories', 2200)
        calorie_hits = sum(1 for d in data if abs(d.get('calories', 0) - cal_target) <= cal_target * 0.1)
        
        # Calculate compliance percentage
        compliance_pct = round((calorie_hits / len(data) * 100) if data else 0, 1)
        
        summary = {
            'start_date': data[0]['date'],
            'end_date': data[-1]['date'],
            'days_logged': len(data),
            'averages': {
                'calories': round(avg_calories, 1),
                'protein': round(avg_protein, 1),
                'carbs': round(avg_carbs, 1),
                'fat': round(avg_fat, 1),
            },
            'goal_hits': {
                'protein': protein_hits,
                'calories': calorie_hits,
            },
            'compliance_percentage': compliance_pct,
        }
        
        return summary
    
    def calculate_monthly_summary(self) -> Dict:
        """Calculate summary for the last 30 days."""
        month_data = self.get_date_range_data(30)
        
        if not month_data:
            logger.warning("No data available for monthly summary")
            return None
        
        # Calculate averages
        avg_calories = mean([d.get('calories', 0) for d in month_data])
        avg_protein = mean([d.get('protein', 0) for d in month_data])
        avg_carbs = mean([d.get('carbs', 0) for d in month_data])
        avg_fat = mean([d.get('fat', 0) for d in month_data])
        
        # Calculate standard deviations (consistency metric)
        try:
            cal_stdev = stdev([d.get('calories', 0) for d in month_data]) if len(month_data) > 1 else 0
            protein_stdev = stdev([d.get('protein', 0) for d in month_data]) if len(month_data) > 1 else 0
        except:
            cal_stdev = protein_stdev = 0
        
        # Count goal hits
        protein_target = self.goals.get('protein', 200)
        protein_hits = sum(1 for d in month_data if d.get('protein', 0) >= protein_target)
        
        summary = {
            'period': f"{month_data[0]['date']} to {month_data[-1]['date']}",
            'days_logged': len(month_data),
            'averages': {
                'calories': round(avg_calories, 1),
                'protein': round(avg_protein, 1),
                'carbs': round(avg_carbs, 1),
                'fat': round(avg_fat, 1),
            },
            'consistency': {
                'calorie_stdev': round(cal_stdev, 1),
                'protein_stdev': round(protein_stdev, 1),
            },
            'goal_hits': {
                'protein_days': protein_hits,
                'protein_percentage': round((protein_hits / len(month_data) * 100) if month_data else 0, 1),
            }
        }
        
        return summary
    
    def identify_patterns(self) -> Dict:
        """Identify patterns in the data."""
        week_data = self.get_date_range_data(14)
        
        if len(week_data) < 5:
            return {'note': 'Not enough data for pattern analysis'}
        
        # Find best and worst days
        calories_sorted = sorted(week_data, key=lambda x: x.get('calories', 0), reverse=True)
        protein_sorted = sorted(week_data, key=lambda x: x.get('protein', 0), reverse=True)
        
        best_cal_day = calories_sorted[0] if calories_sorted else None
        worst_cal_day = calories_sorted[-1] if calories_sorted else None
        best_protein_day = protein_sorted[0] if protein_sorted else None
        worst_protein_day = protein_sorted[-1] if protein_sorted else None
        
        # Day of week analysis
        day_performance = {}
        for entry in week_data:
            date_obj = datetime.strptime(entry['date'], '%Y-%m-%d')
            day_name = date_obj.strftime('%A')
            
            if day_name not in day_performance:
                day_performance[day_name] = {'calories': [], 'protein': []}
            
            day_performance[day_name]['calories'].append(entry.get('calories', 0))
            day_performance[day_name]['protein'].append(entry.get('protein', 0))
        
        # Calculate averages per day of week
        day_averages = {}
        for day, metrics in day_performance.items():
            day_averages[day] = {
                'avg_calories': round(mean(metrics['calories']) if metrics['calories'] else 0, 1),
                'avg_protein': round(mean(metrics['protein']) if metrics['protein'] else 0, 1),
            }
        
        patterns = {
            'best_days': {
                'highest_calories': {
                    'date': best_cal_day['date'] if best_cal_day else None,
                    'calories': best_cal_day.get('calories', 0) if best_cal_day else 0,
                },
                'highest_protein': {
                    'date': best_protein_day['date'] if best_protein_day else None,
                    'protein': best_protein_day.get('protein', 0) if best_protein_day else 0,
                },
            },
            'worst_days': {
                'lowest_calories': {
                    'date': worst_cal_day['date'] if worst_cal_day else None,
                    'calories': worst_cal_day.get('calories', 0) if worst_cal_day else 0,
                },
                'lowest_protein': {
                    'date': worst_protein_day['date'] if worst_protein_day else None,
                    'protein': worst_protein_day.get('protein', 0) if worst_protein_day else 0,
                },
            },
            'day_of_week_performance': day_averages,
        }
        
        return patterns
    
    def generate_insights(self) -> List[str]:
        """Generate natural language insights about performance."""
        insights = []
        
        # Weekly comparison
        this_week = self.calculate_weekly_summary(weeks_ago=0)
        last_week = self.calculate_weekly_summary(weeks_ago=1)
        
        if this_week and last_week:
            # Protein compliance insight
            protein_hits_this = this_week['goal_hits']['protein']
            protein_hits_last = last_week['goal_hits']['protein']
            days_this = this_week['days_logged']
            days_last = last_week['days_logged']
            
            compliance_this = round((protein_hits_this / days_this * 100) if days_this else 0, 0)
            compliance_last = round((protein_hits_last / days_last * 100) if days_last else 0, 0)
            
            trend = "Up" if compliance_this > compliance_last else "Down" if compliance_this < compliance_last else "Steady"
            
            insights.append(
                f"You hit protein {protein_hits_this}/{days_this} days this week. "
                f"{int(compliance_this)}% compliance. {trend} from {int(compliance_last)}% last week."
            )
            
            # Calorie compliance
            cal_compliance_this = this_week['compliance_percentage']
            cal_compliance_last = last_week['compliance_percentage']
            cal_diff = cal_compliance_this - cal_compliance_last
            
            if abs(cal_diff) >= 10:
                direction = "improved" if cal_diff > 0 else "dropped"
                insights.append(
                    f"Calorie compliance {direction} by {abs(int(cal_diff))}% "
                    f"({int(cal_compliance_this)}% vs {int(cal_compliance_last)}%)."
                )
            
            # Average comparison
            avg_protein_this = this_week['averages']['protein']
            avg_protein_last = last_week['averages']['protein']
            protein_change = avg_protein_this - avg_protein_last
            
            if abs(protein_change) >= 10:
                direction = "up" if protein_change > 0 else "down"
                insights.append(
                    f"Average daily protein {direction} {abs(int(protein_change))}g "
                    f"({int(avg_protein_this)}g vs {int(avg_protein_last)}g)."
                )
        
        # Pattern-based insights
        patterns = self.identify_patterns()
        
        if 'day_of_week_performance' in patterns and patterns['day_of_week_performance']:
            day_avgs = patterns['day_of_week_performance']
            
            # Find best and worst day of week
            best_day = max(day_avgs.items(), key=lambda x: x[1]['avg_protein'])
            worst_day = min(day_avgs.items(), key=lambda x: x[1]['avg_protein'])
            
            if best_day[0] != worst_day[0]:
                insights.append(
                    f"{best_day[0]}s are your strongest ({int(best_day[1]['avg_protein'])}g protein). "
                    f"{worst_day[0]}s need work ({int(worst_day[1]['avg_protein'])}g)."
                )
        
        # Monthly consistency insight
        monthly = self.calculate_monthly_summary()
        if monthly:
            consistency = monthly['consistency']['protein_stdev']
            if consistency < 20:
                insights.append(f"Very consistent protein intake (±{int(consistency)}g) - great job!")
            elif consistency > 40:
                insights.append(f"Protein intake varies widely (±{int(consistency)}g) - try to be more consistent.")
        
        # Recent trend
        recent_data = self.get_date_range_data(3)
        if len(recent_data) >= 3:
            recent_avg = mean([d.get('protein', 0) for d in recent_data])
            target = self.goals.get('protein', 200)
            
            if recent_avg >= target:
                insights.append(f"🔥 On fire! {len(recent_data)}-day protein streak at {int(recent_avg)}g/day!")
            elif recent_avg < target * 0.8:
                insights.append(f"⚠️ Below target last {len(recent_data)} days ({int(recent_avg)}g/day). Time to refocus!")
        
        return insights
    
    def save_summary(self, summary: Dict):
        """Save weekly summary to JSON file."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Load existing summaries
        if SUMMARY_FILE.exists():
            with open(SUMMARY_FILE, 'r') as f:
                summaries = json.load(f)
        else:
            summaries = {'weekly_summaries': [], 'last_updated': None}
        
        # Add new summary
        summaries['weekly_summaries'].append(summary)
        summaries['last_updated'] = datetime.now().isoformat()
        
        # Keep only last 12 weeks
        summaries['weekly_summaries'] = summaries['weekly_summaries'][-12:]
        
        # Save
        with open(SUMMARY_FILE, 'w') as f:
            json.dump(summaries, f, indent=2)
        
        logger.info(f"Summary saved to {SUMMARY_FILE}")
    
    def run_daily_summary(self):
        """Main entry point for daily summary generation."""
        logger.info("=" * 60)
        logger.info("Starting daily fitness summary")
        logger.info("=" * 60)
        
        try:
            # Fetch latest data
            self.fetch_data()
            
            # Calculate summaries
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            daily = self.calculate_daily_summary(yesterday)
            weekly = self.calculate_weekly_summary(weeks_ago=0)
            monthly = self.calculate_monthly_summary()
            patterns = self.identify_patterns()
            insights = self.generate_insights()
            
            # Create comprehensive summary
            summary = {
                'generated_at': datetime.now().isoformat(),
                'yesterday': daily,
                'this_week': weekly,
                'monthly': monthly,
                'patterns': patterns,
                'insights': insights,
            }
            
            # Save summary
            self.save_summary(summary)
            
            # Log insights
            logger.info("\n📊 FITNESS INSIGHTS:")
            for insight in insights:
                logger.info(f"  • {insight}")
            
            logger.info("\n✅ Daily summary completed successfully")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}", exc_info=True)
            raise


def main():
    """CLI entry point."""
    aggregator = FitnessAggregator()
    summary = aggregator.run_daily_summary()
    
    # Print summary to stdout for easy viewing
    print("\n" + "=" * 60)
    print("FITNESS SUMMARY")
    print("=" * 60)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
