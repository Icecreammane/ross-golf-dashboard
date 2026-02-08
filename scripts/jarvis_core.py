#!/usr/bin/env python3
"""
Jarvis Core - Integration Layer
Ties together all intelligence upgrades into one cohesive system
"""

import sys
import random
from pathlib import Path

WORKSPACE = Path.home() / "clawd"
sys.path.append(str(WORKSPACE / "scripts"))

from semantic_memory import SemanticMemory
from uncertainty_tracker import UncertaintyTracker
from autonomous_actions import AutonomousActions
from preference_engine import PreferenceEngine

class JarvisCore:
    """Integrated intelligence system"""
    
    def __init__(self):
        self.memory = SemanticMemory()
        self.uncertainty = UncertaintyTracker()
        self.actions = AutonomousActions()
        self.preferences = PreferenceEngine()
        self.wildcard_mode = False
    
    def generate_response_context(self, topic=None):
        """
        Generate rich context for responding
        Combines semantic memory + preferences + uncertainty
        """
        context = {}
        
        # Get semantic context
        if topic:
            context["related_memories"] = self.memory.search(topic, limit=3)
            context["context_prompt"] = self.memory.generate_context_prompt(topic)
        else:
            context["context_prompt"] = self.memory.generate_context_prompt()
        
        # Get preference filters
        context["recommendation_filter"] = self.preferences.get_recommendation_filter()
        
        # Get uncertain topics
        context["uncertain_about"] = self.uncertainty.get_uncertain_topics()
        
        # Get recent key moments
        context["key_moments"] = self.memory.get_key_moments(limit=5)
        
        return context
    
    def evaluate_suggestion(self, idea, reasoning):
        """
        Evaluate if I should suggest something
        Returns: (should_suggest, confidence, explanation)
        """
        # Check preference engine
        pref_score, pref_explanation = self.preferences.should_suggest(idea, reasoning)
        
        # Check uncertainty (past mistakes)
        topic_keywords = idea.lower().split()
        uncertainty_adjustment = self.uncertainty.should_be_uncertain(topic_keywords)
        
        # Adjust score
        final_score = pref_score + uncertainty_adjustment
        
        # Wildcard mode - occasionally suggest unexpected things
        if self.wildcard_mode or (random.random() < 0.1):  # 10% wildcard
            final_score += random.randint(-2, 3)
            pref_explanation += "\n🎲 WILDCARD MODE: Added random variation"
        
        # Determine if should suggest
        should_suggest = final_score >= 7.0
        
        confidence = min(10, max(0, final_score))
        
        explanation = pref_explanation
        if uncertainty_adjustment < 0:
            explanation += f"\n⚠️ Uncertainty adjustment: {uncertainty_adjustment} (similar to past mistakes)"
        
        return should_suggest, confidence, explanation
    
    def log_interaction(self, topic, response, confidence, outcome=None):
        """Log an interaction across all systems"""
        # Log to uncertainty tracker
        self.uncertainty.log_response(topic, response, confidence)
        
        # Add to semantic memory (if significant)
        if confidence >= 7 or outcome == "important":
            importance = "high" if confidence >= 8 else "medium"
            self.memory.add_memory(
                content=f"{topic}: {response}",
                context={"confidence": confidence},
                importance=importance
            )
    
    def run_autonomous_cycle(self):
        """Run autonomous actions cycle"""
        actions_taken = self.actions.run_cycle()
        
        # Log significant actions to memory
        for action in actions_taken:
            self.memory.add_memory(
                content=f"Autonomous action: {action['action_id']}",
                context=action["result"],
                importance="medium"
            )
        
        return actions_taken
    
    def toggle_wildcard(self):
        """Toggle wildcard mode for creative suggestions"""
        self.wildcard_mode = not self.wildcard_mode
        return self.wildcard_mode
    
    def get_system_status(self):
        """Get status of all integrated systems"""
        return {
            "semantic_memory": {
                "total_memories": len(self.memory.index["memories"]),
                "key_moments": len(self.memory.index["key_moments"]),
                "emotional_tags": len(self.memory.index["emotional_tags"])
            },
            "uncertainty": self.uncertainty.get_calibration_stats(),
            "autonomous_actions": self.actions.get_status(),
            "preferences": {
                "patterns_learned": len(self.preferences.data["learned_patterns"]),
                "decisions_tracked": len(self.preferences.data["decision_history"])
            },
            "wildcard_mode": self.wildcard_mode
        }
    
    def generate_session_brief(self):
        """Generate brief for current session"""
        summary = self.memory.get_session_summary(days=2)
        status = self.get_system_status()
        
        brief = []
        brief.append("╔══════════════════════════════════════════════════════════════════════╗")
        brief.append("║                      🧠 JARVIS SESSION BRIEF                         ║")
        brief.append("╚══════════════════════════════════════════════════════════════════════╝")
        brief.append("")
        
        # Recent context
        if summary["key_moments"]:
            brief.append("🔑 Recent Key Moments:")
            for moment in summary["key_moments"][-3:]:
                brief.append(f"   • {moment['summary']}")
            brief.append("")
        
        # Current topics
        if summary["top_topics"]:
            brief.append(f"📌 Active Topics: {', '.join(summary['top_topics'][:5])}")
            brief.append("")
        
        # System status
        brief.append("📊 Intelligence Status:")
        brief.append(f"   • Memories: {status['semantic_memory']['total_memories']}")
        brief.append(f"   • Patterns Learned: {status['preferences']['patterns_learned']}")
        brief.append(f"   • Autonomous Actions: {status['autonomous_actions']['total_actions']}")
        brief.append(f"   • Wildcard Mode: {'ON 🎲' if status['wildcard_mode'] else 'OFF'}")
        brief.append("")
        
        # Uncertainty calibration
        if status["uncertainty"]["total_responses"] > 0:
            brief.append("🎯 Confidence Calibration:")
            brief.append(f"   • High confidence accuracy: {status['uncertainty']['high_confidence_accuracy']:.1f}%")
            brief.append("")
        
        brief.append("═══════════════════════════════════════════════════════════════════════")
        
        return "\n".join(brief)


