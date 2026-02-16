#!/usr/bin/env python3
"""
Personality Learning Loop - Evolve Jarvis based on Ross's reactions
Tracks humor success, tone preferences, communication style, and builds inside jokes
"""

import json
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter

WORKSPACE = Path("/Users/clawdbot/clawd")
MEMORY_DIR = WORKSPACE / "memory"
PERSONALITY_MODEL = MEMORY_DIR / "personality_model.json"
REACTION_LOG = MEMORY_DIR / "reaction_log.json"

class PersonalityEvolution:
    def __init__(self):
        self.model = self.load_model()
        self.reactions = self.load_reactions()
    
    def load_model(self):
        """Load personality model"""
        if PERSONALITY_MODEL.exists():
            with open(PERSONALITY_MODEL) as f:
                return json.load(f)
        
        return {
            "humor_profile": {
                "styles_that_work": [],  # Sarcasm, puns, references, etc.
                "styles_that_fail": [],
                "success_rate": 0.0,
                "inside_jokes": []
            },
            "tone_preferences": {
                "default": "casual_professional",
                "context_specific": {
                    "morning": "energetic",
                    "evening": "relaxed",
                    "work_context": "focused",
                    "personal_context": "casual"
                },
                "formality_scale": 3  # 1-5, where 3 is balanced
            },
            "communication_style": {
                "preferred_length": "concise",  # concise, detailed, balanced
                "emoji_usage": "moderate",  # rare, moderate, frequent
                "technical_depth": "high",  # low, medium, high
                "proactivity_level": "high"  # low, medium, high
            },
            "reaction_patterns": {
                "positive_triggers": [],  # What makes Ross happy
                "negative_triggers": [],  # What annoys Ross
                "neutral_topics": []
            },
            "learning_stats": {
                "total_interactions": 0,
                "humor_attempts": 0,
                "humor_successes": 0,
                "tone_adjustments": 0,
                "personality_version": "1.0"
            }
        }
    
    def load_reactions(self):
        """Load reaction log"""
        if REACTION_LOG.exists():
            with open(REACTION_LOG) as f:
                return json.load(f)
        return {
            "reactions": [],
            "sentiment_history": []
        }
    
    def log_interaction(self, jarvis_message, ross_response, context=None):
        """Log an interaction and analyze reaction"""
        context = context or {}
        
        # Analyze sentiment
        sentiment = self._analyze_sentiment(ross_response)
        
        # Detect humor attempt
        was_humor = self._detect_humor_attempt(jarvis_message)
        humor_success = self._detect_humor_success(ross_response) if was_humor else None
        
        # Detect tone
        jarvis_tone = self._detect_tone(jarvis_message)
        
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "jarvis_message": jarvis_message[:200],
            "ross_response": ross_response[:200],
            "sentiment": sentiment,
            "was_humor": was_humor,
            "humor_success": humor_success,
            "jarvis_tone": jarvis_tone,
            "context": context
        }
        
        self.reactions["reactions"].append(interaction)
        self.reactions["sentiment_history"].append({
            "timestamp": interaction["timestamp"],
            "sentiment": sentiment
        })
        
        # Update model
        self._update_from_interaction(interaction)
        
        # Keep last 500 interactions
        if len(self.reactions["reactions"]) > 500:
            self.reactions["reactions"] = self.reactions["reactions"][-500:]
        
        self.save_reactions()
        self.save_model()
    
    def _analyze_sentiment(self, text):
        """Analyze sentiment of Ross's response"""
        text_lower = text.lower()
        
        # Positive indicators
        positive_words = ['great', 'awesome', 'perfect', 'love', 'excellent', 'nice', 'good', 
                         'thanks', 'haha', 'lol', '😂', '🔥', '👍', '💪', '✅']
        positive_count = sum(1 for word in positive_words if word in text_lower)
        
        # Negative indicators
        negative_words = ['no', 'wrong', 'bad', 'stop', 'dont', "don't", 'annoying', 
                         'unnecessary', 'not good', 'issue']
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Neutral/Command indicators
        command_words = ['do', 'make', 'build', 'create', 'update', 'fix', 'check']
        is_command = any(word in text_lower for word in command_words)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        elif is_command:
            return "command"
        else:
            return "neutral"
    
    def _detect_humor_attempt(self, message):
        """Detect if Jarvis attempted humor"""
        indicators = [
            '😂', '😎', '🤣', '💀',
            'lol', 'lmao',
            '(but', '(though',  # Parenthetical asides often humorous
        ]
        
        message_lower = message.lower()
        return any(ind in message_lower for ind in indicators)
    
    def _detect_humor_success(self, response):
        """Detect if humor landed"""
        success_indicators = ['haha', 'lol', 'lmao', '😂', '🤣', '💀', 'funny']
        failure_indicators = ['not funny', 'stop', 'unnecessary']
        
        response_lower = response.lower()
        
        has_success = any(ind in response_lower for ind in success_indicators)
        has_failure = any(ind in response_lower for ind in failure_indicators)
        
        if has_success and not has_failure:
            return True
        elif has_failure:
            return False
        return None  # Unknown
    
    def _detect_tone(self, message):
        """Detect tone of Jarvis's message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['fuck', 'shit', 'damn']):
            return "casual_edgy"
        elif message.count('!') > 2:
            return "energetic"
        elif len(message) > 500:
            return "detailed"
        elif len(message) < 50:
            return "concise"
        else:
            return "balanced"
    
    def _update_from_interaction(self, interaction):
        """Update personality model from interaction"""
        self.model["learning_stats"]["total_interactions"] += 1
        
        # Update humor learning
        if interaction["was_humor"]:
            self.model["learning_stats"]["humor_attempts"] += 1
            
            if interaction["humor_success"] == True:
                self.model["learning_stats"]["humor_successes"] += 1
            elif interaction["humor_success"] == False:
                # Note the failed style
                tone = interaction["jarvis_tone"]
                if tone not in self.model["humor_profile"]["styles_that_fail"]:
                    self.model["humor_profile"]["styles_that_fail"].append(tone)
        
        # Calculate humor success rate
        if self.model["learning_stats"]["humor_attempts"] > 0:
            self.model["humor_profile"]["success_rate"] = (
                self.model["learning_stats"]["humor_successes"] / 
                self.model["learning_stats"]["humor_attempts"]
            )
        
        # Track sentiment patterns
        sentiment = interaction["sentiment"]
        if sentiment == "positive":
            # Extract what caused positive reaction
            trigger = interaction["jarvis_message"][:100]
            if trigger not in self.model["reaction_patterns"]["positive_triggers"]:
                self.model["reaction_patterns"]["positive_triggers"].append(trigger)
        elif sentiment == "negative":
            trigger = interaction["jarvis_message"][:100]
            if trigger not in self.model["reaction_patterns"]["negative_triggers"]:
                self.model["reaction_patterns"]["negative_triggers"].append(trigger)
    
    def get_recommended_tone(self, context=None):
        """Get recommended tone for current context"""
        context = context or {}
        
        hour = datetime.now().hour
        
        # Time-based
        if 6 <= hour < 12:
            time_tone = self.model["tone_preferences"]["context_specific"].get("morning", "energetic")
        elif 17 <= hour < 23:
            time_tone = self.model["tone_preferences"]["context_specific"].get("evening", "relaxed")
        else:
            time_tone = self.model["tone_preferences"]["default"]
        
        # Context-based override
        if context.get("work_related"):
            return self.model["tone_preferences"]["context_specific"].get("work_context", "focused")
        elif context.get("personal"):
            return self.model["tone_preferences"]["context_specific"].get("personal_context", "casual")
        
        return time_tone
    
    def should_attempt_humor(self, context=None):
        """Decide if humor is appropriate"""
        # Check success rate
        if self.model["humor_profile"]["success_rate"] < 0.3:
            return False  # Too many failures
        
        # Check context
        if context and context.get("serious", False):
            return False
        
        # Time-based (less humor at night)
        hour = datetime.now().hour
        if hour < 6 or hour > 23:
            return False
        
        # Random chance based on success rate
        import random
        return random.random() < (self.model["humor_profile"]["success_rate"] * 0.5)
    
    def get_inside_jokes(self):
        """Get list of inside jokes"""
        return self.model["humor_profile"].get("inside_jokes", [])
    
    def add_inside_joke(self, joke_reference):
        """Add an inside joke"""
        if joke_reference not in self.model["humor_profile"]["inside_jokes"]:
            self.model["humor_profile"]["inside_jokes"].append(joke_reference)
            self.save_model()
    
    def get_personality_report(self):
        """Get report on personality evolution"""
        stats = self.model["learning_stats"]
        humor = self.model["humor_profile"]
        
        report = f"""
