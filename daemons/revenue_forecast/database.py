#!/usr/bin/env python3
"""
Database management for revenue forecasting
"""
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Tuple

class RevenueDatabase:
    def __init__(self, db_path: str = "data/revenue_forecast.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database with schema"""
        schema_path = Path(__file__).parent / "schema.sql"
        with sqlite3.connect(self.db_path) as conn:
            with open(schema_path) as f:
                conn.executescript(f.read())
    
    def add_mrr_snapshot(self, mrr_cents: int, customer_count: int = 0, 
                        source: str = "manual", notes: str = None, timestamp: str = None):
        """Record current MRR snapshot"""
        with sqlite3.connect(self.db_path) as conn:
            if timestamp:
                conn.execute("""
                    INSERT INTO mrr_snapshots (mrr_cents, customer_count, source, notes, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (mrr_cents, customer_count, source, notes, timestamp))
            else:
                conn.execute("""
                    INSERT INTO mrr_snapshots (mrr_cents, customer_count, source, notes)
                    VALUES (?, ?, ?, ?)
                """, (mrr_cents, customer_count, source, notes))
    
    def get_current_mrr(self) -> Optional[Dict]:
        """Get most recent MRR snapshot"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            result = conn.execute("""
                SELECT * FROM mrr_snapshots 
                ORDER BY timestamp DESC LIMIT 1
            """).fetchone()
            return dict(result) if result else None
    
    def get_historical_mrr(self, days: int = 30) -> List[Dict]:
        """Get MRR history for last N days"""
        cutoff = datetime.now() - timedelta(days=days)
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            results = conn.execute("""
                SELECT 
                    DATE(timestamp) as date,
                    AVG(mrr_cents) as avg_mrr_cents,
                    AVG(customer_count) as avg_customers
                FROM mrr_snapshots
                WHERE timestamp >= ?
                GROUP BY DATE(timestamp)
                ORDER BY date ASC
            """, (cutoff.isoformat(),)).fetchall()
            return [dict(row) for row in results]
    
    def save_growth_metrics(self, date: str, daily_rate: float, weekly_rate: float,
                           monthly_proj: int, days_to_target: int, customers_needed: int):
        """Save calculated growth metrics"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO growth_metrics 
                (date, daily_growth_rate, weekly_growth_rate, monthly_projection_cents,
                 days_to_target, customers_needed)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (date, daily_rate, weekly_rate, monthly_proj, days_to_target, customers_needed))
    
    def get_latest_metrics(self) -> Optional[Dict]:
        """Get latest calculated metrics"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            result = conn.execute("SELECT * FROM latest_metrics LIMIT 1").fetchone()
            return dict(result) if result else None
    
    def save_scenario(self, scenario_name: str, additional_mrr_cents: int, 
                     projected_days: int):
        """Save a forecast scenario"""
        today = datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO forecast_scenarios 
                (date, scenario_name, additional_mrr_cents, projected_days_to_target)
                VALUES (?, ?, ?, ?)
            """, (today, scenario_name, additional_mrr_cents, projected_days))
    
    def get_scenarios_for_today(self) -> List[Dict]:
        """Get all scenarios calculated today"""
        today = datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            results = conn.execute("""
                SELECT * FROM forecast_scenarios 
                WHERE date = ?
                ORDER BY projected_days_to_target ASC
            """, (today,)).fetchall()
            return [dict(row) for row in results]
    
    def save_daily_update(self, update_text: str) -> bool:
        """Save daily update for morning brief"""
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO daily_updates (date, update_text)
                    VALUES (?, ?)
                """, (today, update_text))
            return True
        except Exception as e:
            print(f"Error saving daily update: {e}")
            return False
    
    def get_daily_update(self, date: str = None) -> Optional[str]:
        """Get daily update for specific date (default: today)"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute("""
                SELECT update_text FROM daily_updates 
                WHERE date = ?
            """, (date,)).fetchone()
            return result[0] if result else None
    
    def mark_update_delivered(self, date: str = None):
        """Mark daily update as delivered"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE daily_updates SET delivered = 1 
                WHERE date = ?
            """, (date,))
    
    def get_trend_summary(self, days: int = 7) -> Dict:
        """Get summary of recent trends"""
        history = self.get_historical_mrr(days)
        if len(history) < 2:
            return {"status": "insufficient_data", "days": len(history)}
        
        first = history[0]['avg_mrr_cents']
        last = history[-1]['avg_mrr_cents']
        change = last - first
        pct_change = (change / first * 100) if first > 0 else 0
        
        return {
            "status": "ok",
            "days_analyzed": len(history),
            "start_mrr": first / 100,
            "end_mrr": last / 100,
            "change": change / 100,
            "pct_change": pct_change,
            "trend": "up" if change > 0 else "down" if change < 0 else "flat"
        }
