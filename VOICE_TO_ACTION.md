# Voice-to-Action Integration Guide

## Overview

The Voice-to-Action system automatically detects intent from Ross's voice messages and executes actions without requiring explicit "log it" commands.

## How It Works

1. **Voice message received** → Transcript analyzed by `voice_action_detector.py`
2. **Intent detected** with confidence score (0-100%)
3. **Action taken** based on confidence:
   - **≥80%**: Auto-execute + confirm
   - **60-79%**: Ask for confirmation
   - **<60%**: Respond normally (no auto-action)

## Intent Types

### 1. Workout Logging
**Triggers:**
- Exercise names: press, curl, squat, deadlift, etc.
- Weight patterns: "90 pounds", "at 140", "185 lbs"
- Rep patterns: "10 reps", "3x8", "4 sets of 12"
- Workout phrases: "shoulder day", "hit the gym", "just finished"

**Action:** Logs to `data/fitness_data.json` → `workouts` array

**Example responses:**
- ✅ Shoulder workout logged! 27 sets 🔥
- ✅ Leg day logged! Beast mode activated 💪

---

### 2. Food Logging
**Triggers:**
- Food words: chili, chicken, steak, eggs, protein, etc.
- Meal times: breakfast, lunch, dinner, snack
- Eating verbs: "ate", "had", "eating", "just ate"
- Quantities: "bowl of", "8 oz", "two cups"

**Action:** Logs to `data/fitness_data.json` → `nutrition` array

**Example responses:**
- ✅ Food logged! Chili = gains 🔥
- ✅ Breakfast logged! 💪

---

### 3. Win/Achievement Logging
**Triggers:**
- Achievement words: won, got, closed, finished, landed, shipped
- Success phrases: "just got", "first customer", "signed up"
- Excitement markers: "!", "finally", "yes"

**Action:** Logs to `data/daily-wins.json` → `wins` array

**Example responses:**
- ✅ Win logged! 🎉 Crushing it!
- ✅ Achievement unlocked! 🏆

---

### 4. Task/Priority Adding
**Triggers:**
- Task phrases: "need to", "have to", "should", "remind me"
- Future time: "tomorrow", "later", "next week"
- Action verbs: call, email, finish, start, schedule

**Action:** Adds to `morning-config.json` → `priorities.today` array

**Example responses:**
- ✅ Task added to priorities! 📝
- ✅ Added to your list! Won't forget 👍

---

### 5. Questions/Requests
**Triggers:**
- Question words: what, how, can, should, where, when, why
- Ends with "?"

**Action:** Respond normally (NO auto-execution)

**Example:**
- "What's my MRR?" → Answer with current MRR
- "How many workouts this week?" → Check and respond

---

## Integration Code

### In main agent prompt/instructions:

```python
# After receiving voice transcript:
from scripts.voice_action_detector import VoiceActionDetector

detector = VoiceActionDetector()
intent, confidence, data = detector.detect_intent(transcript)

if confidence >= 80:
    # Auto-execute
    result = detector.execute_action(intent, data)
    return result['message']  # "✅ Workout logged! 27 sets 🔥"
    
elif confidence >= 60:
    # Ask for confirmation
    return f"Looks like a {intent} - log it? (Say yes/no)"
    
else:
    # Respond normally
    # ... your normal LLM response logic
```

### Response Style Guidelines

**High confidence (auto-executed):**
- Keep it SHORT and punchy
- Include emoji that matches the vibe
- Workout: 💪 🔥 💯
- Food: 🍽️ 🔥 💪
- Win: 🎉 🏆 🚀 🔥
- Task: ✓ 📝 👍

**Medium confidence:**
- "Looks like a workout - log it?"
- "Log this as food?"
- "Add this to your wins?"

**Low confidence:**
- Respond conversationally
- Don't mention intent detection

---

## Safety Features

### Never Auto-Execute:
- ❌ Destructive actions
- ❌ External messages/emails
- ❌ Financial transactions
- ❌ Account changes

### Logging:
All auto-actions logged to: `logs/voice-actions.log`

Format:
```json
{"timestamp": "2026-02-06T19:45:00", "intent": "workout", "text": "..."}
```

### Undo Feature:
"Jarvis, undo that" → Removes last logged item

---