Personality Evolution Report:
- Total interactions: {stats['total_interactions']}
- Humor attempts: {stats['humor_attempts']}
- Humor success rate: {humor['success_rate']:.0%}
- Inside jokes: {len(humor.get('inside_jokes', []))}
- Tone adjustments: {stats['tone_adjustments']}

Current Style:
- Default tone: {self.model['tone_preferences']['default']}
- Communication: {self.model['communication_style']['preferred_length']}
- Technical depth: {self.model['communication_style']['technical_depth']}
- Proactivity: {self.model['communication_style']['proactivity_level']}

What works:
{chr(10).join('- ' + x for x in humor['styles_that_work'][:3]) or '- Building data...'}

What doesn't:
{chr(10).join('- ' + x for x in humor['styles_that_fail'][:3]) or '- None yet'}
"""
        return report.strip()
    
    def get_sentiment_trend(self, days=7):
        """Get sentiment trend over recent days"""
        recent = self.reactions["sentiment_history"][-days*10:]  # Rough estimate
        
        if not recent:
            return "Insufficient data"
        
        sentiments = [s["sentiment"] for s in recent]
        counter = Counter(sentiments)
        
        trend = f"Recent sentiment: {dict(counter)}"
        return trend
    
    def save_model(self):
        """Save personality model"""
        PERSONALITY_MODEL.parent.mkdir(exist_ok=True)
        with open(PERSONALITY_MODEL, "w") as f:
            json.dump(self.model, f, indent=2)
    
    def save_reactions(self):
        """Save reaction log"""
        REACTION_LOG.parent.mkdir(exist_ok=True)
        with open(REACTION_LOG, "w") as f:
            json.dump(self.reactions, f, indent=2)


def test_personality():
    """Test personality evolution system"""
    personality = PersonalityEvolution()
    
    print("Personality Learning Loop Test:\n")
    
    # Simulate interactions
    interactions = [
        ("Built the thing you asked for 🔥", "Awesome, thanks!", {"work_related": True}),
        ("That bug was being a real asshole lol", "haha nice", {"casual": True}),
        ("Here's a detailed 500-word explanation...", "Just give me the summary", {"work_related": True}),
        ("Ship it! 🚀", "Perfect", {"work_related": True}),
        ("Made another dad joke...", "Not funny", {"casual": True}),
    ]
    
    for jarvis_msg, ross_resp, ctx in interactions:
        personality.log_interaction(jarvis_msg, ross_resp, ctx)
        print(f"Logged: {jarvis_msg[:50]}... → Sentiment: {personality._analyze_sentiment(ross_resp)}")
    
    print("\n" + personality.get_personality_report())
    print("\n" + personality.get_sentiment_trend())
    
    print("\n✅ Personality evolution system working!")


if __name__ == "__main__":
    test_personality()
