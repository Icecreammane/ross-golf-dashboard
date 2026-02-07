#!/usr/bin/env python3
"""
Pattern Learning System

Learns Ross's routines and pre-builds what he needs.
Tracks requests over time and builds predictions with confidence scores.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

class Pattern:
    def __init__(self, pattern_id: str, description: str, trigger: Dict, action: str):
        self.id = pattern_id
        self.description = description
        self.trigger = trigger  # {"day": "thursday", "time": "morning", etc.}
        self.action = action
        self.occurrences = []
        self.confidence = 0.0
        self.last_triggered = None
        self.auto_execute = False
    
    def record_occurrence(self):
        """Record an occurrence of this pattern"""
        self.occurrences.append(datetime.now().isoformat())
        self.confidence = self._calculate_confidence()
        self.last_triggered = datetime.now()
    
    def _calculate_confidence(self) -> float:
        """Calculate confidence score based on occurrences"""
        if len(self.occurrences) < 2:
            return 0.2
        elif len(self.occurrences) < 3:
            return 0.5
        elif len(self.occurrences) < 5:
            return 0.7
        else:
            # Check consistency (are they actually regular?)
            return self._check_consistency()
    
    def _check_consistency(self) -> float:
        """Check if occurrences are consistent (regular pattern)"""
        if len(self.occurrences) < 3:
            return 0.5
        
        # Check if occurrences happen at similar times
        times = [datetime.fromisoformat(t) for t in self.occurrences[-5:]]
        
        # Check day-of-week consistency
        days = [t.weekday() for t in times]
        if len(set(days)) == 1:  # Same day of week
            return 0.9
        
        # Check hour consistency
        hours = [t.hour for t in times]
        hour_variance = max(hours) - min(hours)
        if hour_variance <= 2:  # Within 2 hours
            return 0.8
        
        return 0.6
    
    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "trigger": self.trigger,
            "action": self.action,
            "occurrences": self.occurrences,
            "confidence": self.confidence,
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None,
            "auto_execute": self.auto_execute
        }
    
    @staticmethod
    def from_dict(data):
        pattern = Pattern(
            pattern_id=data["id"],
            description=data["description"],
            trigger=data["trigger"],
            action=data["action"]
        )
        pattern.occurrences = data.get("occurrences", [])
        pattern.confidence = data.get("confidence", 0.0)
        if data.get("last_triggered"):
            pattern.last_triggered = datetime.fromisoformat(data["last_triggered"])
        pattern.auto_execute = data.get("auto_execute", False)
        return pattern

class PatternLearner:
    def __init__(self, patterns_file="autonomous/data/patterns.json"):
        self.patterns_file = patterns_file
        self.patterns: List[Pattern] = []
        self.request_log = []
        self.load_patterns()
    
    def load_patterns(self):
        """Load learned patterns"""
        if os.path.exists(self.patterns_file):
            with open(self.patterns_file, 'r') as f:
                data = json.load(f)
                self.patterns = [Pattern.from_dict(p) for p in data.get("patterns", [])]
                self.request_log = data.get("request_log", [])[-1000:]  # Keep last 1000
    
    def save_patterns(self):
        """Save patterns to disk"""
        os.makedirs(os.path.dirname(self.patterns_file), exist_ok=True)
        data = {
            "last_updated": datetime.now().isoformat(),
            "patterns": [p.to_dict() for p in self.patterns],
            "request_log": self.request_log[-1000:]
        }
        with open(self.patterns_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def log_request(self, request_type: str, context: Dict):
        """Log a user request for pattern analysis"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": request_type,
            "context": context,
            "day_of_week": datetime.now().weekday(),
            "hour": datetime.now().hour,
            "day_name": datetime.now().strftime("%A")
        }
        self.request_log.append(log_entry)
        
        # Analyze for patterns after logging
        self._analyze_for_patterns(request_type, log_entry)
        self.save_patterns()
    
    def _analyze_for_patterns(self, request_type: str, new_entry: Dict):
        """Analyze recent requests to detect patterns"""
        # Find similar past requests
        similar = [
            entry for entry in self.request_log[-50:]  # Last 50 requests
            if entry["type"] == request_type
        ]
        
        if len(similar) < 3:
            return  # Need at least 3 occurrences
        
        # Check for time-based patterns
        days = [entry["day_of_week"] for entry in similar]
        hours = [entry["hour"] for entry in similar]
        
        # Same day of week pattern
        day_counts = defaultdict(int)
        for day in days:
            day_counts[day] += 1
        
        most_common_day = max(day_counts, key=day_counts.get)
        if day_counts[most_common_day] >= 3:
            # Found a day-of-week pattern
            pattern_id = f"pattern_{request_type}_{most_common_day}"
            
            # Check if pattern already exists
            existing = next((p for p in self.patterns if p.id == pattern_id), None)
            
            if not existing:
                pattern = Pattern(
                    pattern_id=pattern_id,
                    description=f"{request_type} on {datetime(2024, 1, most_common_day+1).strftime('%A')}s",
                    trigger={"day_of_week": most_common_day, "type": "weekly"},
                    action=request_type
                )
                pattern.occurrences = [e["timestamp"] for e in similar if e["day_of_week"] == most_common_day]
                pattern.confidence = pattern._calculate_confidence()
                self.patterns.append(pattern)
            else:
                existing.record_occurrence()
        
        # Time of day pattern
        hour_counts = defaultdict(int)
        for hour in hours:
            # Group by 2-hour windows
            window = (hour // 2) * 2
            hour_counts[window] += 1
        
        most_common_hour = max(hour_counts, key=hour_counts.get)
        if hour_counts[most_common_hour] >= 3:
            pattern_id = f"pattern_{request_type}_hour_{most_common_hour}"
            
            existing = next((p for p in self.patterns if p.id == pattern_id), None)
            
            if not existing:
                pattern = Pattern(
                    pattern_id=pattern_id,
                    description=f"{request_type} around {most_common_hour}:00",
                    trigger={"hour_window": most_common_hour, "type": "daily"},
                    action=request_type
                )
                pattern.occurrences = [
                    e["timestamp"] for e in similar 
                    if (e["hour"] // 2) * 2 == most_common_hour
                ]
                pattern.confidence = pattern._calculate_confidence()
                self.patterns.append(pattern)
            else:
                existing.record_occurrence()
    
    def get_predictions(self) -> List[Dict]:
        """Get current predictions based on time and patterns"""
        now = datetime.now()
        predictions = []
        
        for pattern in self.patterns:
            if pattern.confidence < 0.5:
                continue  # Only high-confidence patterns
            
            # Check if trigger matches current time
            trigger = pattern.trigger
            matches = False
            
            if trigger.get("type") == "weekly":
                if now.weekday() == trigger.get("day_of_week"):
                    matches = True
            
            elif trigger.get("type") == "daily":
                hour_window = trigger.get("hour_window")
                if hour_window <= now.hour < hour_window + 2:
                    matches = True
            
            if matches:
                predictions.append({
                    "pattern_id": pattern.id,
                    "description": pattern.description,
                    "action": pattern.action,
                    "confidence": pattern.confidence,
                    "auto_execute": pattern.auto_execute
                })
        
        return predictions
    
    def suggest_pre_builds(self) -> List[Dict]:
        """Suggest things to pre-build based on patterns"""
        suggestions = []
        now = datetime.now()
        
        # Check patterns that will trigger soon (within 12 hours)
        for pattern in self.patterns:
            if pattern.confidence < 0.7:  # Only very confident patterns
                continue
            
            trigger = pattern.trigger
            
            if trigger.get("type") == "weekly":
                target_day = trigger.get("day_of_week")
                # Check if target day is tomorrow
                tomorrow = (now.weekday() + 1) % 7
                
                if target_day == tomorrow:
                    suggestions.append({
                        "pattern_id": pattern.id,
                        "action": pattern.action,
                        "description": f"Pre-build for tomorrow: {pattern.description}",
                        "confidence": pattern.confidence,
                        "reason": "Pattern triggers tomorrow"
                    })
            
            elif trigger.get("type") == "daily":
                hour_window = trigger.get("hour_window")
                hours_until = hour_window - now.hour
                
                if -2 <= hours_until <= 4:  # 2 hours before to 4 hours after
                    suggestions.append({
                        "pattern_id": pattern.id,
                        "action": pattern.action,
                        "description": f"Pre-build: {pattern.description}",
                        "confidence": pattern.confidence,
                        "reason": f"Pattern triggers in ~{hours_until} hours"
                    })
        
        return suggestions
    
    def enable_auto_execute(self, pattern_id: str):
        """Enable auto-execution for a pattern"""
        pattern = next((p for p in self.patterns if p.id == pattern_id), None)
        if pattern and pattern.confidence >= 0.8:
            pattern.auto_execute = True
            self.save_patterns()
            return True
        return False
    
    def get_stats(self) -> Dict:
        """Get pattern learning statistics"""
        total_patterns = len(self.patterns)
        high_confidence = sum(1 for p in self.patterns if p.confidence >= 0.7)
        auto_execute = sum(1 for p in self.patterns if p.auto_execute)
        
        return {
            "total_patterns": total_patterns,
            "high_confidence": high_confidence,
            "auto_execute_enabled": auto_execute,
            "request_log_size": len(self.request_log),
            "patterns_by_confidence": {
                "high (>0.7)": high_confidence,
                "medium (0.5-0.7)": sum(1 for p in self.patterns if 0.5 <= p.confidence < 0.7),
                "low (<0.5)": sum(1 for p in self.patterns if p.confidence < 0.5)
            }
        }

def main():
    """CLI interface"""
    import sys
    
    learner = PatternLearner()
    
    if len(sys.argv) < 2:
        print("Usage: pattern_learner.py [command]")
        print("Commands: log, predict, suggest, list, stats, enable")
        return
    
    command = sys.argv[1]
    
    if command == "log":
        # Example: log "nba_rankings" '{"source": "manual"}'
        if len(sys.argv) < 3:
            print("Usage: log <request_type> [context_json]")
            return
        
        request_type = sys.argv[2]
        context = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        
        learner.log_request(request_type, context)
        print(f"✅ Logged: {request_type}")
    
    elif command == "predict":
        predictions = learner.get_predictions()
        if predictions:
            print("\n🔮 Current Predictions:\n")
            for pred in predictions:
                print(f"• {pred['description']}")
                print(f"  Confidence: {pred['confidence']:.0%}")
                print(f"  Action: {pred['action']}")
                if pred['auto_execute']:
                    print(f"  ✅ Auto-execute enabled")
                print()
        else:
            print("No predictions for current time")
    
    elif command == "suggest":
        suggestions = learner.suggest_pre_builds()
        if suggestions:
            print("\n💡 Pre-Build Suggestions:\n")
            for sugg in suggestions:
                print(f"• {sugg['description']}")
                print(f"  Reason: {sugg['reason']}")
                print(f"  Confidence: {sugg['confidence']:.0%}\n")
        else:
            print("No pre-build suggestions")
    
    elif command == "list":
        if learner.patterns:
            print(f"\n📊 Learned Patterns ({len(learner.patterns)}):\n")
            for pattern in sorted(learner.patterns, key=lambda p: p.confidence, reverse=True):
                conf_icon = "🟢" if pattern.confidence >= 0.7 else "🟡" if pattern.confidence >= 0.5 else "🔴"
                auto_icon = "🤖" if pattern.auto_execute else ""
                print(f"{conf_icon} {auto_icon} {pattern.description}")
                print(f"   Confidence: {pattern.confidence:.0%} | Occurrences: {len(pattern.occurrences)}")
                print(f"   Trigger: {pattern.trigger}\n")
        else:
            print("No patterns learned yet")
    
    elif command == "stats":
        stats = learner.get_stats()
        print("\n📈 Pattern Learning Statistics:\n")
        print(f"Total patterns: {stats['total_patterns']}")
        print(f"High confidence: {stats['high_confidence']}")
        print(f"Auto-execute enabled: {stats['auto_execute_enabled']}")
        print(f"Request log size: {stats['request_log_size']}\n")
        print("Patterns by confidence:")
        for level, count in stats['patterns_by_confidence'].items():
            print(f"  {level}: {count}")
    
    elif command == "enable":
        if len(sys.argv) < 3:
            print("Usage: enable <pattern_id>")
            return
        
        pattern_id = sys.argv[2]
        if learner.enable_auto_execute(pattern_id):
            print(f"✅ Enabled auto-execute for {pattern_id}")
        else:
            print(f"❌ Cannot enable (pattern not found or confidence too low)")

if __name__ == "__main__":
    main()
