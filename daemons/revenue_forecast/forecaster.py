#!/usr/bin/env python3
"""
Revenue forecasting and projection calculations
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from .database import RevenueDatabase
except ImportError:
    from database import RevenueDatabase

class RevenueForecast:
    def __init__(self, config_path: str = None):
        if not config_path:
            config_path = Path(__file__).parent / "config.json"
        
        with open(config_path) as f:
            self.config = json.load(f)
        
        self.db = RevenueDatabase(self.config.get('database_path', 'data/revenue_forecast.db'))
        self.target_mrr_cents = self.config['target_mrr'] * 100
    
    def calculate_growth_rates(self) -> Optional[Dict]:
        """Calculate daily and weekly growth rates from historical data"""
        history = self.db.get_historical_mrr(30)
        
        if len(history) < 2:
            return None
        
        # Daily growth rate (average change per day over last 7 days)
        recent = history[-7:] if len(history) >= 7 else history
        if len(recent) >= 2:
            first = recent[0]['avg_mrr_cents']
            last = recent[-1]['avg_mrr_cents']
            days = len(recent) - 1
            daily_change = (last - first) / days if days > 0 else 0
            daily_rate = (daily_change / first * 100) if first > 0 else 0
        else:
            daily_rate = 0
            daily_change = 0
        
        # Weekly growth rate (last 7 days vs previous 7 days)
        if len(history) >= 14:
            prev_week = history[-14:-7]
            this_week = history[-7:]
            prev_avg = sum(d['avg_mrr_cents'] for d in prev_week) / len(prev_week)
            this_avg = sum(d['avg_mrr_cents'] for d in this_week) / len(this_week)
            weekly_rate = ((this_avg - prev_avg) / prev_avg * 100) if prev_avg > 0 else 0
        else:
            weekly_rate = 0
        
        # Monthly projection (current MRR + 30 days of growth)
        current_mrr = history[-1]['avg_mrr_cents']
        monthly_projection = int(current_mrr + (daily_change * 30))
        
        return {
            'daily_rate': round(daily_rate, 2),
            'weekly_rate': round(weekly_rate, 2),
            'monthly_projection_cents': monthly_projection,
            'daily_change_cents': int(daily_change)
        }
    
    def days_to_target(self, current_mrr_cents: int, daily_change_cents: float) -> int:
        """Calculate days until target MRR is reached"""
        if daily_change_cents <= 0:
            return -1  # Not growing, won't reach target
        
        gap = self.target_mrr_cents - current_mrr_cents
        if gap <= 0:
            return 0  # Already at or above target
        
        days = gap / daily_change_cents
        return int(days) if days > 0 else -1
    
    def customers_needed(self, current_mrr_cents: int, avg_customer_value_cents: int = 2900) -> int:
        """Calculate how many more customers needed to hit target"""
        gap = self.target_mrr_cents - current_mrr_cents
        if gap <= 0:
            return 0
        
        return int((gap + avg_customer_value_cents - 1) / avg_customer_value_cents)
    
    def calculate_scenario(self, scenario_name: str, additional_mrr_cents: int) -> Dict:
        """Calculate forecast for a specific scenario"""
        current = self.db.get_current_mrr()
        if not current:
            return {"error": "No current MRR data"}
        
        growth = self.calculate_growth_rates()
        if not growth:
            return {"error": "Insufficient historical data"}
        
        new_mrr = current['mrr_cents'] + additional_mrr_cents
        gap = self.target_mrr_cents - new_mrr
        
        if gap <= 0:
            days = 0
            message = f"✅ {scenario_name}: You'd hit ${self.config['target_mrr']} immediately!"
        else:
            daily_change = growth['daily_change_cents']
            if daily_change <= 0:
                days = -1
                message = f"⚠️ {scenario_name}: Need positive growth to reach target"
            else:
                days = int(gap / daily_change)
                date = (datetime.now() + timedelta(days=days)).strftime("%B %d, %Y")
                message = f"📈 {scenario_name}: Hit ${self.config['target_mrr']} in {days} days ({date})"
        
        return {
            'scenario_name': scenario_name,
            'additional_mrr': additional_mrr_cents / 100,
            'new_mrr': new_mrr / 100,
            'days_to_target': days,
            'message': message
        }
    
    def generate_all_scenarios(self) -> List[Dict]:
        """Generate forecasts for all configured scenarios"""
        scenarios = []
        for scenario in self.config.get('scenarios', []):
            result = self.calculate_scenario(
                scenario['name'],
                scenario['monthly_value'] * 100
            )
            if 'error' not in result:
                scenarios.append(result)
                # Save to database
                self.db.save_scenario(
                    scenario['name'],
                    scenario['monthly_value'] * 100,
                    result['days_to_target']
                )
        return scenarios
    
    def update_metrics(self) -> Dict:
        """Calculate and save current metrics"""
        current = self.db.get_current_mrr()
        if not current:
            return {"error": "No MRR data available"}
        
        growth = self.calculate_growth_rates()
        if not growth:
            return {"error": "Insufficient historical data for growth calculations"}
        
        current_mrr = current['mrr_cents']
        days_to_target = self.days_to_target(current_mrr, growth['daily_change_cents'])
        customers = self.customers_needed(current_mrr)
        
        today = datetime.now().strftime("%Y-%m-%d")
        self.db.save_growth_metrics(
            date=today,
            daily_rate=growth['daily_rate'],
            weekly_rate=growth['weekly_rate'],
            monthly_proj=growth['monthly_projection_cents'],
            days_to_target=days_to_target,
            customers_needed=customers
        )
        
        return {
            'current_mrr': current_mrr / 100,
            'target_mrr': self.target_mrr_cents / 100,
            'daily_growth_rate': growth['daily_rate'],
            'weekly_growth_rate': growth['weekly_rate'],
            'monthly_projection': growth['monthly_projection_cents'] / 100,
            'days_to_target': days_to_target,
            'customers_needed': customers,
            'updated_at': datetime.now().isoformat()
        }
    
    def generate_daily_update(self) -> str:
        """Generate one-sentence update for morning brief"""
        metrics = self.db.get_latest_metrics()
        if not metrics:
            return "💰 Revenue tracking: Waiting for initial data"
        
        current_mrr = metrics['current_mrr']
        target = self.config['target_mrr']
        pct_complete = (current_mrr / target * 100)
        
        # Different messages based on status
        if current_mrr >= target:
            return f"🎯 Revenue: ${current_mrr:.0f} MRR - Target hit! (+{pct_complete-100:.0f}% over)"
        
        days = metrics.get('days_to_target', -1)
        weekly_rate = metrics.get('weekly_growth_rate', 0)
        
        if days > 0:
            date = (datetime.now() + timedelta(days=days)).strftime("%b %d")
            trend = "📈" if weekly_rate > 0 else "📊"
            return f"{trend} Revenue: ${current_mrr:.0f}/{target} MRR ({pct_complete:.0f}%) - Hit ${target} on {date}"
        elif weekly_rate > 0:
            return f"📈 Revenue: ${current_mrr:.0f}/{target} MRR ({pct_complete:.0f}%) - Growing +{weekly_rate:.1f}% weekly"
        else:
            return f"📊 Revenue: ${current_mrr:.0f}/{target} MRR ({pct_complete:.0f}%) - Need growth momentum"
    
    def get_dashboard_data(self) -> Dict:
        """Get data formatted for dashboard widget"""
        metrics = self.db.get_latest_metrics()
        if not metrics:
            return {
                'status': 'no_data',
                'message': 'No revenue data available yet'
            }
        
        current_mrr = metrics['current_mrr']
        target = self.config['target_mrr']
        pct_complete = min(100, (current_mrr / target * 100))
        
        history = self.db.get_historical_mrr(30)
        trend_data = [
            {
                'date': h['date'],
                'mrr': h['avg_mrr_cents'] / 100
            }
            for h in history
        ]
        
        return {
            'status': 'ok',
            'current_mrr': current_mrr,
            'target_mrr': target,
            'pct_complete': round(pct_complete, 1),
            'days_to_target': metrics.get('days_to_target', -1),
            'daily_growth_rate': metrics.get('daily_growth_rate', 0),
            'weekly_growth_rate': metrics.get('weekly_growth_rate', 0),
            'monthly_projection': metrics.get('monthly_projection', 0),
            'customers_needed': metrics.get('customers_needed', 0),
            'trend_data': trend_data,
            'updated_at': metrics.get('timestamp', datetime.now().isoformat())
        }
