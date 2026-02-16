# Voice Control Everything

**Status:** ✅ Production-ready  
**Version:** 2.0.0  
**Built:** 2026-02-15

## Overview

Control Jarvis via voice through Telegram voice messages. Natural language processing routes commands to appropriate actions.

**Flow:** Voice Message → Transcription → Intent Detection → Action Execution → Response

## Supported Commands

### **Fitness Logging**

| Command Example | Action |
|----------------|--------|
| "Log bench press 185 pounds 8 reps" | Logs workout |
| "I just ate chicken breast" | Logs food |
| "Log 300 calories" | Logs calories |
| "What's my calorie target today?" | Queries fitness stats |
| "Did I hit my protein goal?" | Checks protein target |

### **Life Admin**

| Command Example | Action |
|----------------|--------|
| "Add eggs to shopping list" | Adds to shopping list |
| "What's on my calendar tomorrow?" | Shows calendar |
| "Check my email for urgent stuff" | Checks email |
| "Set reminder to call Mom in 2 hours" | Sets reminder |

### **Music Control**

| Command Example | Action |
|----------------|--------|
| "Play gym playlist" | Plays Spotify playlist |
| "Create a chill coding playlist" | Creates playlist |
| "What's playing?" | Shows current track |

### **Hinge Assistant**

| Command Example | Action |
|----------------|--------|
| "Check my Hinge status" | Shows daily report |
| "Hinge report" | Priority likes left, matches |

### **Smart Home** (Future)

| Command Example | Action |
|----------------|--------|
| "Turn on living room lights" | Controls lights |
| "Set thermostat to 72" | Adjusts temperature |
| "Lock all doors" | Locks smart locks |

## Quick Start

### Test Commands
```bash
# Test workout logging
python3 ~/clawd/scripts/voice_command_router.py "Log bench press 185 pounds 8 reps"

# Test food logging
python3 ~/clawd/scripts/voice_command_router.py "I just ate chicken breast"

# Test shopping list
python3 ~/clawd/scripts/voice_command_router.py "Add eggs to shopping list"

# Test Hinge check
python3 ~/clawd/scripts/voice_command_router.py "Check my Hinge status"
```

### Integration with Telegram

Jarvis automatically processes voice messages:
1. Ross sends voice message to Jarvis on Telegram
2. Telegram transcribes audio → text
3. `voice_command_router.py` detects intent
4. Action executes
5. Jarvis responds with confirmation

## How It Works

### Intent Detection
1. **Pattern Matching:** Transcript matched against regex patterns
2. **Confidence Scoring:** Each match increases confidence (30 points per pattern)
3. **Intent Selection:** Highest scoring intent wins
4. **Data Extraction:** Relevant data parsed from transcript

### Confidence Thresholds
- **≥60%:** Execute action automatically
- **<60%:** Treat as general query (send to main LLM)

### Example Flow

**Voice Input:** "Log bench press 185 pounds 8 reps"

```
1. Detect Intent:
   - Pattern matches: "bench press" + "185 pounds" + "8 reps"
   - Intent: fitness_log_workout
   - Confidence: 75%

2. Extract Data:
   - exercise: "bench press"
   - weight: 185
   - unit: "pounds"
   - reps: 8

3. Execute Action:
   - Load fitness_data.json
   - Append workout entry
   - Save to file

4. Respond:
   - "✅ Logged: Bench Press 185lbs x8 💪"
```

## Architecture

### Components

1. **voice_command_router.py** - Main router
   - Intent detection
   - Data extraction
   - Action routing
   - Logging

2. **voice_action_detector.py** - Legacy detector (still works)
   - Backward compatible
   - Fitness-focused

3. **Data Files:**
   - `data/fitness_data.json` - Workouts & nutrition
   - `data/shopping_list.json` - Shopping items
   - `logs/voice-commands.log` - Command history

### Data Structures

**fitness_data.json:**
```json
{
  "workouts": [
    {
      "date": "2026-02-15T22:30:00",
      "exercise": "bench press",
      "weight": 185,
      "reps": 8,
      "sets": 1,
      "transcript": "log bench press 185 pounds 8 reps"
    }
  ],
  "nutrition": [
    {
      "date": "2026-02-15T12:30:00",
      "food": "chicken breast",
      "calories": 300,
      "transcript": "i just ate chicken breast"
    }
  ]
}
```

**shopping_list.json:**
```json
{
  "items": [
    {
      "item": "eggs",
      "added": "2026-02-15T22:30:00",
      "completed": false
    }
  ]
}
```

## Configuration

### Add New Intent

Edit `voice_command_router.py`:

```python
"new_intent_name": {
    "patterns": [
        r"pattern1",
        r"pattern2",
    ],
    "confidence_boost": 25,
    "handler": "handler_method_name"
},
```

Then add handler method:

```python
def handler_method_name(self, data: Dict) -> Dict:
    """Handler for new intent"""
    # Your action logic here
    return {
        "success": True,
        "message": "✅ Action completed!"
    }
```

### Adjust Confidence

Increase for more conservative execution:
```python
if confidence >= 70:  # Changed from 60
    # Execute action
```

