#!/usr/bin/env python3
"""
Uncertainty Tracker
Track confidence levels and learn from mistakes
Be honest about when I'm not sure
"""

import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path.home() / "clawd"
UNCERTAINTY_LOG = WORKSPACE / "memory" / "uncertainty_log.json"

class UncertaintyTracker:
    """Track confidence and learn from mistakes"""
    
    def __init__(self):
        self.log_file = UNCERTAINTY_LOG
        self.load_log()
    
    def load_log(self):
        """Load uncertainty log"""
        if self.log_file.exists():
            with open(self.log_file) as f:
                self.log = json.load(f)
        else:
            self.log = {
                "version": "1.0",
                "responses": [],
                "mistakes": [],
                "confidence_calibration": {
                    "high_confidence_correct": 0,
                    "high_confidence_wrong": 0,
                    "low_confidence_correct": 0,
                    "low_confidence_wrong": 0
                }
            }
    
    def save_log(self):
        """Save uncertainty log"""
        self.log_file.parent.mkdir(exist_ok=True)
        with open(self.log_file, 'w') as f:
            json.dump(self.log, f, indent=2)
    
    def log_response(self, topic, response, confidence, reasoning=None):
        """
        Log a response with confidence level
        
        Args:
            topic: What the response was about
            response: The actual response
            confidence: 0-10 confidence level
            reasoning: Why this confidence level
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "response": response[:200],  # First 200 chars
            "confidence": confidence,
            "reasoning": reasoning,
            "outcome": None  # Will be filled in later
        }
        
        self.log["responses"].append(entry)
        
        # Keep only last 100 responses
        if len(self.log["responses"]) > 100:
            self.log["responses"] = self.log["responses"][-100:]
        
        self.save_log()
        
        return entry
    
    def log_mistake(self, topic, what_was_wrong, why_it_happened, lesson_learned):
        """
        Log a mistake to learn from
        
        Args:
            topic: What it was about
            what_was_wrong: What I got wrong
            why_it_happened: Why I made the mistake
            lesson_learned: What to do differently
        """
        mistake = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "what_was_wrong": what_was_wrong,
            "why_it_happened": why_it_happened,
            "lesson_learned": lesson_learned
        }
        
        self.log["mistakes"].append(mistake)
        
        # Keep only last 50 mistakes
        if len(self.log["mistakes"]) > 50:
            self.log["mistakes"] = self.log["mistakes"][-50:]
        
        self.save_log()
        
        print(f"📝 Mistake logged: {what_was_wrong}")
        print(f"   Lesson: {lesson_learned}")
        
        return mistake
    
    def mark_outcome(self, response_index, was_correct):
        """
        Mark whether a response was correct
        
        Args:
            response_index: Index in responses list (or -1 for most recent)
            was_correct: True if response was correct/helpful
        """
        if response_index == -1:
            response_index = len(self.log["responses"]) - 1
        
        if 0 <= response_index < len(self.log["responses"]):
            response = self.log["responses"][response_index]
            response["outcome"] = "correct" if was_correct else "incorrect"
            
            # Update calibration stats
            confidence = response["confidence"]
            high_conf = confidence >= 7
            
            if high_conf and was_correct:
                self.log["confidence_calibration"]["high_confidence_correct"] += 1
            elif high_conf and not was_correct:
                self.log["confidence_calibration"]["high_confidence_wrong"] += 1
            elif not high_conf and was_correct:
                self.log["confidence_calibration"]["low_confidence_correct"] += 1
            elif not high_conf and not was_correct:
                self.log["confidence_calibration"]["low_confidence_wrong"] += 1
            
            self.save_log()
    
    def should_be_uncertain(self, topic_keywords):
        """
        Check if topic matches past mistakes
        Returns confidence adjustment (-2 to 0)
        """
        recent_mistakes = self.log["mistakes"][-20:]  # Last 20 mistakes
        
        for mistake in recent_mistakes:
            mistake_words = mistake["topic"].lower().split()
            topic_words = [w.lower() for w in topic_keywords]
            
            # Check overlap
            overlap = set(mistake_words) & set(topic_words)
            if len(overlap) >= 2:
                return -2  # Reduce confidence
        
        return 0  # No adjustment
    
    def get_calibration_stats(self):
        """Get confidence calibration statistics"""
        cal = self.log["confidence_calibration"]
        
        total_high = cal["high_confidence_correct"] + cal["high_confidence_wrong"]
        total_low = cal["low_confidence_correct"] + cal["low_confidence_wrong"]
        
        stats = {
            "high_confidence_accuracy": (cal["high_confidence_correct"] / total_high * 100) if total_high > 0 else 0,
            "low_confidence_accuracy": (cal["low_confidence_correct"] / total_low * 100) if total_low > 0 else 0,
            "total_responses": len(self.log["responses"]),
            "total_mistakes": len(self.log["mistakes"])
        }
        
        return stats
    
    def generate_confidence_report(self):
        """Generate human-readable confidence report"""
        stats = self.get_calibration_stats()
        
        report = []
        report.append("=" * 70)
        report.append("📊 CONFIDENCE CALIBRATION")
        report.append("=" * 70)
        report.append("")
        
        report.append(f"Total responses tracked: {stats['total_responses']}")
        report.append(f"Total mistakes logged: {stats['total_mistakes']}")
        report.append("")
        
        report.append("Accuracy by confidence level:")
        report.append(f"  High confidence (7-10): {stats['high_confidence_accuracy']:.1f}% accurate")
        report.append(f"  Low confidence (0-6): {stats['low_confidence_accuracy']:.1f}% accurate")
        report.append("")
        
        # Recent mistakes
        if self.log["mistakes"]:
            report.append("Recent mistakes:")
            for mistake in self.log["mistakes"][-5:]:
                timestamp = datetime.fromisoformat(mistake["timestamp"]).strftime("%m/%d")
                report.append(f"  • [{timestamp}] {mistake['what_was_wrong']}")
                report.append(f"    Lesson: {mistake['lesson_learned']}")
            report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def get_uncertain_topics(self):
        """Get list of topics where I should be uncertain"""
        mistake_topics = set()
        
        for mistake in self.log["mistakes"][-20:]:
            topic_words = mistake["topic"].lower().split()
            for word in topic_words:
                if len(word) > 3:  # Skip short words
                    mistake_topics.add(word)
        
        return list(mistake_topics)


def test_uncertainty_tracker():
    """Test uncertainty tracker"""
    ut = UncertaintyTracker()
    
    print("=" * 70)
    print("🤔 UNCERTAINTY TRACKER TEST")
    print("=" * 70)
    print()
    
    # Log some responses
    print("📝 Logging test responses...")
    
    ut.log_response(
        topic="party demo suggestions",
        response="I think Roast Bot will work great",
        confidence=8,
        reasoning="Ross likes interactive, fun tools"
    )
    
    ut.log_response(
        topic="fitness tracker predictions",
        response="Not sure about the best approach here",
        confidence=4,
        reasoning="Haven't seen Ross use tracker much yet"
    )
    
    ut.log_response(
        topic="build time estimate",
        response="This will take 2-3 hours",
        confidence=6,
        reasoning="Similar to past builds but some unknowns"
    )
    
    print("  ✅ 3 responses logged")
    print()
    
    # Log a mistake
    print("📝 Logging test mistake...")
    ut.log_mistake(
        topic="time estimation",
        what_was_wrong="Said build would take 1 hour, actually took 3 hours",
        why_it_happened="Underestimated complexity, didn't account for debugging",
        lesson_learned="Add 2x buffer for new integrations, especially with external APIs"
    )
    print()
    
    # Check calibration
    print(ut.generate_confidence_report())


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_uncertainty_tracker()
    else:
        ut = UncertaintyTracker()
        print(ut.generate_confidence_report())


if __name__ == "__main__":
    main()
