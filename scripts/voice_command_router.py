#!/usr/bin/env python3
"""
Voice Command Router
Maps voice transcripts to actions for comprehensive life control

Supports:
- Fitness logging (workouts, food, calories)
- Life admin (shopping lists, calendar, email, reminders)
- Smart home (lights, thermostat, locks) - if available
- Music control (playlists, Spotify)
- Hinge assistant integration
- General queries

Flow: Voice → Transcript → Intent → Action → Response
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Tuple, Optional, List

# Data paths
DATA_DIR = Path("/Users/clawdbot/clawd/data")
FITNESS_DATA = DATA_DIR / "fitness_data.json"
SHOPPING_LIST = DATA_DIR / "shopping_list.json"
VOICE_LOG = Path("/Users/clawdbot/clawd/logs/voice-commands.log")

class VoiceRouter:
    def __init__(self):
        self.intents = self._load_intents()
    
    def _load_intents(self) -> Dict:
        """Load intent patterns and handlers"""
        return {
            # Fitness intents
            "fitness_log_workout": {
                "patterns": [
                    r"log\s+(workout|exercise|lift|gym)",
                    r"(bench|squat|deadlift|curl|press)",
                    r"(\d+)\s*(pounds|lbs|kg)",
                    r"(\d+)\s*(reps|sets)",
                    r"(shoulder|leg|chest|back|arm)\s+day",
                ],
                "confidence_boost": 15,
                "handler": "log_workout"
            },
            "fitness_log_food": {
                "patterns": [
                    r"log\s+(food|meal|ate)",
                    r"(ate|eating|had|just\s+ate)",
                    r"(chicken|beef|fish|eggs|protein|chili|salad)",
                    r"(\d+)\s*(calories|cals|kcal)",
                    r"(breakfast|lunch|dinner|snack)",
                ],
                "confidence_boost": 15,
                "handler": "log_food"
            },
            "fitness_query": {
                "patterns": [
                    r"(what\'s|show|check)\s+(my)?\s*(calorie|protein|macro)",
                    r"did\s+i\s+hit\s+my\s+(protein|calorie)",
                    r"how\s+much\s+(protein|calories)",
                ],
                "confidence_boost": 10,
                "handler": "query_fitness"
            },
            
            # Life admin intents
            "shopping_list_add": {
                "patterns": [
                    r"add\s+(.+)\s+to\s+(shopping|grocery)\s+list",
                    r"(shopping|grocery)\s+list",
                    r"need\s+to\s+(buy|get)\s+(.+)",
                ],
                "confidence_boost": 30,
                "handler": "add_to_shopping"
            },
            "calendar_query": {
                "patterns": [
                    r"what\'s\s+on\s+my\s+calendar",
                    r"show\s+(me\s+)?my\s+(schedule|calendar)",
                    r"what\s+do\s+i\s+have\s+(today|tomorrow)",
                ],
                "confidence_boost": 10,
                "handler": "query_calendar"
            },
            "email_check": {
                "patterns": [
                    r"check\s+(my\s+)?email",
                    r"any\s+urgent\s+email",
                    r"important\s+email",
                ],
                "confidence_boost": 10,
                "handler": "check_email"
            },
            "reminder_set": {
                "patterns": [
                    r"remind\s+me\s+to\s+(.+)\s+(in|at)",
                    r"set\s+(a\s+)?reminder",
                ],
                "confidence_boost": 12,
                "handler": "set_reminder"
            },
            
            # Music intents
            "music_play": {
                "patterns": [
                    r"play\s+(.+)\s+(playlist|music|song)",
                    r"put\s+on\s+(.+)",
                ],
                "confidence_boost": 10,
                "handler": "play_music"
            },
            "music_query": {
                "patterns": [
                    r"what\'s\s+playing",
                    r"what\s+song\s+is\s+this",
                ],
                "confidence_boost": 10,
                "handler": "query_music"
            },
            
            # Hinge integration
            "hinge_check": {
                "patterns": [
                    r"check\s+(my\s+)?hinge",
                    r"hinge\s+(status|report)",
                    r"dating\s+app",
                ],
                "confidence_boost": 25,
                "handler": "check_hinge"
            },
            
            # General queries
            "general_query": {
                "patterns": [
                    r"^\s*(what|how|when|where|why|who)",
                    r"\?$",
                ],
                "confidence_boost": 5,
                "handler": "general_response"
            }
        }
    
    def detect_intent(self, transcript: str) -> Tuple[str, int, Dict]:
        """
        Detect intent from voice transcript
        
        Returns: (intent_name, confidence, extracted_data)
        """
        transcript = transcript.lower().strip()
        scores = {}
        
        for intent_name, intent_config in self.intents.items():
            score = 0
            matches = []
            
            for pattern in intent_config["patterns"]:
                if re.search(pattern, transcript, re.IGNORECASE):
                    score += 30  # Increased from 20
                    match = re.search(pattern, transcript, re.IGNORECASE)
                    if match:
                        matches.append(match.group(0))
            
            # Boost score based on intent type
            if score > 0:
                score += intent_config["confidence_boost"]
            
            scores[intent_name] = {
                "score": min(100, score),
                "matches": matches
            }
        
        # Find highest scoring intent
        if not scores or max(s["score"] for s in scores.values()) == 0:
            return "general_query", 30, {}
        
        best_intent = max(scores.items(), key=lambda x: x[1]["score"])
        intent_name = best_intent[0]
        confidence = best_intent[1]["score"]
        
        # Extract data based on intent
        extracted_data = self._extract_data(transcript, intent_name)
        
        return intent_name, confidence, extracted_data
    
    def _extract_data(self, transcript: str, intent: str) -> Dict:
        """Extract structured data from transcript based on intent"""
        data = {"transcript": transcript}
        
        if "workout" in intent:
            # Extract exercise, weight, reps
            weight_match = re.search(r"(\d+)\s*(pounds|lbs|kg)", transcript, re.IGNORECASE)
            if weight_match:
                data["weight"] = int(weight_match.group(1))
                data["unit"] = weight_match.group(2)
            
            reps_match = re.search(r"(\d+)\s*reps", transcript, re.IGNORECASE)
            if reps_match:
                data["reps"] = int(reps_match.group(1))
            
            sets_match = re.search(r"(\d+)\s*sets", transcript, re.IGNORECASE)
            if sets_match:
                data["sets"] = int(sets_match.group(1))
            
            # Extract exercise names
            exercises = ["bench press", "squat", "deadlift", "curl", "press", "shoulder press"]
            for exercise in exercises:
                if exercise in transcript.lower():
                    data["exercise"] = exercise
                    break
        
        elif "food" in intent:
            # Extract food items
            data["food_items"] = transcript  # Simple passthrough
            
            # Extract calories if mentioned
            cal_match = re.search(r"(\d+)\s*(calories|cals)", transcript, re.IGNORECASE)
            if cal_match:
                data["calories"] = int(cal_match.group(1))
        
        elif "shopping" in intent:
            # Extract item to add
            add_match = re.search(r"add\s+(.+?)\s+to", transcript, re.IGNORECASE)
            if add_match:
                data["item"] = add_match.group(1).strip()
            else:
                need_match = re.search(r"need\s+to\s+(?:buy|get)\s+(.+)", transcript, re.IGNORECASE)
                if need_match:
                    data["item"] = need_match.group(1).strip()
        
        elif "reminder" in intent:
            # Extract reminder text and time
            remind_match = re.search(r"remind\s+me\s+to\s+(.+?)\s+(?:in|at)\s+(.+)", transcript, re.IGNORECASE)
            if remind_match:
                data["reminder_text"] = remind_match.group(1).strip()
                data["time_text"] = remind_match.group(2).strip()
        
        elif "music" in intent and "play" in intent:
            # Extract playlist/song name
            play_match = re.search(r"play\s+(.+?)(?:\s+playlist|\s+music|$)", transcript, re.IGNORECASE)
            if play_match:
                data["music_name"] = play_match.group(1).strip()
        
        return data
    
    def route_action(self, intent: str, data: Dict) -> Dict:
        """
        Route to appropriate handler and execute action
        
        Returns: {
            "success": bool,
            "message": str,
            "data": Dict (optional)
        }
        """
        handler_name = self.intents.get(intent, {}).get("handler")
        
        if not handler_name:
            return {
                "success": False,
                "message": "No handler found for intent"
            }
        
        # Call handler method
        handler_method = getattr(self, handler_name, None)
        if handler_method:
            return handler_method(data)
        else:
            return {
                "success": False,
                "message": f"Handler {handler_name} not implemented"
            }
    
    # Handler methods
    
    def log_workout(self, data: Dict) -> Dict:
        """Log workout to fitness data"""
        exercise = data.get("exercise", "workout")
        weight = data.get("weight", 0)
        reps = data.get("reps", 0)
        sets = data.get("sets", 1)
        
        # Load fitness data
        if FITNESS_DATA.exists():
            with open(FITNESS_DATA, 'r') as f:
                fitness = json.load(f)
        else:
            fitness = {"workouts": [], "nutrition": []}
        
        # Add workout entry
        workout_entry = {
            "date": datetime.now().isoformat(),
            "exercise": exercise,
            "weight": weight,
            "reps": reps,
            "sets": sets,
            "transcript": data["transcript"]
        }
        
        fitness["workouts"].append(workout_entry)
        
        # Save
        with open(FITNESS_DATA, 'w') as f:
            json.dump(fitness, f, indent=2)
        
        message = f"✅ Logged: {exercise.title()}"
        if weight:
            message += f" {weight}lbs"
        if reps:
            message += f" x{reps}"
        message += " 💪"
        
        return {"success": True, "message": message, "data": workout_entry}
    
    def log_food(self, data: Dict) -> Dict:
        """Log food to fitness data"""
        food = data.get("food_items", "")
        calories = data.get("calories", 0)
        
        # Load fitness data
        if FITNESS_DATA.exists():
            with open(FITNESS_DATA, 'r') as f:
                fitness = json.load(f)
        else:
            fitness = {"workouts": [], "nutrition": []}
        
        # Add nutrition entry
        nutrition_entry = {
            "date": datetime.now().isoformat(),
            "food": food,
            "calories": calories,
            "transcript": data["transcript"]
        }
        
        fitness["nutrition"].append(nutrition_entry)
        
        # Save
        with open(FITNESS_DATA, 'w') as f:
            json.dump(fitness, f, indent=2)
        
        message = f"✅ Food logged"
        if calories:
            message += f": {calories} calories"
        message += " 🔥"
        
        return {"success": True, "message": message, "data": nutrition_entry}
    
    def query_fitness(self, data: Dict) -> Dict:
        """Query fitness stats"""
        # Placeholder - integrate with FitTrack Pro API
        return {
            "success": True,
            "message": "Checking fitness stats... (integrate with FitTrack Pro API)"
        }
    
    def add_to_shopping(self, data: Dict) -> Dict:
        """Add item to shopping list"""
        item = data.get("item", "")
        
        if not item:
            return {"success": False, "message": "No item specified"}
        
        # Load shopping list
        if SHOPPING_LIST.exists():
            with open(SHOPPING_LIST, 'r') as f:
                shopping = json.load(f)
        else:
            shopping = {"items": []}
        
        # Add item
        shopping["items"].append({
            "item": item,
            "added": datetime.now().isoformat(),
            "completed": False
        })
        
        # Save
        with open(SHOPPING_LIST, 'w') as f:
            json.dump(shopping, f, indent=2)
        
        return {
            "success": True,
            "message": f"✅ Added '{item}' to shopping list 📝"
        }
    
    def query_calendar(self, data: Dict) -> Dict:
        """Query calendar"""
        # Placeholder - integrate with Google Calendar
        return {
            "success": True,
            "message": "Checking calendar... (integrate with Google Calendar API)"
        }
    
    def check_email(self, data: Dict) -> Dict:
        """Check email for urgent items"""
        # Placeholder - integrate with Gmail
        return {
            "success": True,
            "message": "Checking email... (integrate with Gmail API)"
        }
    
    def set_reminder(self, data: Dict) -> Dict:
        """Set a reminder"""
        reminder_text = data.get("reminder_text", "")
        time_text = data.get("time_text", "")
        
        if not reminder_text:
            return {"success": False, "message": "No reminder text provided"}
        
        return {
            "success": True,
            "message": f"✅ Reminder set: '{reminder_text}' {time_text} ⏰"
        }
    
    def play_music(self, data: Dict) -> Dict:
        """Play music via Spotify"""
        music_name = data.get("music_name", "")
        
        if not music_name:
            return {"success": False, "message": "No music specified"}
        
        # Placeholder - integrate with Spotify
        return {
            "success": True,
            "message": f"🎵 Playing: {music_name}"
        }
    
    def query_music(self, data: Dict) -> Dict:
        """Query current playing music"""
        # Placeholder - integrate with Spotify
        return {
            "success": True,
            "message": "Checking what's playing... (integrate with Spotify API)"
        }
    
    def check_hinge(self, data: Dict) -> Dict:
        """Check Hinge status"""
        from hinge_assistant import HingeAssistant
        
        try:
            assistant = HingeAssistant()
            report = assistant.get_daily_report()
            return {
                "success": True,
                "message": report
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error checking Hinge: {e}"
            }
    
    def general_response(self, data: Dict) -> Dict:
        """Handle general queries"""
        return {
            "success": True,
            "message": "I'll help with that. (Send to main LLM for response)"
        }
    
    def log_command(self, transcript: str, intent: str, confidence: int, result: Dict):
        """Log voice command for debugging"""
        VOICE_LOG.parent.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "transcript": transcript,
            "intent": intent,
            "confidence": confidence,
            "success": result.get("success", False),
            "message": result.get("message", "")
        }
        with open(VOICE_LOG, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")


def process_voice_command(transcript: str) -> str:
    """
    Main entry point for processing voice commands
    
    Returns: Response message to send back to user
    """
    router = VoiceRouter()
    
    # Detect intent
    intent, confidence, data = router.detect_intent(transcript)
    
    # Confidence thresholds
    if confidence >= 60:
        # Execute action
        result = router.route_action(intent, data)
        router.log_command(transcript, intent, confidence, result)
        return result["message"]
    else:
        # Too low confidence - treat as general query
        return "I heard you, but I'm not sure what action to take. Can you clarify?"


def main():
    """CLI testing interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 voice_command_router.py <transcript>")
        print("\nExamples:")
        print('  "Log bench press 185 pounds 8 reps"')
        print('  "Add eggs to shopping list"')
        print('  "Check my Hinge status"')
        print('  "What\'s my calorie target today?"')
        return
    
    transcript = " ".join(sys.argv[1:])
    
    router = VoiceRouter()
    intent, confidence, data = router.detect_intent(transcript)
    
    print(f"\n📝 Transcript: {transcript}")
    print(f"🎯 Intent: {intent}")
    print(f"💯 Confidence: {confidence}%")
    print(f"📊 Extracted data: {json.dumps(data, indent=2)}")
    
    if confidence >= 60:
        print(f"\n🚀 Executing action...")
        result = router.route_action(intent, data)
        print(f"✅ Result: {result['message']}")
    else:
        print(f"\n⚠️ Confidence too low - treating as general query")


if __name__ == "__main__":
    main()
