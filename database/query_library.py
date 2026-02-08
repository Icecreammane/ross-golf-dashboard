#!/usr/bin/env python3
"""
SQLite Query Library
Common queries for all data tables with performance optimization
All queries target < 10ms execution time
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json

DB_PATH = Path.home() / "clawd" / "database" / "data.db"

class DatabaseQuery:
    """Base class for database queries with connection management"""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = None
    
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
    
    def _dict_from_row(self, row) -> Dict[str, Any]:
        """Convert sqlite3.Row to dictionary"""
        if row is None:
            return None
        return dict(zip(row.keys(), row))
    
    def _dicts_from_rows(self, rows) -> List[Dict[str, Any]]:
        """Convert list of sqlite3.Row to list of dictionaries"""
        return [self._dict_from_row(row) for row in rows]

class OpportunityQueries(DatabaseQuery):
    """Queries for opportunities table"""
    
    def get_top_opportunities(self, limit=10, min_score=50) -> List[Dict]:
        """Get top opportunities by score"""
        cursor = self.conn.execute('''
            SELECT * FROM opportunities 
            WHERE score >= ? AND status = 'pending'
            ORDER BY score DESC, detected_at DESC
            LIMIT ?
        ''', (min_score, limit))
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_by_source(self, source: str, limit=50) -> List[Dict]:
        """Get opportunities from specific source"""
        cursor = self.conn.execute('''
            SELECT * FROM opportunities 
            WHERE source = ?
            ORDER BY detected_at DESC
            LIMIT ?
        ''', (source, limit))
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_converted(self, days=30) -> List[Dict]:
        """Get converted opportunities from last N days"""
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        cursor = self.conn.execute('''
            SELECT * FROM opportunities 
            WHERE converted = 1 AND conversion_date >= ?
            ORDER BY conversion_date DESC
        ''', (since_date,))
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_pending_by_type(self, opp_type: str) -> List[Dict]:
        """Get pending opportunities by type"""
        cursor = self.conn.execute('''
            SELECT * FROM opportunities 
            WHERE type = ? AND status = 'pending'
            ORDER BY score DESC, detected_at DESC
        ''', (opp_type,))
        return self._dicts_from_rows(cursor.fetchall())
    
    def search(self, query: str, limit=20) -> List[Dict]:
        """Full-text search in opportunities"""
        search_term = f"%{query}%"
        cursor = self.conn.execute('''
            SELECT * FROM opportunities 
            WHERE title LIKE ? OR context LIKE ? OR content_preview LIKE ?
            ORDER BY score DESC
            LIMIT ?
        ''', (search_term, search_term, search_term, limit))
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_stats(self) -> Dict:
        """Get opportunity statistics"""
        cursor = self.conn.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN converted = 1 THEN 1 ELSE 0 END) as converted,
                AVG(score) as avg_score,
                SUM(CASE WHEN converted = 1 THEN actual_revenue ELSE 0 END) as total_revenue
            FROM opportunities
        ''')
        return self._dict_from_row(cursor.fetchone())

class FitnessQueries(DatabaseQuery):
    """Queries for fitness tables"""
    
    def get_recent_workouts(self, days=30) -> List[Dict]:
        """Get workouts from last N days with lift details"""
        since_date = (datetime.now() - timedelta(days=days)).date().isoformat()
        cursor = self.conn.execute('''
            SELECT w.*, 
                   COUNT(l.id) as total_lifts,
                   SUM(l.weight * l.reps * l.sets) as total_volume
            FROM workouts w
            LEFT JOIN lifts l ON w.id = l.workout_id
            WHERE w.date >= ?
            GROUP BY w.id
            ORDER BY w.date DESC
        ''', (since_date,))
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_workout_details(self, workout_id: int) -> Dict:
        """Get full workout with all lifts"""
        cursor = self.conn.execute('''
            SELECT * FROM workouts WHERE id = ?
        ''', (workout_id,))
        workout = self._dict_from_row(cursor.fetchone())
        
        if workout:
            cursor = self.conn.execute('''
                SELECT * FROM lifts WHERE workout_id = ? ORDER BY id
            ''', (workout_id,))
            workout['lifts'] = self._dicts_from_rows(cursor.fetchall())
        
        return workout
    
    def get_lift_progress(self, lift_name: str, limit=10) -> List[Dict]:
        """Get progress for specific lift"""
        cursor = self.conn.execute('''
            SELECT l.*, w.date
            FROM lifts l
            JOIN workouts w ON l.workout_id = w.id
            WHERE l.name = ?
            ORDER BY w.date DESC
            LIMIT ?
        ''', (lift_name, limit))
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_daily_nutrition(self, date: str = None) -> Dict:
        """Get nutrition totals for a specific date"""
        if date is None:
            date = datetime.now().date().isoformat()
        
        cursor = self.conn.execute('''
            SELECT 
                date,
                SUM(calories) as total_calories,
                SUM(protein) as total_protein,
                SUM(carbs) as total_carbs,
                SUM(fat) as total_fat,
                COUNT(*) as meal_count
            FROM food_logs
            WHERE date = ?
            GROUP BY date
        ''', (date,))
        return self._dict_from_row(cursor.fetchone()) or {}
    
    def get_nutrition_week(self, days=7) -> List[Dict]:
        """Get nutrition summary for last N days"""
        since_date = (datetime.now() - timedelta(days=days)).date().isoformat()
        cursor = self.conn.execute('''
            SELECT 
                date,
                SUM(calories) as total_calories,
                SUM(protein) as total_protein,
                SUM(carbs) as total_carbs,
                SUM(fat) as total_fat,
                COUNT(*) as meal_count
            FROM food_logs
            WHERE date >= ?
            GROUP BY date
            ORDER BY date DESC
        ''', (since_date,))
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_weight_trend(self, days=30) -> List[Dict]:
        """Get weight trend"""
        since_date = (datetime.now() - timedelta(days=days)).date().isoformat()
        cursor = self.conn.execute('''
            SELECT * FROM weight_logs 
            WHERE date >= ?
            ORDER BY date DESC
        ''', (since_date,))
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_settings(self) -> Dict:
        """Get fitness settings"""
        cursor = self.conn.execute('SELECT * FROM fitness_settings WHERE id = 1')
        return self._dict_from_row(cursor.fetchone()) or {}
    
    def get_lift_names(self) -> List[str]:
        """Get all unique lift names"""
        cursor = self.conn.execute('''
            SELECT DISTINCT name FROM lifts ORDER BY name
        ''')
        return [row['name'] for row in cursor.fetchall()]

class GolfQueries(DatabaseQuery):
    """Queries for golf tables"""
    
    def get_recent_rounds(self, limit=10) -> List[Dict]:
        """Get recent golf rounds"""
        cursor = self.conn.execute('''
            SELECT * FROM golf_rounds 
            ORDER BY date DESC 
            LIMIT ?
        ''', (limit,))
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_course_stats(self, course: str) -> Dict:
        """Get statistics for specific course"""
        cursor = self.conn.execute('''
            SELECT * FROM golf_courses WHERE course_name = ?
        ''', (course,))
        return self._dict_from_row(cursor.fetchone())
    
    def get_all_courses(self) -> List[Dict]:
        """Get all course statistics"""
        cursor = self.conn.execute('''
            SELECT * FROM golf_courses 
            ORDER BY rounds_played DESC
        ''')
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_handicap_trend(self, limit=20) -> List[Dict]:
        """Get handicap differential trend"""
        cursor = self.conn.execute('''
            SELECT date, course, score, differential 
            FROM golf_rounds 
            ORDER BY date DESC 
            LIMIT ?
        ''', (limit,))
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_best_rounds(self, limit=5) -> List[Dict]:
        """Get best rounds by score"""
        cursor = self.conn.execute('''
            SELECT * FROM golf_rounds 
            ORDER BY score ASC 
            LIMIT ?
        ''', (limit,))
        return self._dicts_from_rows(cursor.fetchall())

class EmailQueries(DatabaseQuery):
    """Queries for email tables"""
    
    def get_recent_emails(self, days=7, limit=50) -> List[Dict]:
        """Get recent email summaries"""
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        cursor = self.conn.execute('''
            SELECT * FROM email_summaries 
            WHERE timestamp >= ?
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (since_date, limit))
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_email_with_points(self, email_id: int) -> Dict:
        """Get email with key points"""
        cursor = self.conn.execute('''
            SELECT * FROM email_summaries WHERE id = ?
        ''', (email_id,))
        email = self._dict_from_row(cursor.fetchone())
        
        if email:
            cursor = self.conn.execute('''
                SELECT key_point FROM email_key_points WHERE email_id = ?
            ''', (email_id,))
            email['key_points'] = [row['key_point'] for row in cursor.fetchall()]
        
        return email
    
    def search_emails(self, query: str, limit=20) -> List[Dict]:
        """Search emails by subject or content"""
        search_term = f"%{query}%"
        cursor = self.conn.execute('''
            SELECT * FROM email_summaries 
            WHERE subject LIKE ? OR preview LIKE ? OR sender LIKE ?
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (search_term, search_term, search_term, limit))
        return self._dicts_from_rows(cursor.fetchall())

class TwitterQueries(DatabaseQuery):
    """Queries for Twitter tables"""
    
    def get_top_opportunities(self, limit=20, min_score=30) -> List[Dict]:
        """Get top Twitter opportunities"""
        cursor = self.conn.execute('''
            SELECT * FROM twitter_opportunities 
            WHERE score >= ?
            ORDER BY score DESC, timestamp DESC 
            LIMIT ?
        ''', (min_score, limit))
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_by_type(self, opp_type: str, limit=20) -> List[Dict]:
        """Get opportunities by type"""
        cursor = self.conn.execute('''
            SELECT DISTINCT t.* FROM twitter_opportunities t
            JOIN twitter_opportunity_types tt ON t.id = tt.twitter_id
            WHERE tt.type = ?
            ORDER BY t.score DESC 
            LIMIT ?
        ''', (opp_type, limit))
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_high_engagement(self, min_followers=1000, limit=20) -> List[Dict]:
        """Get opportunities from high-follower accounts"""
        cursor = self.conn.execute('''
            SELECT * FROM twitter_opportunities 
            WHERE author_followers >= ?
            ORDER BY author_followers DESC, score DESC 
            LIMIT ?
        ''', (min_followers, limit))
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_with_types(self, twitter_id: str) -> Dict:
        """Get Twitter opportunity with all types and reasons"""
        cursor = self.conn.execute('''
            SELECT * FROM twitter_opportunities WHERE id = ?
        ''', (twitter_id,))
        tweet = self._dict_from_row(cursor.fetchone())
        
        if tweet:
            cursor = self.conn.execute('''
                SELECT type FROM twitter_opportunity_types WHERE twitter_id = ?
            ''', (twitter_id,))
            tweet['all_types'] = [row['type'] for row in cursor.fetchall()]
            
            cursor = self.conn.execute('''
                SELECT reason FROM twitter_opportunity_reasons WHERE twitter_id = ?
            ''', (twitter_id,))
            tweet['reasons'] = [row['reason'] for row in cursor.fetchall()]
        
        return tweet

class AnalyticsQueries(DatabaseQuery):
    """Queries for analytics and revenue tables"""
    
    def get_recent_posts(self, days=30, limit=50) -> List[Dict]:
        """Get recent social posts"""
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        cursor = self.conn.execute('''
            SELECT *, (likes + retweets + replies) as total_engagement
            FROM social_posts 
            WHERE posted_at >= ?
            ORDER BY posted_at DESC 
            LIMIT ?
        ''', (since_date, limit))
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_top_posts(self, limit=10) -> List[Dict]:
        """Get top posts by engagement"""
        cursor = self.conn.execute('''
            SELECT *, (likes + retweets + replies) as total_engagement
            FROM social_posts 
            ORDER BY total_engagement DESC 
            LIMIT ?
        ''', (limit,))
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_conversions(self, days=90) -> List[Dict]:
        """Get recent conversions"""
        since_date = (datetime.now() - timedelta(days=days)).date().isoformat()
        cursor = self.conn.execute('''
            SELECT * FROM conversions 
            WHERE date >= ?
            ORDER BY date DESC
        ''', (since_date,))
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_revenue_by_source(self) -> List[Dict]:
        """Get revenue breakdown by source"""
        cursor = self.conn.execute('''
            SELECT source, 
                   SUM(revenue) as total_revenue,
                   COUNT(*) as conversion_count,
                   AVG(revenue) as avg_revenue
            FROM conversions 
            GROUP BY source
            ORDER BY total_revenue DESC
        ''')
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_engagement_by_hour(self) -> List[Dict]:
        """Get engagement statistics by hour"""
        cursor = self.conn.execute('''
            SELECT * FROM engagement_by_hour ORDER BY hour
        ''')
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_source_performance(self) -> List[Dict]:
        """Get performance metrics by source"""
        cursor = self.conn.execute('''
            SELECT * FROM source_performance ORDER BY revenue DESC
        ''')
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_total_revenue(self, days=None) -> float:
        """Get total revenue (all time or last N days)"""
        if days:
            since_date = (datetime.now() - timedelta(days=days)).date().isoformat()
            cursor = self.conn.execute('''
                SELECT SUM(revenue) as total FROM conversions WHERE date >= ?
            ''', (since_date,))
        else:
            cursor = self.conn.execute('SELECT SUM(revenue) as total FROM conversions')
        
        result = cursor.fetchone()
        return result['total'] if result['total'] else 0.0

class DecisionQueries(DatabaseQuery):
    """Queries for decisions table"""
    
    def get_recent_decisions(self, days=30, limit=50) -> List[Dict]:
        """Get recent decisions"""
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        cursor = self.conn.execute('''
            SELECT * FROM decisions 
            WHERE timestamp >= ?
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (since_date, limit))
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_by_category(self, category: str, limit=50) -> List[Dict]:
        """Get decisions by category"""
        cursor = self.conn.execute('''
            SELECT * FROM decisions 
            WHERE category = ?
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (category, limit))
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_with_lessons(self, decision_id: int) -> Dict:
        """Get decision with lessons learned"""
        cursor = self.conn.execute('''
            SELECT * FROM decisions WHERE id = ?
        ''', (decision_id,))
        decision = self._dict_from_row(cursor.fetchone())
        
        if decision:
            cursor = self.conn.execute('''
                SELECT lesson FROM decision_lessons WHERE decision_id = ?
            ''', (decision_id,))
            decision['lessons'] = [row['lesson'] for row in cursor.fetchall()]
        
        return decision
    
    def get_by_hour_pattern(self) -> List[Dict]:
        """Get decision patterns by hour"""
        cursor = self.conn.execute('''
            SELECT hour, 
                   COUNT(*) as count,
                   AVG(confidence) as avg_confidence
            FROM decisions 
            WHERE hour IS NOT NULL
            GROUP BY hour
            ORDER BY hour
        ''')
        return self._dicts_from_rows(cursor.fetchall())
    
    def get_by_day_pattern(self) -> List[Dict]:
        """Get decision patterns by day of week"""
        cursor = self.conn.execute('''
            SELECT day_of_week, 
                   COUNT(*) as count,
                   AVG(confidence) as avg_confidence
            FROM decisions 
            WHERE day_of_week IS NOT NULL
            GROUP BY day_of_week
        ''')
        return self._dicts_from_rows(cursor.fetchall())

# Convenience wrapper for all queries
class Database:
    """Main database interface with all query classes"""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.opportunities = OpportunityQueries(db_path)
        self.fitness = FitnessQueries(db_path)
        self.golf = GolfQueries(db_path)
        self.email = EmailQueries(db_path)
        self.twitter = TwitterQueries(db_path)
        self.analytics = AnalyticsQueries(db_path)
        self.decisions = DecisionQueries(db_path)
    
    def health_check(self) -> Dict:
        """Check database health and get counts"""
        with DatabaseQuery(self.db_path) as db:
            cursor = db.conn.execute('''
                SELECT 
                    (SELECT COUNT(*) FROM opportunities) as opportunities,
                    (SELECT COUNT(*) FROM workouts) as workouts,
                    (SELECT COUNT(*) FROM food_logs) as food_logs,
                    (SELECT COUNT(*) FROM golf_rounds) as golf_rounds,
                    (SELECT COUNT(*) FROM email_summaries) as emails,
                    (SELECT COUNT(*) FROM twitter_opportunities) as twitter,
                    (SELECT COUNT(*) FROM social_posts) as social_posts,
                    (SELECT COUNT(*) FROM conversions) as conversions,
                    (SELECT COUNT(*) FROM decisions) as decisions
            ''')
            return db._dict_from_row(cursor.fetchone())

# Example usage
if __name__ == '__main__':
    db = Database()
    
    print("Database Health Check:")
    print(json.dumps(db.health_check(), indent=2))
    
    print("\n\nTop Opportunities:")
    with db.opportunities as opp:
        for o in opp.get_top_opportunities(limit=5):
            print(f"  • [{o['score']}] {o['title']} ({o['source']})")
    
    print("\n\nRecent Workouts:")
    with db.fitness as fit:
        for w in fit.get_recent_workouts(days=7):
            print(f"  • {w['date']}: {w['total_lifts']} lifts, {w['total_volume']:.0f} total volume")
    
    print("\n\nTotal Revenue:")
    with db.analytics as analytics:
        total = analytics.get_total_revenue()
        print(f"  ${total:.2f}")
