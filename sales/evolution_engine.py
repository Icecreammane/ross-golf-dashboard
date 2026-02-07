#!/usr/bin/env python3
"""
Evolution Engine - Evolve messages based on winning patterns
Generates new variations that combine characteristics of winners
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from sales.learning_engine import LearningEngine
from sales.response_tracker import ResponseTracker

class EvolutionEngine:
    def __init__(self, workspace_root: str = "/Users/clawdbot/clawd"):
        self.workspace = Path(workspace_root)
        self.learning = LearningEngine(workspace_root)
        self.tracker = ResponseTracker(workspace_root)
        self.evolution_log = self.workspace / "sales" / "evolution-log.jsonl"
    
    def evolve_messages(
        self,
        product: str,
        audience: str,
        pain_point: str,
        benefit: str,
        generation: int = 2
    ) -> List[Dict]:
        """
        Generate evolved message variations based on winners
        
        Args:
            product: Product name
            audience: Target audience
            pain_point: Problem solved
            benefit: Main benefit
            generation: Generation number (2, 3, 4...)
        
        Returns:
            List of evolved message variations
        """
        # Get current insights
        insights = self.learning.get_latest_insights()
        
        if not insights:
            return []
        
        winner_approach = insights["winner"]["approach"]
        winner_rate = insights["winner"]["reply_rate"]
        
        # Get actual winning messages
        winning_messages = self._get_winning_messages(winner_approach)
        
        # Generate evolved variations
        evolved = []
        
        # Strategy 1: Amplify winning approach (3 variations)
        for i in range(3):
            msg = self._amplify_winner(
                winner_approach,
                winning_messages,
                product, audience, pain_point, benefit
            )
            evolved.append({
                "variation_id": f"{winner_approach}_evolved_{generation}_{i+1}",
                "approach": f"{winner_approach}_evolved",
                "message": msg,
                "generation": generation,
                "parent_approach": winner_approach,
                "strategy": "amplify_winner",
                "created_at": datetime.now().isoformat()
            })
        
        # Strategy 2: Hybrid approaches (2 variations)
        top_3 = insights.get("insights", [])
        if len(top_3) >= 2:
            for i in range(2):
                msg = self._create_hybrid(
                    winner_approach,
                    winning_messages,
                    product, audience, pain_point, benefit
                )
                evolved.append({
                    "variation_id": f"hybrid_{generation}_{i+1}",
                    "approach": f"{winner_approach}_hybrid",
                    "message": msg,
                    "generation": generation,
                    "parent_approach": winner_approach,
                    "strategy": "hybrid",
                    "created_at": datetime.now().isoformat()
                })
        
        # Strategy 3: Mutate winner (2 variations)
        for i in range(2):
            msg = self._mutate_winner(
                winner_approach,
                winning_messages,
                product, audience, pain_point, benefit
            )
            evolved.append({
                "variation_id": f"{winner_approach}_mutated_{generation}_{i+1}",
                "approach": f"{winner_approach}_mutated",
                "message": msg,
                "generation": generation,
                "parent_approach": winner_approach,
                "strategy": "mutation",
                "created_at": datetime.now().isoformat()
            })
        
        # Strategy 4: Extreme version (1 variation)
        msg = self._create_extreme(
            winner_approach,
            winning_messages,
            product, audience, pain_point, benefit
        )
        evolved.append({
            "variation_id": f"{winner_approach}_extreme_{generation}",
            "approach": f"{winner_approach}_extreme",
            "message": msg,
            "generation": generation,
            "parent_approach": winner_approach,
            "strategy": "extreme",
            "created_at": datetime.now().isoformat()
        })
        
        # Strategy 5: Keep 2 best from previous gen unchanged
        # (Preserve winning formula while testing improvements)
        
        # Log evolution
        self._log_evolution(generation, winner_approach, len(evolved))
        
        return evolved
    
    def _get_winning_messages(self, approach: str) -> List[str]:
        """Get actual messages from winning approach"""
        entries = self.tracker._load_entries()
        
        winning_entries = [
            e for e in entries
            if e["approach"] == approach and e.get("replied", False)
        ]
        
        return [e["message"] for e in winning_entries]
    
    def _amplify_winner(
        self,
        approach: str,
        winning_messages: List[str],
        product: str, audience: str, pain: str, benefit: str
    ) -> str:
        """Amplify what makes the winner work"""
        
        # Patterns by approach
        if approach == "personal_story":
            # Make story more vivid and relatable
            msg = f"Hey,\n\n"
            msg += f"Three months ago, I was drowning in {pain}. Every. Single. Day.\n\n"
            msg += f"Built {product} out of pure frustration. Took 2 weeks.\n\n"
            msg += f"Now? I {benefit}. Zero stress.\n\n"
            msg += f"Other {audience} have been asking about it. Figured you might want in.\n\n"
            msg += "Interested?\n\n- Ross"
            
        elif approach == "question_led":
            # Make question more specific and provocative
            msg = f"Hey,\n\n"
            msg += f"Quick question: How much time did you waste on {pain} last week?\n\n"
            msg += f"I'm guessing 5+ hours. Maybe 10.\n\n"
            msg += f"Built {product} to kill that completely. {benefit.capitalize()} in minutes.\n\n"
            msg += "Worth checking out?\n\n- Ross"
            
        elif approach == "problem_focused":
            # Make problem more urgent and specific
            msg = f"Hey,\n\n"
            msg += f"{audience.title()} waste 10+ hours/week on {pain}.\n\n"
            msg += f"That's 500+ hours/year. On something totally fixable.\n\n"
            msg += f"{product} fixes it. {benefit.capitalize()}. Simple as that.\n\n"
            msg += "Try it?\n\n- Ross"
            
        else:
            # Default amplification - add specificity
            msg = f"Hey,\n\n"
            msg += f"{product} = {benefit}\n\n"
            msg += f"Built specifically for {audience}. Kills {pain} completely.\n\n"
            msg += "Simple. Fast. Works.\n\n"
            msg += "Interested?\n\n- Ross"
        
        return msg
    
    def _create_hybrid(
        self,
        winner_approach: str,
        winning_messages: List[str],
        product: str, audience: str, pain: str, benefit: str
    ) -> str:
        """Combine elements from multiple winning approaches"""
        
        # Hybrid: Personal story + problem focus
        msg = f"Hey,\n\n"
        msg += f"Was talking to a {audience} yesterday. Said they waste 8 hours/week on {pain}.\n\n"
        msg += f"Same problem I had. Built {product} to fix it.\n\n"
        msg += f"Now I {benefit}. They want in too.\n\n"
        msg += "You?\n\n- Ross"
        
        return msg
    
    def _mutate_winner(
        self,
        winner_approach: str,
        winning_messages: List[str],
        product: str, audience: str, pain: str, benefit: str
    ) -> str:
        """Small mutations to winning formula"""
        
        # Mutation: Change hook, keep structure
        hooks = [
            "Quick thing:",
            "Saw your work -",
            "Random question:",
            "So here's the deal:",
            "Real talk:"
        ]
        
        hook = random.choice(hooks)
        
        msg = f"Hey,\n\n"
        msg += f"{hook}\n\n"
        msg += f"{product} for {audience}. {benefit.capitalize()}.\n\n"
        msg += f"Solves {pain}. Fast.\n\n"
        msg += "In?\n\n- Ross"
        
        return msg
    
    def _create_extreme(
        self,
        winner_approach: str,
        winning_messages: List[str],
        product: str, audience: str, pain: str, benefit: str
    ) -> str:
        """Create extreme/bold version of winner"""
        
        # Ultra-short, ultra-direct
        msg = f"Hey,\n\n"
        msg += f"{product}.\n\n"
        msg += f"{benefit.capitalize()}. Zero {pain}.\n\n"
        msg += f"Yes or no?\n\n"
        msg += "- Ross"
        
        return msg
    
    def _log_evolution(self, generation: int, parent_approach: str, variations_count: int):
        """Log evolution event"""
        entry = {
            "timestamp": int(datetime.now().timestamp()),
            "datetime": datetime.now().isoformat(),
            "generation": generation,
            "parent_approach": parent_approach,
            "variations_generated": variations_count
        }
        
        with open(self.evolution_log, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def should_evolve(self, min_sends: int = 50) -> Dict[str, any]:
        """
        Determine if it's time to evolve messages
        
        Args:
            min_sends: Minimum total sends before evolving
        
        Returns:
            Decision with reasoning
        """
        insights = self.learning.get_latest_insights()
        
        if not insights:
            return {
                "should_evolve": False,
                "reason": "No data yet - collect baseline first"
            }
        
        total_sends = insights.get("total_sends", 0)
        winner_rate = insights["winner"]["reply_rate"]
        
        if total_sends < min_sends:
            return {
                "should_evolve": False,
                "reason": f"Only {total_sends} sends - need {min_sends} for reliable evolution"
            }
        
        if winner_rate < 0.15:  # < 15% reply rate
            return {
                "should_evolve": True,
                "reason": "Low performance - need new approaches",
                "urgency": "high"
            }
        
        if winner_rate > 0.4:  # > 40% reply rate
            return {
                "should_evolve": True,
                "reason": "Winner is crushing - test bolder variations",
                "urgency": "medium"
            }
        
        return {
            "should_evolve": True,
            "reason": f"Sufficient data ({total_sends} sends) - ready to evolve",
            "urgency": "normal"
        }


# CLI interface
if __name__ == "__main__":
    import sys
    
    engine = EvolutionEngine()
    
    # Check if should evolve
    decision = engine.should_evolve()
    
    print(f"🧬 Evolution Check\n")
    print(f"Should evolve: {decision['should_evolve']}")
    print(f"Reason: {decision['reason']}")
    
    if decision["should_evolve"]:
        print("\n🚀 Generating evolved variations...\n")
        
        evolved = engine.evolve_messages(
            product="FitTrack",
            audience="indie makers",
            pain_point="forget to track workouts",
            benefit="never miss a workout",
            generation=2
        )
        
        print(f"✅ Generated {len(evolved)} evolved variations\n")
        
        for var in evolved[:3]:  # Show first 3
            print(f"{'='*60}")
            print(f"{var['approach']} (Gen {var['generation']}, {var['strategy']})")
            print(f"{'='*60}")
            print(var['message'])
            print()
