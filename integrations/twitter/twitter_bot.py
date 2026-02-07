"""
Twitter Automation Engine
Automated posting, engagement, and monitoring
"""

import os
import json
import tweepy
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
import time
import random

load_dotenv()

class TwitterBot:
    def __init__(self):
        # Twitter API credentials
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_secret = os.getenv('TWITTER_ACCESS_SECRET')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        self.client = None
        self.api = None
        
        self.tweet_queue_file = 'tweet_queue.json'
        self.engagement_log_file = 'engagement_log.json'
        
    def authenticate(self):
        """Authenticate with Twitter API v2"""
        if not all([self.api_key, self.api_secret, self.access_token, self.access_secret]):
            raise Exception("Twitter credentials not configured")
        
        # v2 client
        self.client = tweepy.Client(
            bearer_token=self.bearer_token,
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_secret
        )
        
        # v1.1 API for some features
        auth = tweepy.OAuth1UserHandler(
            self.api_key, self.api_secret,
            self.access_token, self.access_secret
        )
        self.api = tweepy.API(auth)
        
        # Verify authentication
        try:
            user = self.api.verify_credentials()
            print(f"✅ Authenticated as @{user.screen_name}")
            return True
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
    
    def load_tweet_queue(self) -> List[Dict]:
        """Load tweet queue from JSON"""
        if os.path.exists(self.tweet_queue_file):
            with open(self.tweet_queue_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_tweet_queue(self, queue: List[Dict]):
        """Save tweet queue to JSON"""
        with open(self.tweet_queue_file, 'w') as f:
            json.dump(queue, f, indent=2)
    
    def get_next_tweet(self) -> Optional[Dict]:
        """Get next scheduled tweet"""
        queue = self.load_tweet_queue()
        
        # Find next unposted tweet
        for tweet in queue:
            if not tweet.get('posted', False):
                return tweet
        
        return None
    
    def post_tweet(self, text: str, tweet_id: Optional[str] = None) -> Optional[str]:
        """Post a tweet"""
        if not self.client:
            self.authenticate()
        
        try:
            response = self.client.create_tweet(text=text)
            tweet_id = response.data['id']
            
            print(f"✅ Posted: {text[:50]}...")
            return tweet_id
            
        except Exception as e:
            print(f"❌ Failed to post tweet: {e}")
            return None
    
    def post_from_queue(self) -> bool:
        """Post next tweet from queue"""
        tweet = self.get_next_tweet()
        
        if not tweet:
            print("⚠️  No tweets in queue")
            return False
        
        text = tweet['text']
        tweet_id = self.post_tweet(text)
        
        if tweet_id:
            # Mark as posted
            queue = self.load_tweet_queue()
            for t in queue:
                if t['text'] == text:
                    t['posted'] = True
                    t['posted_at'] = datetime.now().isoformat()
                    t['tweet_id'] = tweet_id
                    break
            
            self.save_tweet_queue(queue)
            return True
        
        return False
    
    def search_mentions(self, query: str = "FitTrack", max_results: int = 10) -> List[Dict]:
        """Search for mentions or keywords"""
        if not self.client:
            self.authenticate()
        
        try:
            # Search recent tweets
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'author_id']
            )
            
            if not tweets.data:
                return []
            
            results = []
            for tweet in tweets.data:
                results.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'author_id': tweet.author_id,
                    'created_at': str(tweet.created_at),
                    'metrics': tweet.public_metrics
                })
            
            return results
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
    
    def like_tweet(self, tweet_id: str) -> bool:
        """Like a tweet"""
        if not self.client:
            self.authenticate()
        
        try:
            # Get own user ID
            me = self.client.get_me()
            self.client.like(tweet_id=tweet_id, user_id=me.data.id)
            
            print(f"❤️  Liked tweet: {tweet_id}")
            self.log_engagement('like', tweet_id)
            return True
            
        except Exception as e:
            print(f"❌ Failed to like tweet: {e}")
            return False
    
    def reply_to_tweet(self, tweet_id: str, text: str) -> bool:
        """Reply to a tweet"""
        if not self.client:
            self.authenticate()
        
        try:
            self.client.create_tweet(text=text, in_reply_to_tweet_id=tweet_id)
            
            print(f"💬 Replied to {tweet_id}: {text[:50]}...")
            self.log_engagement('reply', tweet_id, text)
            return True
            
        except Exception as e:
            print(f"❌ Failed to reply: {e}")
            return False
    
    def log_engagement(self, action: str, tweet_id: str, content: str = ""):
        """Log engagement activity"""
        log = []
        if os.path.exists(self.engagement_log_file):
            with open(self.engagement_log_file, 'r') as f:
                log = json.load(f)
        
        log.append({
            'action': action,
            'tweet_id': tweet_id,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        
        with open(self.engagement_log_file, 'w') as f:
            json.dump(log, f, indent=2)
    
    def auto_engage(self, keywords: List[str] = None, max_actions: int = 5):
        """Automatically engage with relevant content"""
        if keywords is None:
            keywords = ['macro tracking', 'fitness app', 'nutrition tracking', 
                       'calorie counting', 'fitness goals']
        
        print(f"🤖 Auto-engaging with content about: {', '.join(keywords)}")
        
        actions_taken = 0
        
        for keyword in keywords:
            if actions_taken >= max_actions:
                break
            
            # Search for keyword
            tweets = self.search_mentions(keyword, max_results=5)
            
            for tweet in tweets:
                if actions_taken >= max_actions:
                    break
                
                # Skip if already engaged
                if self.has_engaged(tweet['id']):
                    continue
                
                # Random chance to engage (50%)
                if random.random() > 0.5:
                    continue
                
                # Like the tweet
                if self.like_tweet(tweet['id']):
                    actions_taken += 1
                
                # Small delay to avoid rate limits
                time.sleep(2)
        
        print(f"✅ Took {actions_taken} engagement actions")
    
    def has_engaged(self, tweet_id: str) -> bool:
        """Check if already engaged with tweet"""
        if not os.path.exists(self.engagement_log_file):
            return False
        
        with open(self.engagement_log_file, 'r') as f:
            log = json.load(f)
        
        return any(e['tweet_id'] == tweet_id for e in log)
    
    def get_engagement_stats(self, days: int = 7) -> Dict:
        """Get engagement statistics"""
        if not os.path.exists(self.engagement_log_file):
            return {'likes': 0, 'replies': 0, 'tweets': 0}
        
        with open(self.engagement_log_file, 'r') as f:
            log = json.load(f)
        
        # Filter by date range
        since = datetime.now() - timedelta(days=days)
        recent = [e for e in log if datetime.fromisoformat(e['timestamp']) > since]
        
        stats = {
            'likes': sum(1 for e in recent if e['action'] == 'like'),
            'replies': sum(1 for e in recent if e['action'] == 'reply'),
            'tweets': sum(1 for e in recent if e['action'] == 'tweet')
        }
        
        return stats


if __name__ == "__main__":
    bot = TwitterBot()
    
    try:
        print("🐦 Twitter Bot Initializing...")
        bot.authenticate()
        
        print("\n" + "="*50)
        print("Choose action:")
        print("1. Post from queue")
        print("2. Auto-engage with content")
        print("3. Search mentions")
        print("4. View engagement stats")
        print("="*50)
        
        choice = input("\nEnter choice (1-4): ")
        
        if choice == '1':
            bot.post_from_queue()
        elif choice == '2':
            bot.auto_engage(max_actions=5)
        elif choice == '3':
            mentions = bot.search_mentions("FitTrack", max_results=10)
            print(f"\nFound {len(mentions)} mentions:")
            for m in mentions[:5]:
                print(f"  - {m['text'][:100]}...")
        elif choice == '4':
            stats = bot.get_engagement_stats(days=7)
            print(f"\nEngagement (last 7 days):")
            print(f"  ❤️  Likes: {stats['likes']}")
            print(f"  💬 Replies: {stats['replies']}")
            print(f"  📝 Tweets: {stats['tweets']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
