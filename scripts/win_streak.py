#!/usr/bin/env python3
"""
Win Streak Amplifier
Gamified momentum tracker that makes progress feel like leveling up
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path.home() / "clawd"
STREAK_FILE = WORKSPACE / "memory" / "win_streaks.json"

class WinStreakAmplifier:
    """Track wins, streaks, and momentum"""
    
    def __init__(self):
        self.streak_file = STREAK_FILE
        self.load_data()
    
    def load_data(self):
        """Load existing streak data"""
        if self.streak_file.exists():
            with open(self.streak_file) as f:
                self.data = json.load(f)
        else:
            self.data = self.initialize_data()
            self.save_data()
    
    def initialize_data(self):
        """Initialize streak structure"""
        return {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "categories": {
                "workout": {
                    "name": "Workout Warrior",
                    "emoji": "💪",
                    "current_streak": 0,
                    "longest_streak": 0,
                    "total_wins": 0,
                    "last_win_date": None
                },
                "protein": {
                    "name": "Protein Pro",
                    "emoji": "🥩",
                    "current_streak": 0,
                    "longest_streak": 0,
                    "total_wins": 0,
                    "last_win_date": None
                },
                "side_project": {
                    "name": "Builder Mode",
                    "emoji": "🔨",
                    "current_streak": 0,
                    "longest_streak": 0,
                    "total_wins": 0,
                    "last_win_date": None
                },
                "revenue_action": {
                    "name": "Money Moves",
                    "emoji": "💰",
                    "current_streak": 0,
                    "longest_streak": 0,
                    "total_wins": 0,
                    "last_win_date": None
                }
            },
            "daily_wins": [],
            "achievements": [],
            "multiplier": 1.0,
            "level": 1,
            "total_points": 0
        }
    
    def save_data(self):
        """Save streak data"""
        self.data["last_updated"] = datetime.now().isoformat()
        self.streak_file.parent.mkdir(exist_ok=True)
        with open(self.streak_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def log_win(self, category, description, impact="medium"):
        """Log a win in a category"""
        today = datetime.now().date().isoformat()
        
        if category not in self.data["categories"]:
            print(f"❌ Unknown category: {category}")
            return
        
        cat_data = self.data["categories"][category]
        
        # Update streak
        last_win = cat_data["last_win_date"]
        if last_win:
            last_date = datetime.fromisoformat(last_win).date()
            days_ago = (datetime.now().date() - last_date).days
            
            if days_ago == 0:
                # Already logged today
                print(f"⚠️  Already logged {category} today!")
                return
            elif days_ago == 1:
                # Consecutive day
                cat_data["current_streak"] += 1
            else:
                # Streak broken
                cat_data["current_streak"] = 1
        else:
            # First win
            cat_data["current_streak"] = 1
        
        # Update stats
        cat_data["last_win_date"] = datetime.now().isoformat()
        cat_data["total_wins"] += 1
        
        # Update longest streak
        if cat_data["current_streak"] > cat_data["longest_streak"]:
            cat_data["longest_streak"] = cat_data["current_streak"]
        
        # Log to daily wins
        win_entry = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "description": description,
            "impact": impact,
            "streak_at_time": cat_data["current_streak"]
        }
        self.data["daily_wins"].append(win_entry)
        
        # Calculate points
        base_points = {"low": 1, "medium": 3, "high": 5}[impact]
        streak_bonus = min(cat_data["current_streak"] * 0.5, 10)  # Cap at +10
        points = int((base_points + streak_bonus) * self.data["multiplier"])
        
        self.data["total_points"] += points
        
        # Check for level up
        self.check_level_up()
        
        # Check for achievements
        self.check_achievements(category, cat_data["current_streak"])
        
        # Update multiplier
        self.update_multiplier()
        
        self.save_data()
        
        # Return feedback
        return {
            "points_earned": points,
            "current_streak": cat_data["current_streak"],
            "multiplier": self.data["multiplier"],
            "level": self.data["level"]
        }
    
    def update_multiplier(self):
        """Calculate combo multiplier based on active streaks"""
        active_streaks = sum(
            1 for cat in self.data["categories"].values()
            if cat["current_streak"] > 0
        )
        
        # Multiplier: 1.0 + (0.25 per active streak)
        self.data["multiplier"] = 1.0 + (active_streaks * 0.25)
    
    def check_level_up(self):
        """Check if player leveled up"""
        points = self.data["total_points"]
        
        # Level formula: every 100 points
        new_level = (points // 100) + 1
        
        if new_level > self.data["level"]:
            old_level = self.data["level"]
            self.data["level"] = new_level
            
            achievement = {
                "timestamp": datetime.now().isoformat(),
                "type": "level_up",
                "title": f"Level {new_level} Reached!",
                "description": f"Leveled up from {old_level} to {new_level}"
            }
            self.data["achievements"].append(achievement)
            
            return True
        
        return False
    
    def check_achievements(self, category, streak):
        """Check for streak achievements"""
        achievements_to_check = [
            (3, "🔥 On Fire", "3-day streak"),
            (7, "⚡ Week Warrior", "7-day streak"),
            (14, "💎 Two Week Terror", "14-day streak"),
            (30, "🏆 Month Master", "30-day streak"),
            (100, "👑 Century Legend", "100-day streak")
        ]
        
        cat_name = self.data["categories"][category]["name"]
        
        for milestone, title, desc in achievements_to_check:
            if streak == milestone:
                achievement = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "streak_milestone",
                    "title": f"{title} - {cat_name}",
                    "description": f"{desc} in {cat_name}!",
                    "category": category,
                    "streak": streak
                }
                self.data["achievements"].append(achievement)
                break
    
    def get_dashboard_data(self):
        """Get data for dashboard display"""
        today = datetime.now().date().isoformat()
        
        # Get today's wins
        todays_wins = [
            w for w in self.data["daily_wins"]
            if datetime.fromisoformat(w["timestamp"]).date().isoformat() == today
        ]
        
        # Active streaks
        active_streaks = {
            name: cat for name, cat in self.data["categories"].items()
            if cat["current_streak"] > 0
        }
        
        # Recent achievements (last 5)
        recent_achievements = self.data["achievements"][-5:] if self.data["achievements"] else []
        
        return {
            "level": self.data["level"],
            "total_points": self.data["total_points"],
            "multiplier": self.data["multiplier"],
            "categories": self.data["categories"],
            "todays_wins": todays_wins,
            "active_streaks": active_streaks,
            "recent_achievements": recent_achievements
        }
    
    def get_status_message(self):
        """Get a motivational status message"""
        active_count = sum(
            1 for cat in self.data["categories"].values()
            if cat["current_streak"] > 0
        )
        
        if active_count == 4:
            return "🔥 BEAST MODE ACTIVATED! All streaks active!"
        elif active_count >= 3:
            return "💪 Crushing it! Keep the momentum!"
        elif active_count >= 2:
            return "⚡ Building momentum! Don't break the chain!"
        elif active_count == 1:
            return "🎯 One streak going - time to stack more!"
        else:
            return "🚀 Let's start a streak! Log your first win!"
    
    def generate_report(self):
        """Generate human-readable report"""
        data = self.get_dashboard_data()
        
        report = []
        report.append("╔══════════════════════════════════════════════════════════════════════╗")
        report.append("║                    🔥 WIN STREAK AMPLIFIER 🔥                        ║")
        report.append("╚══════════════════════════════════════════════════════════════════════╝")
        report.append("")
        report.append(f"📊 LEVEL: {data['level']}")
        report.append(f"⭐ TOTAL POINTS: {data['total_points']}")
        report.append(f"🎯 COMBO MULTIPLIER: {data['multiplier']:.2f}x")
        report.append(f"📈 STATUS: {self.get_status_message()}")
        report.append("")
        report.append("═══════════════════════════════════════════════════════════════════════")
        report.append("📅 ACTIVE STREAKS")
        report.append("═══════════════════════════════════════════════════════════════════════")
        
        for name, cat in data["categories"].items():
            emoji = cat["emoji"]
            streak = cat["current_streak"]
            longest = cat["longest_streak"]
            total = cat["total_wins"]
            
            status = "🔥" if streak > 0 else "💤"
            
            report.append(f"{status} {emoji} {cat['name']}")
            report.append(f"   Current: {streak} days | Record: {longest} days | Total: {total} wins")
        
        if data["recent_achievements"]:
            report.append("")
            report.append("═══════════════════════════════════════════════════════════════════════")
            report.append("🏆 RECENT ACHIEVEMENTS")
            report.append("═══════════════════════════════════════════════════════════════════════")
            
            for achievement in data["recent_achievements"]:
                timestamp = datetime.fromisoformat(achievement["timestamp"]).strftime("%m/%d %I:%M%p")
                report.append(f"[{timestamp}] {achievement['title']}")
                report.append(f"   {achievement['description']}")
        
        if data["todays_wins"]:
            report.append("")
            report.append("═══════════════════════════════════════════════════════════════════════")
            report.append("✅ TODAY'S WINS")
            report.append("═══════════════════════════════════════════════════════════════════════")
            
            for win in data["todays_wins"]:
                cat_name = self.data["categories"][win["category"]]["name"]
                timestamp = datetime.fromisoformat(win["timestamp"]).strftime("%I:%M%p")
                report.append(f"[{timestamp}] {cat_name}: {win['description']}")
        
        report.append("")
        report.append("═══════════════════════════════════════════════════════════════════════")
        
        return "\n".join(report)


def demo():
    """Demo the win streak system"""
    ws = WinStreakAmplifier()
    
    print(ws.generate_report())
    print()
    
    # Log some wins
    print("🎯 Logging sample wins...\n")
    
    wins_to_log = [
        ("workout", "Chest day - 90 minutes", "high"),
        ("protein", "Hit 200g protein target", "medium"),
        ("side_project", "Built party demo apps", "high"),
    ]
    
    for category, description, impact in wins_to_log:
        result = ws.log_win(category, description, impact)
        if result:
            cat_name = ws.data["categories"][category]["name"]
            emoji = ws.data["categories"][category]["emoji"]
            print(f"{emoji} {cat_name}: {description}")
            print(f"   +{result['points_earned']} points | {result['current_streak']} day streak | {result['multiplier']:.2f}x multiplier")
            print()
    
    print("\n" + "="*70)
    print(ws.generate_report())


def main():
    """Initialize win streak system"""
    ws = WinStreakAmplifier()
    
    print("✅ Win Streak Amplifier initialized!")
    print(f"📁 Data file: {STREAK_FILE}")
    print()
    
    demo()


if __name__ == "__main__":
    main()
