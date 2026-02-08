#!/usr/bin/env python3
"""
Smart Suggestions
Filter ideas through preference engine before suggesting
Only suggest 7+ rated ideas
"""

import sys
from pathlib import Path

# Add scripts to path
sys.path.append(str(Path.home() / "clawd" / "scripts"))

from preference_engine import PreferenceEngine

class SmartSuggester:
    """Smart suggestion system using preference engine"""
    
    def __init__(self, min_score=7.0):
        self.engine = PreferenceEngine()
        self.min_score = min_score
    
    def filter_ideas(self, ideas):
        """
        Filter list of ideas through preference engine
        
        Args:
            ideas: List of dicts with 'title' and 'description'
        
        Returns:
            List of filtered ideas with scores
        """
        filtered = []
        
        for idea in ideas:
            title = idea.get("title", "")
            desc = idea.get("description", "")
            full_text = f"{title}. {desc}"
            
            score, explanation = self.engine.should_suggest(full_text, desc)
            
            if score >= self.min_score:
                filtered.append({
                    **idea,
                    "score": score,
                    "explanation": explanation,
                    "recommended": True
                })
        
        # Sort by score (highest first)
        filtered.sort(key=lambda x: x["score"], reverse=True)
        
        return filtered
    
    def get_top_n(self, ideas, n=3):
        """Get top N ideas"""
        filtered = self.filter_ideas(ideas)
        return filtered[:n]
    
    def format_suggestions(self, ideas, show_scores=False):
        """Format filtered ideas for display"""
        if not ideas:
            return "No ideas match your preferences. Need to expand search criteria."
        
        output = []
        
        for i, idea in enumerate(ideas, 1):
            title = idea.get("title", "Untitled")
            desc = idea.get("description", "")
            score = idea.get("score", 0)
            
            output.append(f"**Option {i}: {title}**")
            if desc:
                output.append(f"{desc}")
            
            if show_scores:
                output.append(f"*Match score: {score:.1f}/10*")
                if "explanation" in idea:
                    output.append(f"*Why: {idea['explanation'].split(chr(10))[0]}*")  # First line only
            
            output.append("")  # Blank line
        
        return "\n".join(output)
    
    def explain_why_filtered(self, ideas):
        """Explain why some ideas were filtered out"""
        all_ideas = []
        
        for idea in ideas:
            title = idea.get("title", "")
            desc = idea.get("description", "")
            full_text = f"{title}. {desc}"
            
            score, explanation = self.engine.should_suggest(full_text, desc)
            
            all_ideas.append({
                "title": title,
                "score": score,
                "passed": score >= self.min_score
            })
        
        filtered_out = [i for i in all_ideas if not i["passed"]]
        
        if not filtered_out:
            return "All ideas passed the filter!"
        
        output = [f"Filtered out {len(filtered_out)} ideas (score < {self.min_score}):"]
        for idea in filtered_out:
            output.append(f"  ❌ {idea['title']} (score: {idea['score']:.1f})")
        
        return "\n".join(output)


def test_suggester():
    """Test the smart suggester"""
    suggester = SmartSuggester(min_score=7.0)
    
    # Sample ideas
    test_ideas = [
        {
            "title": "Gamified Workout Tracker",
            "description": "Track workouts with streak counter, points, and level-ups. Competitive leaderboard with friends. Visual progress charts."
        },
        {
            "title": "Philosophical Journal",
            "description": "Deep reflection app for exploring life's big questions. Guided prompts for existential thinking. No metrics, just thoughts."
        },
        {
            "title": "Revenue Dashboard v2",
            "description": "Real-time $ tracker. Every action = money value. Shows path to $500 MRR goal. Clear progress bars."
        },
        {
            "title": "Quantum Computing Research Tool",
            "description": "Study quantum mechanics theory. Academic paper organizer. Complex mathematical notation support."
        },
        {
            "title": "Quick Win Generator",
            "description": "Suggests fast tasks under 30 min. Track completion rate. Gamified streak system. Mobile-friendly."
        },
        {
            "title": "Abstract Art Mood Board",
            "description": "Create emotional visual collages. Explore feelings through color and shape. No structure, pure expression."
        }
    ]
    
    print("=" * 70)
    print("🧠 SMART SUGGESTION FILTER TEST")
    print("=" * 70)
    print(f"Minimum score: {suggester.min_score}/10")
    print()
    
    # Filter ideas
    filtered = suggester.filter_ideas(test_ideas)
    
    print(f"📊 Results: {len(filtered)}/{len(test_ideas)} ideas passed")
    print()
    
    if filtered:
        print("✅ RECOMMENDED:")
        print()
        for idea in filtered:
            print(f"   {idea['title']}")
            print(f"   Score: {idea['score']:.1f}/10")
            print(f"   {idea['explanation'].split(chr(10))[0]}")  # First line
            print()
    
    # Show filtered out
    print(suggester.explain_why_filtered(test_ideas))
    print()
    
    # Format for user
    print("=" * 70)
    print("📋 FORMATTED FOR ROSS:")
    print("=" * 70)
    print()
    print(suggester.format_suggestions(filtered))


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_suggester()
    else:
        print("Usage: python3 smart_suggest.py test")
        print()
        print("Or import and use SmartSuggester class:")
        print()
        print("from smart_suggest import SmartSuggester")
        print("suggester = SmartSuggester(min_score=7.0)")
        print("filtered = suggester.filter_ideas(ideas)")


if __name__ == "__main__":
    main()
