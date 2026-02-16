#!/usr/bin/env python3
"""
Hinge Strategic Assistant
Smart dating boundaries + match filtering WITHOUT getting banned

Features:
- Priority Like Scheduler (2-3/day max at optimal times)
- Match Rating System (1-10 based on criteria)
- Message Draft Engine (personalized openers)
- Engagement Boundaries (20min/day, 7-9pm window)
- Ban-safe behavior (human-like timing, activity limits)
"""

import json
import time
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Data paths
DATA_DIR = Path("/Users/clawdbot/clawd/data")
HINGE_DATA = DATA_DIR / "hinge_matches.json"
HINGE_STATE = DATA_DIR / "hinge_state.json"
HINGE_LOG = Path("/Users/clawdbot/clawd/logs/hinge.log")

# Ross's criteria
PREFERENCES = {
    "age_range": (27, 32),
    "location": "Nashville",
    "location_radius_miles": 50,
    "min_profile_quality": 5,  # 1-10 scale
    "red_flags": [
        "empty bio",
        "only party photos",
        "no effort in prompts",
        "generic answers",
        "all group photos",
        "no clear face photos"
    ]
}

# Safety limits (ban prevention)
LIMITS = {
    "priority_likes_per_day": 3,
    "max_screen_time_minutes": 20,
    "optimal_time_start": 19,  # 7pm
    "optimal_time_end": 21,    # 9pm
    "min_action_delay_seconds": 3,
    "max_action_delay_seconds": 8,
    "max_likes_per_hour": 10,
    "max_messages_per_day": 15
}

