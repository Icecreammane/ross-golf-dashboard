#!/usr/bin/env python3
"""
Twitter Monitoring Daemon for Ross

Monitors:
- Mentions to Ross (@_icecreammane)
- Direct Messages
- Engagement opportunities

Flags opportunities in:
- Golf, fitness, coaching, partnerships, product feedback

Runs every 15 minutes via launchd.
"""

import os
import sys
import json
import logging
import tweepy
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv
import time

# Setup paths
WORKSPACE = Path("/Users/clawdbot/clawd")
DATA_FILE = WORKSPACE / "data" / "twitter-opportunities.json"
STATE_FILE = WORKSPACE / "data" / "twitter-daemon-state.json"
LOG_FILE = WORKSPACE / "logs" / "twitter-daemon.log"

# Ensure directories exist
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
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

# Load environment variables
load_dotenv(WORKSPACE / ".env")


class OpportunityScorer:
    """Scores opportunities based on keywords and context"""
    
    # Opportunity keywords and their weights
    KEYWORDS = {
        'golf': {
            'keywords': ['golf', 'golfer', 'course', 'handicap', 'swing', 'putting', 'tee time'],
            'weight': 8
        },
        'fitness': {
            'keywords': ['fitness', 'workout', 'training', 'gym', 'exercise', 'strength', 'cardio', 'nutrition', 'macros'],
            'weight': 9
        },
        'coaching': {
            'keywords': ['coach', 'coaching', 'mentor', 'consulting', 'advice', 'guidance', 'help me', 'teach'],
            'weight': 10
        },
        'partnership': {
            'keywords': ['partner', 'partnership', 'collaborate', 'work together', 'joint venture', 'co-founder', 'opportunity'],
            'weight': 10
        },
        'product_feedback': {
            'keywords': ['feedback', 'feature', 'suggestion', 'improve', 'bug', 'issue', 'would be great', 'wish'],
            'weight': 7
        }
    }
    
    URGENCY_SIGNALS = [
        'asap', 'urgent', 'quickly', 'soon', 'now', 'immediately',
        'looking for', 'need', 'seeking', 'interested in', 'want to'
    ]
    
    ENGAGEMENT_SIGNALS = [
        'love', 'amazing', 'awesome', 'great', 'fantastic', 'incredible',
        'impressed', 'wow', 'brilliant', 'perfect', 'exactly'
    ]
    
    @classmethod
    def score(cls, text: str, author_metrics: Optional[Dict] = None) -> Dict:
        """
        Score an opportunity based on content and author metrics
        
        Returns:
            {
                'score': int (0-100),
                'opportunity_type': str,
                'reasons': List[str]
            }
        """
        text_lower = text.lower()
        score = 0
        detected_types = []
        reasons = []
        
        # Check for opportunity keywords
        for opp_type, config in cls.KEYWORDS.items():
            matches = [kw for kw in config['keywords'] if kw in text_lower]
            if matches:
                score += config['weight']
                detected_types.append(opp_type)
                reasons.append(f"{opp_type}: {', '.join(matches)}")
        
        # Check urgency signals
        urgency_matches = [sig for sig in cls.URGENCY_SIGNALS if sig in text_lower]
        if urgency_matches:
            score += 5
            reasons.append(f"urgency: {', '.join(urgency_matches)}")
        
        # Check engagement signals
        engagement_matches = [sig for sig in cls.ENGAGEMENT_SIGNALS if sig in text_lower]
        if engagement_matches:
            score += 3
            reasons.append(f"positive engagement: {', '.join(engagement_matches)}")
        
        # Question signals (people asking questions are more engaged)
        if '?' in text:
            score += 2
            reasons.append("contains question")
        
        # Author influence (if metrics provided)
        if author_metrics:
            followers = author_metrics.get('followers_count', 0)
            if followers > 10000:
                score += 5
                reasons.append(f"influential author ({followers:,} followers)")
            elif followers > 1000:
                score += 2
                reasons.append(f"notable author ({followers:,} followers)")
        
        # Cap score at 100
        score = min(score, 100)
        
        # Determine primary opportunity type
        primary_type = detected_types[0] if detected_types else 'general'
        
        return {
            'score': score,
            'opportunity_type': primary_type,
            'all_types': detected_types,
            'reasons': reasons
        }


