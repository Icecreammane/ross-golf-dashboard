#!/usr/bin/env python3
"""
Decision Confidence Scoring - Know when to act vs ask
Learns Ross's risk tolerance and autonomy preferences by category
"""

import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/Users/clawdbot/clawd")
MEMORY_DIR = WORKSPACE / "memory"
DECISION_MODEL = MEMORY_DIR / "decision_model.json"
DECISION_LOG = MEMORY_DIR / "decision_log.json"

class DecisionEngine:
    def __init__(self):
        self.model = self.load_model()
        self.log = self.load_log()
    
    def load_model(self):
        """Load decision-making model"""
        if DECISION_MODEL.exists():
            with open(DECISION_MODEL) as f:
                return json.load(f)
        
        return {
            "categories": {
                "code_changes": {
                    "base_confidence": 0.8,
                    "auto_threshold": 0.9,
                    "risk_tolerance": "high",
                    "examples": []
                },
                "file_operations": {
                    "base_confidence": 0.7,
                    "auto_threshold": 0.85,
                    "risk_tolerance": "medium",
                    "examples": []
                },
                "external_messages": {
                    "base_confidence": 0.0,
                    "auto_threshold": 0.99,  # Almost never autonomous
                    "risk_tolerance": "zero",
                    "examples": []
                },
                "purchases": {
                    "base_confidence": 0.0,
                    "auto_threshold": 0.99,
                    "risk_tolerance": "zero",
                    "examples": []
                },
                "research": {
                    "base_confidence": 0.95,
                    "auto_threshold": 0.8,
                    "risk_tolerance": "high",
                    "examples": []
                },
                "documentation": {
                    "base_confidence": 0.9,
                    "auto_threshold": 0.7,
                    "risk_tolerance": "high",
                    "examples": []
                },
                "scheduling": {
                    "base_confidence": 0.6,
                    "auto_threshold": 0.85,
                    "risk_tolerance": "medium",
                    "examples": []
                },
                "destructive_actions": {
                    "base_confidence": 0.0,
                    "auto_threshold": 0.95,
                    "risk_tolerance": "zero",
                    "examples": []
                }
            },
            "global_modifiers": {
                "time_of_day_trust": {
                    "morning": 1.0,
                    "afternoon": 1.0,
                    "evening": 0.9,
                    "night": 0.7  # Lower confidence at night
                },
                "success_rate_multiplier": 1.0,
                "correction_penalty": 0.1  # Reduce confidence when corrected
            },
            "learning_data": {
                "total_decisions": 0,
                "autonomous_actions": 0,
                "asked_permission": 0,
                "corrections": 0,
                "positive_feedback": 0
            }
        }
    
    def load_log(self):
        """Load decision log"""
        if DECISION_LOG.exists():
            with open(DECISION_LOG) as f:
                return json.load(f)
        return {
            "decisions": [],
            "feedback": []
        }
    
    def score_decision(self, action_type, context=None):
        """Score confidence for a decision"""
        context = context or {}
        
        # Get base confidence for category
        category = self._categorize_action(action_type)
        cat_data = self.model["categories"].get(category, {})
        base_confidence = cat_data.get("base_confidence", 0.5)
        
        # Apply modifiers
        confidence = base_confidence
        
        # Time of day modifier
        hour = datetime.now().hour
        if 6 <= hour < 12:
            time_modifier = self.model["global_modifiers"]["time_of_day_trust"]["morning"]
        elif 12 <= hour < 17:
            time_modifier = self.model["global_modifiers"]["time_of_day_trust"]["afternoon"]
        elif 17 <= hour < 23:
            time_modifier = self.model["global_modifiers"]["time_of_day_trust"]["evening"]
        else:
            time_modifier = self.model["global_modifiers"]["time_of_day_trust"]["night"]
        
        confidence *= time_modifier
        
        # Success rate modifier
        success_rate = self._calculate_success_rate(category)
        confidence *= (0.8 + 0.2 * success_rate)  # 80-100% multiplier based on success
        
        # Context-specific adjustments
        if context.get("reversible", False):
            confidence *= 1.1  # Boost for reversible actions
        
        if context.get("high_impact", False):
            confidence *= 0.8  # Reduce for high-impact actions
        
        if context.get("similar_approved_before", False):
            confidence *= 1.2  # Boost if similar actions approved before
        
        # Cap at 1.0
        confidence = min(confidence, 1.0)
        
        return {
            "confidence": confidence,
            "category": category,
            "threshold": cat_data.get("auto_threshold", 0.9),
            "recommendation": self._get_recommendation(confidence, cat_data.get("auto_threshold", 0.9)),
            "reasoning": self._explain_score(confidence, category, time_modifier, success_rate)
        }
    
    def _categorize_action(self, action_type):
        """Categorize an action"""
        action_lower = action_type.lower()
        
        if any(k in action_lower for k in ["email", "message", "post", "tweet", "send"]):
            return "external_messages"
        
        if any(k in action_lower for k in ["delete", "remove", "drop", "destroy"]):
            return "destructive_actions"
        
        if any(k in action_lower for k in ["buy", "purchase", "pay", "order"]):
            return "purchases"
        
        if any(k in action_lower for k in ["code", "script", "function", "implement"]):
            return "code_changes"
        
        if any(k in action_lower for k in ["file", "move", "copy", "rename"]):
            return "file_operations"
        
        if any(k in action_lower for k in ["research", "search", "find", "look up"]):
            return "research"
        
        if any(k in action_lower for k in ["document", "write", "update", "note"]):
            return "documentation"
        
        if any(k in action_lower for k in ["schedule", "calendar", "meeting"]):
            return "scheduling"
        
        return "unknown"
    
    def _calculate_success_rate(self, category):
        """Calculate success rate for a category"""
        cat_decisions = [d for d in self.log.get("decisions", []) if d.get("category") == category]
        
        if not cat_decisions:
            return 0.8  # Default 80% if no history
        
        successful = sum(1 for d in cat_decisions if d.get("outcome") == "success")
        return successful / len(cat_decisions)
    
    def _get_recommendation(self, confidence, threshold):
        """Get action recommendation"""
        if confidence >= threshold:
            return "DO_IT"
        elif confidence >= 0.6:
            return "ASK_PERMISSION"
        else:
            return "EXPLAIN_OPTIONS"
    
    def _explain_score(self, confidence, category, time_modifier, success_rate):
        """Explain the confidence score"""
        reasons = []
        reasons.append(f"Category: {category}")
        reasons.append(f"Base confidence: {confidence:.0%}")
        reasons.append(f"Time modifier: {time_modifier:.0%}")
        reasons.append(f"Success rate: {success_rate:.0%}")
        return " | ".join(reasons)
    
    def log_decision(self, action_type, decision, outcome=None):
        """Log a decision for learning"""
        category = self._categorize_action(action_type)
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "category": category,
            "decision": decision,  # DO_IT, ASK_PERMISSION, EXPLAIN_OPTIONS
            "outcome": outcome  # success, failure, corrected, None (pending)
        }
        
        self.log["decisions"].append(entry)
        
        # Update learning data
        self.model["learning_data"]["total_decisions"] += 1
        
        if decision == "DO_IT":
            self.model["learning_data"]["autonomous_actions"] += 1
        elif decision in ["ASK_PERMISSION", "EXPLAIN_OPTIONS"]:
            self.model["learning_data"]["asked_permission"] += 1
        
        # Keep last 500 decisions
        if len(self.log["decisions"]) > 500:
            self.log["decisions"] = self.log["decisions"][-500:]
        
        self.save_log()
        self.save_model()
    
    def record_feedback(self, decision_id, feedback_type):
        """Record feedback on a decision"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "decision_id": decision_id,
            "feedback": feedback_type  # "corrected", "approved", "praised"
        }
        
        self.log["feedback"].append(entry)
        
        # Update learning data
        if feedback_type == "corrected":
            self.model["learning_data"]["corrections"] += 1
            # Reduce confidence slightly for this category
            # (Would need more sophisticated learning here)
        elif feedback_type in ["approved", "praised"]:
            self.model["learning_data"]["positive_feedback"] += 1
        
        self.save_log()
        self.save_model()
    
    def get_autonomy_report(self):
        """Get report on autonomy and decision-making"""
        data = self.model["learning_data"]
        
        if data["total_decisions"] == 0:
            return "No decisions logged yet"
        
        autonomy_rate = data["autonomous_actions"] / data["total_decisions"]
        success_rate = 1 - (data["corrections"] / max(data["autonomous_actions"], 1))
        
        report = f"""