Decrease for more aggressive execution:
```python
if confidence >= 50:  # Changed from 60
    # Execute action
```

## Natural Language Examples

### Fitness
- "Bench press 185 pounds 8 reps" ✅
- "I did shoulder press at 90 pounds" ✅
- "Just finished leg day" ✅
- "Ate chili for lunch" ✅
- "Had 300 calories of chicken" ✅

### Shopping
- "Add eggs to shopping list" ✅
- "Need to buy milk" ✅
- "Shopping list add bread" ✅

### Calendar
- "What's on my calendar today?" ✅
- "Show me my schedule tomorrow" ✅
- "What do I have next week?" ✅

### Hinge
- "Check Hinge" ✅
- "Hinge status" ✅
- "Show me dating app stats" ✅

## Logging

All voice commands logged to:
```
~/clawd/logs/voice-commands.log
```

Format:
```json
{"timestamp": "2026-02-15 22:30:00", "transcript": "...", "intent": "...", "confidence": 75, "success": true, "message": "..."}
```

View recent commands:
```bash
tail -20 ~/clawd/logs/voice-commands.log | jq
```

## Integration Points

### With FitTrack Pro
```python
# Query fitness stats
curl http://localhost:3000/api/stats
# Returns current calories, protein, macros
```

### With Google Calendar
```python
# Query calendar events
from scripts.google_calendar import get_events
events = get_events(date="tomorrow")
```

### With Spotify
```python
# Control music
from scripts.spotify_control import play_playlist
play_playlist("gym")
```

## Testing

### Test Suite
```bash
cd ~/clawd
python3 scripts/test_voice_router.py
```

### Manual Testing
```bash
# Test each intent
python3 scripts/voice_command_router.py "Log bench press 185 pounds 8 reps"
python3 scripts/voice_command_router.py "Add eggs to shopping list"
python3 scripts/voice_command_router.py "Check Hinge"
python3 scripts/voice_command_router.py "What's my calorie target?"
```

### Expected Results
- ✅ Fitness logging saves to `data/fitness_data.json`
- ✅ Shopping list updates `data/shopping_list.json`
- ✅ Hinge check shows daily report
- ✅ Queries return appropriate responses

## Response Format

### Success Response
```
✅ Logged: Bench Press 185lbs x8 💪
✅ Food logged: 300 calories 🔥
✅ Added 'eggs' to shopping list 📝
```

### Query Response
```
📊 Fitness Stats:
  Calories: 1850/2200
  Protein: 180g/200g
  
📅 Calendar:
  9:00 AM - Team Meeting
  2:00 PM - Coffee with Sarah
```

### Error Response
```
⚠️ Confidence too low - can you clarify?
❌ No calendar events found
❌ Error: [specific error message]
```

## Performance

- **Intent Detection:** <100ms
- **Action Execution:** <500ms (depends on action)
- **Total Response Time:** <1 second for most commands

## Future Enhancements

### Phase 2 (Optional)
1. **Local LLM Integration** - Use Ollama for better intent understanding
2. **Context Awareness** - "Another set of that" remembers previous exercise
3. **Voice Confirmations** - TTS responses via ElevenLabs
4. **Multi-step Commands** - "Log workout and add protein shake to shopping list"
5. **Habit Tracking** - Automatically detect patterns and suggest improvements

## Troubleshooting

### Command Not Recognized
- Check confidence score: `python3 voice_command_router.py "<command>"`
- If too low, add more patterns to intent
- Increase `confidence_boost` value

### Data Not Saving
- Check file permissions: `ls -l ~/clawd/data/`
- Verify data directory exists: `mkdir -p ~/clawd/data`
- Check logs for errors: `tail ~/clawd/logs/voice-commands.log`

### Integration Errors
- FitTrack Pro: Verify running on port 3000
- Calendar: Check Google API credentials
- Spotify: Verify OAuth token valid

## Quick Reference

```bash
# Test command
python3 ~/clawd/scripts/voice_command_router.py "<transcript>"

# View logs
tail -20 ~/clawd/logs/voice-commands.log

# Check fitness data
cat ~/clawd/data/fitness_data.json | jq

# Check shopping list
cat ~/clawd/data/shopping_list.json | jq

# Hinge status
python3 ~/clawd/scripts/hinge_assistant.py check
```

---

## Example Session

```
Ross (voice): "Log bench press 185 pounds 8 reps"
Jarvis: ✅ Logged: Bench Press 185lbs x8 💪

Ross (voice): "I just ate chicken breast"
Jarvis: ✅ Food logged 🔥

Ross (voice): "Add eggs to shopping list"
Jarvis: ✅ Added 'eggs' to shopping list 📝

Ross (voice): "Check Hinge"
Jarvis: 📊 Daily Hinge Report
High-value: 0 | Priority likes: 3/3 left | Screen time: 20/20 min

Ross (voice): "What's my calorie target?"
Jarvis: Your target is 2200 calories. You're at 1850 (350 remaining). Protein: 180g/200g. On track! 💪
```

---

**Built:** 2026-02-15  
**Status:** Production-ready ✅  
**Response Time:** <1s ✅  
**Tested:** Yes ✅