class TwitterDaemon:
    """Twitter monitoring daemon"""
    
    def __init__(self):
        self.client = None
        self.api = None
        self.my_user_id = None
        self.my_username = None
        
        # Load credentials
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_secret = os.getenv('TWITTER_ACCESS_SECRET')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        if not all([self.api_key, self.api_secret, self.access_token, self.access_secret]):
            raise Exception("Twitter API credentials not configured in .env")
    
    def authenticate(self):
        """Authenticate with Twitter API"""
        try:
            # Twitter API v2 client
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_secret,
                wait_on_rate_limit=True
            )
            
            # Get authenticated user info
            me = self.client.get_me(user_auth=True)
            self.my_user_id = me.data.id
            self.my_username = me.data.username
            
            logger.info(f"✅ Authenticated as @{self.my_username} (ID: {self.my_user_id})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            raise
    
    def load_state(self) -> Dict:
        """Load daemon state (last checked IDs)"""
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        return {
            'last_mention_id': None,
            'last_dm_id': None,
            'last_run': None
        }
    
    def save_state(self, state: Dict):
        """Save daemon state"""
        state['last_run'] = datetime.now(timezone.utc).isoformat()
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        logger.info(f"State saved: last_mention={state.get('last_mention_id')}, last_dm={state.get('last_dm_id')}")
    
    def load_opportunities(self) -> List[Dict]:
        """Load existing opportunities"""
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def save_opportunities(self, opportunities: List[Dict]):
        """Save opportunities to JSON"""
        # Sort by score (descending) and timestamp (newest first)
        opportunities.sort(key=lambda x: (x['score'], x['timestamp']), reverse=True)
        
        with open(DATA_FILE, 'w') as f:
            json.dump(opportunities, f, indent=2)
        
        logger.info(f"💾 Saved {len(opportunities)} opportunities to {DATA_FILE}")
    
    def check_mentions(self, state: Dict) -> List[Dict]:
        """Check for new mentions"""
        logger.info("🔍 Checking mentions...")
        
        opportunities = []
        
        try:
            # Get mentions (tweets that mention the authenticated user)
            params = {
                'max_results': 100,
                'tweet_fields': ['created_at', 'public_metrics', 'conversation_id'],
                'expansions': ['author_id'],
                'user_fields': ['username', 'public_metrics']
            }
            
            # If we have a last mention ID, only get tweets since then
            if state.get('last_mention_id'):
                params['since_id'] = state['last_mention_id']
            
            response = self.client.get_users_mentions(
                id=self.my_user_id,
                **params
            )
            
            if not response.data:
                logger.info("  No new mentions")
                return []
            
            # Build user lookup
            users = {}
            if response.includes and 'users' in response.includes:
                users = {user.id: user for user in response.includes['users']}
            
            # Process mentions
            for tweet in response.data:
                author = users.get(tweet.author_id)
                author_username = author.username if author else 'unknown'
                author_metrics = author.public_metrics if author else {}
                
                # Score the opportunity
                scoring = OpportunityScorer.score(tweet.text, author_metrics)
                
                # Only save if score is meaningful (>5)
                if scoring['score'] > 5:
                    opportunity = {
                        'id': f"mention_{tweet.id}",
                        'type': 'mention',
                        'sender': author_username,
                        'sender_id': tweet.author_id,
                        'content': tweet.text,
                        'timestamp': tweet.created_at.isoformat(),
                        'url': f"https://twitter.com/{author_username}/status/{tweet.id}",
                        'score': scoring['score'],
                        'opportunity_type': scoring['opportunity_type'],
                        'all_types': scoring['all_types'],
                        'reasons': scoring['reasons'],
                        'metrics': tweet.public_metrics,
                        'author_followers': author_metrics.get('followers_count', 0)
                    }
                    
                    opportunities.append(opportunity)
                    logger.info(f"  ✅ Opportunity found: @{author_username} - {scoring['opportunity_type']} (score: {scoring['score']})")
                    logger.info(f"     {tweet.text[:100]}...")
            
            # Update state with latest mention ID
            if response.data:
                state['last_mention_id'] = response.data[0].id
            
            logger.info(f"  Found {len(opportunities)} new opportunities in mentions")
            
        except tweepy.TweepyException as e:
            logger.error(f"❌ Error checking mentions: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error checking mentions: {e}", exc_info=True)
        
        return opportunities
    
    def check_dms(self, state: Dict) -> List[Dict]:
        """Check for important DMs"""
        logger.info("💬 Checking DMs...")
        
        opportunities = []
        
        try:
            # Note: Twitter API v2 DM access requires elevated API access
            # For now, we'll catch the error gracefully if access isn't available
            
            # Get DM events (this requires elevated access)
            response = self.client.get_direct_message_events(
                max_results=100,
                event_types=['MessageCreate'],
                expansions=['sender_id'],
                user_fields=['username', 'public_metrics']
            )
            
            if not response.data:
                logger.info("  No new DMs")
                return []
            
            # Build user lookup
            users = {}
            if response.includes and 'users' in response.includes:
                users = {user.id: user for user in response.includes['users']}
            
            # Process DMs
            for dm in response.data:
                # Skip DMs from ourselves
                if dm.sender_id == self.my_user_id:
                    continue
                
                # Skip if we've already processed this DM
                if state.get('last_dm_id') and dm.id <= state['last_dm_id']:
                    continue
                
                sender = users.get(dm.sender_id)
                sender_username = sender.username if sender else 'unknown'
                sender_metrics = sender.public_metrics if sender else {}
                
                # Score the DM
                scoring = OpportunityScorer.score(dm.text, sender_metrics)
                
                # DMs are generally more important, so boost score
                scoring['score'] = min(scoring['score'] + 10, 100)
                
                # Only save if score is meaningful (>10 for DMs)
                if scoring['score'] > 10:
                    opportunity = {
                        'id': f"dm_{dm.id}",
                        'type': 'dm',
                        'sender': sender_username,
                        'sender_id': dm.sender_id,
                        'content': dm.text,
                        'timestamp': dm.created_at.isoformat() if hasattr(dm, 'created_at') else datetime.now(timezone.utc).isoformat(),
                        'url': 'https://twitter.com/messages',  # DMs don't have public URLs
                        'score': scoring['score'],
                        'opportunity_type': scoring['opportunity_type'],
                        'all_types': scoring['all_types'],
                        'reasons': scoring['reasons'] + ['direct message (boosted importance)'],
                        'author_followers': sender_metrics.get('followers_count', 0)
                    }
                    
                    opportunities.append(opportunity)
                    logger.info(f"  ✅ Important DM from @{sender_username} - {scoring['opportunity_type']} (score: {scoring['score']})")
            
            # Update state with latest DM ID
            if response.data:
                state['last_dm_id'] = response.data[0].id
            
            logger.info(f"  Found {len(opportunities)} important DMs")
            
        except tweepy.Forbidden as e:
            logger.warning(f"⚠️  DM access requires elevated API access. Skipping DMs. ({e})")
        except tweepy.TweepyException as e:
            logger.error(f"❌ Error checking DMs: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error checking DMs: {e}", exc_info=True)
        
        return opportunities
    
    def run(self):
        """Main daemon run - check for opportunities"""
        logger.info("="*60)
        logger.info("🐦 Twitter Daemon starting...")
        logger.info(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Authenticate
            self.authenticate()
            
            # Load state
            state = self.load_state()
            logger.info(f"   Last run: {state.get('last_run', 'never')}")
            
            # Load existing opportunities
            all_opportunities = self.load_opportunities()
            existing_ids = {opp['id'] for opp in all_opportunities}
            
            # Check mentions
            new_mentions = self.check_mentions(state)
            
            # Check DMs
            new_dms = self.check_dms(state)
            
            # Combine new opportunities
            new_opportunities = new_mentions + new_dms
            
            # Add only new opportunities (avoid duplicates)
            added_count = 0
            for opp in new_opportunities:
                if opp['id'] not in existing_ids:
                    all_opportunities.append(opp)
                    existing_ids.add(opp['id'])
                    added_count += 1
            
            # Save opportunities
            if added_count > 0:
                self.save_opportunities(all_opportunities)
                logger.info(f"✅ Added {added_count} new opportunities (total: {len(all_opportunities)})")
            else:
                logger.info("✅ No new opportunities to add")
            
            # Save state
            self.save_state(state)
            
            # Summary
            high_score_opps = [opp for opp in all_opportunities if opp['score'] >= 50]
            if high_score_opps:
                logger.info(f"🔥 {len(high_score_opps)} high-priority opportunities (score ≥50)")
            
            logger.info("🐦 Twitter Daemon completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Fatal error in daemon: {e}", exc_info=True)
            sys.exit(1)
        
        logger.info("="*60 + "\n")


def main():
    """Entry point"""
    daemon = TwitterDaemon()
    daemon.run()


if __name__ == "__main__":
    main()
