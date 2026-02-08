#!/usr/bin/env python3
"""
Opportunity Aggregator for Jarvis

Aggregates opportunities from:
1. Twitter daemon (mentions, DMs with opportunity scores)
2. Email daemon (coaching inquiries, partnerships)
3. Revenue dashboard (conversion opportunities)

Scores each 0-100 based on:
- Revenue potential (golf coaching = 90-100, partnerships = 70-80, feedback = 20-40)
- Urgency (time-sensitive signals)
- Sender influence

Runs every 30 minutes via launchd.
Output: /Users/clawdbot/clawd/data/opportunities.json
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional
import hashlib
import re

# Setup paths
WORKSPACE = Path("/Users/clawdbot/clawd")
DATA_DIR = WORKSPACE / "data"
LOG_FILE = WORKSPACE / "logs" / "opportunity-aggregator.log"

# Input files
TWITTER_FILE = DATA_DIR / "twitter-opportunities.json"
EMAIL_FILE = DATA_DIR / "email-summary.json"
REVENUE_FILE = DATA_DIR / "revenue-tasks.json"

# Output file
OUTPUT_FILE = DATA_DIR / "opportunities.json"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class OpportunityAggregator:
    """Aggregates and scores opportunities from multiple sources"""
    
    # Revenue potential scoring ranges
    REVENUE_SCORING = {
        'golf_coaching': (90, 100),
        'coaching': (90, 100),
        'partnership': (70, 80),
        'partnerships': (70, 80),
        'product_feedback': (20, 40),
        'feedback': (20, 40),
        'fitness': (50, 70),  # Fitness coaching
        'general': (10, 30)
    }
    
    # Urgency keywords boost score
    URGENCY_KEYWORDS = [
        'asap', 'urgent', 'quickly', 'soon', 'now', 'immediately',
        'today', 'tomorrow', 'deadline', 'time-sensitive',
        'need', 'looking for', 'seeking', 'interested in'
    ]
    
    def __init__(self):
        self.opportunities = []
        self.seen_hashes = set()
    
    def load_json(self, filepath: Path) -> Optional[Dict]:
        """Load JSON file safely"""
        if not filepath.exists():
            logger.warning(f"File not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from {filepath}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
            return None
    
    def content_hash(self, text: str) -> str:
        """Generate hash for deduplication"""
        # Normalize text: lowercase, remove extra whitespace
        normalized = re.sub(r'\s+', ' ', text.lower().strip())
        return hashlib.md5(normalized.encode()).hexdigest()[:12]
    
    def calculate_revenue_score(
        self,
        opp_type: str,
        content: str,
        base_score: int = 0,
        sender_influence: int = 0
    ) -> int:
        """
        Calculate final revenue potential score (0-100)
        
        Args:
            opp_type: Type of opportunity (coaching, partnership, feedback, etc.)
            content: Text content of opportunity
            base_score: Initial score from source (e.g., Twitter scoring)
            sender_influence: Influence score of sender (0-20)
        
        Returns:
            Score 0-100
        """
        content_lower = content.lower()
        
        # Get base revenue range for opportunity type
        revenue_range = self.REVENUE_SCORING.get(
            opp_type.lower(),
            self.REVENUE_SCORING['general']
        )
        
        # Start with midpoint of revenue range
        score = (revenue_range[0] + revenue_range[1]) // 2
        
        # Adjust based on urgency signals
        urgency_count = sum(1 for kw in self.URGENCY_KEYWORDS if kw in content_lower)
        urgency_boost = min(urgency_count * 3, 15)  # Max +15 for urgency
        
        # Add sender influence (max +20)
        influence_boost = min(sender_influence, 20)
        
        # If there's a base score from source, incorporate it (weighted 30%)
        if base_score > 0:
            score = int(score * 0.7 + base_score * 0.3)
        
        # Apply boosts
        score += urgency_boost + influence_boost
        
        # Cap at revenue range maximum
        score = min(score, revenue_range[1])
        score = max(score, revenue_range[0] - 10)  # Allow slightly below range minimum
        
        # Final bounds
        return max(0, min(100, score))
    
    def is_duplicate(self, content: str) -> bool:
        """Check if opportunity is duplicate based on content hash"""
        content_hash = self.content_hash(content)
        if content_hash in self.seen_hashes:
            return True
        self.seen_hashes.add(content_hash)
        return False
    
    def process_twitter(self):
        """Process Twitter opportunities"""
        logger.info("📱 Processing Twitter opportunities...")
        
        data = self.load_json(TWITTER_FILE)
        if not data:
            return
        
        # Twitter file is a list of opportunities
        opportunities = data if isinstance(data, list) else []
        
        for item in opportunities:
            content = item.get('content', '')
            
            # Skip duplicates
            if self.is_duplicate(content):
                logger.debug(f"  Skipping duplicate Twitter opportunity")
                continue
            
            # Calculate sender influence (0-20 based on followers)
            followers = item.get('author_followers', 0)
            if followers > 50000:
                influence = 20
            elif followers > 10000:
                influence = 15
            elif followers > 5000:
                influence = 10
            elif followers > 1000:
                influence = 5
            else:
                influence = 2
            
            # Get opportunity type and base score
            opp_type = item.get('opportunity_type', 'general')
            base_score = item.get('score', 0)
            
            # Calculate final revenue score
            revenue_score = self.calculate_revenue_score(
                opp_type=opp_type,
                content=content,
                base_score=base_score,
                sender_influence=influence
            )
            
            # Determine action required
            action = self._determine_action(opp_type, item)
            
            opportunity = {
                'type': opp_type,
                'score': revenue_score,
                'source': 'twitter',
                'sender': item.get('sender', 'unknown'),
                'content': content[:500],  # Limit content length
                'revenue_potential': self._get_revenue_estimate(opp_type, revenue_score),
                'action_required': action,
                'timestamp': item.get('timestamp', datetime.now(timezone.utc).isoformat()),
                'url': item.get('url', ''),
                'raw_score': base_score,
                'influence_score': influence
            }
            
            self.opportunities.append(opportunity)
            logger.info(f"  ✅ Twitter: {opp_type} from @{opportunity['sender']} (score: {revenue_score})")
    
    def process_email(self):
        """Process email opportunities"""
        logger.info("📧 Processing email opportunities...")
        
        data = self.load_json(EMAIL_FILE)
        if not data:
            return
        
        # Email file is a list of summaries
        emails = data if isinstance(data, list) else []
        
        for item in emails:
            subject = item.get('subject', '')
            sender = item.get('sender', '')
            preview = item.get('preview', '')
            content = f"{subject} {preview}"
            
            # Skip duplicates
            if self.is_duplicate(content):
                logger.debug(f"  Skipping duplicate email opportunity")
                continue
            
            # Detect opportunity type from email content
            opp_type = self._detect_email_type(subject, preview)
            
            # Email from verified sender gets influence boost
            influence = 10 if '@' in item.get('from_email', '') else 5
            
            # Calculate revenue score
            revenue_score = self.calculate_revenue_score(
                opp_type=opp_type,
                content=content,
                sender_influence=influence
            )
            
            # Determine action
            action = self._determine_action(opp_type, item)
            
            opportunity = {
                'type': opp_type,
                'score': revenue_score,
                'source': 'email',
                'sender': sender,
                'content': preview[:500],
                'revenue_potential': self._get_revenue_estimate(opp_type, revenue_score),
                'action_required': action,
                'timestamp': item.get('timestamp', datetime.now(timezone.utc).isoformat()),
                'subject': subject,
                'importance_reason': item.get('importance_reason', ''),
                'influence_score': influence
            }
            
            self.opportunities.append(opportunity)
            logger.info(f"  ✅ Email: {opp_type} from {sender} (score: {revenue_score})")
    
    def process_revenue_tasks(self):
        """Process revenue dashboard tasks"""
        logger.info("💰 Processing revenue dashboard tasks...")
        
        data = self.load_json(REVENUE_FILE)
        if not data:
            return
        
        tasks = data.get('tasks', [])
        
        for item in tasks:
            # Only process pending tasks
            if item.get('status') != 'pending':
                continue
            
            task_desc = item.get('task', '')
            
            # Skip duplicates
            if self.is_duplicate(task_desc):
                logger.debug(f"  Skipping duplicate revenue task")
                continue
            
            # Revenue tasks are conversion opportunities
            opp_type = self._detect_revenue_task_type(task_desc)
            
            # Use the revenue_potential from the task
            revenue_potential = item.get('revenue_potential', 0)
            
            # Convert revenue potential to score
            # $0-100 = 50-70, $100-300 = 70-85, $300+ = 85-100
            if revenue_potential >= 300:
                revenue_score = min(85 + (revenue_potential - 300) // 50, 100)
            elif revenue_potential >= 100:
                revenue_score = 70 + (revenue_potential - 100) // 15
            else:
                revenue_score = 50 + revenue_potential // 2
            
            revenue_score = max(50, min(100, revenue_score))
            
            opportunity = {
                'type': opp_type,
                'score': revenue_score,
                'source': 'revenue_dashboard',
                'sender': 'system',
                'content': task_desc,
                'revenue_potential': f"${revenue_potential}",
                'action_required': task_desc,
                'timestamp': item.get('created', datetime.now().strftime('%Y-%m-%d')),
                'ease': item.get('ease', 'unknown'),
                'time_required': item.get('time_required', 0),
                'task_id': item.get('id')
            }
            
            self.opportunities.append(opportunity)
            logger.info(f"  ✅ Revenue: {opp_type} - {task_desc[:50]} (score: {revenue_score})")
    
    def _detect_email_type(self, subject: str, content: str) -> str:
        """Detect opportunity type from email"""
        text = f"{subject} {content}".lower()
        
        # Check for golf coaching (highest priority)
        if any(kw in text for kw in ['golf', 'swing', 'putting', 'handicap', 'course']):
            if any(kw in text for kw in ['coach', 'lesson', 'help', 'teach', 'improve']):
                return 'golf_coaching'
        
        # Check for coaching
        if any(kw in text for kw in ['coach', 'coaching', 'mentor', 'consulting']):
            return 'coaching'
        
        # Check for partnership
        if any(kw in text for kw in ['partner', 'partnership', 'collaborate', 'work together']):
            return 'partnership'
        
        # Check for feedback
        if any(kw in text for kw in ['feedback', 'review', 'suggestion', 'feature']):
            return 'product_feedback'
        
        return 'general'
    
    def _detect_revenue_task_type(self, task: str) -> str:
        """Detect opportunity type from revenue task"""
        task_lower = task.lower()
        
        if 'golf' in task_lower and 'coach' in task_lower:
            return 'golf_coaching'
        elif 'coach' in task_lower:
            return 'coaching'
        elif 'partner' in task_lower:
            return 'partnership'
        elif any(kw in task_lower for kw in ['post', 'launch', 'marketing', 'stripe', 'payment']):
            return 'conversion'
        
        return 'general'
    
    def _get_revenue_estimate(self, opp_type: str, score: int) -> str:
        """Estimate revenue potential based on type and score"""
        if opp_type in ['golf_coaching', 'coaching']:
            if score >= 95:
                return "$500-1000"
            elif score >= 90:
                return "$200-500"
            else:
                return "$100-200"
        elif opp_type in ['partnership', 'partnerships']:
            if score >= 75:
                return "$300-800"
            else:
                return "$100-300"
        elif opp_type == 'conversion':
            if score >= 90:
                return "$300-500"
            elif score >= 70:
                return "$100-300"
            else:
                return "$50-100"
        elif opp_type in ['product_feedback', 'feedback']:
            return "$0-50"
        else:
            return "$0-100"
    
    def _determine_action(self, opp_type: str, item: Dict) -> str:
        """Determine required action for opportunity"""
        if opp_type in ['golf_coaching', 'coaching']:
            return "Reply with coaching offer and availability"
        elif opp_type in ['partnership', 'partnerships']:
            return "Schedule call to discuss partnership details"
        elif opp_type in ['product_feedback', 'feedback']:
            return "Review feedback and send thank you"
        elif 'url' in item:
            return "Respond to message"
        else:
            return "Review and take appropriate action"
    
    def merge_and_deduplicate(self):
        """Merge similar opportunities and remove duplicates"""
        logger.info("🔄 Merging and deduplicating opportunities...")
        
        # Already deduplicated by content hash during processing
        # This is a placeholder for future similarity detection
        
        initial_count = len(self.opportunities)
        logger.info(f"  {initial_count} unique opportunities after deduplication")
    
    def rank_opportunities(self):
        """Sort opportunities by revenue potential (score)"""
        logger.info("📊 Ranking opportunities by revenue potential...")
        
        # Sort by score (descending), then by timestamp (newest first)
        self.opportunities.sort(
            key=lambda x: (x['score'], x['timestamp']),
            reverse=True
        )
        
        if self.opportunities:
            top_score = self.opportunities[0]['score']
            logger.info(f"  Top opportunity score: {top_score}")
    
    def save_opportunities(self):
        """Save aggregated opportunities to JSON"""
        logger.info(f"💾 Saving {len(self.opportunities)} opportunities to {OUTPUT_FILE}")
        
        output = {
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'total_opportunities': len(self.opportunities),
            'opportunities': self.opportunities,
            'summary': self._generate_summary()
        }
        
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(output, f, indent=2)
        
        logger.info(f"✅ Saved to {OUTPUT_FILE}")
    
    def _generate_summary(self) -> Dict:
        """Generate summary statistics"""
        if not self.opportunities:
            return {
                'high_priority': 0,
                'medium_priority': 0,
                'low_priority': 0,
                'by_type': {},
                'by_source': {}
            }
        
        high = sum(1 for o in self.opportunities if o['score'] >= 80)
        medium = sum(1 for o in self.opportunities if 50 <= o['score'] < 80)
        low = sum(1 for o in self.opportunities if o['score'] < 50)
        
        by_type = {}
        by_source = {}
        
        for opp in self.opportunities:
            opp_type = opp['type']
            source = opp['source']
            
            by_type[opp_type] = by_type.get(opp_type, 0) + 1
            by_source[source] = by_source.get(source, 0) + 1
        
        return {
            'high_priority': high,
            'medium_priority': medium,
            'low_priority': low,
            'by_type': by_type,
            'by_source': by_source
        }
    
    def run(self):
        """Main aggregation process"""
        logger.info("=" * 70)
        logger.info("🎯 OPPORTUNITY AGGREGATOR STARTING")
        logger.info(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 70)
        
        try:
            # Process each source
            self.process_twitter()
            self.process_email()
            self.process_revenue_tasks()
            
            # Merge and deduplicate
            self.merge_and_deduplicate()
            
            # Rank by revenue potential
            self.rank_opportunities()
            
            # Save results
            self.save_opportunities()
            
            # Summary
            summary = self._generate_summary()
            logger.info("")
            logger.info("📈 SUMMARY")
            logger.info(f"   Total opportunities: {len(self.opportunities)}")
            logger.info(f"   High priority (80-100): {summary['high_priority']}")
            logger.info(f"   Medium priority (50-79): {summary['medium_priority']}")
            logger.info(f"   Low priority (<50): {summary['low_priority']}")
            logger.info("")
            logger.info("   By type:")
            for opp_type, count in sorted(summary['by_type'].items(), key=lambda x: x[1], reverse=True):
                logger.info(f"     {opp_type}: {count}")
            logger.info("")
            logger.info("   By source:")
            for source, count in sorted(summary['by_source'].items()):
                logger.info(f"     {source}: {count}")
            
            logger.info("")
            logger.info("✅ OPPORTUNITY AGGREGATOR COMPLETED SUCCESSFULLY")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}", exc_info=True)
            sys.exit(1)


def main():
    """Entry point"""
    aggregator = OpportunityAggregator()
    aggregator.run()


if __name__ == "__main__":
    main()
