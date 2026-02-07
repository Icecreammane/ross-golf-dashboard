#!/usr/bin/env python3
"""
Response Generator - Generate natural voice responses
Converts data into conversational, contextual responses
"""

from typing import Dict, Any, Optional
from datetime import datetime

class ResponseGenerator:
    def __init__(self):
        self.personality = "direct, energetic, motivating"
    
    def generate(
        self,
        intent: str,
        result: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate natural language response
        
        Args:
            intent: Command intent (from parser)
            result: Execution result (from router)
            context: Additional context (time of day, current goals, etc.)
        
        Returns:
            Natural language response string
        """
        # Route to specific generator
        generators = {
            "get_mrr": self._generate_mrr_response,
            "get_revenue": self._generate_revenue_response,
            "get_progress": self._generate_progress_response,
            "get_next_task": self._generate_next_task_response,
            "check_launch": self._generate_launch_response,
            "activate_sales_mode": self._generate_sales_mode_response,
            "activate_build_mode": self._generate_build_mode_response,
            "log_workout": self._generate_workout_response,
            "log_food": self._generate_food_response,
            "log_win": self._generate_win_response,
            "check_accountability": self._generate_accountability_response
        }
        
        generator = generators.get(intent, self._generate_fallback)
        return generator(result, context or {})
    
    def _generate_mrr_response(self, result: Dict, context: Dict) -> str:
        """Generate MRR status response"""
        # Placeholder - would integrate with actual Stripe data
        mrr = result.get("mrr", 47)
        goal = 50
        progress = (mrr / goal) * 100
        
        response = f"Currently ${mrr} MRR. "
        
        if mrr < goal:
            remaining = goal - mrr
            response += f"${remaining} to hit your first ${goal}. "
            response += f"That's {progress:.0f}% there. "
            
            if progress > 90:
                response += "So close! One more push."
            elif progress > 75:
                response += "Almost there. Keep going."
            else:
                response += "Keep building."
        else:
            response += f"You crushed the ${goal} goal! 🎉"
        
        return response
    
    def _generate_revenue_response(self, result: Dict, context: Dict) -> str:
        """Generate revenue response"""
        revenue = result.get("total_revenue", 0)
        
        if revenue == 0:
            return "No revenue yet. But that's about to change. What are you building today?"
        
        return f"Total revenue: ${revenue}. Every dollar counts. Keep shipping."
    
    def _generate_progress_response(self, result: Dict, context: Dict) -> str:
        """Generate progress check response"""
        # Get today's commitment from context or result
        commitment = context.get("commitment", "your commitment")
        deadline = context.get("deadline", "deadline")
        
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        
        response = f"It's {time_str}. "
        response += f"Today's commitment: {commitment}. "
        
        # Check if on track (would integrate with actual tracking)
        hours_left = 12 - now.hour  # Assume noon deadline
        
        if hours_left > 2:
            response += f"You've got {hours_left} hours. You're on track."
        elif hours_left > 0:
            response += f"You've got {hours_left} hours left. Cutting it close but doable."
        else:
            response += "Deadline passed. What's the move?"
        
        return response
    
    def _generate_next_task_response(self, result: Dict, context: Dict) -> str:
        """Generate next task guidance"""
        # Would integrate with actual task system
        return "Your next priority: Ship something that makes money. What's the fastest path to revenue today?"
    
    def _generate_launch_response(self, result: Dict, context: Dict) -> str:
        """Generate launch status response"""
        return "Launch tracking integration pending. For now: Are you shipping or stalling?"
    
    def _generate_sales_mode_response(self, result: Dict, context: Dict) -> str:
        """Generate sales mode activation response"""
        leads = result.get("leads_to_find", 5)
        
        response = f"Sales mode activated. Finding {leads} perfect leads. "
        response += "Time to make money. Let's hunt."
        
        return response
    
    def _generate_build_mode_response(self, result: Dict, context: Dict) -> str:
        """Generate build mode activation response"""
        return "Build mode activated. Ship fast, ship often. What's the MVP today?"
    
    def _generate_workout_response(self, result: Dict, context: Dict) -> str:
        """Generate workout logging response"""
        description = result.get("logged", "workout")
        
        responses = [
            f"✅ {description} logged. Building strength builds everything else.",
            f"✅ {description} tracked. Physical progress = mental progress.",
            f"✅ Got it. {description} done. You're winning today.",
            f"✅ {description} logged. Discipline in the gym = discipline in business."
        ]
        
        # Rotate based on time
        idx = datetime.now().hour % len(responses)
        return responses[idx]
    
    def _generate_food_response(self, result: Dict, context: Dict) -> str:
        """Generate food logging response"""
        description = result.get("logged", "meal")
        
        return f"✅ {description} logged. Fuel the machine."
    
    def _generate_win_response(self, result: Dict, context: Dict) -> str:
        """Generate win logging response"""
        description = result.get("logged", "win")
        
        responses = [
            f"🎉 {description}! That's what I'm talking about. Keep stacking wins.",
            f"✅ {description} logged. Momentum builds on momentum.",
            f"💪 {description}! Another one. You're on fire.",
            f"🚀 {description}! This is how you build. One win at a time."
        ]
        
        idx = datetime.now().second % len(responses)
        return responses[idx]
    
    def _generate_accountability_response(self, result: Dict, context: Dict) -> str:
        """Generate accountability check response"""
        risk_level = result.get("risk_level", "unknown")
        
        if risk_level == "low":
            return "You're locked in. No procrastination detected. Keep this energy."
        elif risk_level == "medium":
            return "Watch it. You're entering procrastination territory. Stay focused."
        elif risk_level == "high":
            return "🚨 High risk detected. You're about to scroll. Don't. Get back to work NOW."
        else:
            return "Can't read your patterns yet. Keep logging activities."
    
    def _generate_fallback(self, result: Dict, context: Dict) -> str:
        """Fallback for unknown intents"""
        return "I heard you, but I'm not sure how to handle that yet. Try asking differently?"
    
    def add_context_flavor(self, response: str, context: Dict) -> str:
        """Add contextual flavor based on time, energy, etc."""
        hour = datetime.now().hour
        
        # Morning energy
        if 5 <= hour < 12:
            if "locked in" in response or "on track" in response:
                response += " Morning energy is peak. Use it."
        
        # Afternoon slump
        elif 14 <= hour < 16:
            if "procrastination" in response.lower():
                response += " Afternoon slump is real. Push through."
        
        # Evening wrap
        elif 18 <= hour < 22:
            if "win" in response.lower() or "done" in response.lower():
                response += " Finish strong."
        
        return response


# CLI interface
if __name__ == "__main__":
    import sys
    from voice.command_parser import VoiceCommandParser
    from voice.mode_router import ModeRouter
    
    if len(sys.argv) < 2:
        print("Usage: python response_generator.py <command>")
        sys.exit(1)
    
    text = " ".join(sys.argv[1:])
    
    # Parse
    parser = VoiceCommandParser()
    parsed = parser.parse(text)
    
    if not parsed:
        print("❌ Could not parse command")
        sys.exit(1)
    
    # Route
    router = ModeRouter()
    routing = router.route(parsed)
    result = router.execute(routing)
    
    # Generate response
    generator = ResponseGenerator()
    
    if result["success"]:
        response = generator.generate(parsed.intent, result["result"])
        response = generator.add_context_flavor(response, {})
        print(f"\n🎙️  Jarvis: {response}\n")
    else:
        print(f"❌ Error: {result['error']}")
