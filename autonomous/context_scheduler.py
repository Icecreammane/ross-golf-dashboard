#!/usr/bin/env python3
"""
Context-Aware Work Scheduler

Selects appropriate work based on Ross's location/activity.
Auto-detects context and schedules matching tasks.
"""

import json
import os
from datetime import datetime, time as dt_time
from typing import Dict, List, Optional
from enum import Enum

class Context(Enum):
    GYM = "gym"
    WORK = "work"
    SLEEPING = "sleeping"
    AVAILABLE = "available"
    UNKNOWN = "unknown"

class ContextScheduler:
    def __init__(self, context_file="autonomous/data/context_state.json"):
        self.context_file = context_file
        self.current_context = Context.UNKNOWN
        self.context_history = []
        self.load_state()
    
    def load_state(self):
        """Load context state"""
        if os.path.exists(self.context_file):
            with open(self.context_file, 'r') as f:
                data = json.load(f)
                self.context_history = data.get("history", [])
                if data.get("current_context"):
                    self.current_context = Context(data["current_context"])
    
    def save_state(self):
        """Save context state"""
        os.makedirs(os.path.dirname(self.context_file), exist_ok=True)
        data = {
            "last_updated": datetime.now().isoformat(),
            "current_context": self.current_context.value,
            "history": self.context_history[-100:]  # Keep last 100 entries
        }
        with open(self.context_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def detect_context(self) -> Context:
        """Auto-detect current context based on time patterns"""
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        day_of_week = now.weekday()  # 0=Monday, 6=Sunday
        
        # Sleeping (11pm - 7am)
        if hour >= 23 or hour < 7:
            return Context.SLEEPING
        
        # Weekday patterns
        if day_of_week < 5:  # Monday-Friday
            # Morning gym (6am-7:30am)
            if hour == 6 or (hour == 7 and minute < 30):
                return Context.GYM
            
            # Work hours (9am-5pm)
            if 9 <= hour < 17:
                return Context.WORK
            
            # Evening gym (5pm-6:30pm)
            if hour == 17 or (hour == 18 and minute < 30):
                return Context.GYM
            
            # Available (7pm-11pm)
            if 19 <= hour < 23:
                return Context.AVAILABLE
        
        # Weekend - mostly available
        else:
            if 8 <= hour < 23:
                return Context.AVAILABLE
        
        return Context.UNKNOWN
    
    def set_context(self, context: Context, explicit: bool = False):
        """Set context (auto-detected or explicitly set)"""
        if context != self.current_context:
            # Log transition
            self.context_history.append({
                "timestamp": datetime.now().isoformat(),
                "from": self.current_context.value,
                "to": context.value,
                "explicit": explicit
            })
            
            self.current_context = context
            self.save_state()
    
    def get_appropriate_work_categories(self, context: Optional[Context] = None) -> List[str]:
        """Get work categories appropriate for current context"""
        if context is None:
            context = self.current_context
        
        work_map = {
            Context.GYM: [
                "Fitness optimization",
                "Workout data analysis",
                "Nutrition tools",
                "Health tracking"
            ],
            Context.WORK: [
                "Productivity tools",
                "Revenue research",
                "Business automation",
                "System testing",
                "Market analysis"
            ],
            Context.SLEEPING: [
                "Long builds",
                "Data processing",
                "System optimization",
                "Performance tuning",
                "Machine learning",
                "Research",
                "Infrastructure"
            ],
            Context.AVAILABLE: [
                "Quick iteration",
                "Bug fixes",
                "Documentation",
                "Code review"
            ],
            Context.UNKNOWN: [
                "Low-risk tasks",
                "Documentation",
                "Testing"
            ]
        }
        
        return work_map.get(context, [])
    
    def get_work_intensity(self, context: Optional[Context] = None) -> str:
        """Get appropriate work intensity level"""
        if context is None:
            context = self.current_context
        
        intensity_map = {
            Context.GYM: "moderate",  # Can work, Ross not fully available
            Context.WORK: "high",  # Full autonomous work
            Context.SLEEPING: "maximum",  # Full autonomous work, longest tasks
            Context.AVAILABLE: "minimal",  # Stay responsive, light background only
            Context.UNKNOWN: "low"
        }
        
        return intensity_map.get(context, "low")
    
    def should_work_autonomously(self, context: Optional[Context] = None) -> bool:
        """Determine if autonomous work is appropriate"""
        if context is None:
            context = self.current_context
        
        # Full autonomous work during gym, work, sleeping
        # Minimal during available time
        return context in [Context.GYM, Context.WORK, Context.SLEEPING]
    
    def get_max_concurrent_builds(self, context: Optional[Context] = None) -> int:
        """Get max concurrent builds for context"""
        if context is None:
            context = self.current_context
        
        concurrent_map = {
            Context.GYM: 2,
            Context.WORK: 3,
            Context.SLEEPING: 3,
            Context.AVAILABLE: 1,
            Context.UNKNOWN: 1
        }
        
        return concurrent_map.get(context, 1)
    
    def get_context_summary(self) -> Dict:
        """Get summary of current context and recommendations"""
        context = self.detect_context()
        self.set_context(context)
        
        return {
            "current_context": context.value,
            "detected_at": datetime.now().isoformat(),
            "appropriate_categories": self.get_appropriate_work_categories(context),
            "work_intensity": self.get_work_intensity(context),
            "should_work_autonomously": self.should_work_autonomously(context),
            "max_concurrent_builds": self.get_max_concurrent_builds(context),
            "recommendations": self._get_recommendations(context)
        }
    
    def _get_recommendations(self, context: Context) -> List[str]:
        """Get specific recommendations for context"""
        recommendations = {
            Context.GYM: [
                "Focus on fitness-related builds",
                "Analyze recent workout data",
                "Prepare nutrition summaries",
                "Moderate intensity - 2 concurrent max"
            ],
            Context.WORK: [
                "High productivity - build ambitious features",
                "Research revenue opportunities",
                "Optimize existing systems",
                "Test and QA thoroughly",
                "Up to 3 concurrent builds"
            ],
            Context.SLEEPING: [
                "MAXIMUM PRODUCTIVITY TIME",
                "Launch longest builds (4-6 hours)",
                "Process large datasets",
                "Train models if applicable",
                "Deep system optimizations",
                "This is prime building time - use it fully"
            ],
            Context.AVAILABLE: [
                "Stay responsive - minimal background work",
                "Quick iterations only",
                "Be ready to help immediately",
                "Light builds only (1-2 hours max)"
            ],
            Context.UNKNOWN: [
                "Conservative approach",
                "Low-risk tasks only",
                "Stay ready to adapt"
            ]
        }
        
        return recommendations.get(context, [])
    
    def get_upcoming_contexts(self, hours_ahead: int = 24) -> List[Dict]:
        """Predict upcoming contexts for planning"""
        now = datetime.now()
        predictions = []
        
        for hour_offset in range(hours_ahead):
            future = now.replace(hour=(now.hour + hour_offset) % 24, minute=0, second=0)
            
            # Simulate detection for future time
            saved_now = datetime.now
            datetime.now = lambda: future
            predicted_context = self.detect_context()
            datetime.now = saved_now
            
            predictions.append({
                "time": future.isoformat(),
                "context": predicted_context.value,
                "hour_offset": hour_offset
            })
        
        return predictions

def main():
    """CLI interface"""
    import sys
    
    scheduler = ContextScheduler()
    
    if len(sys.argv) < 2:
        print("Usage: context_scheduler.py [command]")
        print("Commands: detect, summary, upcoming, set")
        return
    
    command = sys.argv[1]
    
    if command == "detect":
        context = scheduler.detect_context()
        print(f"\n🎯 Detected context: {context.value}\n")
        
        categories = scheduler.get_appropriate_work_categories(context)
        print("Appropriate work categories:")
        for cat in categories:
            print(f"  • {cat}")
        
        print(f"\nWork intensity: {scheduler.get_work_intensity(context)}")
        print(f"Autonomous work: {'Yes' if scheduler.should_work_autonomously(context) else 'No'}")
        print(f"Max concurrent: {scheduler.get_max_concurrent_builds(context)}")
    
    elif command == "summary":
        summary = scheduler.get_context_summary()
        print("\n📊 Context Summary:\n")
        print(f"Context: {summary['current_context']}")
        print(f"Work intensity: {summary['work_intensity']}")
        print(f"Autonomous: {summary['should_work_autonomously']}")
        print(f"Max concurrent: {summary['max_concurrent_builds']}\n")
        
        print("🎯 Recommendations:")
        for rec in summary['recommendations']:
            print(f"  • {rec}")
    
    elif command == "upcoming":
        predictions = scheduler.get_upcoming_contexts(hours_ahead=12)
        print("\n🔮 Upcoming Contexts (next 12 hours):\n")
        
        current_context = None
        for pred in predictions:
            if pred['context'] != current_context:
                hour = datetime.fromisoformat(pred['time']).hour
                print(f"{hour:02d}:00 - {pred['context']}")
                current_context = pred['context']
    
    elif command == "set":
        if len(sys.argv) < 3:
            print("Usage: set <context>")
            print(f"Contexts: {', '.join(c.value for c in Context)}")
            return
        
        context = Context(sys.argv[2])
        scheduler.set_context(context, explicit=True)
        print(f"✅ Set context to: {context.value}")

if __name__ == "__main__":
    main()
