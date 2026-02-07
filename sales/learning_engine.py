#!/usr/bin/env python3
"""
Learning Engine - Learn from A/B test results
Identifies winning patterns and generates insights
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sales.response_tracker import ResponseTracker

class LearningEngine:
    def __init__(self, workspace_root: str = "/Users/clawdbot/clawd"):
        self.workspace = Path(workspace_root)
        self.tracker = ResponseTracker(workspace_root)
        self.insights_file = self.workspace / "sales" / "learning-insights.json"
    
    def analyze_results(self, min_sends: int = 10) -> Dict:
        """
        Analyze A/B test results and identify winners
        
        Args:
            min_sends: Minimum sends required for statistical significance
        
        Returns:
            Analysis with winners, losers, and insights
        """
        leaderboard = self.tracker.get_leaderboard("reply_rate", min_sends=min_sends)
        
        if not leaderboard:
            return {
                "status": "insufficient_data",
                "min_sends_required": min_sends,
                "message": f"Need at least {min_sends} sends per variation to analyze"
            }
        
        # Identify winner (highest reply rate)
        winner = leaderboard[0]
        
        # Identify losers (bottom 30%)
        cutoff_index = max(1, int(len(leaderboard) * 0.7))
        losers = leaderboard[cutoff_index:]
        
        # Compare winner to average
        avg_reply_rate = sum(e["reply_rate"] for e in leaderboard) / len(leaderboard)
        winner_lift = (winner["reply_rate"] - avg_reply_rate) / avg_reply_rate if avg_reply_rate > 0 else 0
        
        # Generate insights
        insights = self._generate_insights(winner, losers, leaderboard)
        
        analysis = {
            "analyzed_at": datetime.now().isoformat(),
            "total_sends": sum(e["send_count"] for e in leaderboard),
            "approaches_tested": len(leaderboard),
            "winner": {
                "approach": winner["approach"],
                "reply_rate": winner["reply_rate"],
                "send_count": winner["send_count"],
                "reply_count": winner["reply_count"],
                "lift_vs_average": winner_lift
            },
            "losers": [
                {
                    "approach": loser["approach"],
                    "reply_rate": loser["reply_rate"],
                    "send_count": loser["send_count"]
                }
                for loser in losers
            ],
            "insights": insights,
            "recommendations": self._generate_recommendations(winner, losers, insights)
        }
        
        # Save insights
        self._save_insights(analysis)
        
        return analysis
    
    def _generate_insights(
        self,
        winner: Dict,
        losers: List[Dict],
        all_approaches: List[Dict]
    ) -> List[str]:
        """Generate human-readable insights"""
        insights = []
        
        # Winner insights
        winner_rate = winner["reply_rate"] * 100
        winner_approach = winner["approach"]
        
        insights.append(
            f"'{winner_approach}' approach converts best at {winner_rate:.1f}% reply rate"
        )
        
        # Find patterns in losers
        loser_approaches = [l["approach"] for l in losers]
        
        if "direct" in loser_approaches:
            insights.append("Direct pitches underperform - people want context first")
        
        if "scarcity" in loser_approaches:
            insights.append("Scarcity/urgency tactics don't resonate with this audience")
        
        # Look for high-performers
        high_performers = [
            e for e in all_approaches 
            if e["reply_rate"] > 0.3  # > 30% reply rate
        ]
        
        if len(high_performers) > 1:
            approaches = [e["approach"] for e in high_performers]
            insights.append(f"Multiple strong performers: {', '.join(approaches)}")
        
        # Open rate vs reply rate analysis
        for approach in all_approaches[:3]:  # Top 3
            if approach["open_rate"] > 0.7 and approach["reply_rate"] < 0.2:
                insights.append(
                    f"'{approach['approach']}' gets opened but not replied to - message doesn't deliver"
                )
        
        return insights
    
    def _generate_recommendations(
        self,
        winner: Dict,
        losers: List[Dict],
        insights: List[str]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        winner_approach = winner["approach"]
        winner_rate = winner["reply_rate"]
        
        # Recommendation 1: Double down on winner
        recommendations.append(
            f"Generate 3 new variations based on '{winner_approach}' pattern"
        )
        
        # Recommendation 2: Eliminate losers
        if losers:
            loser_names = [l["approach"] for l in losers]
            recommendations.append(
                f"Stop using: {', '.join(loser_names)} - consistently underperform"
            )
        
        # Recommendation 3: Test evolved versions
        if winner_rate > 0.4:  # > 40% reply rate
            recommendations.append(
                f"'{winner_approach}' is crushing it - test bolder variations"
            )
        elif winner_rate < 0.2:  # < 20% reply rate
            recommendations.append(
                "Overall performance low - test completely different approaches"
            )
        
        # Recommendation 4: Personalization
        recommendations.append(
            "Add more lead-specific personalization to winning approach"
        )
        
        return recommendations
    
    def identify_winning_patterns(self) -> Dict[str, any]:
        """
        Identify specific patterns in winning messages
        
        Returns:
            Patterns analysis (length, structure, tone, etc.)
        """
        # Load all entries
        entries = self.tracker._load_entries()
        
        if not entries:
            return {"status": "no_data"}
        
        # Separate winners (replied) and losers
        winners = [e for e in entries if e.get("replied", False)]
        losers = [e for e in entries if not e.get("replied", False)]
        
        if not winners:
            return {"status": "no_replies_yet"}
        
        # Analyze patterns
        patterns = {
            "avg_length_winners": self._avg_message_length(winners),
            "avg_length_losers": self._avg_message_length(losers),
            "common_words_winners": self._extract_common_words(winners),
            "winning_approaches": self._count_approaches(winners),
            "losing_approaches": self._count_approaches(losers)
        }
        
        return patterns
    
    def _avg_message_length(self, entries: List[Dict]) -> int:
        """Calculate average message length"""
        if not entries:
            return 0
        lengths = [len(e.get("message", "")) for e in entries]
        return sum(lengths) // len(lengths)
    
    def _extract_common_words(self, entries: List[Dict], top_n: int = 10) -> List[str]:
        """Extract most common words in messages"""
        from collections import Counter
        import re
        
        all_text = " ".join(e.get("message", "") for e in entries)
        words = re.findall(r'\b[a-z]{4,}\b', all_text.lower())
        
        # Filter common words
        stop_words = {"that", "this", "with", "from", "have", "been", "were", "your"}
        words = [w for w in words if w not in stop_words]
        
        counter = Counter(words)
        return [word for word, count in counter.most_common(top_n)]
    
    def _count_approaches(self, entries: List[Dict]) -> Dict[str, int]:
        """Count occurrences of each approach"""
        from collections import Counter
        approaches = [e["approach"] for e in entries]
        return dict(Counter(approaches))
    
    def _save_insights(self, analysis: Dict):
        """Save insights to file"""
        with open(self.insights_file, "w") as f:
            json.dump(analysis, f, indent=2)
    
    def get_latest_insights(self) -> Optional[Dict]:
        """Load latest insights from file"""
        if not self.insights_file.exists():
            return None
        
        with open(self.insights_file, "r") as f:
            return json.load(f)
    
    def generate_report(self, min_sends: int = 10) -> str:
        """Generate human-readable learning report"""
        analysis = self.analyze_results(min_sends)
        
        if analysis.get("status") == "insufficient_data":
            return f"⏳ Not enough data yet. Need {min_sends} sends per variation.\n\nKeep sending messages and check back soon!"
        
        report = "# A/B Test Learning Report\n\n"
        
        # Summary
        report += f"**Analyzed**: {analysis['analyzed_at'][:10]}\n"
        report += f"**Total sends**: {analysis['total_sends']}\n"
        report += f"**Approaches tested**: {analysis['approaches_tested']}\n\n"
        
        # Winner
        winner = analysis["winner"]
        report += "## 🏆 Winner\n\n"
        report += f"**{winner['approach']}**\n"
        report += f"- Reply rate: {winner['reply_rate']*100:.1f}%\n"
        report += f"- Total sends: {winner['send_count']}\n"
        report += f"- Replies: {winner['reply_count']}\n"
        report += f"- Lift vs average: {winner['lift_vs_average']*100:+.1f}%\n\n"
        
        # Insights
        report += "## 💡 Insights\n\n"
        for insight in analysis["insights"]:
            report += f"- {insight}\n"
        report += "\n"
        
        # Recommendations
        report += "## 🎯 Recommendations\n\n"
        for i, rec in enumerate(analysis["recommendations"], 1):
            report += f"{i}. {rec}\n"
        report += "\n"
        
        # Losers
        if analysis["losers"]:
            report += "## ❌ Underperformers\n\n"
            for loser in analysis["losers"]:
                report += f"- **{loser['approach']}**: {loser['reply_rate']*100:.1f}% reply rate\n"
        
        return report


# CLI interface
if __name__ == "__main__":
    import sys
    
    engine = LearningEngine()
    
    print(engine.generate_report(min_sends=5))
