#!/usr/bin/env python3
"""
Auto-Log Wins
Parse messages and automatically log wins to Win Streak system
"""

import re
import json
from datetime import datetime
from pathlib import Path
import sys

# Add scripts to path
sys.path.append(str(Path.home() / "clawd" / "scripts"))

from win_streak import WinStreakAmplifier

class AutoWinLogger:
    """Automatically detect and log wins from messages"""
    
    def __init__(self):
        self.ws = WinStreakAmplifier()
        
        # Patterns for each category
        self.patterns = {
            "workout": [
                r"(chest|back|legs|shoulders|arms|workout|gym|lift)",
                r"(bench|squat|deadlift|pull.*up|push.*up)",
                r"(bicep|tricep|delt|lat|quad|hamstring)",
                r"\d+\s*(minutes?|mins?|hours?|hrs?)\s*(workout|gym|lifting)"
            ],
            "protein": [
                r"(hit|reached|got)\s*\d+g?\s*(protein|pro)",
                r"\d+g?\s*protein",
                r"protein.*target",
                r"(ate|had).*protein"
            ],
            "side_project": [
                r"(built|shipped|created|made|finished|completed)",
                r"(deployed|launched|released)",
                r"(coded|programmed|developed)",
                r"working on.*project"
            ],
            "revenue_action": [
                r"(made|earned|generated).*\$\d+",
                r"(customer|client|sale|revenue)",
                r"(launched|published).*product",
                r"(stripe|payment|transaction)"
            ]
        }
    
    def detect_category(self, message):
        """Detect which category a message belongs to"""
        message_lower = message.lower()
        
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return category
        
        return None
    
    def extract_description(self, message, category):
        """Extract a clean description from the message"""
        # Clean up common filler words
        desc = message.strip()
        
        # Remove leading "I" or "Just"
        desc = re.sub(r'^(i |just |i just )', '', desc, flags=re.IGNORECASE)
        
        # Capitalize first letter
        if desc:
            desc = desc[0].upper() + desc[1:]
        
        return desc
    
    def estimate_impact(self, message, category):
        """Estimate impact level based on message content"""
        message_lower = message.lower()
        
        # High impact indicators
        high_indicators = [
            r'(great|amazing|awesome|killer|insane|beast)',
            r'\d+\s*(hours?|hrs?)',  # Long duration
            r'(finished|completed|shipped)',
            r'pr\b',  # Personal record
            r'\$\d{3,}',  # $100+
        ]
        
        # Low impact indicators  
        low_indicators = [
            r'(quick|short|small|minor)',
            r'(tried|attempted|started)',
            r'\d{1,2}\s*(minutes?|mins?)',  # Short duration
        ]
        
        for pattern in high_indicators:
            if re.search(pattern, message_lower):
                return "high"
        
        for pattern in low_indicators:
            if re.search(pattern, message_lower):
                return "low"
        
        return "medium"
    
    def should_auto_log(self, message):
        """Determine if message should be auto-logged"""
        # Don't auto-log if it's a question
        if '?' in message:
            return False
        
        # Don't auto-log if it starts with "should" or "could"
        if re.match(r'^(should|could|would|might)', message.lower()):
            return False
        
        # Don't auto-log if it's about planning (not doing)
        planning_words = ['plan', 'planning', 'gonna', 'going to', 'will', 'tomorrow']
        if any(word in message.lower() for word in planning_words):
            return False
        
        return True
    
    def process_message(self, message, auto_log=True):
        """
        Process a message and optionally log the win
        Returns: (category, description, impact, should_log)
        """
        category = self.detect_category(message)
        
        if not category:
            return None, None, None, False
        
        if not self.should_auto_log(message):
            return category, None, None, False
        
        description = self.extract_description(message, category)
        impact = self.estimate_impact(message, category)
        
        if auto_log:
            try:
                result = self.ws.log_win(category, description, impact)
                return category, description, impact, True, result
            except Exception as e:
                print(f"Error logging win: {e}")
                return category, description, impact, False, None
        
        return category, description, impact, True, None


def test_auto_logger():
    """Test the auto-logger with sample messages"""
    logger = AutoWinLogger()
    
    test_messages = [
        "chest day 90 minutes felt great",
        "hit 200g protein today",
        "built the cool down system",
        "just finished shoulder workout",
        "made $50 on side project",
        "should I workout today?",  # Question - shouldn't log
        "gonna hit the gym tomorrow",  # Planning - shouldn't log
        "quick 20 min workout",
        "shipped party demo apps",
        "ate 180g protein"
    ]
    
    print("="*70)
    print("🧪 AUTO-LOG WINS - TEST MODE")
    print("="*70)
    print()
    
    for msg in test_messages:
        result = logger.process_message(msg, auto_log=False)
        category, desc, impact, should_log = result[:4]
        
        print(f"📝 Message: {msg}")
        
        if should_log:
            emoji = {"workout": "💪", "protein": "🥩", "side_project": "🔨", "revenue_action": "💰"}
            print(f"   ✅ WOULD LOG: {emoji.get(category, '📌')} {category}")
            print(f"   Description: {desc}")
            print(f"   Impact: {impact}")
        else:
            if category:
                print(f"   ⏭️  SKIP: Detected {category} but shouldn't auto-log")
            else:
                print(f"   ⏭️  SKIP: No win detected")
        
        print()


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_auto_logger()
        else:
            # Process a message from command line
            message = " ".join(sys.argv[1:])
            logger = AutoWinLogger()
            result = logger.process_message(message, auto_log=True)
            
            if len(result) > 4 and result[4]:
                cat_name = logger.ws.data["categories"][result[0]]["name"]
                print(f"✅ Logged win: {cat_name}")
                print(f"   +{result[4]['points_earned']} points")
                print(f"   {result[4]['current_streak']} day streak")
            elif result[3]:
                print(f"✅ Would log: {result[0]} - {result[1]}")
            else:
                print("No win detected or shouldn't auto-log")
    else:
        test_auto_logger()


if __name__ == "__main__":
    main()