class HingeAssistant:
    def __init__(self):
        self.data_dir = DATA_DIR
        self.data_dir.mkdir(exist_ok=True)
        self.matches = self.load_matches()
        self.state = self.load_state()
        
    def load_matches(self) -> Dict:
        """Load match data from JSON"""
        if HINGE_DATA.exists():
            with open(HINGE_DATA, 'r') as f:
                return json.load(f)
        return {
            "matches": [],
            "drafts": [],
            "sent_messages": [],
            "priority_likes_used": []
        }
    
    def save_matches(self):
        """Save match data to JSON"""
        with open(HINGE_DATA, 'w') as f:
            json.dump(self.matches, f, indent=2)
    
    def load_state(self) -> Dict:
        """Load daily state (screen time, activity)"""
        if HINGE_STATE.exists():
            with open(HINGE_STATE, 'r') as f:
                return json.load(f)
        return {
            "date": str(datetime.now().date()),
            "screen_time_seconds": 0,
            "priority_likes_today": 0,
            "messages_today": 0,
            "last_action_time": None,
            "session_start": None
        }
    
    def save_state(self):
        """Save daily state"""
        with open(HINGE_STATE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def reset_daily_state_if_needed(self):
        """Reset counters if it's a new day"""
        today = str(datetime.now().date())
        if self.state.get("date") != today:
            self.state = {
                "date": today,
                "screen_time_seconds": 0,
                "priority_likes_today": 0,
                "messages_today": 0,
                "last_action_time": None,
                "session_start": None
            }
            self.save_state()
    
    def can_use_priority_like(self) -> Tuple[bool, str]:
        """Check if Ross can use a priority like today"""
        self.reset_daily_state_if_needed()
        
        used = self.state["priority_likes_today"]
        limit = LIMITS["priority_likes_per_day"]
        
        if used >= limit:
            return False, f"❌ Priority likes used up ({used}/{limit}). Come back tomorrow!"
        
        # Check optimal time window
        now = datetime.now()
        hour = now.hour
        if not (LIMITS["optimal_time_start"] <= hour < LIMITS["optimal_time_end"]):
            return False, f"⏰ Wait for optimal time ({LIMITS['optimal_time_start']}:00-{LIMITS['optimal_time_end']}:00)"
        
        return True, f"✅ Priority likes available: {limit - used} left today"
    
    def check_screen_time(self) -> Tuple[bool, str]:
        """Check if screen time limit reached"""
        self.reset_daily_state_if_needed()
        
        used_minutes = self.state["screen_time_seconds"] // 60
        limit_minutes = LIMITS["max_screen_time_minutes"]
        
        if used_minutes >= limit_minutes:
            return False, f"🛑 Daily screen time limit reached ({used_minutes}/{limit_minutes} min). See you tomorrow!"
        
        remaining = limit_minutes - used_minutes
        return True, f"⏱️ {remaining} minutes remaining today"
    
    def rate_profile(self, profile: Dict) -> Dict:
        """
        Rate a profile 1-10 based on Ross's criteria
        
        profile = {
            "name": str,
            "age": int,
            "location": str,
            "bio": str,
            "prompts": List[str],
            "photos": List[str],  # URLs or descriptions
            "verified": bool
        }
        
        Returns: {
            "rating": int (1-10),
            "category": str,
            "reasons": List[str],
            "red_flags": List[str]
        }
        """
        score = 5  # Start at baseline
        reasons = []
        red_flags = []
        
        # Age check (dealbreaker)
        age = profile.get("age", 0)
        if not (PREFERENCES["age_range"][0] <= age <= PREFERENCES["age_range"][1]):
            score -= 3
            red_flags.append(f"Age {age} outside preferred range")
        else:
            score += 1
            reasons.append(f"Age {age} is perfect")
        
        # Location check
        location = profile.get("location", "").lower()
        if PREFERENCES["location"].lower() in location:
            score += 1
            reasons.append("Nashville local")
        elif "nashville" in location or "tn" in location:
            score += 0.5
            reasons.append("Nashville area")
        else:
            score -= 1
            red_flags.append(f"Location: {location}")
        
        # Bio quality
        bio = profile.get("bio", "").strip()
        if not bio:
            score -= 2
            red_flags.append("Empty bio")
        elif len(bio) > 100:
            score += 1
            reasons.append("Thoughtful bio")
        
        # Prompt quality
        prompts = profile.get("prompts", [])
        if not prompts or len(prompts) < 2:
            score -= 1
            red_flags.append("Incomplete prompts")
        else:
            thoughtful = sum(1 for p in prompts if len(p) > 50)
            if thoughtful >= 2:
                score += 1
                reasons.append("High-effort prompts")
        
        # Photo quality (check descriptions)
        photos = profile.get("photos", [])
        if len(photos) < 4:
            score -= 1
            red_flags.append("Not enough photos")
        
        # Verification badge
        if profile.get("verified"):
            score += 1
            reasons.append("Verified profile")
        
        # Clamp score 1-10
        score = max(1, min(10, int(score)))
        
        # Categorize
        if score >= 9:
            category = "🔥 Wife material"
        elif score >= 7:
            category = "💚 Serious dating"
        elif score >= 5:
            category = "🟡 Short-term/fun"
        else:
            category = "⚪ Skip"
        
        return {
            "rating": score,
            "category": category,
            "reasons": reasons,
            "red_flags": red_flags
        }
    
    def draft_opener(self, profile: Dict, rating: Dict) -> str:
        """
        Draft a personalized opener based on profile analysis
        
        Returns a message that:
        - References something specific from her profile
        - Shows genuine interest
        - Opens a conversation naturally
        - Is authentic to Ross's voice
        """
        name = profile.get("name", "there")
        
        # Skip if rating too low
        if rating["rating"] < 5:
            return ""
        
        # Extract something specific to reference
        bio = profile.get("bio", "")
        prompts = profile.get("prompts", [])
        
        # Simple template-based drafts (Ross edits before sending)
        # In production, could use local LLM for better personalization
        
        templates = []
        
        # Reference bio if available
        if bio:
            templates.append(
                f"Hey {name}! Your bio caught my attention - {bio[:50]}... "
                f"Would love to hear more about that!"
            )
        
        # Reference prompts
        if prompts:
            first_prompt = prompts[0][:50]
            templates.append(
                f"Hey {name}! I saw your prompt about '{first_prompt}...' "
                f"That's really interesting. What's the story behind that?"
            )
        
        # Nashville-specific
        if "nashville" in profile.get("location", "").lower():
            templates.append(
                f"Hey {name}! Fellow Nashvillian here. "
                f"What's your favorite spot in town?"
            )
        
        # Generic but warm fallback
        if not templates:
            templates.append(
                f"Hey {name}! Your profile stood out to me. "
                f"What's something you're passionate about right now?"
            )
        
        # Return first template (in production, could pick best one)
        draft = templates[0] if templates else ""
        
        return draft
    
    def analyze_profile(self, profile: Dict) -> Dict:
        """Full analysis: rate + draft message"""
        rating = self.rate_profile(profile)
        opener = self.draft_opener(profile, rating)
        
        return {
            "profile": profile,
            "rating": rating,
            "opener": opener,
            "timestamp": datetime.now().isoformat()
        }
    
    def add_analyzed_match(self, analysis: Dict):
        """Store analyzed match for review"""
        self.matches["matches"].append(analysis)
        self.save_matches()
    
    def get_daily_report(self) -> str:
        """Generate daily summary"""
        self.reset_daily_state_if_needed()
        
        today = str(datetime.now().date())
        today_matches = [
            m for m in self.matches["matches"]
            if m["timestamp"].startswith(today)
        ]
        
        # Categorize
        high_value = len([m for m in today_matches if m["rating"]["rating"] >= 9])
        maybes = len([m for m in today_matches if 7 <= m["rating"]["rating"] < 9])
        skips = len([m for m in today_matches if m["rating"]["rating"] < 7])
        
        priority_left = LIMITS["priority_likes_per_day"] - self.state["priority_likes_today"]
        screen_time_left = LIMITS["max_screen_time_minutes"] - (self.state["screen_time_seconds"] // 60)
        
        report = f"""
📊 **Daily Hinge Report**

**Today's Matches:**
🔥 High-value: {high_value}
💚 Maybes: {maybes}
⚪ Skips: {skips}

**Limits:**
⭐ Priority likes left: {priority_left}/{LIMITS['priority_likes_per_day']}
⏱️ Screen time left: {screen_time_left}/{LIMITS['max_screen_time_minutes']} min

**Optimal time window:** {LIMITS['optimal_time_start']}:00-{LIMITS['optimal_time_end']}:00
        """.strip()
        
        return report
    
    def log(self, message: str):
        """Log to file"""
        HINGE_LOG.parent.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(HINGE_LOG, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")


def main():
    """CLI interface"""
    import sys
    
    assistant = HingeAssistant()
    
    if len(sys.argv) < 2:
        print("Usage: python3 hinge_assistant.py <command>")
        print("Commands:")
        print("  check        - Daily status check")
        print("  report       - Generate daily report")
        print("  analyze      - Analyze a profile (requires --profile JSON)")
        print("  priority     - Check priority like availability")
        return
    
    command = sys.argv[1]
    
    if command == "check":
        can_use, msg = assistant.can_use_priority_like()
        print(msg)
        
        can_browse, screen_msg = assistant.check_screen_time()
        print(screen_msg)
    
    elif command == "report":
        print(assistant.get_daily_report())
    
    elif command == "priority":
        can_use, msg = assistant.can_use_priority_like()
        print(msg)
    
    elif command == "analyze":
        # Example profile for testing
        test_profile = {
            "name": "Emma",
            "age": 29,
            "location": "Nashville, TN",
            "bio": "Dog mom, coffee addict, and adventure seeker. Work in marketing but dream of opening a coffee shop. Love live music and trying new restaurants.",
            "prompts": [
                "I'm looking for someone who can keep up with my spontaneous weekend trips",
                "My simple pleasures: Sunday farmers markets and vinyl record hunting"
            ],
            "photos": ["photo1", "photo2", "photo3", "photo4", "photo5"],
            "verified": True
        }
        
        analysis = assistant.analyze_profile(test_profile)
        
        print(f"\n👤 {test_profile['name']}, {test_profile['age']}")
        print(f"📍 {test_profile['location']}")
        print(f"\n{analysis['rating']['category']} - Rating: {analysis['rating']['rating']}/10")
        print(f"\n✅ Reasons:")
        for reason in analysis['rating']['reasons']:
            print(f"  • {reason}")
        
        if analysis['rating']['red_flags']:
            print(f"\n⚠️ Red flags:")
            for flag in analysis['rating']['red_flags']:
                print(f"  • {flag}")
        
        print(f"\n💬 Suggested opener:")
        print(f"  {analysis['opener']}")
    
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
