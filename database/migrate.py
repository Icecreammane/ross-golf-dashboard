#!/usr/bin/env python3
"""
SQLite Migration Script
Migrates all JSON data to SQLite database
Usage: python3 migrate.py [--dry-run] [--backup] [--force]
"""

import sqlite3
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
import argparse
import sys

# Paths
WORKSPACE = Path.home() / "clawd"
DB_PATH = WORKSPACE / "database" / "data.db"
SCHEMA_PATH = WORKSPACE / "database" / "schema.sql"
BACKUP_DIR = WORKSPACE / "database" / "backups"

# JSON file paths
JSON_FILES = {
    'opportunities': WORKSPACE / 'revenue' / 'opportunities.json',
    'fitness': WORKSPACE / 'fitness-tracker' / 'fitness_data.json',
    'golf': WORKSPACE / 'data' / 'golf-data.json',
    'email': WORKSPACE / 'data' / 'email-summary.json',
    'twitter': WORKSPACE / 'data' / 'twitter-opportunities.json',
    'analytics': WORKSPACE / 'data' / 'analytics.json',
    'decisions': WORKSPACE / 'memory' / 'decisions.json',
    'queue': WORKSPACE / 'opportunities' / 'queue.json',
}

class DatabaseMigrator:
    def __init__(self, db_path, schema_path, dry_run=False):
        self.db_path = db_path
        self.schema_path = schema_path
        self.dry_run = dry_run
        self.conn = None
        self.stats = {
            'opportunities': 0,
            'workouts': 0,
            'lifts': 0,
            'food_logs': 0,
            'weight_logs': 0,
            'golf_rounds': 0,
            'email_summaries': 0,
            'twitter_opportunities': 0,
            'social_posts': 0,
            'conversions': 0,
            'decisions': 0,
            'errors': []
        }
    
    def connect(self):
        """Create database connection and initialize schema"""
        if self.dry_run:
            print("[DRY RUN] Would connect to database:", self.db_path)
            return
        
        # Create directory if needed
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Load schema
        with open(self.schema_path, 'r') as f:
            schema = f.read()
        
        self.conn.executescript(schema)
        self.conn.commit()
        print(f"✓ Database initialized: {self.db_path}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def migrate_opportunities(self, file_path):
        """Migrate opportunities from revenue/opportunities.json"""
        if not file_path.exists():
            print(f"⚠ File not found: {file_path}")
            return
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        opportunities = data.get('inventory', {}).get('opportunities', [])
        
        if self.dry_run:
            print(f"[DRY RUN] Would migrate {len(opportunities)} revenue opportunities")
            return
        
        for opp in opportunities:
            try:
                # Generate ID from opportunity name
                opp_id = f"revenue_{opp.get('opportunity', '').lower().replace(' ', '_')}"
                
                self.conn.execute('''
                    INSERT OR REPLACE INTO opportunities 
                    (id, source, type, title, context, score, revenue_potential, 
                     detected_at, tracked_at, status, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    opp_id,
                    'revenue_plan',
                    opp.get('opportunity', '').split()[0].lower(),
                    opp.get('opportunity'),
                    opp.get('description'),
                    opp.get('difficulty', 5) * 10,  # Convert difficulty to score
                    opp.get('monthly_potential', ''),
                    data.get('generated_at', datetime.now().isoformat()),
                    datetime.now().isoformat(),
                    'pending',
                    datetime.now().isoformat()
                ))
                self.stats['opportunities'] += 1
            except Exception as e:
                self.stats['errors'].append(f"Opportunity error: {e}")
        
        self.conn.commit()
        print(f"✓ Migrated {self.stats['opportunities']} revenue opportunities")
    
    def migrate_queue_opportunities(self, file_path):
        """Migrate opportunities from opportunities/queue.json"""
        if not file_path.exists():
            print(f"⚠ File not found: {file_path}")
            return
        
        with open(file_path, 'r') as f:
            queue = json.load(f)
        
        if self.dry_run:
            print(f"[DRY RUN] Would migrate {len(queue)} queue opportunities")
            return
        
        for opp in queue:
            try:
                self.conn.execute('''
                    INSERT OR REPLACE INTO opportunities 
                    (id, source, type, title, context, url, score, 
                     detected_at, tracked_at, status, draft, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    opp['id'],
                    opp['source'],
                    opp['type'],
                    opp['title'],
                    opp['context'],
                    opp.get('url'),
                    opp['score'],
                    opp['detected_at'],
                    datetime.now().isoformat(),
                    opp['status'],
                    opp.get('draft'),
                    datetime.now().isoformat()
                ))
                self.stats['opportunities'] += 1
            except Exception as e:
                self.stats['errors'].append(f"Queue opportunity error: {e}")
        
        self.conn.commit()
        print(f"✓ Migrated {len(queue)} queue opportunities")
    
    def migrate_fitness(self, file_path):
        """Migrate fitness data"""
        if not file_path.exists():
            print(f"⚠ File not found: {file_path}")
            return
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Migrate workouts and lifts
        workouts = data.get('workouts', [])
        if self.dry_run:
            print(f"[DRY RUN] Would migrate {len(workouts)} workouts")
        else:
            for workout in workouts:
                try:
                    cursor = self.conn.execute('''
                        INSERT INTO workouts (date, timestamp, notes)
                        VALUES (?, ?, ?)
                    ''', (
                        workout['date'],
                        workout['timestamp'],
                        workout.get('notes')
                    ))
                    workout_id = cursor.lastrowid
                    self.stats['workouts'] += 1
                    
                    # Migrate lifts for this workout
                    for lift in workout.get('lifts', []):
                        self.conn.execute('''
                            INSERT INTO lifts (workout_id, name, weight, reps, sets, notes)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            workout_id,
                            lift['name'],
                            lift['weight'],
                            lift['reps'],
                            lift['sets'],
                            lift.get('notes')
                        ))
                        self.stats['lifts'] += 1
                except Exception as e:
                    self.stats['errors'].append(f"Workout error: {e}")
            
            self.conn.commit()
            print(f"✓ Migrated {self.stats['workouts']} workouts, {self.stats['lifts']} lifts")
        
        # Migrate food logs
        food_logs = data.get('food_logs', [])
        if self.dry_run:
            print(f"[DRY RUN] Would migrate {len(food_logs)} food logs")
        else:
            for food in food_logs:
                try:
                    self.conn.execute('''
                        INSERT INTO food_logs (date, timestamp, description, calories, protein, carbs, fat)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        food['date'],
                        food['timestamp'],
                        food.get('description'),
                        food['calories'],
                        food['protein'],
                        food['carbs'],
                        food['fat']
                    ))
                    self.stats['food_logs'] += 1
                except Exception as e:
                    self.stats['errors'].append(f"Food log error: {e}")
            
            self.conn.commit()
            print(f"✓ Migrated {self.stats['food_logs']} food logs")
        
        # Migrate weight logs
        weight_logs = data.get('weight_logs', [])
        if self.dry_run:
            print(f"[DRY RUN] Would migrate {len(weight_logs)} weight logs")
        else:
            for weight in weight_logs:
                try:
                    self.conn.execute('''
                        INSERT OR REPLACE INTO weight_logs (date, timestamp, weight)
                        VALUES (?, ?, ?)
                    ''', (
                        weight['date'],
                        weight['timestamp'],
                        weight['weight']
                    ))
                    self.stats['weight_logs'] += 1
                except Exception as e:
                    self.stats['errors'].append(f"Weight log error: {e}")
            
            self.conn.commit()
            print(f"✓ Migrated {self.stats['weight_logs']} weight logs")
        
        # Migrate settings
        settings = data.get('settings', {})
        if settings and not self.dry_run:
            try:
                self.conn.execute('''
                    INSERT OR REPLACE INTO fitness_settings 
                    (id, target_weight, current_weight, daily_calories, daily_protein, daily_carbs, daily_fat, birthday)
                    VALUES (1, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    settings.get('target_weight'),
                    settings.get('current_weight'),
                    settings.get('daily_calories'),
                    settings.get('daily_protein'),
                    settings.get('daily_carbs'),
                    settings.get('daily_fat'),
                    settings.get('birthday')
                ))
                self.conn.commit()
                print("✓ Migrated fitness settings")
            except Exception as e:
                self.stats['errors'].append(f"Settings error: {e}")
    
    def migrate_golf(self, file_path):
        """Migrate golf data"""
        if not file_path.exists():
            print(f"⚠ File not found: {file_path}")
            return
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        rounds = data.get('rounds', [])
        if self.dry_run:
            print(f"[DRY RUN] Would migrate {len(rounds)} golf rounds")
        else:
            for round_data in rounds:
                try:
                    self.conn.execute('''
                        INSERT INTO golf_rounds 
                        (date, course, score, par, differential, handicap_estimate, notes, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        round_data['date'],
                        round_data['course'],
                        round_data['score'],
                        round_data['par'],
                        round_data['differential'],
                        round_data.get('handicap_estimate'),
                        round_data.get('notes'),
                        round_data['timestamp']
                    ))
                    self.stats['golf_rounds'] += 1
                except Exception as e:
                    self.stats['errors'].append(f"Golf round error: {e}")
            
            self.conn.commit()
            print(f"✓ Migrated {self.stats['golf_rounds']} golf rounds")
        
        # Migrate course stats
        courses = data.get('courses', {})
        if courses and not self.dry_run:
            for course_name, stats in courses.items():
                try:
                    self.conn.execute('''
                        INSERT OR REPLACE INTO golf_courses
                        (course_name, rounds_played, total_score, best_score, worst_score, average_score)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        course_name,
                        stats['rounds_played'],
                        stats['total_score'],
                        stats['best_score'],
                        stats['worst_score'],
                        stats['average_score']
                    ))
                except Exception as e:
                    self.stats['errors'].append(f"Golf course error: {e}")
            
            self.conn.commit()
            print(f"✓ Migrated {len(courses)} golf courses")
    
    def migrate_email(self, file_path):
        """Migrate email summaries"""
        if not file_path.exists():
            print(f"⚠ File not found: {file_path}")
            return
        
        with open(file_path, 'r') as f:
            emails = json.load(f)
        
        if self.dry_run:
            print(f"[DRY RUN] Would migrate {len(emails)} email summaries")
            return
        
        for email in emails:
            try:
                cursor = self.conn.execute('''
                    INSERT INTO email_summaries 
                    (sender, sender_email, subject, preview, importance_reason, timestamp, date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    email['sender'],
                    email.get('from_email', ''),
                    email['subject'],
                    email['preview'],
                    email.get('importance_reason', ''),
                    email['timestamp'],
                    email['date']
                ))
                email_id = cursor.lastrowid
                self.stats['email_summaries'] += 1
                
                # Migrate key points
                for point in email.get('key_points', []):
                    self.conn.execute('''
                        INSERT INTO email_key_points (email_id, key_point)
                        VALUES (?, ?)
                    ''', (email_id, point))
            except Exception as e:
                self.stats['errors'].append(f"Email error: {e}")
        
        self.conn.commit()
        print(f"✓ Migrated {self.stats['email_summaries']} email summaries")
    
    def migrate_twitter(self, file_path):
        """Migrate Twitter opportunities"""
        if not file_path.exists():
            print(f"⚠ File not found: {file_path}")
            return
        
        with open(file_path, 'r') as f:
            twitter_data = json.load(f)
        
        if self.dry_run:
            print(f"[DRY RUN] Would migrate {len(twitter_data)} Twitter opportunities")
            return
        
        for tweet in twitter_data:
            try:
                metrics = tweet.get('metrics', {})
                
                self.conn.execute('''
                    INSERT OR REPLACE INTO twitter_opportunities
                    (id, type, sender, sender_id, content, timestamp, url, score, opportunity_type,
                     author_followers, retweet_count, reply_count, like_count, quote_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    tweet['id'],
                    tweet['type'],
                    tweet['sender'],
                    tweet['sender_id'],
                    tweet['content'],
                    tweet['timestamp'],
                    tweet['url'],
                    tweet['score'],
                    tweet['opportunity_type'],
                    tweet.get('author_followers', 0),
                    metrics.get('retweet_count', 0),
                    metrics.get('reply_count', 0),
                    metrics.get('like_count', 0),
                    metrics.get('quote_count', 0)
                ))
                self.stats['twitter_opportunities'] += 1
                
                # Migrate all types
                for type_name in tweet.get('all_types', []):
                    self.conn.execute('''
                        INSERT INTO twitter_opportunity_types (twitter_id, type)
                        VALUES (?, ?)
                    ''', (tweet['id'], type_name))
                
                # Migrate reasons
                for reason in tweet.get('reasons', []):
                    self.conn.execute('''
                        INSERT INTO twitter_opportunity_reasons (twitter_id, reason)
                        VALUES (?, ?)
                    ''', (tweet['id'], reason))
                
            except Exception as e:
                self.stats['errors'].append(f"Twitter error: {e}")
        
        self.conn.commit()
        print(f"✓ Migrated {self.stats['twitter_opportunities']} Twitter opportunities")
    
    def migrate_analytics(self, file_path):
        """Migrate analytics data"""
        if not file_path.exists():
            print(f"⚠ File not found: {file_path}")
            return
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Migrate opportunities (these may overlap with other sources)
        opportunities = data.get('opportunities', [])
        if opportunities and not self.dry_run:
            for opp in opportunities:
                try:
                    self.conn.execute('''
                        INSERT OR REPLACE INTO opportunities
                        (id, source, type, score, revenue_potential, timestamp, sender, 
                         content_preview, detected_at, tracked_at, status, converted, 
                         conversion_date, actual_revenue, conversion_notes, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        opp.get('tracking_id', f"analytics_{opp.get('timestamp', '')}"),
                        opp['source'],
                        opp['type'],
                        opp['score'],
                        opp.get('revenue_potential', ''),
                        opp['timestamp'],
                        opp.get('sender', ''),
                        opp.get('content_preview', ''),
                        opp.get('tracked_at', opp['timestamp']),
                        opp.get('tracked_at', datetime.now().isoformat()),
                        opp.get('status', 'pending'),
                        1 if opp.get('converted', False) else 0,
                        opp.get('conversion_date'),
                        opp.get('actual_revenue'),
                        opp.get('conversion_notes'),
                        opp.get('last_updated', datetime.now().isoformat())
                    ))
                except Exception as e:
                    self.stats['errors'].append(f"Analytics opportunity error: {e}")
            self.conn.commit()
        
        # Migrate social posts
        posts = data.get('social_posts', [])
        if self.dry_run:
            print(f"[DRY RUN] Would migrate {len(posts)} social posts")
        else:
            for post in posts:
                try:
                    self.conn.execute('''
                        INSERT OR REPLACE INTO social_posts
                        (id, text, posted_at, tracked_at, likes, retweets, replies, clicks)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        post['id'],
                        post['text'],
                        post['posted_at'],
                        post['tracked_at'],
                        post.get('likes', 0),
                        post.get('retweets', 0),
                        post.get('replies', 0),
                        post.get('clicks', 0)
                    ))
                    self.stats['social_posts'] += 1
                except Exception as e:
                    self.stats['errors'].append(f"Social post error: {e}")
            self.conn.commit()
            print(f"✓ Migrated {self.stats['social_posts']} social posts")
        
        # Migrate conversions
        conversions = data.get('conversions', [])
        if self.dry_run:
            print(f"[DRY RUN] Would migrate {len(conversions)} conversions")
        else:
            for conv in conversions:
                try:
                    self.conn.execute('''
                        INSERT INTO conversions
                        (tracking_id, source, type, revenue, date, notes)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        conv['tracking_id'],
                        conv['source'],
                        conv['type'],
                        conv['revenue'],
                        conv['date'],
                        conv.get('notes', '')
                    ))
                    self.stats['conversions'] += 1
                except Exception as e:
                    self.stats['errors'].append(f"Conversion error: {e}")
            self.conn.commit()
            print(f"✓ Migrated {self.stats['conversions']} conversions")
        
        # Migrate engagement by hour
        engagement_by_hour = data.get('engagement_by_hour', {})
        if engagement_by_hour and not self.dry_run:
            for hour, stats in engagement_by_hour.items():
                try:
                    self.conn.execute('''
                        INSERT OR REPLACE INTO engagement_by_hour (hour, posts, engagement)
                        VALUES (?, ?, ?)
                    ''', (int(hour), stats['posts'], stats['engagement']))
                except Exception as e:
                    self.stats['errors'].append(f"Engagement hour error: {e}")
            self.conn.commit()
        
        # Migrate source performance
        source_perf = data.get('source_performance', {})
        if source_perf and not self.dry_run:
            for source, stats in source_perf.items():
                try:
                    self.conn.execute('''
                        INSERT OR REPLACE INTO source_performance (source, total, converted, revenue)
                        VALUES (?, ?, ?, ?)
                    ''', (source, stats['total'], stats['converted'], stats['revenue']))
                except Exception as e:
                    self.stats['errors'].append(f"Source performance error: {e}")
            self.conn.commit()
    
    def migrate_decisions(self, file_path):
        """Migrate decisions data"""
        if not file_path.exists():
            print(f"⚠ File not found: {file_path}")
            return
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        decisions = data.get('decisions', [])
        if self.dry_run:
            print(f"[DRY RUN] Would migrate {len(decisions)} decisions")
            return
        
        for decision in decisions:
            try:
                cursor = self.conn.execute('''
                    INSERT INTO decisions
                    (timestamp, decision, context, category, confidence, hour, 
                     day_of_week, outcome, outcome_recorded)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    decision['timestamp'],
                    decision['decision'],
                    decision.get('context'),
                    decision.get('category'),
                    decision.get('confidence'),
                    decision.get('hour'),
                    decision.get('day_of_week'),
                    decision.get('outcome'),
                    decision.get('outcome_recorded')
                ))
                decision_id = cursor.lastrowid
                self.stats['decisions'] += 1
                
                # Migrate lessons
                for lesson in decision.get('lessons', []):
                    self.conn.execute('''
                        INSERT INTO decision_lessons (decision_id, lesson)
                        VALUES (?, ?)
                    ''', (decision_id, lesson))
            except Exception as e:
                self.stats['errors'].append(f"Decision error: {e}")
        
        self.conn.commit()
        print(f"✓ Migrated {self.stats['decisions']} decisions")
    
    def print_stats(self):
        """Print migration statistics"""
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        for key, value in self.stats.items():
            if key != 'errors':
                print(f"{key:25s}: {value:>6}")
        
        if self.stats['errors']:
            print("\n" + "="*60)
            print("ERRORS")
            print("="*60)
            for error in self.stats['errors'][:10]:  # Show first 10 errors
                print(f"  • {error}")
            if len(self.stats['errors']) > 10:
                print(f"  ... and {len(self.stats['errors']) - 10} more errors")
        
        print("="*60)

def backup_json_files():
    """Backup all JSON files before migration"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"json_backup_{timestamp}"
    backup_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating backup in: {backup_path}")
    
    for name, file_path in JSON_FILES.items():
        if file_path.exists():
            dest = backup_path / file_path.name
            shutil.copy2(file_path, dest)
            print(f"  ✓ Backed up {file_path.name}")
    
    print(f"✓ Backup complete: {backup_path}\n")
    return backup_path

def main():
    parser = argparse.ArgumentParser(description='Migrate JSON data to SQLite')
    parser.add_argument('--dry-run', action='store_true', help='Simulate migration without making changes')
    parser.add_argument('--backup', action='store_true', help='Create backup of JSON files before migration')
    parser.add_argument('--force', action='store_true', help='Force migration even if database exists')
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("SQLite MIGRATION TOOL")
    print("="*60 + "\n")
    
    # Check if database exists
    if DB_PATH.exists() and not args.force and not args.dry_run:
        print(f"⚠ Database already exists: {DB_PATH}")
        response = input("Overwrite existing database? [y/N]: ")
        if response.lower() != 'y':
            print("Migration cancelled.")
            sys.exit(0)
    
    # Backup if requested
    if args.backup and not args.dry_run:
        backup_json_files()
    
    # Create migrator
    migrator = DatabaseMigrator(DB_PATH, SCHEMA_PATH, dry_run=args.dry_run)
    
    try:
        # Connect and initialize
        migrator.connect()
        
        # Run migrations
        print("\nMigrating data...\n")
        migrator.migrate_opportunities(JSON_FILES['opportunities'])
        migrator.migrate_queue_opportunities(JSON_FILES['queue'])
        migrator.migrate_fitness(JSON_FILES['fitness'])
        migrator.migrate_golf(JSON_FILES['golf'])
        migrator.migrate_email(JSON_FILES['email'])
        migrator.migrate_twitter(JSON_FILES['twitter'])
        migrator.migrate_analytics(JSON_FILES['analytics'])
        migrator.migrate_decisions(JSON_FILES['decisions'])
        
        # Print summary
        migrator.print_stats()
        
        if args.dry_run:
            print("\n[DRY RUN] No changes were made to the database.")
        else:
            print(f"\n✓ Migration complete! Database: {DB_PATH}")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        migrator.close()

if __name__ == '__main__':
    main()
