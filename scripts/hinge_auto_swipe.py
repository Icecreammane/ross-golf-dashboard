#!/usr/bin/env python3
"""
Hinge Auto-Swiper
Main automation that analyzes profiles and auto-swipes based on preferences
"""

import json
import asyncio
import sys
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from hinge_browser import HingeBrowser
from hinge_profile_analyzer import HingeProfileAnalyzer

WORKSPACE = Path("/Users/clawdbot/clawd")
PREFS_FILE = WORKSPACE / "data" / "hinge_preferences.json"
ACTIVITY_FILE = WORKSPACE / "data" / "hinge_activity.json"
MATCHES_FILE = WORKSPACE / "data" / "hinge_matches.json"


class HingeAutoSwiper:
    def __init__(self):
        self.browser = HingeBrowser()
        self.analyzer = HingeProfileAnalyzer()
        self.prefs = self.load_preferences()
        self.activity = self.load_activity()
        self.matches = self.load_matches()
        
    def load_preferences(self) -> Dict:
        """Load preferences"""
        with open(PREFS_FILE) as f:
            return json.load(f)
    
    def load_activity(self) -> Dict:
        """Load activity log"""
        with open(ACTIVITY_FILE) as f:
            return json.load(f)
    
    def load_matches(self) -> Dict:
        """Load matches"""
        with open(MATCHES_FILE) as f:
            return json.load(f)
    
    def save_activity(self):
        """Save activity log"""
        with open(ACTIVITY_FILE, 'w') as f:
            json.dump(self.activity, f, indent=2)
    
    def save_matches(self):
        """Save matches"""
        with open(MATCHES_FILE, 'w') as f:
            json.dump(self.matches, f, indent=2)
    
    def save_preferences(self):
        """Save preferences"""
        with open(PREFS_FILE, 'w') as f:
            json.dump(self.prefs, f, indent=2)
    
    def check_daily_limit(self) -> bool:
        """Check if we've hit today's like limit"""
        today = date.today().isoformat()
        
        # Reset counter if new day
        if self.prefs['session'].get('last_run_date') != today:
            self.prefs['session']['likes_today'] = 0
            self.prefs['session']['last_run_date'] = today
            self.save_preferences()
        
        likes_today = self.prefs['session']['likes_today']
        daily_limit = self.prefs['automation']['daily_limit']
        
        return likes_today < daily_limit
    
    def increment_likes_counter(self):
        """Increment today's like counter"""
        self.prefs['session']['likes_today'] = self.prefs['session'].get('likes_today', 0) + 1
        self.save_preferences()
    
    async def run_swipe_session(self, max_profiles: int = 20):
        """
        Run a swipe session
        
        Args:
            max_profiles: Maximum profiles to review in this session
        """
        print("=" * 70)
        print("🤖 HINGE AUTO-SWIPER")
        print("=" * 70)
        
        # Check daily limit
        if not self.check_daily_limit():
            print("⏸️  Daily like limit reached. Stopping.")
            return
        
        # Start browser
        await self.browser.setup_browser()
        
        # Login
        login_success = await self.browser.login()
        if not login_success:
            print("❌ Login failed. Exiting.")
            await self.browser.close()
            return
        
        # Session tracking
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'profiles_seen': 0,
            'profiles_liked': 0,
            'profiles_skipped': 0,
            'matches_found': 0,
            'profiles': []
        }
        
        print(f"\n📊 Session started: {session_data['timestamp']}")
        print(f"💰 Likes remaining today: {self.prefs['automation']['daily_limit'] - self.prefs['session']['likes_today']}")
        print("=" * 70)
        
        # Swipe loop
        for i in range(max_profiles):
            # Check limit
            if not self.check_daily_limit():
                print("\n⏸️  Daily like limit reached during session. Stopping.")
                break
            
            print(f"\n[{i+1}/{max_profiles}] Analyzing profile...")
            
            # Extract profile
            profile = await self.browser.extract_profile_data()
            if not profile:
                print("⚠️  No profile found. End of stack?")
                break
            
            session_data['profiles_seen'] += 1
            
            # Analyze profile
            analysis = self.analyzer.analyze_profile(profile)
            
            # Add analysis to profile
            profile['analysis'] = analysis
            session_data['profiles'].append(profile)
            
            # Display results
            print(f"\n👤 {profile.get('name', 'Unknown')}, {profile.get('age', '?')}")
            print(f"📍 {profile.get('distance', '?')} miles")
            print(f"📏 {profile.get('height', 'Unknown height')}")
            print(f"⭐ Score: {analysis['score']}/10")
            print(f"🎯 Decision: {analysis['decision']}")
            print(f"💭 {analysis['reasoning']}")
            
            if analysis['green_flags']:
                print(f"✨ Green flags: {', '.join(analysis['green_flags'])}")
            if analysis['red_flags']:
                print(f"🚩 Red flags: {', '.join(analysis['red_flags'])}")
            
            # Execute decision
            if analysis['decision'] == 'LIKE' and self.prefs['automation']['auto_like']:
                print("💚 Sending like...")
                success = await self.browser.like_profile()
                if success:
                    session_data['profiles_liked'] += 1
                    self.increment_likes_counter()
                    self.activity['total_likes_sent'] += 1
                    
                    # Check for match
                    await asyncio.sleep(2)
                    new_matches = await self.browser.check_for_matches()
                    if new_matches:
                        session_data['matches_found'] += len(new_matches)
                        for match in new_matches:
                            self.handle_new_match(match)
                    
            else:
                print("❌ Skipping...")
                success = await self.browser.skip_profile()
                if success:
                    session_data['profiles_skipped'] += 1
            
            # Human-like delay
            await self.browser.random_delay()
            
            self.activity['total_profiles_seen'] += 1
        
        # Save session data
        self.activity['sessions'].append(session_data)
        
        # Update daily stats
        today = date.today().isoformat()
        if today not in self.activity['daily_stats']:
            self.activity['daily_stats'][today] = {
                'profiles_seen': 0,
                'profiles_liked': 0,
                'profiles_skipped': 0,
                'matches': 0
            }
        
        self.activity['daily_stats'][today]['profiles_seen'] += session_data['profiles_seen']
        self.activity['daily_stats'][today]['profiles_liked'] += session_data['profiles_liked']
        self.activity['daily_stats'][today]['profiles_skipped'] += session_data['profiles_skipped']
        self.activity['daily_stats'][today]['matches'] += session_data['matches_found']
        
        self.save_activity()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 SESSION SUMMARY")
        print("=" * 70)
        print(f"Profiles reviewed: {session_data['profiles_seen']}")
        print(f"Liked: {session_data['profiles_liked']} 💚")
        print(f"Skipped: {session_data['profiles_skipped']} ❌")
        print(f"Matches: {session_data['matches_found']} 🔥")
        print(f"Likes remaining today: {self.prefs['automation']['daily_limit'] - self.prefs['session']['likes_today']}")
        print("=" * 70)
        
        # Close browser
        await self.browser.close()
    
    def handle_new_match(self, match_data: Dict):
        """Handle a new match - save and notify"""
        print("\n" + "🔥" * 35)
        print(f"🔥 NEW MATCH: {match_data.get('name', 'Unknown')}, {match_data.get('age', '?')}")
        print("🔥" * 35)
        
        # Save match
        match_data['matched_at'] = datetime.now().isoformat()
        self.matches['matches'].append(match_data)
        self.activity['total_matches'] += 1
        self.save_matches()
        
        # Send Telegram notification
        if self.prefs['automation']['notify_on_match']:
            self.send_match_notification(match_data)
    
    def send_match_notification(self, match_data: Dict):
        """Send Telegram notification for new match"""
        name = match_data.get('name', 'Unknown')
        age = match_data.get('age', '?')
        bio = match_data.get('bio', 'No bio')
        
        # Truncate bio to 2 lines
        bio_lines = bio.split('\n')[:2]
        bio_summary = '\n'.join(bio_lines)
        if len(bio_lines) > 2:
            bio_summary += '...'
        
        message = f"""🔥 **New Hinge Match!**

👤 **{name}, {age}**

{bio_summary}

🔗 Open Hinge to start chatting!
"""
        
        # Write notification request for main agent to pick up
        notification_file = WORKSPACE / "data" / "pending_notification.txt"
        with open(notification_file, 'w') as f:
            f.write(f"HINGE_MATCH:{message}")
        
        print(f"📱 Notification queued: {notification_file}")


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hinge Auto-Swiper')
    parser.add_argument('--max-profiles', type=int, default=20,
                        help='Maximum profiles to review (default: 20)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Run without actually swiping')
    
    args = parser.parse_args()
    
    swiper = HingeAutoSwiper()
    
    if args.dry_run:
        print("🧪 DRY RUN MODE - No swipes will be sent")
        swiper.prefs['automation']['auto_like'] = False
    
    await swiper.run_swipe_session(max_profiles=args.max_profiles)


if __name__ == "__main__":
    asyncio.run(main())
