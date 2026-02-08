#!/usr/bin/env python3
"""
Analytics Tracker - Core analytics engine for Mac mini
Tracks opportunity conversions, social engagement, and source quality
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict

# Configure logging
LOG_DIR = Path.home() / "clawd" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "analytics_tracker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("analytics_tracker")

# File paths
WORKSPACE = Path.home() / "clawd"
DATA_DIR = WORKSPACE / "data"
ANALYTICS_FILE = DATA_DIR / "analytics.json"
OPPORTUNITIES_FILE = DATA_DIR / "opportunities.json"
SOCIAL_POSTS_FILE = DATA_DIR / "social-posts-queue.json"


class AnalyticsTracker:
    """Main analytics tracking system"""
    
    def __init__(self):
        self.analytics_data = self._load_analytics()
        logger.info("Analytics Tracker initialized")
    
    def _load_analytics(self) -> Dict:
        """Load existing analytics or create new structure"""
        if ANALYTICS_FILE.exists():
            try:
                with open(ANALYTICS_FILE) as f:
                    data = json.load(f)
                    logger.info(f"Loaded existing analytics: {len(data.get('opportunities', []))} opportunities tracked")
                    return data
            except Exception as e:
                logger.error(f"Error loading analytics: {e}")
        
        # Initialize new analytics structure
        return {
            "version": "1.0",
            "last_updated": datetime.utcnow().isoformat(),
            "opportunities": [],
            "social_posts": [],
            "conversions": [],
            "engagement_by_hour": {str(h): {"posts": 0, "engagement": 0} for h in range(24)},
            "source_performance": {
                "email": {"total": 0, "converted": 0, "revenue": 0},
                "twitter": {"total": 0, "converted": 0, "revenue": 0},
                "reddit": {"total": 0, "converted": 0, "revenue": 0},
                "other": {"total": 0, "converted": 0, "revenue": 0}
            },
            "opportunity_types": {},
            "weekly_stats": []
        }
    
    def _save_analytics(self):
        """Save analytics to file"""
        try:
            self.analytics_data["last_updated"] = datetime.utcnow().isoformat()
            with open(ANALYTICS_FILE, 'w') as f:
                json.dump(self.analytics_data, f, indent=2)
            logger.info("Analytics data saved successfully")
        except Exception as e:
            logger.error(f"Error saving analytics: {e}")
    
    def track_opportunity(self, opportunity: Dict) -> bool:
        """
        Track a new or updated opportunity
        
        Args:
            opportunity: Dict with fields like source, type, score, revenue_potential, timestamp
        
        Returns:
            bool: Success status
        """
        try:
            # Create tracking ID if not present
            if 'tracking_id' not in opportunity:
                opportunity['tracking_id'] = f"{opportunity.get('source', 'unknown')}_{opportunity.get('timestamp', datetime.utcnow().isoformat())}"
            
            # Check if already tracked
            existing = next((o for o in self.analytics_data['opportunities'] if o.get('tracking_id') == opportunity['tracking_id']), None)
            
            if existing:
                # Update existing
                existing.update(opportunity)
                existing['last_updated'] = datetime.utcnow().isoformat()
                logger.info(f"Updated opportunity: {opportunity['tracking_id']}")
            else:
                # Add new
                opportunity['tracked_at'] = datetime.utcnow().isoformat()
                opportunity['status'] = opportunity.get('status', 'pending')
                opportunity['converted'] = False
                self.analytics_data['opportunities'].append(opportunity)
                
                # Update source counts
                source = self._normalize_source(opportunity.get('source', 'other'))
                self.analytics_data['source_performance'][source]['total'] += 1
                
                logger.info(f"Tracked new opportunity: {opportunity['tracking_id']} from {source}")
            
            self._save_analytics()
            return True
            
        except Exception as e:
            logger.error(f"Error tracking opportunity: {e}")
            return False
    
    def mark_conversion(self, tracking_id: str, revenue: float, notes: str = "") -> bool:
        """
        Mark an opportunity as converted
        
        Args:
            tracking_id: Opportunity tracking ID
            revenue: Revenue amount
            notes: Additional notes
        
        Returns:
            bool: Success status
        """
        try:
            opportunity = next((o for o in self.analytics_data['opportunities'] if o.get('tracking_id') == tracking_id), None)
            
            if not opportunity:
                logger.warning(f"Opportunity not found: {tracking_id}")
                return False
            
            # Mark as converted
            opportunity['converted'] = True
            opportunity['conversion_date'] = datetime.utcnow().isoformat()
            opportunity['actual_revenue'] = revenue
            opportunity['conversion_notes'] = notes
            
            # Update source performance
            source = self._normalize_source(opportunity.get('source', 'other'))
            self.analytics_data['source_performance'][source]['converted'] += 1
            self.analytics_data['source_performance'][source]['revenue'] += revenue
            
            # Add to conversions list
            self.analytics_data['conversions'].append({
                "tracking_id": tracking_id,
                "source": source,
                "type": opportunity.get('type'),
                "revenue": revenue,
                "date": datetime.utcnow().isoformat(),
                "notes": notes
            })
            
            logger.info(f"Marked conversion: {tracking_id} - ${revenue} from {source}")
            self._save_analytics()
            return True
            
        except Exception as e:
            logger.error(f"Error marking conversion: {e}")
            return False
    
    def track_social_post(self, post: Dict) -> bool:
        """
        Track social media post for engagement analysis
        
        Args:
            post: Dict with fields like id, text, posted_at, twitter_id
        
        Returns:
            bool: Success status
        """
        try:
            post_id = post.get('id') or post.get('twitter_id')
            if not post_id:
                logger.warning("Post missing ID, cannot track")
                return False
            
            # Check if already tracked
            existing = next((p for p in self.analytics_data['social_posts'] if p.get('id') == post_id), None)
            
            if existing:
                # Update engagement metrics
                if 'likes' in post:
                    existing['likes'] = post['likes']
                if 'retweets' in post:
                    existing['retweets'] = post['retweets']
                if 'replies' in post:
                    existing['replies'] = post['replies']
                if 'clicks' in post:
                    existing['clicks'] = post['clicks']
                existing['last_checked'] = datetime.utcnow().isoformat()
                logger.info(f"Updated social post: {post_id}")
            else:
                # Add new post
                post['tracked_at'] = datetime.utcnow().isoformat()
                post['likes'] = post.get('likes', 0)
                post['retweets'] = post.get('retweets', 0)
                post['replies'] = post.get('replies', 0)
                post['clicks'] = post.get('clicks', 0)
                self.analytics_data['social_posts'].append(post)
                
                # Track posting time
                if 'posted_at' in post:
                    hour = self._extract_hour(post['posted_at'])
                    if hour is not None:
                        self.analytics_data['engagement_by_hour'][str(hour)]['posts'] += 1
                
                logger.info(f"Tracked new social post: {post_id}")
            
            # Update engagement by hour
            if 'posted_at' in post:
                hour = self._extract_hour(post['posted_at'])
                if hour is not None:
                    engagement = post.get('likes', 0) + post.get('retweets', 0) * 2 + post.get('replies', 0) * 3
                    self.analytics_data['engagement_by_hour'][str(hour)]['engagement'] = max(
                        self.analytics_data['engagement_by_hour'][str(hour)]['engagement'],
                        engagement
                    )
            
            self._save_analytics()
            return True
            
        except Exception as e:
            logger.error(f"Error tracking social post: {e}")
            return False
    
    def sync_opportunities(self) -> int:
        """
        Sync opportunities from opportunities.json
        
        Returns:
            int: Number of opportunities synced
        """
        try:
            if not OPPORTUNITIES_FILE.exists():
                logger.warning("Opportunities file not found")
                return 0
            
            with open(OPPORTUNITIES_FILE) as f:
                data = json.load(f)
            
            opportunities = data.get('opportunities', [])
            synced = 0
            
            for opp in opportunities:
                # Create tracking structure
                tracking_opp = {
                    'tracking_id': f"{opp.get('source', 'unknown')}_{opp.get('timestamp', datetime.utcnow().isoformat())}_{opp.get('sender', 'unknown')}",
                    'source': opp.get('source', 'other'),
                    'type': opp.get('type', 'unknown'),
                    'score': opp.get('score', 0),
                    'revenue_potential': opp.get('revenue_potential', '$0'),
                    'timestamp': opp.get('timestamp', datetime.utcnow().isoformat()),
                    'sender': opp.get('sender'),
                    'content_preview': opp.get('content', '')[:200]
                }
                
                if self.track_opportunity(tracking_opp):
                    synced += 1
            
            logger.info(f"Synced {synced} opportunities from opportunities.json")
            return synced
            
        except Exception as e:
            logger.error(f"Error syncing opportunities: {e}")
            return 0
    
    def sync_social_posts(self) -> int:
        """
        Sync social posts from social-posts-queue.json
        
        Returns:
            int: Number of posts synced
        """
        try:
            if not SOCIAL_POSTS_FILE.exists():
                logger.warning("Social posts file not found")
                return 0
            
            with open(SOCIAL_POSTS_FILE) as f:
                posts = json.load(f)
            
            synced = 0
            for post in posts:
                if post.get('posted') and post.get('posted_at'):
                    if self.track_social_post(post):
                        synced += 1
            
            logger.info(f"Synced {synced} social posts from queue")
            return synced
            
        except Exception as e:
            logger.error(f"Error syncing social posts: {e}")
            return 0
    
    def get_conversion_rate(self, source: Optional[str] = None) -> float:
        """Calculate conversion rate for a source or overall"""
        try:
            if source:
                source = self._normalize_source(source)
                perf = self.analytics_data['source_performance'][source]
                if perf['total'] == 0:
                    return 0.0
                return (perf['converted'] / perf['total']) * 100
            else:
                # Overall conversion rate
                total = sum(p['total'] for p in self.analytics_data['source_performance'].values())
                converted = sum(p['converted'] for p in self.analytics_data['source_performance'].values())
                if total == 0:
                    return 0.0
                return (converted / total) * 100
        except Exception as e:
            logger.error(f"Error calculating conversion rate: {e}")
            return 0.0
    
    def get_best_posting_time(self) -> Dict[str, Any]:
        """Find best time to post based on engagement"""
        try:
            engagement_data = self.analytics_data['engagement_by_hour']
            
            # Calculate average engagement per post for each hour
            best_hour = None
            best_avg = 0
            hourly_avgs = {}
            
            for hour, data in engagement_data.items():
                if data['posts'] > 0:
                    avg = data['engagement'] / data['posts']
                    hourly_avgs[hour] = avg
                    if avg > best_avg:
                        best_avg = avg
                        best_hour = hour
            
            return {
                "best_hour": best_hour,
                "avg_engagement": best_avg,
                "hourly_breakdown": hourly_avgs
            }
        except Exception as e:
            logger.error(f"Error finding best posting time: {e}")
            return {"best_hour": None, "avg_engagement": 0, "hourly_breakdown": {}}
    
    def _normalize_source(self, source: str) -> str:
        """Normalize source names"""
        source = source.lower()
        if 'email' in source:
            return 'email'
        elif 'twitter' in source or 'tweet' in source:
            return 'twitter'
        elif 'reddit' in source:
            return 'reddit'
        else:
            return 'other'
    
    def _extract_hour(self, timestamp: str) -> Optional[int]:
        """Extract hour from ISO timestamp"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.hour
        except:
            return None
    
    def generate_summary(self) -> Dict:
        """Generate analytics summary"""
        try:
            total_opps = len(self.analytics_data['opportunities'])
            converted = sum(1 for o in self.analytics_data['opportunities'] if o.get('converted'))
            total_revenue = sum(c['revenue'] for c in self.analytics_data['conversions'])
            
            source_perf = {}
            for source, data in self.analytics_data['source_performance'].items():
                if data['total'] > 0:
                    source_perf[source] = {
                        "total": data['total'],
                        "converted": data['converted'],
                        "conversion_rate": (data['converted'] / data['total']) * 100,
                        "revenue": data['revenue']
                    }
            
            best_time = self.get_best_posting_time()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "opportunities": {
                    "total": total_opps,
                    "converted": converted,
                    "conversion_rate": (converted / total_opps * 100) if total_opps > 0 else 0,
                    "total_revenue": total_revenue
                },
                "source_performance": source_perf,
                "social_posts": {
                    "total_tracked": len(self.analytics_data['social_posts']),
                    "best_posting_time": best_time
                }
            }
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {}


def main():
    """Main execution"""
    logger.info("=== Analytics Tracker Starting ===")
    
    tracker = AnalyticsTracker()
    
    # Sync data
    logger.info("Syncing opportunities...")
    tracker.sync_opportunities()
    
    logger.info("Syncing social posts...")
    tracker.sync_social_posts()
    
    # Generate summary
    summary = tracker.generate_summary()
    logger.info(f"Analytics Summary: {json.dumps(summary, indent=2)}")
    
    logger.info("=== Analytics Tracker Complete ===")


if __name__ == "__main__":
    main()