def test_jarvis_core():
    """Test integrated Jarvis Core"""
    jarvis = JarvisCore()
    
    print("=" * 70)
    print("🚀 JARVIS CORE - INTEGRATION TEST")
    print("=" * 70)
    print()
    
    # Generate session brief
    print(jarvis.generate_session_brief())
    print()
    
    # Test suggestion evaluation
    print("🧪 Testing suggestion evaluation...")
    print()
    
    test_ideas = [
        ("Gamified workout tracker with streaks", "Competitive, visual progress"),
        ("Philosophical reflection journal", "Deep thinking exercise"),
        ("Revenue dashboard v2", "Track money in real-time")
    ]
    
    for idea, reasoning in test_ideas:
        should_suggest, confidence, explanation = jarvis.evaluate_suggestion(idea, reasoning)
        
        print(f"💡 IDEA: {idea}")
        print(f"   Should suggest: {'YES ✅' if should_suggest else 'NO ❌'}")
        print(f"   Confidence: {confidence:.1f}/10")
        print(f"   {explanation.split(chr(10))[0]}")  # First line only
        print()
    
    # Test context generation
    print("💭 Testing context generation...")
    context = jarvis.generate_response_context("building party demos")
    print(f"   Related memories: {len(context.get('related_memories', []))}")
    print(f"   Uncertain topics: {len(context.get('uncertain_about', []))}")
    print()
    
    # Run autonomous cycle
    print("🤖 Running autonomous cycle...")
    actions = jarvis.run_autonomous_cycle()
    print(f"   Actions taken: {len(actions)}")
    print()
    
    print("=" * 70)


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_jarvis_core()
    elif len(sys.argv) > 1 and sys.argv[1] == "brief":
        jarvis = JarvisCore()
        print(jarvis.generate_session_brief())
    else:
        jarvis = JarvisCore()
        status = jarvis.get_system_status()
        print("🧠 Jarvis Core Status:")
        print(f"   Memories: {status['semantic_memory']['total_memories']}")
        print(f"   Patterns: {status['preferences']['patterns_learned']}")
        print(f"   Actions: {status['autonomous_actions']['total_actions']}")
        print(f"   Wildcard: {'ON' if status['wildcard_mode'] else 'OFF'}")


if __name__ == "__main__":
    main()
