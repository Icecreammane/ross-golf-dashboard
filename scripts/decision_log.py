#!/usr/bin/env python3
"""
Decision Log & ROI Feedback Loop

Tracks every decision made on opportunities:
- What opportunity was presented
- What action was chosen
- Outcome (customer acquired, deal closed, feedback received)
- Revenue generated
- Conversion rates by source type
- ROI per decision type
- Predictive scoring for future opportunities

Stores in SQLite for historical analysis and learning.
Integrates with opportunity_aggregator to improve scoring over time.
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import statistics

# Paths
WORKSPACE = Path("/Users/clawdbot/clawd")
DB_PATH = WORKSPACE / "data" / "decision_log.db"
LOG_FILE = WORKSPACE / "logs" / "decision-log.log"

# Ensure directories exist
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DecisionLog:
    """Logs decisions and tracks ROI"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with schema"""
        logger.info(f"Initializing database at {self.db_path}")
        
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        
        cursor = self.conn.cursor()
        
        # Decisions table - core decision log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                opportunity_type TEXT NOT NULL,
                opportunity_source TEXT NOT NULL,
                opportunity_content TEXT,
                opportunity_score INTEGER,
                sender TEXT,
                action_taken TEXT NOT NULL,
                decision_maker TEXT DEFAULT 'jarvis',
                context TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Outcomes table - tracks what happened after decision
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision_id TEXT NOT NULL,
                outcome_type TEXT NOT NULL,
                outcome_status TEXT NOT NULL,
                revenue_generated REAL DEFAULT 0,
                customer_acquired BOOLEAN DEFAULT 0,
                deal_closed BOOLEAN DEFAULT 0,
                response_received BOOLEAN DEFAULT 0,
                time_to_outcome_hours REAL,
                notes TEXT,
                recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (decision_id) REFERENCES decisions(decision_id)
            )
        """)
        
        # Conversion metrics - aggregated conversion rates
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversion_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_type TEXT NOT NULL,
                opportunity_type TEXT NOT NULL,
                total_decisions INTEGER DEFAULT 0,
                total_responses INTEGER DEFAULT 0,
                total_customers INTEGER DEFAULT 0,
                total_deals_closed INTEGER DEFAULT 0,
                total_revenue REAL DEFAULT 0,
                avg_time_to_conversion_hours REAL,
                conversion_rate REAL,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(source_type, opportunity_type)
            )
        """)
        
        # Insights - generated insights from patterns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                confidence_score REAL,
                data_points INTEGER,
                generated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Predictions - ML-based predictions for opportunities
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opportunity_id TEXT NOT NULL,
                predicted_outcome TEXT,
                predicted_revenue REAL,
                predicted_conversion_probability REAL,
                similar_past_decisions TEXT,
                reasoning TEXT,
                predicted_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_decisions_timestamp 
            ON decisions(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_decisions_type 
            ON decisions(opportunity_type, opportunity_source)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_outcomes_decision 
            ON outcomes(decision_id)
        """)
        
        self.conn.commit()
        logger.info("✅ Database initialized successfully")
    
    def log_decision(
        self,
        decision_id: str,
        opportunity_type: str,
        opportunity_source: str,
        action_taken: str,
        opportunity_content: str = "",
        opportunity_score: int = 0,
        sender: str = "",
        decision_maker: str = "jarvis",
        context: dict = None
    ) -> bool:
        """
        Log a decision made on an opportunity
        
        Args:
            decision_id: Unique identifier for this decision
            opportunity_type: Type (coaching, partnership, etc.)
            opportunity_source: Source (twitter, email, etc.)
            action_taken: What action was chosen
            opportunity_content: Content of opportunity
            opportunity_score: Original score from aggregator
            sender: Who sent the opportunity
            decision_maker: Who made the decision
            context: Additional context as dict
        
        Returns:
            True if logged successfully
        """
        try:
            cursor = self.conn.cursor()
            
            timestamp = datetime.now(timezone.utc).isoformat()
            context_json = json.dumps(context) if context else None
            
            cursor.execute("""
                INSERT INTO decisions (
                    decision_id, timestamp, opportunity_type, opportunity_source,
                    opportunity_content, opportunity_score, sender, action_taken,
                    decision_maker, context
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                decision_id, timestamp, opportunity_type, opportunity_source,
                opportunity_content[:1000], opportunity_score, sender, action_taken,
                decision_maker, context_json
            ))
            
            self.conn.commit()
            
            logger.info(f"✅ Logged decision {decision_id}: {action_taken} on {opportunity_type} from {opportunity_source}")
            return True
            
        except sqlite3.IntegrityError:
            logger.warning(f"⚠️  Decision {decision_id} already exists")
            return False
        except Exception as e:
            logger.error(f"❌ Error logging decision: {e}")
            return False
    
    def record_outcome(
        self,
        decision_id: str,
        outcome_type: str,
        outcome_status: str,
        revenue_generated: float = 0,
        customer_acquired: bool = False,
        deal_closed: bool = False,
        response_received: bool = False,
        notes: str = ""
    ) -> bool:
        """
        Record the outcome of a decision
        
        Args:
            decision_id: The decision this outcome is for
            outcome_type: Type of outcome (response, conversion, closed, etc.)
            outcome_status: Status (success, failed, pending, etc.)
            revenue_generated: Revenue in USD
            customer_acquired: Whether a new customer was acquired
            deal_closed: Whether the deal closed
            response_received: Whether we got a response
            notes: Additional notes
        
        Returns:
            True if recorded successfully
        """
        try:
            # Get decision timestamp to calculate time to outcome
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT timestamp FROM decisions WHERE decision_id = ?
            """, (decision_id,))
            
            row = cursor.fetchone()
            if not row:
                logger.error(f"❌ Decision {decision_id} not found")
                return False
            
            decision_time = datetime.fromisoformat(row['timestamp'])
            outcome_time = datetime.now(timezone.utc)
            time_to_outcome = (outcome_time - decision_time).total_seconds() / 3600  # hours
            
            # Insert outcome
            cursor.execute("""
                INSERT INTO outcomes (
                    decision_id, outcome_type, outcome_status, revenue_generated,
                    customer_acquired, deal_closed, response_received,
                    time_to_outcome_hours, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                decision_id, outcome_type, outcome_status, revenue_generated,
                customer_acquired, deal_closed, response_received,
                time_to_outcome, notes
            ))
            
            self.conn.commit()
            
            # Update conversion metrics
            self._update_conversion_metrics(decision_id)
            
            logger.info(f"✅ Recorded outcome for {decision_id}: {outcome_status} (${revenue_generated})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error recording outcome: {e}")
            return False
    
    def _update_conversion_metrics(self, decision_id: str):
        """Update aggregated conversion metrics after an outcome is recorded"""
        try:
            cursor = self.conn.cursor()
            
            # Get decision details
            cursor.execute("""
                SELECT opportunity_type, opportunity_source
                FROM decisions
                WHERE decision_id = ?
            """, (decision_id,))
            
            row = cursor.fetchone()
            if not row:
                return
            
            opp_type = row['opportunity_type']
            source = row['opportunity_source']
            
            # Calculate metrics for this source+type combination
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT d.decision_id) as total_decisions,
                    SUM(CASE WHEN o.response_received = 1 THEN 1 ELSE 0 END) as total_responses,
                    SUM(CASE WHEN o.customer_acquired = 1 THEN 1 ELSE 0 END) as total_customers,
                    SUM(CASE WHEN o.deal_closed = 1 THEN 1 ELSE 0 END) as total_deals,
                    SUM(o.revenue_generated) as total_revenue,
                    AVG(CASE WHEN o.deal_closed = 1 THEN o.time_to_outcome_hours END) as avg_time
                FROM decisions d
                LEFT JOIN outcomes o ON d.decision_id = o.decision_id
                WHERE d.opportunity_type = ? AND d.opportunity_source = ?
            """, (opp_type, source))
            
            metrics = cursor.fetchone()
            
            total_decisions = metrics['total_decisions'] or 0
            total_customers = metrics['total_customers'] or 0
            conversion_rate = (total_customers / total_decisions * 100) if total_decisions > 0 else 0
            
            # Upsert metrics
            cursor.execute("""
                INSERT INTO conversion_metrics (
                    source_type, opportunity_type, total_decisions, total_responses,
                    total_customers, total_deals_closed, total_revenue,
                    avg_time_to_conversion_hours, conversion_rate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_type, opportunity_type) DO UPDATE SET
                    total_decisions = excluded.total_decisions,
                    total_responses = excluded.total_responses,
                    total_customers = excluded.total_customers,
                    total_deals_closed = excluded.total_deals_closed,
                    total_revenue = excluded.total_revenue,
                    avg_time_to_conversion_hours = excluded.avg_time_to_conversion_hours,
                    conversion_rate = excluded.conversion_rate,
                    last_updated = CURRENT_TIMESTAMP
            """, (
                source, opp_type, total_decisions, metrics['total_responses'],
                total_customers, metrics['total_deals'], metrics['total_revenue'],
                metrics['avg_time'], conversion_rate
            ))
            
            self.conn.commit()
            logger.info(f"✅ Updated conversion metrics for {source}/{opp_type}: {conversion_rate:.1f}% conversion")
            
        except Exception as e:
            logger.error(f"❌ Error updating conversion metrics: {e}")
    
    def get_conversion_rates(self) -> List[Dict]:
        """Get conversion rates by source and opportunity type"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                source_type,
                opportunity_type,
                total_decisions,
                total_customers,
                total_deals_closed,
                total_revenue,
                conversion_rate,
                avg_time_to_conversion_hours
            FROM conversion_metrics
            ORDER BY conversion_rate DESC
        """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def calculate_roi_by_type(self) -> List[Dict]:
        """Calculate ROI per decision type"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                d.opportunity_type,
                d.opportunity_source,
                COUNT(DISTINCT d.decision_id) as decisions_made,
                SUM(o.revenue_generated) as total_revenue,
                AVG(o.revenue_generated) as avg_revenue_per_decision,
                SUM(CASE WHEN o.deal_closed = 1 THEN 1 ELSE 0 END) as closed_deals,
                AVG(o.time_to_outcome_hours) as avg_time_hours
            FROM decisions d
            LEFT JOIN outcomes o ON d.decision_id = o.decision_id
            GROUP BY d.opportunity_type, d.opportunity_source
            HAVING total_revenue > 0
            ORDER BY total_revenue DESC
        """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def generate_insights(self) -> List[Dict]:
        """Generate insights from decision data"""
        insights = []
        cursor = self.conn.cursor()
        
        # Insight 1: Best converting source
        cursor.execute("""
            SELECT source_type, opportunity_type, conversion_rate, total_decisions
            FROM conversion_metrics
            WHERE total_decisions >= 3
            ORDER BY conversion_rate DESC
            LIMIT 1
        """)
        best = cursor.fetchone()
        if best:
            insights.append({
                'type': 'conversion',
                'title': f"{best['source_type'].title()} converts best",
                'description': f"{best['source_type'].title()} {best['opportunity_type']} opportunities convert at {best['conversion_rate']:.1f}% ({best['total_decisions']} decisions)",
                'confidence': 0.9 if best['total_decisions'] >= 10 else 0.7,
                'data_points': best['total_decisions']
            })
        
        # Insight 2: Compare sources
        cursor.execute("""
            SELECT source_type, AVG(conversion_rate) as avg_conversion
            FROM conversion_metrics
            WHERE total_decisions >= 2
            GROUP BY source_type
            HAVING COUNT(*) >= 1
            ORDER BY avg_conversion DESC
        """)
        sources = cursor.fetchall()
        if len(sources) >= 2:
            best_source = sources[0]
            worst_source = sources[-1]
            ratio = best_source['avg_conversion'] / worst_source['avg_conversion'] if worst_source['avg_conversion'] > 0 else 0
            if ratio > 1.5:
                insights.append({
                    'type': 'comparison',
                    'title': f"{best_source['source_type'].title()} converts {ratio:.1f}x better than {worst_source['source_type'].title()}",
                    'description': f"{best_source['source_type'].title()} averages {best_source['avg_conversion']:.1f}% conversion vs {worst_source['avg_conversion']:.1f}% for {worst_source['source_type'].title()}",
                    'confidence': 0.85,
                    'data_points': len(sources)
                })
        
        # Insight 3: Time to conversion
        cursor.execute("""
            SELECT opportunity_type, AVG(avg_time_to_conversion_hours) as avg_hours
            FROM conversion_metrics
            WHERE avg_time_to_conversion_hours IS NOT NULL
            GROUP BY opportunity_type
            ORDER BY avg_hours DESC
        """)
        times = cursor.fetchall()
        if times:
            slowest = times[0]
            days = slowest['avg_hours'] / 24
            insights.append({
                'type': 'timing',
                'title': f"{slowest['opportunity_type'].replace('_', ' ').title()} takes ~{days:.0f} days on average",
                'description': f"Average time from decision to closed deal: {slowest['avg_hours']:.1f} hours ({days:.1f} days)",
                'confidence': 0.8,
                'data_points': len(times)
            })
        
        # Insight 4: Revenue per type
        roi_data = self.calculate_roi_by_type()
        if roi_data:
            best_roi = roi_data[0]
            insights.append({
                'type': 'revenue',
                'title': f"{best_roi['opportunity_type'].replace('_', ' ').title()} generates most revenue",
                'description': f"${best_roi['total_revenue']:.2f} total from {best_roi['decisions_made']} decisions (${best_roi['avg_revenue_per_decision']:.2f} avg)",
                'confidence': 0.9,
                'data_points': best_roi['decisions_made']
            })
        
        # Save insights to database
        for insight in insights:
            try:
                cursor.execute("""
                    INSERT INTO insights (
                        insight_type, title, description, confidence_score, data_points
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    insight['type'], insight['title'], insight['description'],
                    insight['confidence'], insight['data_points']
                ))
            except Exception as e:
                logger.error(f"Error saving insight: {e}")
        
        self.conn.commit()
        
        return insights
    
    def predict_outcome(self, opportunity: Dict) -> Dict:
        """
        Predict outcome for a new opportunity based on historical data
        
        Args:
            opportunity: Opportunity dict with type, source, content, etc.
        
        Returns:
            Prediction dict with probability, expected revenue, reasoning
        """
        cursor = self.conn.cursor()
        
        opp_type = opportunity.get('type', 'general')
        source = opportunity.get('source', 'unknown')
        
        # Get historical data for similar opportunities
        cursor.execute("""
            SELECT 
                d.decision_id,
                d.opportunity_content,
                d.opportunity_score,
                o.customer_acquired,
                o.revenue_generated,
                o.time_to_outcome_hours
            FROM decisions d
            LEFT JOIN outcomes o ON d.decision_id = o.decision_id
            WHERE d.opportunity_type = ? AND d.opportunity_source = ?
            AND o.outcome_status IS NOT NULL
            ORDER BY d.timestamp DESC
            LIMIT 20
        """, (opp_type, source))
        
        similar = cursor.fetchall()
        
        if not similar:
            return {
                'predicted_outcome': 'unknown',
                'conversion_probability': 0.0,
                'predicted_revenue': 0.0,
                'confidence': 0.0,
                'reasoning': 'No historical data for this opportunity type/source combination',
                'similar_count': 0
            }
        
        # Calculate statistics from similar opportunities
        conversions = [1 if row['customer_acquired'] else 0 for row in similar]
        revenues = [row['revenue_generated'] or 0 for row in similar]
        times = [row['time_to_outcome_hours'] or 0 for row in similar if row['time_to_outcome_hours']]
        
        conversion_rate = sum(conversions) / len(conversions) if conversions else 0
        avg_revenue = statistics.mean(revenues) if revenues else 0
        avg_time = statistics.mean(times) if times else 0
        
        # Build prediction
        prediction = {
            'predicted_outcome': 'conversion' if conversion_rate >= 0.5 else 'no_conversion',
            'conversion_probability': round(conversion_rate * 100, 1),
            'predicted_revenue': round(avg_revenue, 2),
            'avg_time_to_close_hours': round(avg_time, 1),
            'avg_time_to_close_days': round(avg_time / 24, 1),
            'confidence': min(len(similar) / 20, 1.0),  # More data = higher confidence
            'reasoning': self._generate_prediction_reasoning(
                opp_type, source, conversion_rate, avg_revenue, len(similar)
            ),
            'similar_count': len(similar)
        }
        
        # Find most similar past decision
        if similar:
            best_match = similar[0]
            prediction['most_similar_decision'] = {
                'decision_id': best_match['decision_id'],
                'revenue': best_match['revenue_generated'],
                'converted': bool(best_match['customer_acquired'])
            }
        
        return prediction
    
    def _generate_prediction_reasoning(
        self,
        opp_type: str,
        source: str,
        conversion_rate: float,
        avg_revenue: float,
        sample_size: int
    ) -> str:
        """Generate human-readable reasoning for prediction"""
        
        confidence = "high" if sample_size >= 10 else "moderate" if sample_size >= 5 else "low"
        
        reasoning = f"Based on {sample_size} similar {opp_type.replace('_', ' ')} opportunities from {source}, "
        reasoning += f"we've seen a {conversion_rate*100:.1f}% conversion rate "
        reasoning += f"with average revenue of ${avg_revenue:.2f}. "
        
        if conversion_rate >= 0.7:
            reasoning += "This is a strong opportunity type. "
        elif conversion_rate >= 0.4:
            reasoning += "This opportunity type has moderate success. "
        else:
            reasoning += "This opportunity type has historically low conversion. "
        
        reasoning += f"Confidence: {confidence} ({sample_size} data points)."
        
        return reasoning
    
    def get_daily_summary(self, date: str = None) -> Dict:
        """
        Generate daily summary of decisions and outcomes
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
        
        Returns:
            Summary dict with decisions, outcomes, revenue, insights
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        cursor = self.conn.cursor()
        
        # Decisions made today
        cursor.execute("""
            SELECT COUNT(*) as count,
                   GROUP_CONCAT(DISTINCT opportunity_type) as types,
                   GROUP_CONCAT(DISTINCT opportunity_source) as sources
            FROM decisions
            WHERE DATE(timestamp) = ?
        """, (date,))
        
        decisions = cursor.fetchone()
        
        # Outcomes recorded today
        cursor.execute("""
            SELECT 
                COUNT(*) as total_outcomes,
                SUM(revenue_generated) as revenue_today,
                SUM(customer_acquired) as customers_today,
                SUM(deal_closed) as deals_closed_today
            FROM outcomes
            WHERE DATE(recorded_at) = ?
        """, (date,))
        
        outcomes = cursor.fetchone()
        
        # Recent insights
        insights = self.generate_insights()
        
        return {
            'date': date,
            'decisions': {
                'count': decisions['count'] or 0,
                'types': decisions['types'].split(',') if decisions['types'] else [],
                'sources': decisions['sources'].split(',') if decisions['sources'] else []
            },
            'outcomes': {
                'total': outcomes['total_outcomes'] or 0,
                'revenue': outcomes['revenue_today'] or 0,
                'customers': outcomes['customers_today'] or 0,
                'deals_closed': outcomes['deals_closed_today'] or 0
            },
            'insights': insights[:5],  # Top 5 insights
            'conversion_rates': self.get_conversion_rates()[:3]  # Top 3
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


def main():
    """CLI interface for decision log"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: decision_log.py [summary|insights|conversions|roi]")
        sys.exit(1)
    
    log = DecisionLog()
    
    command = sys.argv[1]
    
    if command == "summary":
        summary = log.get_daily_summary()
        print(json.dumps(summary, indent=2))
    
    elif command == "insights":
        insights = log.generate_insights()
        for insight in insights:
            print(f"\n{insight['title']}")
            print(f"  {insight['description']}")
            print(f"  Confidence: {insight['confidence']*100:.0f}% ({insight['data_points']} data points)")
    
    elif command == "conversions":
        conversions = log.get_conversion_rates()
        for conv in conversions:
            print(f"\n{conv['source_type']} → {conv['opportunity_type']}")
            print(f"  Conversion rate: {conv['conversion_rate']:.1f}%")
            print(f"  Revenue: ${conv['total_revenue']:.2f}")
            print(f"  Decisions: {conv['total_decisions']}")
    
    elif command == "roi":
        roi_data = log.calculate_roi_by_type()
        for roi in roi_data:
            print(f"\n{roi['opportunity_type']} ({roi['opportunity_source']})")
            print(f"  Total revenue: ${roi['total_revenue']:.2f}")
            print(f"  Avg per decision: ${roi['avg_revenue_per_decision']:.2f}")
            print(f"  Decisions: {roi['decisions_made']}, Closed: {roi['closed_deals']}")
    
    log.close()


if __name__ == "__main__":
    main()
