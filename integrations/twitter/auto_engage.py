"""
Smart Auto-Engagement
Automatically engage with relevant content (with safety limits)
"""

from twitter_bot import TwitterBot
from engagement_monitor import EngagementMonitor
from typing import List, Dict
import time
import random

class AutoEngage:
    def __init__(self, dry_run: bool = False):
        self.bot = TwitterBot()
        self.monitor = EngagementMonitor()
        self.dry_run = dry_run
        
        # Safety limits
        self.max_likes_per_hour = 10
        self.max_replies_per_hour = 3
        self.max_total_per_day = 50
        
    def should_engage(self, opportunity: Dict) -> bool:
        """Determine if we should engage with this opportunity"""
        # Skip if already engaged
        if self.bot.has_engaged(opportunity['tweet_id']):
            return False
        
        # Higher chance for high priority
        if opportunity['priority'] == 'high':
            return random.random() > 0.2  # 80% chance
        elif opportunity['priority'] == 'medium':
            return random.random() > 0.5  # 50% chance
        else:
            return random.random() > 0.7  # 30% chance
    
    def engage_with_opportunity(self, opportunity: Dict) -> bool:
        """Engage with a specific opportunity"""
        tweet_id = opportunity['tweet_id']
        action = opportunity['suggested_action']
        
        if self.dry_run:
            print(f"[DRY RUN] Would engage with: {opportunity['type']}")
            print(f"[DRY RUN] Tweet: {opportunity['text'][:80]}...")
            return True
        
        # Always like first
        like_success = self.bot.like_tweet(tweet_id)
        
        # Reply if it's a high-value interaction
        if action in ['reply_thanks', 'reply_helpful', 'reply_answer']:
            if opportunity['priority'] == 'high':
                reply_text = self.monitor.get_reply_template(opportunity)
                self.bot.reply_to_tweet(tweet_id, reply_text)
        
        return like_success
    
    def run_engagement_cycle(self, max_actions: int = 10):
        """Run one engagement cycle"""
        print("="*50)
        print("🤖 Auto-Engagement Cycle")
        print("="*50)
        
        if self.dry_run:
            print("⚠️  DRY RUN MODE - No actual engagement")
        
        # Authenticate
        if not self.bot.authenticate():
            return
        
        # Get opportunities
        print("\n📊 Identifying opportunities...")
        opportunities = self.monitor.identify_opportunities()
        
        if not opportunities:
            print("✅ No opportunities found")
            return
        
        print(f"Found {len(opportunities)} opportunities")
        
        # Engage with opportunities
        actions_taken = 0
        for opp in opportunities:
            if actions_taken >= max_actions:
                break
            
            if self.should_engage(opp):
                print(f"\n💬 Engaging with: {opp['type']}")
                print(f"   {opp['text'][:60]}...")
                
                if self.engage_with_opportunity(opp):
                    actions_taken += 1
                
                # Rate limit protection
                time.sleep(random.uniform(3, 7))
        
        print("\n" + "="*50)
        print(f"✅ Took {actions_taken} engagement actions")
        
        # Show stats
        stats = self.bot.get_engagement_stats(days=1)
        print(f"\nToday's stats:")
        print(f"  ❤️  Likes: {stats['likes']}")
        print(f"  💬 Replies: {stats['replies']}")
        print(f"  📝 Tweets: {stats['tweets']}")


if __name__ == "__main__":
    import sys
    
    # Check for dry run flag
    dry_run = '--dry-run' in sys.argv
    
    auto = AutoEngage(dry_run=dry_run)
    
    print("🐦 Twitter Auto-Engagement")
    if dry_run:
        print("⚠️  Running in DRY RUN mode (no actual engagement)")
    print("")
    
    auto.run_engagement_cycle(max_actions=10)
