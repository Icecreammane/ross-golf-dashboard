#!/usr/bin/env python3
"""
Test suite for Voice-to-Action detector
"""

from voice_action_detector import VoiceActionDetector

def test_detector():
    """Run comprehensive tests on the voice action detector."""
    detector = VoiceActionDetector()
    
    test_cases = [
        # Workout tests
        {
            'input': 'Shoulder press machine, 90, 140, 180, 200, 210 pounds, 10 reps each',
            'expected_intent': 'workout',
            'expected_min_confidence': 85,
            'description': 'Typical shoulder workout with weights and reps'
        },
        {
            'input': 'Just finished leg day - squats, lunges, and leg press',
            'expected_intent': 'workout',
            'expected_min_confidence': 80,
            'description': 'Leg day workout'
        },
        {
            'input': 'Hit the gym today, did 3 sets of 10 bench press at 185',
            'expected_intent': 'workout',
            'expected_min_confidence': 85,
            'description': 'Bench press workout'
        },
        {
            'input': 'Cable lateral raises, 40 pounds, 12 reps, 4 sets',
            'expected_intent': 'workout',
            'expected_min_confidence': 90,
            'description': 'Cable exercises'
        },
        {
            'input': 'Shoulder workout complete - overhead press, lateral raises, front raises, shrugs',
            'expected_intent': 'workout',
            'expected_min_confidence': 85,
            'description': 'Complete shoulder routine'
        },
        
        # Food tests
        {
            'input': 'I just ate chili',
            'expected_intent': 'food',
            'expected_min_confidence': 75,  # Adjusted - single food item
            'description': 'Simple food log'
        },
        {
            'input': 'Had chicken breast, rice, and broccoli for lunch',
            'expected_intent': 'food',
            'expected_min_confidence': 85,
            'description': 'Meal with multiple items'
        },
        {
            'input': 'Eating a protein shake and banana post-workout',
            'expected_intent': 'food',
            'expected_min_confidence': 85,
            'description': 'Post-workout meal'
        },
        {
            'input': 'Just had 8 oz steak with a bowl of pasta',
            'expected_intent': 'food',
            'expected_min_confidence': 85,
            'description': 'Food with quantities'
        },
        {
            'input': 'Breakfast was 4 eggs and oatmeal',
            'expected_intent': 'food',
            'expected_min_confidence': 85,
            'description': 'Breakfast log'
        },
        
        # Win tests
        {
            'input': 'Just got my first customer!',
            'expected_intent': 'win',
            'expected_min_confidence': 75,
            'description': 'First customer achievement'
        },
        {
            'input': 'Closed a $500 deal today',
            'expected_intent': 'win',
            'expected_min_confidence': 70,
            'description': 'Sales win'
        },
        {
            'input': 'Finally finished the landing page',
            'expected_intent': 'win',
            'expected_min_confidence': 70,
            'description': 'Completion win'
        },
        {
            'input': 'Shipped the new feature!',
            'expected_intent': 'win',
            'expected_min_confidence': 70,
            'description': 'Shipping win'
        },
        {
            'input': 'Hit 10 consecutive free throws at the gym',
            'expected_intent': 'win',
            'expected_min_confidence': 65,
            'description': 'Personal achievement'
        },
        
        # Task tests
        {
            'input': 'Need to call the dentist tomorrow',
            'expected_intent': 'task',
            'expected_min_confidence': 70,
            'description': 'Reminder task'
        },
        {
            'input': 'Remind me to email the client about the proposal',
            'expected_intent': 'task',
            'expected_min_confidence': 75,
            'description': 'Email reminder'
        },
        {
            'input': 'Tomorrow I should work on the marketing copy',
            'expected_intent': 'task',
            'expected_min_confidence': 70,
            'description': 'Tomorrow task'
        },
        {
            'input': 'Have to finish the presentation by Friday',
            'expected_intent': 'task',
            'expected_min_confidence': 70,
            'description': 'Deadline task'
        },
        {
            'input': 'Don\'t forget to schedule the meeting',
            'expected_intent': 'task',
            'expected_min_confidence': 75,
            'description': 'Meeting reminder'
        },
        
        # Question tests (should NOT auto-execute)
        {
            'input': 'What\'s the weather today?',
            'expected_intent': 'question',
            'expected_min_confidence': 90,
            'description': 'Weather question'
        },
        {
            'input': 'How much MRR do I have?',
            'expected_intent': 'question',
            'expected_min_confidence': 90,
            'description': 'MRR question'
        },
        {
            'input': 'Can you show me my workout history?',
            'expected_intent': 'question',
            'expected_min_confidence': 90,
            'description': 'History request'
        },
        {
            'input': 'Should I work out today?',
            'expected_intent': 'question',
            'expected_min_confidence': 90,
            'description': 'Decision question'
        },
        {
            'input': 'Where did I put my keys?',
            'expected_intent': 'question',
            'expected_min_confidence': 90,
            'description': 'Location question'
        },
        
        # Edge cases
        {
            'input': 'I think I should have eaten more protein',
            'expected_intent': 'food',  # Could be question, but "eaten" is strong signal
            'expected_min_confidence': 50,  # Low confidence due to ambiguity
            'description': 'Ambiguous food statement'
        },
        {
            'input': 'Going to the gym later',
            'expected_intent': 'task',  # Future tense, not completed workout
            'expected_min_confidence': 50,
            'description': 'Future workout (task, not workout log)'
        },
    ]
    
    print("=" * 80)
    print("VOICE-TO-ACTION DETECTOR TEST SUITE")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['description']}")
        print(f"Input: \"{test['input']}\"")
        
        intent, confidence, data = detector.detect_intent(test['input'])
        
        print(f"Expected: {test['expected_intent']} (≥{test['expected_min_confidence']}%)")
        print(f"Got: {intent} ({confidence}%)")
        
        intent_match = intent == test['expected_intent']
        confidence_match = confidence >= test['expected_min_confidence']
        
        if intent_match and confidence_match:
            print("✅ PASS")
            passed += 1
        else:
            print("❌ FAIL")
            if not intent_match:
                print(f"   Intent mismatch: expected {test['expected_intent']}, got {intent}")
            if not confidence_match:
                print(f"   Confidence too low: expected ≥{test['expected_min_confidence']}%, got {confidence}%")
            failed += 1
        
        # Show action decision
        if confidence >= detector.THRESHOLD_AUTO:
            print("   → Would AUTO-EXECUTE")
        elif confidence >= detector.THRESHOLD_CONFIRM:
            print("   → Would ASK FOR CONFIRMATION")
        else:
            print("   → Would RESPOND NORMALLY")
    
    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed ({passed}/{len(test_cases)} = {100*passed//len(test_cases)}%)")
    print("=" * 80)
    
    return failed == 0


if __name__ == '__main__':
    import sys
    success = test_detector()
    sys.exit(0 if success else 1)
