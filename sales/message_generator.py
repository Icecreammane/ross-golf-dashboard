#!/usr/bin/env python3
"""
Message Generator - Create message variations for A/B testing
Generates 10 different approaches for each outreach message
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class MessageGenerator:
    def __init__(self, workspace_root: str = "/Users/clawdbot/clawd"):
        self.workspace = Path(workspace_root)
        self.variations_file = self.workspace / "sales" / "message-variations.json"
        
        # Message templates by approach
        self.approaches = {
            "direct": self._generate_direct,
            "personal_story": self._generate_personal_story,
            "question_led": self._generate_question_led,
            "problem_focused": self._generate_problem_focused,
            "solution_focused": self._generate_solution_focused,
            "social_proof": self._generate_social_proof,
            "scarcity": self._generate_scarcity,
            "curiosity": self._generate_curiosity,
            "compliment": self._generate_compliment,
            "value_prop": self._generate_value_prop
        }
    
    def generate_variations(
        self,
        product: str,
        target_audience: str,
        pain_point: str,
        benefit: str,
        lead_context: Optional[Dict] = None
    ) -> List[Dict[str, any]]:
        """
        Generate 10 message variations for A/B testing
        
        Args:
            product: Product name
            target_audience: Who it's for
            pain_point: Problem it solves
            benefit: Main benefit
            lead_context: Additional context about this specific lead
        
        Returns:
            List of message variations with metadata
        """
        variations = []
        
        for approach_name, generator in self.approaches.items():
            message = generator(product, target_audience, pain_point, benefit, lead_context or {})
            
            variations.append({
                "variation_id": f"{approach_name}_{datetime.now().strftime('%Y%m%d')}",
                "approach": approach_name,
                "message": message,
                "created_at": datetime.now().isoformat(),
                "generation": 1  # First generation
            })
        
        return variations
    
    # Individual approach generators
    
    def _generate_direct(self, product, audience, pain, benefit, context) -> str:
        lead_name = context.get("name", "there")
        
        msg = f"Hey {lead_name},\n\n"
        msg += f"I built {product} - {benefit}.\n\n"
        msg += f"Built for {audience} who {pain}.\n\n"
        msg += "Interested?\n\n"
        msg += "- Ross"
        
        return msg
    
    def _generate_personal_story(self, product, audience, pain, benefit, context) -> str:
        lead_name = context.get("name", "there")
        
        msg = f"Hey {lead_name},\n\n"
        msg += f"I was struggling with {pain} for months.\n\n"
        msg += f"Built {product} to solve it. Now I {benefit}.\n\n"
        msg += f"Figured other {audience} might want the same.\n\n"
        msg += "Sound useful?\n\n"
        msg += "- Ross"
        
        return msg
    
    def _generate_question_led(self, product, audience, pain, benefit, context) -> str:
        lead_name = context.get("name", "there")
        
        msg = f"Hey {lead_name},\n\n"
        msg += f"Quick question: Do you {pain}?\n\n"
        msg += f"Built {product} specifically for {audience}. {benefit.capitalize()}.\n\n"
        msg += "Worth a look?\n\n"
        msg += "- Ross"
        
        return msg
    
    def _generate_problem_focused(self, product, audience, pain, benefit, context) -> str:
        lead_name = context.get("name", "there")
        
        msg = f"Hey {lead_name},\n\n"
        msg += f"Most {audience} waste hours on {pain}.\n\n"
        msg += f"{product} fixes that. {benefit.capitalize()}.\n\n"
        msg += "No fluff. Just results.\n\n"
        msg += "Want in?\n\n"
        msg += "- Ross"
        
        return msg
    
    def _generate_solution_focused(self, product, audience, pain, benefit, context) -> str:
        lead_name = context.get("name", "there")
        
        msg = f"Hey {lead_name},\n\n"
        msg += f"{product} = {benefit}\n\n"
        msg += f"Built for {audience}. Solves {pain} in minutes, not hours.\n\n"
        msg += "Simple. Fast. Effective.\n\n"
        msg += "Try it?\n\n"
        msg += "- Ross"
        
        return msg
    
    def _generate_social_proof(self, product, audience, pain, benefit, context) -> str:
        lead_name = context.get("name", "there")
        user_count = context.get("users", "10")
        
        msg = f"Hey {lead_name},\n\n"
        msg += f"{user_count} {audience} already using {product}.\n\n"
        msg += f"They all had the same problem: {pain}.\n\n"
        msg += f"Now they {benefit}.\n\n"
        msg += "You in?\n\n"
        msg += "- Ross"
        
        return msg
    
    def _generate_scarcity(self, product, audience, pain, benefit, context) -> str:
        lead_name = context.get("name", "there")
        
        msg = f"Hey {lead_name},\n\n"
        msg += f"Launching {product} to first {audience} this week.\n\n"
        msg += f"Solves {pain}. {benefit.capitalize()}.\n\n"
        msg += "Early access closing soon. Want a spot?\n\n"
        msg += "- Ross"
        
        return msg
    
    def _generate_curiosity(self, product, audience, pain, benefit, context) -> str:
        lead_name = context.get("name", "there")
        
        msg = f"Hey {lead_name},\n\n"
        msg += f"Found a way to {benefit} without {pain}.\n\n"
        msg += f"Built it into {product}.\n\n"
        msg += f"Most {audience} don't know this exists yet.\n\n"
        msg += "Curious?\n\n"
        msg += "- Ross"
        
        return msg
    
    def _generate_compliment(self, product, audience, pain, benefit, context) -> str:
        lead_name = context.get("name", "there")
        lead_achievement = context.get("achievement", "your work")
        
        msg = f"Hey {lead_name},\n\n"
        msg += f"Saw {lead_achievement} - impressive.\n\n"
        msg += f"I built {product} for {audience} like you. "
        msg += f"Helps with {pain}. {benefit.capitalize()}.\n\n"
        msg += "Think you'd find it useful?\n\n"
        msg += "- Ross"
        
        return msg
    
    def _generate_value_prop(self, product, audience, pain, benefit, context) -> str:
        lead_name = context.get("name", "there")
        
        msg = f"Hey {lead_name},\n\n"
        msg += f"{product} for {audience}:\n\n"
        msg += f"❌ Stop: {pain}\n"
        msg += f"✅ Start: {benefit}\n\n"
        msg += "That simple.\n\n"
        msg += "Interested?\n\n"
        msg += "- Ross"
        
        return msg
    
    def pick_variation(
        self,
        variations: List[Dict],
        strategy: str = "random"
    ) -> Dict:
        """
        Pick which variation to send
        
        Args:
            variations: List of variations
            strategy: "random" (balanced) or "weighted" (favor winners)
        
        Returns:
            Selected variation
        """
        if strategy == "random":
            return random.choice(variations)
        
        # Weighted would integrate with learning engine results
        # For now, random is good for initial data collection
        return random.choice(variations)
    
    def personalize_message(
        self,
        message: str,
        lead_context: Dict
    ) -> str:
        """
        Personalize a message with lead-specific details
        
        Args:
            message: Template message
            lead_context: Lead details (name, company, etc.)
        
        Returns:
            Personalized message
        """
        # Replace placeholders
        personalized = message
        
        for key, value in lead_context.items():
            placeholder = f"{{{key}}}"
            if placeholder in personalized:
                personalized = personalized.replace(placeholder, str(value))
        
        return personalized


# CLI interface
if __name__ == "__main__":
    import sys
    
    generator = MessageGenerator()
    
    # Example usage
    product = "FitTrack"
    audience = "indie makers"
    pain = "forget to track workouts"
    benefit = "never miss a workout again"
    
    context = {
        "name": "Alex",
        "achievement": "your SaaS journey",
        "users": "15"
    }
    
    print("🎯 Generating 10 message variations...\n")
    
    variations = generator.generate_variations(product, audience, pain, benefit, context)
    
    for i, var in enumerate(variations, 1):
        print(f"{'='*60}")
        print(f"Variation {i}: {var['approach'].upper()}")
        print(f"{'='*60}")
        print(var['message'])
        print()
    
    print(f"\n✅ Generated {len(variations)} variations for A/B testing")
