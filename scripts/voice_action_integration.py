#!/usr/bin/env python3
"""
Integration helper for main agent to use voice action detector.

Usage in main agent:
    from scripts.voice_action_integration import process_voice_message
    
    result = process_voice_message(transcript)
    if result['auto_executed']:
        return result['message']
    elif result['needs_confirmation']:
        return result['confirmation_prompt']
    else:
        # Continue with normal LLM response
        pass
"""

from voice_action_detector import VoiceActionDetector
from typing import Dict, Any

def process_voice_message(transcript: str) -> Dict[str, Any]:
    """
    Process voice message and return action result.
    
    Returns:
        {
            'auto_executed': bool,
            'needs_confirmation': bool,
            'intent': str,
            'confidence': int,
            'message': str (if executed),
            'confirmation_prompt': str (if needs confirm),
            'data': dict (parsed data)
        }
    """
    detector = VoiceActionDetector()
    intent, confidence, data = detector.detect_intent(transcript)
    
    result = {
        'auto_executed': False,
        'needs_confirmation': False,
        'intent': intent,
        'confidence': confidence,
        'data': data
    }
    
    # Question intent - never auto-execute
    if intent == 'question':
        result['message'] = '(respond to question normally)'
        return result
    
    # Unknown intent - respond normally
    if intent == 'unknown':
        return result
    
    # High confidence - auto-execute
    if confidence >= detector.THRESHOLD_AUTO:
        exec_result = detector.execute_action(intent, data)
        result['auto_executed'] = True
        result['message'] = _get_response_message(intent, exec_result, data)
        return result
    
    # Medium confidence - ask for confirmation
    if confidence >= detector.THRESHOLD_CONFIRM:
        result['needs_confirmation'] = True
        result['confirmation_prompt'] = _get_confirmation_prompt(intent, confidence)
        return result
    
    # Low confidence - respond normally
    return result


def _get_response_message(intent: str, exec_result: Dict, data: Dict) -> str:
    """Generate enthusiastic response message after successful execution."""
    
    if intent == 'workout':
        responses = [
            "✅ Workout logged! 💪",
            "✅ Logged! Beast mode activated 🔥",
            "✅ Workout logged! Let's gooo 💯",
            "✅ Gains tracked! 💪🔥"
        ]
        # Count sets if available
        if 'reps' in data and len(data['reps']) > 20:
            return f"✅ Workout logged! {len(data['reps'])} sets 🔥"
        return responses[0]
    
    elif intent == 'food':
        responses = [
            "✅ Food logged! 🍽️",
            "✅ Nutrition tracked! Fueling up 💪",
            "✅ Logged! Feeding the machine 🔥",
            "✅ Food logged! Gains incoming 💪"
        ]
        # Check for specific foods
        if 'food_items' in data:
            if 'chili' in data['food_items']:
                return "✅ Food logged! Chili = gains 🔥"
            if 'protein' in data['food_items']:
                return "✅ Food logged! Protein = growth 💪"
        return responses[0]
    
    elif intent == 'win':
        responses = [
            "✅ Win logged! 🎉",
            "✅ Win logged! Let's goooo 🚀",
            "✅ Achievement unlocked! 🏆",
            "✅ Win logged! Crushing it! 🔥"
        ]
        # Check for milestone wins
        text = data.get('raw_text', '').lower()
        if 'first' in text:
            return "✅ Win logged! 🎉 First of many! 🚀"
        if 'customer' in text or 'client' in text:
            return "✅ Win logged! 🎉 Revenue incoming! 💰"
        if 'shipped' in text or 'launched' in text:
            return "✅ Win logged! 🎉 Shipped = progress! 🚀"
        return responses[0]
    
    elif intent == 'task':
        responses = [
            "✅ Task added to priorities! 📝",
            "✅ Added to your list! Won't forget 👍",
            "✅ Task saved! I got you 👊",
            "✅ Added to priorities! On it! ✓"
        ]
        return responses[0]
    
    return "✅ Logged!"


def _get_confirmation_prompt(intent: str, confidence: int) -> str:
    """Generate confirmation prompt for medium-confidence detections."""
    
    prompts = {
        'workout': "Looks like a workout - log it? (Say yes/no)",
        'food': "Looks like food - log it? (Yes/no)",
        'win': "Log this as a win? (Yes/no)",
        'task': "Add this to your priorities? (Yes/no)"
    }
    
    return prompts.get(intent, f"Log this as {intent}? ({confidence}% confident)")


# Example CLI usage
def main():
    """Test the integration helper."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: voice_action_integration.py <transcript>")
        sys.exit(1)
    
    transcript = ' '.join(sys.argv[1:])
    result = process_voice_message(transcript)
    
    print(f"\nIntent: {result['intent']} ({result['confidence']}%)")
    
    if result['auto_executed']:
        print(f"[AUTO-EXECUTED] {result['message']}")
    elif result['needs_confirmation']:
        print(f"[NEEDS CONFIRM] {result['confirmation_prompt']}")
    else:
        print("[RESPOND NORMALLY]")


if __name__ == '__main__':
    main()
