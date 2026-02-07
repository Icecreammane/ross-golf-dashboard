#!/usr/bin/env python3
"""
Voice-to-Action Intent Detector
Automatically detects intent from voice transcripts and executes actions
without explicit "log it" commands.
"""

import json
import re
from datetime import datetime
from typing import Tuple, Dict, Any, Optional
from pathlib import Path

class VoiceActionDetector:
    """Detects intent from voice messages and executes appropriate actions."""
    
    # Paths
    WORKSPACE = Path.home() / "clawd"
    FITNESS_DATA = WORKSPACE / "data" / "fitness_data.json"
    WINS_DATA = WORKSPACE / "data" / "daily-wins.json"
    MORNING_CONFIG = WORKSPACE / "morning-config.json"
    VOICE_LOG = WORKSPACE / "logs" / "voice-actions.log"
    
    # Confidence thresholds
    THRESHOLD_AUTO = 80  # Auto-execute
    THRESHOLD_CONFIRM = 60  # Ask for confirmation
    
    # Exercise vocabulary (expanded)
    EXERCISES = {
        'press', 'curl', 'raise', 'shrug', 'row', 'squat', 'deadlift',
        'bench', 'overhead', 'lateral', 'front', 'dumbbell', 'barbell',
        'cable', 'machine', 'pushup', 'pullup', 'chinup', 'dip',
        'lunge', 'extension', 'fly', 'flye', 'tricep', 'bicep',
        'shoulder', 'chest', 'back', 'leg', 'arm', 'core', 'ab',
        'crunch', 'plank', 'burpee', 'kettlebell', 'smith'
    }
    
    # Food vocabulary
    FOOD_WORDS = {
        'ate', 'had', 'eating', 'chili', 'chicken', 'steak', 'beef',
        'pork', 'fish', 'salmon', 'tuna', 'shrimp', 'egg', 'eggs',
        'protein', 'rice', 'pasta', 'bread', 'oats', 'oatmeal',
        'yogurt', 'cheese', 'milk', 'shake', 'smoothie', 'salad',
        'vegetables', 'broccoli', 'spinach', 'carrots', 'beans',
        'nuts', 'almonds', 'peanut', 'butter', 'avocado', 'fruit',
        'apple', 'banana', 'berries', 'pizza', 'burger', 'sandwich',
        'wrap', 'burrito', 'bowl', 'plate', 'serving', 'cup'
    }
    
    # Meal times
    MEAL_TIMES = {'breakfast', 'lunch', 'dinner', 'snack', 'meal', 'pre-workout', 'post-workout'}
    
    # Achievement words
    ACHIEVEMENT_WORDS = {
        'won', 'got', 'closed', 'finished', 'completed', 'landed',
        'signed', 'launched', 'shipped', 'published', 'achieved',
        'hit', 'reached', 'crushed', 'nailed', 'scored'
    }
    
    # Task/reminder phrases
    TASK_PHRASES = {
        'need to', 'have to', 'should', 'must', 'remind me',
        'don\'t forget', 'tomorrow', 'later', 'next week'
    }
    
    # Question words
    QUESTION_WORDS = {'what', 'how', 'can', 'should', 'where', 'when', 'why', 'who', 'which', 'could', 'would'}
    
    def __init__(self):
        """Initialize the detector and ensure directories exist."""
        self.WORKSPACE.mkdir(exist_ok=True)
        (self.WORKSPACE / "data").mkdir(exist_ok=True)
        (self.WORKSPACE / "logs").mkdir(exist_ok=True)
        
    def detect_intent(self, transcript: str) -> Tuple[str, int, Dict[str, Any]]:
        """
        Detect intent from voice transcript.
        
        Returns:
            (intent, confidence, data) tuple where:
            - intent: 'workout' | 'food' | 'win' | 'task' | 'question' | 'unknown'
            - confidence: 0-100 score
            - data: parsed data dict
        """
        text = transcript.lower().strip()
        
        # Check question first (highest priority to avoid false positives)
        if self._is_question(text):
            return ('question', 95, {'text': transcript})
        
        # Check workout intent
        workout_conf, workout_data = self._check_workout(text)
        
        # Check food intent
        food_conf, food_data = self._check_food(text)
        
        # Check win intent
        win_conf, win_data = self._check_win(text)
        
        # Check task intent
        task_conf, task_data = self._check_task(text)
        
        # Priority logic: workout > food > win > task
        # If workout has exercise indicators, prioritize it over win
        if workout_conf >= 70 and 'detected_exercises' in workout_data:
            # Strong workout signal - use it even if win/task is similar
            return ('workout', workout_conf, workout_data)
        
        # If food has eating verb + food items, prioritize it
        if food_conf >= 70 and 'food_items' in food_data:
            return ('food', food_conf, food_data)
        
        # Otherwise, return highest confidence intent
        candidates = [
            ('workout', workout_conf, workout_data),
            ('food', food_conf, food_data),
            ('win', win_conf, win_data),
            ('task', task_conf, task_data),
        ]
        
        best = max(candidates, key=lambda x: x[1])
        
        if best[1] < 50:
            return ('unknown', best[1], {'text': transcript})
        
        return best
    
    def _is_question(self, text: str) -> bool:
        """Check if text is a question."""
        # Starts with question word
        words = text.split()
        if words and words[0] in self.QUESTION_WORDS:
            return True
        # Ends with ?
        if text.strip().endswith('?'):
            return True
        return False
    
    def _check_workout(self, text: str) -> Tuple[int, Dict]:
        """Check for workout intent and extract data."""
        confidence = 0
        data = {'exercises': [], 'raw_text': text}
        
        # Check for exercise words
        words = set(re.findall(r'\b\w+\b', text))
        exercise_matches = words & self.EXERCISES
        if exercise_matches:
            confidence += 45
            data['detected_exercises'] = list(exercise_matches)
        
        # Check for weight patterns
        weight_patterns = [
            r'\b(\d+)\s*(lbs?|pounds?)\b',
            r'\bat\s*(\d+)\b',
            r'\b(\d+)\s*pound',
        ]
        weights = []
        for pattern in weight_patterns:
            matches = re.findall(pattern, text)
            if matches:
                weights.extend([m if isinstance(m, str) else m[0] for m in matches])
        if weights:
            confidence += 30
            data['weights'] = weights
        
        # Check for rep patterns
        rep_patterns = [
            r'\b(\d+)\s*reps?\b',
            r'\b(\d+)x\b',
            r'\b(\d+)\s*times?\b',
            r'\bsets?\s*of\s*(\d+)\b',
        ]
        reps = []
        for pattern in rep_patterns:
            matches = re.findall(pattern, text)
            if matches:
                reps.extend(matches)
        if reps:
            confidence += 25
            data['reps'] = reps
        
        # Check for workout phrases
        workout_phrases = ['workout', 'gym', 'training', 'lifting', 'shoulder day', 'leg day', 'chest day', 'back day', 'arm day']
        if any(phrase in text for phrase in workout_phrases):
            confidence += 20
        
        # Boost for "complete" if exercise words present
        if 'complete' in text and exercise_matches:
            confidence += 15
        
        # Boost for "just did" or "today's" (but only if there are exercise indicators)
        if any(phrase in text for phrase in ['just did', 'hit the gym', 'at the gym']):
            confidence += 15
        
        # If has exercises + (weights OR reps), strong workout signal
        if exercise_matches and (weights or reps):
            confidence += 15
        
        return (min(confidence, 100), data)
    
    def _check_food(self, text: str) -> Tuple[int, Dict]:
        """Check for food logging intent."""
        confidence = 0
        data = {'raw_text': text}
        
        # Check for eating verbs first (strong signal)
        eating_verbs = ['ate', 'eating', 'eaten']
        has_eating_verb = any(word in text for word in eating_verbs)
        had_verb = ' had ' in text or text.startswith('had ')
        
        if has_eating_verb:
            confidence += 35
        elif had_verb:
            confidence += 25
        
        # Check for food words
        words = set(re.findall(r'\b\w+\b', text))
        food_matches = words & self.FOOD_WORDS
        if food_matches:
            confidence += 45
            data['food_items'] = list(food_matches)
        
        # Check for meal times
        meal_matches = words & self.MEAL_TIMES
        if meal_matches:
            confidence += 20
            data['meal_time'] = list(meal_matches)[0]
        
        # Check for quantity patterns
        quantity_patterns = [
            r'\b(\d+)\s*(oz|ounces?|g|grams?|cups?|bowls?|servings?)\b',
            r'\b(a|one|two|three)\s*(bowl|cup|plate|serving)\s*of\b',
        ]
        for pattern in quantity_patterns:
            if re.search(pattern, text):
                confidence += 15
                break
        
        # Boost for "just ate/had"
        if 'just ate' in text or 'just had' in text:
            confidence += 15
        
        return (min(confidence, 100), data)
    
    def _check_win(self, text: str) -> Tuple[int, Dict]:
        """Check for achievement/win intent."""
        confidence = 0
        data = {'raw_text': text}
        
        # Must not be a question
        if self._is_question(text):
            return (0, data)
        
        # Check for achievement words
        words = set(re.findall(r'\b\w+\b', text))
        achievement_matches = words & self.ACHIEVEMENT_WORDS
        if achievement_matches:
            confidence += 55
            data['achievement_words'] = list(achievement_matches)
        
        # Success phrases (strong signals)
        success_phrases = ['just landed', 'just got', 'just closed', 'just finished', 'first customer', 'signed up', 'made a sale', 'deal', 'shipped', 'my first']
        matching_phrases = [p for p in success_phrases if p in text]
        if matching_phrases:
            confidence += 40
            data['success_phrases'] = matching_phrases
        
        # Boost for excitement markers
        if '!' in text:
            confidence += 15
        if 'finally' in text:
            confidence += 10
        
        # Business/achievement context words
        business_words = ['customer', 'client', 'sale', 'deal', 'revenue', 'mrr', 'feature', 'launch', 'ship']
        if any(word in text for word in business_words):
            confidence += 10
        
        return (min(confidence, 100), data)
    
    def _check_task(self, text: str) -> Tuple[int, Dict]:
        """Check for task/reminder intent."""
        confidence = 0
        data = {'raw_text': text}
        
        # Check for task phrases
        task_phrase_found = False
        for phrase in self.TASK_PHRASES:
            if phrase in text:
                confidence += 50
                data['trigger_phrase'] = phrase
                task_phrase_found = True
                break
        
        # Boost for strong reminder phrases
        if 'remind me' in text or "don't forget" in text:
            confidence += 15
        
        # Check for future time references
        future_words = ['tomorrow', 'later', 'next', 'tonight', 'morning', 'afternoon', 'evening', 'week', 'monday', 'tuesday', 'friday']
        if any(word in text for word in future_words):
            confidence += 20
        
        # Check for action verbs
        action_verbs = ['call', 'email', 'text', 'message', 'finish', 'start', 'work on', 'complete', 'schedule', 'book', 'buy', 'order']
        if any(verb in text for verb in action_verbs):
            confidence += 15
        
        # Must not be a question
        if self._is_question(text):
            confidence -= 40
        
        return (min(max(confidence, 0), 100), data)
    
    def parse_workout(self, text: str) -> Dict[str, Any]:
        """Extract structured workout data."""
        # Simple parser - can be enhanced with LLM if needed
        return {
            'timestamp': datetime.now().isoformat(),
            'raw_text': text,
            'type': 'workout',
            'parsed': True
        }
    
    def parse_food(self, text: str) -> Dict[str, Any]:
        """Extract structured food data."""
        return {
            'timestamp': datetime.now().isoformat(),
            'raw_text': text,
            'type': 'food',
            'parsed': True
        }
    
    def parse_win(self, text: str) -> Dict[str, Any]:
        """Extract win/achievement data."""
        return {
            'timestamp': datetime.now().isoformat(),
            'text': text,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
    
    def parse_task(self, text: str) -> Dict[str, Any]:
        """Extract task/priority data."""
        # Clean up the task text
        task_text = text
        for phrase in ['need to', 'have to', 'should', 'remind me to', 'don\'t forget to']:
            task_text = task_text.replace(phrase, '').strip()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'task': task_text,
            'raw_text': text
        }
    
    def execute_action(self, intent: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the detected action.
        
        Returns:
            Result dict with 'success', 'message', and optional 'data'
        """
        try:
            if intent == 'workout':
                return self._log_workout(data)
            elif intent == 'food':
                return self._log_food(data)
            elif intent == 'win':
                return self._log_win(data)
            elif intent == 'task':
                return self._log_task(data)
            else:
                return {'success': False, 'message': f'Unknown intent: {intent}'}
        except Exception as e:
            return {'success': False, 'message': f'Error executing action: {str(e)}'}
    
    def _log_workout(self, data: Dict) -> Dict:
        """Log workout to fitness_data.json."""
        # Load existing data
        if self.FITNESS_DATA.exists():
            with open(self.FITNESS_DATA) as f:
                fitness_data = json.load(f)
        else:
            fitness_data = {'workouts': [], 'nutrition': []}
        
        # Ensure workouts key exists
        if 'workouts' not in fitness_data:
            fitness_data['workouts'] = []
        
        # Add workout
        workout_entry = self.parse_workout(data['raw_text'])
        fitness_data['workouts'].append(workout_entry)
        
        # Save
        with open(self.FITNESS_DATA, 'w') as f:
            json.dump(fitness_data, f, indent=2)
        
        self._log_action('workout', data['raw_text'])
        
        return {
            'success': True,
            'message': '✅ Workout logged!',
            'data': workout_entry
        }
    
    def _log_food(self, data: Dict) -> Dict:
        """Log food to fitness_data.json."""
        # Load existing data
        if self.FITNESS_DATA.exists():
            with open(self.FITNESS_DATA) as f:
                fitness_data = json.load(f)
        else:
            fitness_data = {'workouts': [], 'nutrition': []}
        
        # Ensure nutrition key exists
        if 'nutrition' not in fitness_data:
            fitness_data['nutrition'] = []
        
        # Add food entry
        food_entry = self.parse_food(data['raw_text'])
        fitness_data['nutrition'].append(food_entry)
        
        # Save
        with open(self.FITNESS_DATA, 'w') as f:
            json.dump(fitness_data, f, indent=2)
        
        self._log_action('food', data['raw_text'])
        
        return {
            'success': True,
            'message': '✅ Food logged!',
            'data': food_entry
        }
    
    def _log_win(self, data: Dict) -> Dict:
        """Log win to daily-wins.json."""
        # Load existing wins
        if self.WINS_DATA.exists():
            with open(self.WINS_DATA) as f:
                wins_data = json.load(f)
        else:
            wins_data = {'wins': []}
        
        # Ensure wins key exists
        if 'wins' not in wins_data:
            wins_data['wins'] = []
        
        # Add win
        win_entry = self.parse_win(data['raw_text'])
        wins_data['wins'].append(win_entry)
        
        # Save
        with open(self.WINS_DATA, 'w') as f:
            json.dump(wins_data, f, indent=2)
        
        self._log_action('win', data['raw_text'])
        
        return {
            'success': True,
            'message': '✅ Win logged! 🎉',
            'data': win_entry
        }
    
    def _log_task(self, data: Dict) -> Dict:
        """Add task to morning-config.json priorities."""
        # Load config
        with open(self.MORNING_CONFIG) as f:
            config = json.load(f)
        
        # Ensure priorities structure exists
        if 'priorities' not in config:
            config['priorities'] = {}
        if 'today' not in config['priorities']:
            config['priorities']['today'] = []
        
        # Parse and add task
        task_entry = self.parse_task(data['raw_text'])
        config['priorities']['today'].append(task_entry['task'])
        
        # Save
        with open(self.MORNING_CONFIG, 'w') as f:
            json.dump(config, f, indent=2)
        
        self._log_action('task', data['raw_text'])
        
        return {
            'success': True,
            'message': '✅ Task added to priorities!',
            'data': task_entry
        }
    
    def _log_action(self, intent: str, text: str):
        """Log executed action to voice-actions.log."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'intent': intent,
            'text': text
        }
        
        with open(self.VOICE_LOG, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def get_last_action(self) -> Optional[Dict]:
        """Get the last logged action (for undo functionality)."""
        if not self.VOICE_LOG.exists():
            return None
        
        with open(self.VOICE_LOG) as f:
            lines = f.readlines()
            if lines:
                return json.loads(lines[-1])
        return None


def main():
    """CLI interface for testing."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: voice_action_detector.py <transcript>")
        sys.exit(1)
    
    transcript = ' '.join(sys.argv[1:])
    detector = VoiceActionDetector()
    
    intent, confidence, data = detector.detect_intent(transcript)
    
    print(f"\nIntent: {intent}")
    print(f"Confidence: {confidence}%")
    print(f"Data: {data}")
    
    if confidence >= detector.THRESHOLD_AUTO:
        print("\n[AUTO-EXECUTE]")
        result = detector.execute_action(intent, data)
        print(f"Result: {result}")
    elif confidence >= detector.THRESHOLD_CONFIRM:
        print("\n[NEEDS CONFIRMATION]")
    else:
        print("\n[LOW CONFIDENCE - RESPOND NORMALLY]")


if __name__ == '__main__':
    main()
