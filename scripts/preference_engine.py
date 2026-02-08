#!/usr/bin/env python3
"""
Ross Preference Engine
Learns what Ross actually likes/hates over time
Makes Jarvis smarter with every interaction
"""

import json
import os
from datetime import datetime
from pathlib import Path

WORKSPACE = Path.home() / "clawd"
PREFS_FILE = WORKSPACE / "memory" / "ross_preferences.json"

class PreferenceEngine:
    """Learn and track Ross's preferences over time"""
    
    def __init__(self):
        self.prefs_file = PREFS_FILE
        self.load_preferences()
    
    def load_preferences(self):
        """Load existing preferences"""
        if self.prefs_file.exists():
            with open(self.prefs_file) as f:
                self.data = json.load(f)
        else:
            self.data = self.initialize_preferences()
            self.save_preferences()
    
    def initialize_preferences(self):
        """Initialize preference structure"""
        return {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "categories": {
                "build_style": {
                    "likes": [
                        "Practical, tangible results",
                        "Fast builds (under 1 hour)",
                        "Competitive/gamified features",
                        "Clear metrics and progress",
                        "Revenue-focused projects"
                    ],
                    "dislikes": [
                        "Abstract/philosophical projects",
                        "Overly complex systems",
                        "Things that take days to see results",
                        "Tools he won't actually use"
                    ]
                },
                "communication": {
                    "likes": [
                        "Options presented (A/B/C format)",
                        "Quick, direct responses",
                        "Recommendations with reasoning",
                        "Actions over explanations"
                    ],
                    "dislikes": [
                        "Long explanations without action",
                        "Open-ended 'what do you think?' questions",
                        "Overthinking simple decisions"
                    ]
                },
                "demo_style": {
                    "likes": [
                        "Interactive (people can touch/use it)",
                        "Fun/entertaining first, impressive second",
                        "Works for groups (volleyball crew, parties)",
                        "Simple to explain"
                    ],
                    "dislikes": [
                        "Too technical/nerdy",
                        "Requires long setup/explanation",
                        "Shows off personal stuff to strangers"
                    ]
                },
                "goals": {
                    "primary": [
                        "$500 MRR by March 31",
                        "Escape corporate job",
                        "Move to Florida (beach volleyball life)",
                        "Build recurring income streams"
                    ],
                    "secondary": [
                        "Win fantasy championship",
                        "Hit fitness goals (200g protein, 2200 cal)",
                        "Level up volleyball skills",
                        "Build in public on social"
                    ]
                },
                "personality": {
                    "traits": [
                        "Competitive (responds to challenges)",
                        "Results-driven (show me the metrics)",
                        "Action-oriented (just ship it)",
                        "Practical > Theoretical",
                        "Values efficiency and speed"
                    ],
                    "motivators": [
                        "Visible progress",
                        "Competition (with self or others)",
                        "Money/revenue potential",
                        "Freedom/autonomy",
                        "Winning/achievement"
                    ]
                }
            },
            "learned_patterns": [],
            "decision_history": []
        }
    
    def save_preferences(self):
        """Save preferences to file"""
        self.data["last_updated"] = datetime.now().isoformat()
        self.prefs_file.parent.mkdir(exist_ok=True)
        with open(self.prefs_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def log_decision(self, context, options_presented, choice, reasoning=None):
        """Log a decision Ross made"""
        decision = {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "options": options_presented,
            "choice": choice,
            "reasoning": reasoning
        }
        
        self.data["decision_history"].append(decision)
        
        # Keep only last 100 decisions
        if len(self.data["decision_history"]) > 100:
            self.data["decision_history"] = self.data["decision_history"][-100:]
        
        self.save_preferences()
    
    def learn_pattern(self, pattern, confidence="medium"):
        """Add a learned pattern about Ross"""
        learning = {
            "timestamp": datetime.now().isoformat(),
            "pattern": pattern,
            "confidence": confidence
        }
        
        self.data["learned_patterns"].append(learning)
        
        # Keep only last 50 patterns
        if len(self.data["learned_patterns"]) > 50:
            self.data["learned_patterns"] = self.data["learned_patterns"][-50:]
        
        self.save_preferences()
        
        print(f"✅ Learned: {pattern}")
    
    def add_like(self, category, item):
        """Add something Ross likes"""
        if category in self.data["categories"]:
            if "likes" not in self.data["categories"][category]:
                self.data["categories"][category]["likes"] = []
            
            if item not in self.data["categories"][category]["likes"]:
                self.data["categories"][category]["likes"].append(item)
                self.save_preferences()
                print(f"✅ Added to likes ({category}): {item}")
    
    def add_dislike(self, category, item):
        """Add something Ross dislikes"""
        if category in self.data["categories"]:
            if "dislikes" not in self.data["categories"][category]:
                self.data["categories"][category]["dislikes"] = []
            
            if item not in self.data["categories"][category]["dislikes"]:
                self.data["categories"][category]["dislikes"].append(item)
                self.save_preferences()
                print(f"✅ Added to dislikes ({category}): {item}")
    
    def get_recommendation_filter(self):
        """Get filters for making better recommendations"""
        return {
            "must_have": [
                "Practical outcome",
                "Under 2 hours to build",
                "Clear success metrics",
                "Ross will actually use it"
            ],
            "avoid": [
                "Purely theoretical",
                "Requires multiple days",
                "Complex infrastructure",
                "Unclear value proposition"
            ],
            "bonus_points": [
                "Competitive element",
                "Revenue potential",
                "Visual progress",
                "Shareable/demo-able"
            ]
        }
    
    def should_suggest(self, idea, reasoning):
        """
        Check if an idea aligns with Ross's preferences
        Returns: (score out of 10, explanation)
        """
        score = 5  # Start neutral
        feedback = []
        
        idea_lower = idea.lower()
        
        # Check against likes
        likes = self.data["categories"]["build_style"]["likes"]
        for like in likes:
            if any(word in idea_lower for word in like.lower().split()):
                score += 1
                feedback.append(f"✅ Aligns with: {like}")
        
        # Check against dislikes
        dislikes = self.data["categories"]["build_style"]["dislikes"]
        for dislike in dislikes:
            if any(word in idea_lower for word in dislike.lower().split()):
                score -= 2
                feedback.append(f"❌ Conflicts with: {dislike}")
        
        # Check motivators
        motivators = self.data["categories"]["personality"]["motivators"]
        for motivator in motivators:
            if any(word in idea_lower for word in motivator.lower().split()):
                score += 0.5
                feedback.append(f"💪 Motivating: {motivator}")
        
        # Cap score at 10
        score = min(10, max(0, score))
        
        explanation = "\n".join(feedback) if feedback else "Neutral (no strong signals)"
        
        return score, explanation
    
    def get_summary(self):
        """Get human-readable summary of preferences"""
        return f"""
╔══════════════════════════════════════════════════════════════════════╗
║                    ROSS PREFERENCE ENGINE v1.0                       ║
╚══════════════════════════════════════════════════════════════════════╝

📊 WHAT ROSS LIKES:
{chr(10).join(f"  ✅ {item}" for item in self.data["categories"]["build_style"]["likes"])}

📊 WHAT ROSS AVOIDS:
{chr(10).join(f"  ❌ {item}" for item in self.data["categories"]["build_style"]["dislikes"])}

🎯 PRIMARY GOALS:
{chr(10).join(f"  • {goal}" for goal in self.data["categories"]["goals"]["primary"])}

💪 MOTIVATORS:
{chr(10).join(f"  🔥 {m}" for m in self.data["categories"]["personality"]["motivators"])}

📈 LEARNING STATS:
  • Patterns learned: {len(self.data["learned_patterns"])}
  • Decisions tracked: {len(self.data["decision_history"])}
  • Last updated: {self.data["last_updated"][:10]}

═══════════════════════════════════════════════════════════════════════
"""


def test_suggestions():
    """Test the preference engine with sample ideas"""
    engine = PreferenceEngine()
    
    print("\n🧪 TESTING PREFERENCE ENGINE\n")
    
    test_ideas = [
        ("Build a gamified workout tracker with streak counter", "Competitive, visual progress"),
        ("Create a philosophical journal about life's meaning", "Deep thinking exercise"),
        ("Build Stripe integration for fitness tracker", "Revenue generation"),
        ("Research quantum computing theory", "Interesting topic"),
        ("Make a dashboard showing daily win count", "Visual progress metrics")
    ]
    
    for idea, reasoning in test_ideas:
        score, explanation = engine.should_suggest(idea, reasoning)
        print(f"💡 IDEA: {idea}")
        print(f"   Score: {score}/10")
        print(f"   {explanation}")
        print()


def main():
    """Initialize preference engine"""
    engine = PreferenceEngine()
    
    print(engine.get_summary())
    
    # Log today's decision
    engine.log_decision(
        context="Saturday night build - party demo vs fun personal project",
        options_presented=[
            "Roast Bot + Ask Anything (party demos)",
            "Fantasy Football AI",
            "Volleyball analyzer",
            "Infrastructure improvements"
        ],
        choice="Party demos + then pivot to infrastructure",
        reasoning="Wanted practical party demo, then pivoted to making Jarvis smarter + personal motivation tool"
    )
    
    # Learn new patterns from tonight
    engine.learn_pattern(
        "Ross responds well to 'Ship it' moments - decisive, action-oriented",
        confidence="high"
    )
    
    engine.learn_pattern(
        "When given abstract options, Ross says 'pivot to something else entirely' - prefers concrete ideas",
        confidence="high"
    )
    
    print("\n✅ Preference Engine initialized and updated!")
    print(f"📁 Saved to: {PREFS_FILE}")
    
    # Test it
    test_suggestions()


if __name__ == "__main__":
    main()
