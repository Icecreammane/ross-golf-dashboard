#!/usr/bin/env python3
"""
Twitter Auto-Poster
Posts queued content to Twitter at scheduled times (2am, 6am, 12pm, 6pm CST)
"""

import json
import logging
import os
import sys
from datetime import datetime, time
from pathlib import Path
from typing import Optional

# Configuration
WORKSPACE = Path("/Users/clawdbot/clawd")
QUEUE_FILE = WORKSPACE / "data" / "social-posts-queue.json"
LOG_FILE = WORKSPACE / "logs" / "social-scheduler.log"
CREDENTIALS_FILE = WORKSPACE / "credentials" / "twitter-api.json"

# Posting schedule (CST)
POSTING_TIMES = [
    time(2, 0),   # 2am
    time(6, 0),   # 6am
    time(12, 0),  # 12pm
    time(18, 0),  # 6pm
]

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_twitter_credentials() -> Optional[dict]:
    """Load Twitter API credentials"""
    if not CREDENTIALS_FILE.exists():
        logger.error(f"Twitter credentials not found at {CREDENTIALS_FILE}")
        logger.info("📝 To set up Twitter API:")
        logger.info("   1. Go to https://developer.twitter.com/")
        logger.info("   2. Create app and get API keys")
        logger.info("   3. Save credentials to: credentials/twitter-api.json")
        logger.info("   Format: {\"api_key\": \"...\", \"api_secret\": \"...\", \"access_token\": \"...\", \"access_token_secret\": \"...\"}")
        return None
    
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            creds = json.load(f)
            required = ["api_key", "api_secret", "access_token", "access_token_secret"]
            if all(k in creds for k in required):
                return creds
            else:
                logger.error(f"Missing required credentials: {required}")
                return None
    except Exception as e:
        logger.error(f"Error loading credentials: {e}")
        return None

def post_to_twitter_api(text: str, credentials: dict) -> Optional[str]:
    """Post to Twitter using API (tweepy)"""
    try:
        import tweepy
    except ImportError:
        logger.error("tweepy not installed. Install with: pip3 install tweepy")
        return None
    
    try:
        # Create API client
        client = tweepy.Client(
            consumer_key=credentials["api_key"],
            consumer_secret=credentials["api_secret"],
            access_token=credentials["access_token"],
            access_token_secret=credentials["access_token_secret"]
        )
        
        # Post tweet
        response = client.create_tweet(text=text)
        
        if response.data:
            tweet_id = response.data['id']
            logger.info(f"✅ Posted to Twitter: {tweet_id}")
            return tweet_id
        else:
            logger.error("Twitter API returned no data")
            return None
            
    except tweepy.TweepyException as e:
        logger.error(f"Twitter API error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error posting to Twitter: {e}")
        return None

def load_queue() -> list:
    """Load post queue"""
    if QUEUE_FILE.exists():
        try:
            with open(QUEUE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading queue: {e}")
            return []
    return []

def save_queue(queue: list):
    """Save queue to file"""
    with open(QUEUE_FILE, 'w') as f:
        json.dump(queue, f, indent=2)

def get_next_unposted(queue: list) -> Optional[dict]:
    """Get next unposted item from queue"""
    for post in queue:
        if not post.get('posted', False):
            return post
    return None

def should_post_now() -> bool:
    """Check if current time matches posting schedule"""
    now = datetime.now().time()
    current_hour = now.hour
    current_minute = now.minute
    
    # Allow 15-minute window around scheduled time
    for scheduled_time in POSTING_TIMES:
        if scheduled_time.hour == current_hour:
            # Within 15 minutes of scheduled time
            if abs(current_minute - scheduled_time.minute) <= 15:
                return True
    
    return False

def post_next_in_queue(dry_run: bool = False):
    """Post next item in queue if it's time"""
    
    # Check if it's posting time
    if not should_post_now() and not dry_run:
        logger.info("⏰ Not posting time yet")
        return False
    
    # Load queue
    queue = load_queue()
    
    if not queue:
        logger.warning("📭 Queue is empty - run generate_social_posts.py first")
        return False
    
    # Get next unposted
    post = get_next_unposted(queue)
    
    if not post:
        logger.warning("📭 No unposted items in queue")
        return False
    
    logger.info(f"📤 Preparing to post: {post['id']}")
    logger.info(f"   Theme: {post['theme']}")
    logger.info(f"   Text: {post['text']}")
    
    if dry_run:
        logger.info("🔍 DRY RUN - Would post this content")
        return True
    
    # Load credentials
    credentials = load_twitter_credentials()
    
    if not credentials:
        logger.error("❌ Cannot post without Twitter credentials")
        return False
    
    # Post to Twitter
    twitter_id = post_to_twitter_api(post['text'], credentials)
    
    if twitter_id:
        # Update post status
        post['posted'] = True
        post['posted_at'] = datetime.now().isoformat()
        post['twitter_id'] = twitter_id
        post['scheduled_for'] = None
        
        save_queue(queue)
        
        logger.info(f"✅ Successfully posted {post['id']} to Twitter")
        logger.info(f"   Twitter ID: {twitter_id}")
        logger.info(f"   Remaining in queue: {len([p for p in queue if not p['posted']])}")
        return True
    else:
        logger.error(f"❌ Failed to post {post['id']}")
        return False

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv or "--test" in sys.argv
    force = "--force" in sys.argv
    
    if dry_run:
        logger.info("🔍 Running in DRY RUN mode")
    
    if force:
        logger.info("⚡ FORCE mode - ignoring schedule check")
        # Temporarily override should_post_now
        original_should_post = should_post_now
        should_post_now = lambda: True
    
    try:
        success = post_next_in_queue(dry_run=dry_run)
        
        if success:
            print("✅ Post processed successfully")
            exit(0)
        else:
            print("⚠️ No post processed (see log for details)")
            exit(0)  # Not an error - just nothing to do
            
    except Exception as e:
        logger.error(f"Fatal error in posting: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        exit(1)
