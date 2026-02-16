#!/usr/bin/env python3
"""
Context Telepathy Engine - Predictive Intelligence for Jarvis
Learns Ross's behavior patterns and anticipates needs before being asked
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import re

WORKSPACE = Path("/Users/clawdbot/clawd")
MEMORY_DIR = WORKSPACE / "memory"
PATTERNS_FILE = MEMORY_DIR / "behavior_patterns.json"
INTERACTION_LOG = MEMORY_DIR / "interaction_patterns.json"

class ContextTelepathy:
    def __init__(self):
        self.patterns = self.load_patterns()
        self.interaction_log = self.load_interactions()
    
    def load_patterns(self):
        """Load existing behavior patterns"""
        if PATTERNS_FILE.exists():
            with open(PATTERNS_FILE) as f:
                return json.load(f)
        return {
            "temporal_patterns": [],  # Time-based behaviors
            "sequential_patterns": [],  # "After X, usually Y"
            "contextual_triggers": {},  # Context → likely next action
            "rhythm_profile": {},  # Morning person, work hours, etc.
            "topic_clusters": {},  # Related topics that come up together
            "prediction_accuracy": {}  # Track how good predictions are
        }
    
    def load_interactions(self):
        """Load interaction history"""
        if INTERACTION_LOG.exists():
            with open(INTERACTION_LOG) as f:
                return json.load(f)
        return {
            "interactions": [],
            "topics": defaultdict(list),
            "last_updated": datetime.now().isoformat()
        }
    
    def log_interaction(self, interaction_type, topic, context=None):
        """Log an interaction for pattern learning"""
        timestamp = datetime.now().isoformat()
        hour = datetime.now().hour
        day_of_week = datetime.now().strftime("%A")
        
        interaction = {
            "timestamp": timestamp,
            "hour": hour,
            "day_of_week": day_of_week,
            "type": interaction_type,
            "topic": topic,
            "context": context or {}
        }
        
        self.interaction_log["interactions"].append(interaction)
        self.interaction_log["topics"][topic].append(timestamp)
        self.interaction_log["last_updated"] = timestamp
        
        # Keep last 1000 interactions
        if len(self.interaction_log["interactions"]) > 1000:
            self.interaction_log["interactions"] = self.interaction_log["interactions"][-1000:]
        
        self.save_interactions()
        
        # Update patterns after every 10 interactions
        if len(self.interaction_log["interactions"]) % 10 == 0:
            self.update_patterns()
    
    def update_patterns(self):
        """Analyze interactions and extract patterns"""
        interactions = self.interaction_log["interactions"]
        
        # 1. TEMPORAL PATTERNS (time-based)
        temporal = defaultdict(lambda: defaultdict(int))
        for interaction in interactions[-100:]:  # Last 100 interactions
            hour = interaction["hour"]
            day = interaction["day_of_week"]
            topic = interaction["topic"]
            temporal[f"{day}_{hour}"][topic] += 1
        
        # Find strong temporal patterns (>3 occurrences)
        strong_temporal = []
        for time_key, topics in temporal.items():
            for topic, count in topics.items():
                if count >= 3:
                    day, hour = time_key.split("_")
                    strong_temporal.append({
                        "day_of_week": day,
                        "hour": int(hour),
                        "topic": topic,
                        "frequency": count,
                        "confidence": min(count / 10.0, 1.0)
                    })
        
        self.patterns["temporal_patterns"] = sorted(
            strong_temporal, 
            key=lambda x: x["confidence"], 
            reverse=True
        )
        
        # 2. SEQUENTIAL PATTERNS ("After X, usually Y")
        sequential = defaultdict(lambda: defaultdict(int))
        for i in range(len(interactions) - 1):
            current = interactions[i]["topic"]
            next_topic = interactions[i + 1]["topic"]
            time_diff = (datetime.fromisoformat(interactions[i + 1]["timestamp"]) - 
                        datetime.fromisoformat(interactions[i]["timestamp"])).total_seconds()
            
            # Only if next interaction within 30 minutes
            if time_diff < 1800:
                sequential[current][next_topic] += 1
        
        # Find strong sequential patterns
        strong_sequential = []
        for trigger, followups in sequential.items():
            for next_topic, count in followups.items():
                if count >= 3:
                    strong_sequential.append({
                        "trigger": trigger,
                        "next_topic": next_topic,
                        "frequency": count,
                        "confidence": min(count / 10.0, 1.0)
                    })
        
        self.patterns["sequential_patterns"] = sorted(
            strong_sequential,
            key=lambda x: x["confidence"],
            reverse=True
        )
        
        # 3. RHYTHM PROFILE (when Ross is most active)
        hour_activity = defaultdict(int)
        for interaction in interactions:
            hour_activity[interaction["hour"]] += 1
        
        # Determine rhythm
        total = sum(hour_activity.values())
        if total > 0:
            morning = sum(hour_activity[h] for h in range(6, 12)) / total
            afternoon = sum(hour_activity[h] for h in range(12, 17)) / total
            evening = sum(hour_activity[h] for h in range(17, 23)) / total
            night = sum(hour_activity[h] for h in [23, 0, 1, 2, 3, 4, 5]) / total
            
            self.patterns["rhythm_profile"] = {
                "most_active": max([
                    ("morning", morning),
                    ("afternoon", afternoon),
                    ("evening", evening),
                    ("night", night)
                ], key=lambda x: x[1])[0],
                "morning_activity": morning,
                "afternoon_activity": afternoon,
                "evening_activity": evening,
                "night_activity": night,
                "peak_hours": sorted(hour_activity.items(), key=lambda x: x[1], reverse=True)[:3]
            }
        
        self.save_patterns()
    
    def predict_next_need(self, current_context=None):
        """Predict what Ross might need next"""
        now = datetime.now()
        hour = now.hour
        day = now.strftime("%A")
        
        predictions = []
        
        # Check temporal patterns
        for pattern in self.patterns.get("temporal_patterns", []):
            if pattern["day_of_week"] == day and abs(pattern["hour"] - hour) <= 1:
                predictions.append({
                    "type": "temporal",
                    "topic": pattern["topic"],
                    "reason": f"Usually checks {pattern['topic']} on {day} around {pattern['hour']}:00",
                    "confidence": pattern["confidence"] * 0.9  # Slightly lower for time proximity
                })
        
        # Check sequential patterns (if we have context)
        if current_context:
            for pattern in self.patterns.get("sequential_patterns", []):
                if current_context.get("last_topic") == pattern["trigger"]:
                    predictions.append({
                        "type": "sequential",
                        "topic": pattern["next_topic"],
                        "reason": f"After {pattern['trigger']}, usually asks about {pattern['next_topic']}",
                        "confidence": pattern["confidence"]
                    })
        
        # Sort by confidence
        predictions = sorted(predictions, key=lambda x: x["confidence"], reverse=True)
        
        return predictions[:5]  # Top 5 predictions
    
    def get_preload_suggestions(self):
        """Get list of data to pre-load based on patterns"""
        predictions = self.predict_next_need()
        
        suggestions = []
        for pred in predictions:
            if pred["confidence"] > 0.5:
                suggestions.append({
                    "action": f"preload_{pred['topic']}",
                    "topic": pred["topic"],
                    "confidence": pred["confidence"],
                    "reason": pred["reason"]
                })
        
        return suggestions
    
    def save_patterns(self):
        """Save patterns to disk"""
        PATTERNS_FILE.parent.mkdir(exist_ok=True)
        with open(PATTERNS_FILE, "w") as f:
            json.dump(self.patterns, f, indent=2)
    
    def save_interactions(self):
        """Save interaction log"""
        INTERACTION_LOG.parent.mkdir(exist_ok=True)
        with open(INTERACTION_LOG, "w") as f:
            json.dump(self.interaction_log, f, indent=2)
    
    def get_rhythm_insights(self):
        """Get insights about Ross's work rhythm"""
        rhythm = self.patterns.get("rhythm_profile", {})
        if not rhythm:
            return "Not enough data yet to determine rhythm patterns"
        
        insights = []
        insights.append(f"Most active: {rhythm.get('most_active', 'unknown').title()}")
        
        if rhythm.get("peak_hours"):
            peak = rhythm["peak_hours"][0]
            insights.append(f"Peak activity: {peak[0]}:00 ({peak[1]} interactions)")
        
        # Determine if morning or evening person
        if rhythm.get("morning_activity", 0) > rhythm.get("evening_activity", 0):
            insights.append("🌅 Morning person - more active before noon")
        else:
            insights.append("🌙 Evening person - more active after 5pm")
        
        return "\n".join(insights)


def test_telepathy():
    """Test the telepathy engine"""
    engine = ContextTelepathy()
    
    # Simulate some interactions
    print("Logging sample interactions...")
    engine.log_interaction("query", "workout", {"details": "evening check"})
    engine.log_interaction("query", "fantasy", {"details": "Tuesday evening"})
    engine.log_interaction("query", "builds", {"details": "after fantasy check"})
    
    print("\nCurrent patterns:")
    print(json.dumps(engine.patterns, indent=2))
    
    print("\nPredictions for now:")
    predictions = engine.predict_next_need()
    for pred in predictions:
        print(f"- {pred['topic']} ({pred['confidence']:.0%}): {pred['reason']}")
    
    print("\nPreload suggestions:")
    suggestions = engine.get_preload_suggestions()
    for sug in suggestions:
        print(f"- {sug['action']} ({sug['confidence']:.0%})")
    
    print("\nRhythm insights:")
    print(engine.get_rhythm_insights())


if __name__ == "__main__":
    test_telepathy()
