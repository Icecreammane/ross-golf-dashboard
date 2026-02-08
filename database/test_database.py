#!/usr/bin/env python3
"""
Comprehensive Database Tests
Tests all tables, queries, and performance
"""

import unittest
import sqlite3
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from query_library import (
    Database, OpportunityQueries, FitnessQueries, GolfQueries,
    EmailQueries, TwitterQueries, AnalyticsQueries, DecisionQueries
)

# Test database path
TEST_DB = Path(__file__).parent / "test_data.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"

class TestDatabase(unittest.TestCase):
    """Base test class with setup/teardown"""
    
    @classmethod
    def setUpClass(cls):
        """Create test database"""
        if TEST_DB.exists():
            TEST_DB.unlink()
        
        conn = sqlite3.connect(TEST_DB)
        with open(SCHEMA_PATH, 'r') as f:
            conn.executescript(f.read())
        conn.close()
        
        print(f"\n✓ Test database created: {TEST_DB}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test database"""
        if TEST_DB.exists():
            TEST_DB.unlink()
        print(f"\n✓ Test database cleaned up")
    
    def setUp(self):
        """Clear all tables before each test"""
        conn = sqlite3.connect(TEST_DB)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = cursor.fetchall()
        
        # Clear each table
        for (table,) in tables:
            if table != 'migration_metadata':
                cursor.execute(f"DELETE FROM {table}")
        
        conn.commit()
        conn.close()

class TestOpportunities(TestDatabase):
    """Test opportunities table and queries"""
    
    def setUp(self):
        super().setUp()
        self.conn = sqlite3.connect(TEST_DB)
        
        # Insert test data
        test_data = [
            ('test_1', 'email', 'coaching', 'Golf Coaching Inquiry', 'Need help with golf', 90, '$500', 
             '2024-02-08T10:00:00', '2024-02-08T10:00:00', 'pending', datetime.now().isoformat()),
            ('test_2', 'twitter', 'partnership', 'Partnership Opportunity', 'Looking to partner', 80, '$1000',
             '2024-02-08T11:00:00', '2024-02-08T11:00:00', 'pending', datetime.now().isoformat()),
            ('test_3', 'email', 'feedback', 'Product Feedback', 'Some feedback on product', 40, '$0',
             '2024-02-08T12:00:00', '2024-02-08T12:00:00', 'pending', datetime.now().isoformat()),
        ]
        
        self.conn.executemany('''
            INSERT INTO opportunities 
            (id, source, type, title, context, score, revenue_potential, 
             detected_at, tracked_at, status, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', test_data)
        self.conn.commit()
    
    def tearDown(self):
        self.conn.close()
    
    def test_top_opportunities(self):
        """Test getting top opportunities"""
        with OpportunityQueries(TEST_DB) as opp:
            start = time.time()
            results = opp.get_top_opportunities(limit=10)
            elapsed = (time.time() - start) * 1000
            
            self.assertEqual(len(results), 3)
            self.assertEqual(results[0]['score'], 90)
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")
    
    def test_get_by_source(self):
        """Test filtering by source"""
        with OpportunityQueries(TEST_DB) as opp:
            start = time.time()
            results = opp.get_by_source('email')
            elapsed = (time.time() - start) * 1000
            
            self.assertEqual(len(results), 2)
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")
    
    def test_search(self):
        """Test search functionality"""
        with OpportunityQueries(TEST_DB) as opp:
            start = time.time()
            results = opp.search('golf')
            elapsed = (time.time() - start) * 1000
            
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['id'], 'test_1')
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")
    
    def test_stats(self):
        """Test statistics query"""
        with OpportunityQueries(TEST_DB) as opp:
            start = time.time()
            stats = opp.get_stats()
            elapsed = (time.time() - start) * 1000
            
            self.assertEqual(stats['total'], 3)
            self.assertEqual(stats['pending'], 3)
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")

class TestFitness(TestDatabase):
    """Test fitness tables and queries"""
    
    def setUp(self):
        super().setUp()
        self.conn = sqlite3.connect(TEST_DB)
        
        # Insert workout
        cursor = self.conn.execute('''
            INSERT INTO workouts (date, timestamp) VALUES (?, ?)
        ''', ('2024-02-08', 1707379200.0))
        workout_id = cursor.lastrowid
        
        # Insert lifts
        lifts = [
            (workout_id, 'Bench Press', 225, 8, 3, None),
            (workout_id, 'Squat', 315, 6, 3, None),
        ]
        self.conn.executemany('''
            INSERT INTO lifts (workout_id, name, weight, reps, sets, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', lifts)
        
        # Insert food logs
        foods = [
            ('2024-02-08', 1707379200.0, 'Chicken Breast', 200, 40, 0, 4),
            ('2024-02-08', 1707382800.0, 'Rice and Beans', 400, 15, 80, 5),
        ]
        self.conn.executemany('''
            INSERT INTO food_logs (date, timestamp, description, calories, protein, carbs, fat)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', foods)
        
        # Insert weight log
        self.conn.execute('''
            INSERT INTO weight_logs (date, timestamp, weight) VALUES (?, ?, ?)
        ''', ('2024-02-08', 1707379200.0, 225.0))
        
        self.conn.commit()
    
    def tearDown(self):
        self.conn.close()
    
    def test_recent_workouts(self):
        """Test getting recent workouts"""
        with FitnessQueries(TEST_DB) as fit:
            start = time.time()
            results = fit.get_recent_workouts(days=30)
            elapsed = (time.time() - start) * 1000
            
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['total_lifts'], 2)
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")
    
    def test_workout_details(self):
        """Test getting workout with lifts"""
        with FitnessQueries(TEST_DB) as fit:
            start = time.time()
            workout = fit.get_workout_details(1)
            elapsed = (time.time() - start) * 1000
            
            self.assertIsNotNone(workout)
            self.assertEqual(len(workout['lifts']), 2)
            self.assertEqual(workout['lifts'][0]['name'], 'Bench Press')
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")
    
    def test_daily_nutrition(self):
        """Test daily nutrition totals"""
        with FitnessQueries(TEST_DB) as fit:
            start = time.time()
            nutrition = fit.get_daily_nutrition('2024-02-08')
            elapsed = (time.time() - start) * 1000
            
            self.assertEqual(nutrition['total_calories'], 600)
            self.assertEqual(nutrition['total_protein'], 55)
            self.assertEqual(nutrition['meal_count'], 2)
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")
    
    def test_weight_trend(self):
        """Test weight trend"""
        with FitnessQueries(TEST_DB) as fit:
            start = time.time()
            results = fit.get_weight_trend(days=30)
            elapsed = (time.time() - start) * 1000
            
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['weight'], 225.0)
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")

class TestGolf(TestDatabase):
    """Test golf tables and queries"""
    
    def setUp(self):
        super().setUp()
        self.conn = sqlite3.connect(TEST_DB)
        
        # Insert golf rounds
        rounds = [
            ('2024-02-08', 'Test Course', 85, 72, 13.0, None, 'Good round', '2024-02-08T10:00:00'),
            ('2024-02-07', 'Test Course', 88, 72, 16.0, None, 'Bad putting', '2024-02-07T10:00:00'),
            ('2024-02-06', 'Other Course', 82, 72, 10.0, None, 'Great round', '2024-02-06T10:00:00'),
        ]
        self.conn.executemany('''
            INSERT INTO golf_rounds (date, course, score, par, differential, handicap_estimate, notes, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', rounds)
        
        # Insert course stats
        self.conn.execute('''
            INSERT INTO golf_courses (course_name, rounds_played, total_score, best_score, worst_score, average_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('Test Course', 2, 173, 85, 88, 86.5))
        
        self.conn.commit()
    
    def tearDown(self):
        self.conn.close()
    
    def test_recent_rounds(self):
        """Test getting recent rounds"""
        with GolfQueries(TEST_DB) as golf:
            start = time.time()
            results = golf.get_recent_rounds(limit=10)
            elapsed = (time.time() - start) * 1000
            
            self.assertEqual(len(results), 3)
            self.assertEqual(results[0]['date'], '2024-02-08')
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")
    
    def test_course_stats(self):
        """Test course statistics"""
        with GolfQueries(TEST_DB) as golf:
            start = time.time()
            stats = golf.get_course_stats('Test Course')
            elapsed = (time.time() - start) * 1000
            
            self.assertEqual(stats['rounds_played'], 2)
            self.assertEqual(stats['best_score'], 85)
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")
    
    def test_best_rounds(self):
        """Test getting best rounds"""
        with GolfQueries(TEST_DB) as golf:
            start = time.time()
            results = golf.get_best_rounds(limit=5)
            elapsed = (time.time() - start) * 1000
            
            self.assertEqual(len(results), 3)
            self.assertEqual(results[0]['score'], 82)
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")

class TestEmail(TestDatabase):
    """Test email tables and queries"""
    
    def setUp(self):
        super().setUp()
        self.conn = sqlite3.connect(TEST_DB)
        
        # Insert email
        cursor = self.conn.execute('''
            INSERT INTO email_summaries 
            (sender, sender_email, subject, preview, importance_reason, timestamp, date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('John Smith', 'john@example.com', 'Golf Coaching', 'Need golf help', 'urgent', 
              '2024-02-08T10:00:00', 'Thu, 8 Feb 2024'))
        email_id = cursor.lastrowid
        
        # Insert key points
        points = [(email_id, 'Has tournament soon'), (email_id, 'Willing to pay')]
        self.conn.executemany('''
            INSERT INTO email_key_points (email_id, key_point) VALUES (?, ?)
        ''', points)
        
        self.conn.commit()
    
    def tearDown(self):
        self.conn.close()
    
    def test_recent_emails(self):
        """Test getting recent emails"""
        with EmailQueries(TEST_DB) as email:
            start = time.time()
            results = email.get_recent_emails(days=7)
            elapsed = (time.time() - start) * 1000
            
            self.assertEqual(len(results), 1)
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")
    
    def test_email_with_points(self):
        """Test getting email with key points"""
        with EmailQueries(TEST_DB) as email:
            start = time.time()
            result = email.get_email_with_points(1)
            elapsed = (time.time() - start) * 1000
            
            self.assertIsNotNone(result)
            self.assertEqual(len(result['key_points']), 2)
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")
    
    def test_search_emails(self):
        """Test email search"""
        with EmailQueries(TEST_DB) as email:
            start = time.time()
            results = email.search_emails('golf')
            elapsed = (time.time() - start) * 1000
            
            self.assertEqual(len(results), 1)
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")

class TestTwitter(TestDatabase):
    """Test Twitter tables and queries"""
    
    def setUp(self):
        super().setUp()
        self.conn = sqlite3.connect(TEST_DB)
        
        # Insert Twitter opportunity
        self.conn.execute('''
            INSERT INTO twitter_opportunities
            (id, type, sender, sender_id, content, timestamp, url, score, opportunity_type,
             author_followers, retweet_count, reply_count, like_count, quote_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('tweet_1', 'mention', 'golf_fan', '12345', 'Love your golf tips!', 
              '2024-02-08T10:00:00', 'https://twitter.com/test', 85, 'coaching',
              5000, 2, 1, 10, 0))
        
        # Insert types
        self.conn.executemany('''
            INSERT INTO twitter_opportunity_types (twitter_id, type) VALUES (?, ?)
        ''', [('tweet_1', 'coaching'), ('tweet_1', 'golf')])
        
        # Insert reasons
        self.conn.execute('''
            INSERT INTO twitter_opportunity_reasons (twitter_id, reason) VALUES (?, ?)
        ''', ('tweet_1', 'golf: golf, tips'))
        
        self.conn.commit()
    
    def tearDown(self):
        self.conn.close()
    
    def test_top_opportunities(self):
        """Test getting top Twitter opportunities"""
        with TwitterQueries(TEST_DB) as twitter:
            start = time.time()
            results = twitter.get_top_opportunities(min_score=50)
            elapsed = (time.time() - start) * 1000
            
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['score'], 85)
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")
    
    def test_high_engagement(self):
        """Test filtering by follower count"""
        with TwitterQueries(TEST_DB) as twitter:
            start = time.time()
            results = twitter.get_high_engagement(min_followers=1000)
            elapsed = (time.time() - start) * 1000
            
            self.assertEqual(len(results), 1)
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")
    
    def test_with_types(self):
        """Test getting opportunity with types and reasons"""
        with TwitterQueries(TEST_DB) as twitter:
            start = time.time()
            result = twitter.get_with_types('tweet_1')
            elapsed = (time.time() - start) * 1000
            
            self.assertIsNotNone(result)
            self.assertEqual(len(result['all_types']), 2)
            self.assertIn('coaching', result['all_types'])
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")

class TestAnalytics(TestDatabase):
    """Test analytics tables and queries"""
    
    def setUp(self):
        super().setUp()
        self.conn = sqlite3.connect(TEST_DB)
        
        # Insert social posts
        posts = [
            ('post_1', 'Great workout today!', '2024-02-08T10:00:00', '2024-02-08T10:00:00', 50, 10, 5, 0),
            ('post_2', 'New golf tips', '2024-02-08T11:00:00', '2024-02-08T11:00:00', 100, 20, 8, 0),
        ]
        self.conn.executemany('''
            INSERT INTO social_posts (id, text, posted_at, tracked_at, likes, retweets, replies, clicks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', posts)
        
        # Insert conversions
        conversions = [
            ('test_1', 'email', 'coaching', 500.0, '2024-02-08', 'Sold coaching package'),
            ('test_2', 'twitter', 'partnership', 1000.0, '2024-02-07', 'Partnership deal'),
        ]
        self.conn.executemany('''
            INSERT INTO conversions (tracking_id, source, type, revenue, date, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', conversions)
        
        # Insert source performance
        self.conn.executemany('''
            INSERT INTO source_performance (source, total, converted, revenue)
            VALUES (?, ?, ?, ?)
        ''', [('email', 10, 3, 1500.0), ('twitter', 15, 2, 1000.0)])
        
        self.conn.commit()
    
    def tearDown(self):
        self.conn.close()
    
    def test_top_posts(self):
        """Test getting top posts by engagement"""
        with AnalyticsQueries(TEST_DB) as analytics:
            start = time.time()
            results = analytics.get_top_posts(limit=10)
            elapsed = (time.time() - start) * 1000
            
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0]['id'], 'post_2')  # Highest engagement
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")
    
    def test_conversions(self):
        """Test getting conversions"""
        with AnalyticsQueries(TEST_DB) as analytics:
            start = time.time()
            results = analytics.get_conversions(days=30)
            elapsed = (time.time() - start) * 1000
            
            self.assertEqual(len(results), 2)
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")
    
    def test_revenue_by_source(self):
        """Test revenue breakdown"""
        with AnalyticsQueries(TEST_DB) as analytics:
            start = time.time()
            results = analytics.get_revenue_by_source()
            elapsed = (time.time() - start) * 1000
            
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0]['total_revenue'], 1500.0)  # Email highest
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")
    
    def test_total_revenue(self):
        """Test total revenue calculation"""
        with AnalyticsQueries(TEST_DB) as analytics:
            start = time.time()
            total = analytics.get_total_revenue()
            elapsed = (time.time() - start) * 1000
            
            self.assertEqual(total, 1500.0)
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")
    
    def test_source_performance(self):
        """Test source performance metrics"""
        with AnalyticsQueries(TEST_DB) as analytics:
            start = time.time()
            results = analytics.get_source_performance()
            elapsed = (time.time() - start) * 1000
            
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0]['conversion_rate'], 30.0)  # 3/10 = 30%
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")

class TestDecisions(TestDatabase):
    """Test decisions tables and queries"""
    
    def setUp(self):
        super().setUp()
        self.conn = sqlite3.connect(TEST_DB)
        
        # Insert decision
        cursor = self.conn.execute('''
            INSERT INTO decisions 
            (timestamp, decision, context, category, confidence, hour, day_of_week)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('2024-02-08T16:00:00', 'Ship all upgrades', 'Weekend build', 'development', 90, 16, 'Friday'))
        decision_id = cursor.lastrowid
        
        # Insert lessons
        self.conn.execute('''
            INSERT INTO decision_lessons (decision_id, lesson) VALUES (?, ?)
        ''', (decision_id, 'Weekend builds are productive'))
        
        self.conn.commit()
    
    def tearDown(self):
        self.conn.close()
    
    def test_recent_decisions(self):
        """Test getting recent decisions"""
        with DecisionQueries(TEST_DB) as decisions:
            start = time.time()
            results = decisions.get_recent_decisions(days=30)
            elapsed = (time.time() - start) * 1000
            
            self.assertEqual(len(results), 1)
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")
    
    def test_by_category(self):
        """Test filtering by category"""
        with DecisionQueries(TEST_DB) as decisions:
            start = time.time()
            results = decisions.get_by_category('development')
            elapsed = (time.time() - start) * 1000
            
            self.assertEqual(len(results), 1)
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")
    
    def test_with_lessons(self):
        """Test getting decision with lessons"""
        with DecisionQueries(TEST_DB) as decisions:
            start = time.time()
            result = decisions.get_with_lessons(1)
            elapsed = (time.time() - start) * 1000
            
            self.assertIsNotNone(result)
            self.assertEqual(len(result['lessons']), 1)
            self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")

class TestDatabase(TestDatabase):
    """Test main Database class"""
    
    def test_health_check(self):
        """Test database health check"""
        db = Database(TEST_DB)
        start = time.time()
        health = db.health_check()
        elapsed = (time.time() - start) * 1000
        
        self.assertIsInstance(health, dict)
        self.assertIn('opportunities', health)
        self.assertLess(elapsed, 10, f"Query took {elapsed:.2f}ms (should be <10ms)")

def run_tests():
    """Run all tests and print summary"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestOpportunities))
    suite.addTests(loader.loadTestsFromTestCase(TestFitness))
    suite.addTests(loader.loadTestsFromTestCase(TestGolf))
    suite.addTests(loader.loadTestsFromTestCase(TestEmail))
    suite.addTests(loader.loadTestsFromTestCase(TestTwitter))
    suite.addTests(loader.loadTestsFromTestCase(TestAnalytics))
    suite.addTests(loader.loadTestsFromTestCase(TestDecisions))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*60)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