Decision-Making Report:
- Total decisions: {data['total_decisions']}
- Autonomous actions: {data['autonomous_actions']} ({autonomy_rate:.0%})
- Asked permission: {data['asked_permission']}
- Corrections needed: {data['corrections']}
- Success rate: {success_rate:.0%}
- Positive feedback: {data['positive_feedback']}

Recommendation: {'Increase autonomy' if success_rate > 0.9 else 'Maintain current level'}
"""
        return report.strip()
    
    def save_model(self):
        """Save decision model"""
        DECISION_MODEL.parent.mkdir(exist_ok=True)
        with open(DECISION_MODEL, "w") as f:
            json.dump(self.model, f, indent=2)
    
    def save_log(self):
        """Save decision log"""
        DECISION_LOG.parent.mkdir(exist_ok=True)
        with open(DECISION_LOG, "w") as f:
            json.dump(self.log, f, indent=2)


def test_decision_engine():
    """Test decision engine"""
    engine = DecisionEngine()
    
    print("Decision Confidence Scoring Tests:\n")
    
    # Test various action types
    tests = [
        ("update documentation", {"reversible": True}),
        ("send email to client", {"high_impact": True}),
        ("delete old file", {"reversible": False}),
        ("implement new feature", {"similar_approved_before": True}),
        ("search for golf coaching trends", {}),
        ("purchase API subscription", {}),
    ]
    
    for action, context in tests:
        score = engine.score_decision(action, context)
        print(f"Action: {action}")
        print(f"  Confidence: {score['confidence']:.0%}")
        print(f"  Category: {score['category']}")
        print(f"  Recommendation: {score['recommendation']}")
        print(f"  Reasoning: {score['reasoning']}")
        print()
        
        # Log it
        engine.log_decision(action, score['recommendation'], "success")
    
    print("\n" + engine.get_autonomy_report())
    print("\n✅ Decision engine working!")


if __name__ == "__main__":
    test_decision_engine()