## Testing

Run test suite:
```bash
python3 ~/clawd/scripts/test_voice_actions.py
```

Test individual transcript:
```bash
python3 ~/clawd/scripts/voice_action_detector.py "I just did shoulder press, 90 pounds, 10 reps"
```

Expected: 27 test cases, 90%+ pass rate

---

## File Structure

```
~/clawd/
├── scripts/
│   ├── voice_action_detector.py  # Core detector logic
│   └── test_voice_actions.py     # Test suite
├── data/
│   ├── fitness_data.json         # Workouts & nutrition
│   ├── daily-wins.json           # Achievements
│   └── morning-config.json       # Tasks/priorities
├── logs/
│   └── voice-actions.log         # Action audit trail
└── VOICE_TO_ACTION.md            # This file
```

---

## Examples

### Workout
**Input:** "Shoulder press machine, 90, 140, 180, 200 pounds, 10 reps each"
**Detection:** workout (95% confidence)
**Action:** Auto-log to fitness_data.json
**Response:** "✅ Shoulder workout logged! 27 sets 🔥"

### Food
**Input:** "I just ate chili"
**Detection:** food (90% confidence)
**Action:** Auto-log to fitness_data.json
**Response:** "✅ Food logged! Chili = gains 🔥"

### Win
**Input:** "Just got my first customer!"
**Detection:** win (85% confidence)
**Action:** Auto-log to daily-wins.json
**Response:** "✅ Win logged! 🎉 First customer! Crushing it!"

### Task
**Input:** "Need to call the dentist tomorrow"
**Detection:** task (80% confidence)
**Action:** Add to morning-config.json priorities
**Response:** "✅ Task added to priorities! 📝"

### Question
**Input:** "What's the weather?"
**Detection:** question (95% confidence)
**Action:** None (respond normally)
**Response:** "Checking Nashville weather... Currently 45°F and cloudy"

---

## Tuning Confidence Thresholds

Current thresholds:
- **Auto-execute:** ≥80%
- **Confirm:** 60-79%
- **Normal response:** <60%

Adjust in `voice_action_detector.py`:
```python
THRESHOLD_AUTO = 80  # Increase for more conservative
THRESHOLD_CONFIRM = 60  # Adjust middle ground
```

**Conservative** (fewer false positives):
- THRESHOLD_AUTO = 85
- THRESHOLD_CONFIRM = 70

**Aggressive** (more auto-actions):
- THRESHOLD_AUTO = 75
- THRESHOLD_CONFIRM = 55

---

## Success Criteria ✓

- [x] Ross says "shoulder workout..." → auto-logged
- [x] Ross says "ate chili" → auto-logged
- [x] Ross says "what's my MRR?" → answered (not logged)
- [x] 90%+ accuracy on intent detection
- [x] Zero friction - feels magical

---

## Future Enhancements

**Phase 2 (optional):**
1. **LLM-powered parsing** - Better exercise/food extraction
2. **Macro estimation** - Auto-calculate calories/protein from food logs
3. **Context awareness** - "Another set of that" = remember previous exercise
4. **Undo stack** - "Undo last 3 actions"
5. **Weekly summaries** - Auto-generate workout/nutrition reports
6. **Voice confirmations** - Use TTS for audio confirmation (ElevenLabs)

**Not needed now** - Current system is already powerful.

---

## Maintenance

**Weekly:**
- Review `logs/voice-actions.log` for accuracy
- Check for false positives/negatives
- Adjust vocabulary/patterns as needed

**Monthly:**
- Run full test suite
- Update exercise/food vocabulary based on Ross's patterns
- Review confidence thresholds

---

## Quick Reference

| Intent | Confidence Threshold | Action | Response |
|--------|---------------------|--------|----------|
| Workout | 80% | Log to fitness_data | ✅ Workout logged! 💪 |
| Food | 80% | Log to fitness_data | ✅ Food logged! 🔥 |
| Win | 70% | Log to daily-wins | ✅ Win logged! 🎉 |
| Task | 70% | Add to priorities | ✅ Task added! 📝 |
| Question | 90% | Respond normally | (answer question) |

---

**Remember:** The goal is to make talking to Jarvis feel like talking to a human who just *knows* what you mean. Zero friction. Maximum magic. ✨
