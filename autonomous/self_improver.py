#!/usr/bin/env python3
"""
Self-Improvement Loop

Monitors own performance, identifies weaknesses, and builds fixes.
Tracks response latency, failures, corrections, and repeated questions.
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

class Weakness:
    def __init__(self, category: str, description: str, evidence: List[str]):
        self.id = f"weak_{int(time.time())}"
        self.category = category
        self.description = description
        self.evidence = evidence
        self.detected_at = datetime.now()
        self.severity = self._calculate_severity()
        self.fix_attempted = False
        self.fix_description = None
        self.fixed_at = None
    
    def _calculate_severity(self) -> str:
        """Calculate severity based on evidence count"""
        if len(self.evidence) >= 5:
            return "high"
        elif len(self.evidence) >= 3:
            return "medium"
        else:
            return "low"
    
    def to_dict(self):
        return {
            "id": self.id,
            "category": self.category,
            "description": self.description,
            "evidence": self.evidence,
            "detected_at": self.detected_at.isoformat(),
            "severity": self.severity,
            "fix_attempted": self.fix_attempted,
            "fix_description": self.fix_description,
            "fixed_at": self.fixed_at.isoformat() if self.fixed_at else None
        }

class Improvement:
    def __init__(self, weakness_id: str, description: str, action: str):
        self.id = f"imp_{int(time.time())}"
        self.weakness_id = weakness_id
        self.description = description
        self.action = action
        self.implemented_at = datetime.now()
        self.impact_measured = False
        self.before_metric = None
        self.after_metric = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "weakness_id": self.weakness_id,
            "description": self.description,
            "action": self.action,
            "implemented_at": self.implemented_at.isoformat(),
            "impact_measured": self.impact_measured,
            "before_metric": self.before_metric,
            "after_metric": self.after_metric
        }

class SelfImprover:
    def __init__(self, state_file="autonomous/data/improvements.json"):
        self.state_file = state_file
        self.improvements_log = "autonomous/logs/improvements.log"
        self.weaknesses: List[Weakness] = []
        self.improvements: List[Improvement] = []
        self.metrics = {
            "response_times": [],
            "api_failures": [],
            "user_corrections": [],
            "repeated_questions": defaultdict(int)
        }
        self.load_state()
    
    def load_state(self):
        """Load improvement state"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                # Simplified loading
                self.weaknesses = data.get("weaknesses", [])
                self.improvements = data.get("improvements", [])
    
    def save_state(self):
        """Save improvement state"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        data = {
            "last_updated": datetime.now().isoformat(),
            "weaknesses": [w.to_dict() if isinstance(w, Weakness) else w for w in self.weaknesses],
            "improvements": [i.to_dict() if isinstance(i, Improvement) else i for i in self.improvements]
        }
        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def log_response_time(self, operation: str, duration_ms: float):
        """Log response time for an operation"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "duration_ms": duration_ms
        }
        self.metrics["response_times"].append(entry)
        
        # Keep last 1000
        self.metrics["response_times"] = self.metrics["response_times"][-1000:]
        
        # Check for slow operations
        if duration_ms > 5000:  # >5 seconds
            self._detect_slow_operation(operation, duration_ms)
    
    def log_api_failure(self, api: str, error: str):
        """Log API failure"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "api": api,
            "error": error
        }
        self.metrics["api_failures"].append(entry)
        self.metrics["api_failures"] = self.metrics["api_failures"][-1000:]
        
        # Check for repeated failures
        recent_failures = [
            f for f in self.metrics["api_failures"][-20:]
            if f["api"] == api
        ]
        
        if len(recent_failures) >= 3:
            self._detect_api_issue(api, recent_failures)
    
    def log_user_correction(self, topic: str, correction: str):
        """Log when user corrects something"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "correction": correction
        }
        self.metrics["user_corrections"].append(entry)
        self.metrics["user_corrections"] = self.metrics["user_corrections"][-1000:]
        
        # Detect knowledge gaps
        corrections_on_topic = [
            c for c in self.metrics["user_corrections"][-50:]
            if c["topic"] == topic
        ]
        
        if len(corrections_on_topic) >= 2:
            self._detect_knowledge_gap(topic, corrections_on_topic)
    
    def log_repeated_question(self, question_type: str):
        """Log repeated question (user asks same thing multiple times)"""
        self.metrics["repeated_questions"][question_type] += 1
        
        if self.metrics["repeated_questions"][question_type] >= 3:
            self._detect_missing_automation(question_type)
    
    def _detect_slow_operation(self, operation: str, duration_ms: float):
        """Detect slow operations that need optimization"""
        weakness = Weakness(
            category="performance",
            description=f"Slow operation: {operation} ({duration_ms:.0f}ms)",
            evidence=[f"Operation took {duration_ms:.0f}ms"]
        )
        self.weaknesses.append(weakness)
        self.save_state()
    
    def _detect_api_issue(self, api: str, failures: List[Dict]):
        """Detect API reliability issues"""
        weakness = Weakness(
            category="reliability",
            description=f"Repeated API failures: {api}",
            evidence=[f"{len(failures)} failures in recent history"]
        )
        self.weaknesses.append(weakness)
        self.save_state()
    
    def _detect_knowledge_gap(self, topic: str, corrections: List[Dict]):
        """Detect knowledge gaps from corrections"""
        weakness = Weakness(
            category="knowledge",
            description=f"Knowledge gap: {topic}",
            evidence=[c["correction"] for c in corrections]
        )
        self.weaknesses.append(weakness)
        self.save_state()
    
    def _detect_missing_automation(self, question_type: str):
        """Detect missing automation opportunities"""
        weakness = Weakness(
            category="automation",
            description=f"Repeated question: {question_type}",
            evidence=[f"Asked {self.metrics['repeated_questions'][question_type]} times"]
        )
        self.weaknesses.append(weakness)
        self.save_state()
    
    def suggest_improvements(self) -> List[Dict]:
        """Suggest improvements for detected weaknesses"""
        suggestions = []
        
        for weakness in self.weaknesses:
            if isinstance(weakness, dict):
                continue
            
            if weakness.fix_attempted:
                continue
            
            suggestion = self._generate_improvement_plan(weakness)
            if suggestion:
                suggestions.append(suggestion)
        
        return suggestions
    
    def _generate_improvement_plan(self, weakness: Weakness) -> Optional[Dict]:
        """Generate improvement plan for a weakness"""
        if weakness.category == "performance":
            return {
                "weakness_id": weakness.id,
                "title": f"Optimize {weakness.description}",
                "description": "Add caching or optimize algorithm",
                "action": "cache_optimization",
                "estimated_hours": 1.0,
                "auto_approve": True
            }
        
        elif weakness.category == "reliability":
            return {
                "weakness_id": weakness.id,
                "title": f"Add error handling for {weakness.description}",
                "description": "Implement retry logic and fallbacks",
                "action": "error_handling",
                "estimated_hours": 1.5,
                "auto_approve": True
            }
        
        elif weakness.category == "knowledge":
            return {
                "weakness_id": weakness.id,
                "title": f"Update documentation: {weakness.description}",
                "description": "Add to knowledge base to prevent future corrections",
                "action": "update_docs",
                "estimated_hours": 0.5,
                "auto_approve": True
            }
        
        elif weakness.category == "automation":
            return {
                "weakness_id": weakness.id,
                "title": f"Automate: {weakness.description}",
                "description": "Build automation to prevent repeated questions",
                "action": "build_automation",
                "estimated_hours": 2.0,
                "auto_approve": False  # Requires approval
            }
        
        return None
    
    def implement_improvement(self, weakness_id: str, description: str, action: str) -> bool:
        """Mark improvement as implemented"""
        weakness = next((w for w in self.weaknesses if isinstance(w, Weakness) and w.id == weakness_id), None)
        if not weakness:
            return False
        
        improvement = Improvement(weakness_id, description, action)
        self.improvements.append(improvement)
        weakness.fix_attempted = True
        weakness.fix_description = description
        weakness.fixed_at = datetime.now()
        
        self.save_state()
        self._log_improvement(improvement)
        return True
    
    def _log_improvement(self, improvement: Improvement):
        """Log improvement to file"""
        os.makedirs(os.path.dirname(self.improvements_log), exist_ok=True)
        with open(self.improvements_log, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] Implemented: {improvement.description}\n")
            f.write(f"  Action: {improvement.action}\n")
            f.write(f"  Weakness: {improvement.weakness_id}\n\n")
    
    def get_stats(self) -> Dict:
        """Get improvement statistics"""
        total_weaknesses = len([w for w in self.weaknesses if isinstance(w, Weakness)])
        fixed = len([w for w in self.weaknesses if isinstance(w, Weakness) and w.fix_attempted])
        
        by_category = defaultdict(int)
        for w in self.weaknesses:
            if isinstance(w, Weakness):
                by_category[w.category] += 1
        
        return {
            "total_weaknesses": total_weaknesses,
            "fixed": fixed,
            "unfixed": total_weaknesses - fixed,
            "total_improvements": len([i for i in self.improvements if isinstance(i, Improvement)]),
            "by_category": dict(by_category),
            "avg_response_time_ms": self._calculate_avg_response_time(),
            "api_failure_rate": self._calculate_failure_rate()
        }
    
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time"""
        if not self.metrics["response_times"]:
            return 0.0
        
        recent = self.metrics["response_times"][-100:]
        total = sum(r["duration_ms"] for r in recent)
        return total / len(recent)
    
    def _calculate_failure_rate(self) -> float:
        """Calculate API failure rate"""
        if not self.metrics["api_failures"]:
            return 0.0
        
        recent_24h = [
            f for f in self.metrics["api_failures"]
            if datetime.fromisoformat(f["timestamp"]) > datetime.now() - timedelta(hours=24)
        ]
        return len(recent_24h) / 24  # Failures per hour

def main():
    """CLI interface"""
    import sys
    
    improver = SelfImprover()
    
    if len(sys.argv) < 2:
        print("Usage: self_improver.py [command]")
        print("Commands: suggest, stats, log-time, log-failure, log-correction")
        return
    
    command = sys.argv[1]
    
    if command == "suggest":
        suggestions = improver.suggest_improvements()
        if suggestions:
            print(f"\n💡 Improvement Suggestions ({len(suggestions)}):\n")
            for sugg in suggestions:
                print(f"• {sugg['title']}")
                print(f"  {sugg['description']}")
                print(f"  Estimated: {sugg['estimated_hours']}h")
                if sugg['auto_approve']:
                    print(f"  ✅ Auto-approve")
                print()
        else:
            print("No improvement suggestions")
    
    elif command == "stats":
        stats = improver.get_stats()
        print("\n📊 Self-Improvement Statistics:\n")
        print(f"Total weaknesses detected: {stats['total_weaknesses']}")
        print(f"Fixed: {stats['fixed']}")
        print(f"Unfixed: {stats['unfixed']}")
        print(f"Total improvements: {stats['total_improvements']}\n")
        
        print("Weaknesses by category:")
        for category, count in stats['by_category'].items():
            print(f"  {category}: {count}")
        
        print(f"\nAvg response time: {stats['avg_response_time_ms']:.0f}ms")
        print(f"API failure rate: {stats['api_failure_rate']:.2f}/hour")
    
    elif command == "log-time":
        # Example: log-time "database_query" 2500
        if len(sys.argv) < 4:
            print("Usage: log-time <operation> <duration_ms>")
            return
        
        operation = sys.argv[2]
        duration = float(sys.argv[3])
        improver.log_response_time(operation, duration)
        print(f"✅ Logged: {operation} ({duration}ms)")
    
    elif command == "log-failure":
        # Example: log-failure "spotify_api" "Rate limit exceeded"
        if len(sys.argv) < 4:
            print("Usage: log-failure <api> <error>")
            return
        
        api = sys.argv[2]
        error = sys.argv[3]
        improver.log_api_failure(api, error)
        print(f"✅ Logged failure: {api}")
    
    elif command == "log-correction":
        # Example: log-correction "nba_schedule" "Games are on Tuesday, not Wednesday"
        if len(sys.argv) < 4:
            print("Usage: log-correction <topic> <correction>")
            return
        
        topic = sys.argv[2]
        correction = sys.argv[3]
        improver.log_user_correction(topic, correction)
        print(f"✅ Logged correction: {topic}")

if __name__ == "__main__":
    main()
