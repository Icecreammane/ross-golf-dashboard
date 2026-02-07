# Voice Commands System 🎤

**Status:** ACTIVE ✅  
**Built:** 2026-02-02 10:18pm CST

## What It Does

Allows Ross to send voice messages to Jarvis on Telegram and have them:
1. **Transcribed** using OpenAI Whisper
2. **Parsed** for known commands
3. **Executed** automatically
4. **Confirmed** with a reply message

## Supported Commands

### Food Logging
- "Log banana" → 105 cal, 1g protein, 27g carbs, 0g fat
- "Log beef bowl" → 650 cal, 45g protein, 60g carbs, 22g fat
- "Usual lunch" → Same as beef bowl
- "Protein shake" → 200 cal, 40g protein, 6g carbs, 3g fat

### Workout Logging
- "Leg day" → Logs legs workout
- "Chest day" → Logs chest workout
- "Back day" → Logs back workout
- "Arm day" → Logs arms workout
- "Cardio" → Logs cardio session

### Status & Progress
- "Status" → Shows current fitness dashboard
- "How am I doing?" → Same as status
- "Progress" → Same as status

### Wins
- "Log win: [text]" → Logs accomplishment to Daily Wins tracker
- "I won [text]" → Same as above
- "Accomplishment: [text]" → Same as above

## How It Works

### Architecture
```
Telegram Voice Message
    ↓
Clawdbot receives message
    ↓
telegram_voice_handler.py downloads audio
    ↓
voice_commands.py transcribes with Whisper
    ↓
Parse transcript for known commands
    ↓
Execute command (log food, workout, etc.)
    ↓
Send confirmation reply to Telegram
```

### Files
- `voice_commands.py` - Core transcription & command processing
- `telegram_voice_handler.py` - Telegram integration
- `temp/` - Temporary audio file storage (auto-cleaned)

## Integration with Clawdbot

When a voice message arrives in Telegram:
1. Clawdbot detects the voice message type
2. Calls `telegram_voice_handler.py` with file_id
3. Handler downloads, processes, and returns result
4. Clawdbot sends formatted reply to Ross

## Benefits

- **Hands-free logging** - At gym, in car, cooking, etc.
- **Faster than typing** - Just speak naturally
- **No app switching** - Stay in Telegram
- **Automatic recognition** - No buttons or forms

## Example Usage

**Ross:** 🎤 "Hey Jarvis, log banana"  
**Jarvis:** ✅ Logged Banana: 105 cal, 1g protein, 27g carbs, 0g fat

**Ross:** 🎤 "Leg day"  
**Jarvis:** 💪 Legs workout logged! Great work!

**Ross:** 🎤 "Log win: finished refactoring the dashboard"  
**Jarvis:** 🏆 Win logged: finished refactoring the dashboard

## Future Enhancements
- [ ] Natural language food parsing ("I ate a chicken breast")
- [ ] Exercise rep/set extraction ("I did 10 reps of bench press")
- [ ] Smart meal recognition ("I had lunch at Chipotle")
- [ ] Voice responses (TTS reply instead of text)
- [ ] Contextual understanding (remember previous commands)

## Dependencies
- `openai` Python package (for Whisper API)
- `requests` for Telegram API calls
- Telegram bot token in environment

## Testing

Test locally:
```bash
# Test voice command processing
python3 ~/clawd/voice/voice_commands.py /path/to/audio.ogg

# Test Telegram integration (requires file_id)
python3 ~/clawd/voice/telegram_voice_handler.py <telegram_file_id>
```

---

**Built in response to:** Ross's request for voice commands (#1 on Top 3 list)  
**Build time:** ~15 minutes  
**Status:** Ready for testing on next voice message! 🚀
