# Voice Brief System - Complete Guide

**Status:** ✅ OPERATIONAL  
**Built:** 2026-02-04  
**Voice:** OpenAI TTS "Onyx" (deep, authoritative)

---

## 🎯 Purpose

Automated voice generation for morning briefs, build updates, and notifications. Ross finds voice WAY more efficient than reading—this saves 5-10 minutes every morning and keeps him informed without context switching.

---

## 📦 Components

### 1. Core Voice Module (`systems/auto_voice.py`)
- **Function:** `generate_voice_message(text, output_path, ...)`
- **Features:**
  - OpenAI TTS integration (Onyx voice)
  - Automatic text splitting for long messages (>4096 chars)
  - Cost tracking (logs every generation)
  - Supports .opus (Telegram) and .mp3 (universal)
  - High quality (tts-1-hd model)

**Usage:**
```python
from systems.auto_voice import generate_voice_message

audio_path = generate_voice_message(
    text="Your message here",
    output_path="output.opus",
    voice="onyx",
    log_purpose="morning_brief"
)
```

**CLI:**
```bash
# Generate voice from text
python3 systems/auto_voice.py "Hello Ross" output.opus

# Get cost summary
python3 systems/auto_voice.py --cost-summary
```

### 2. Morning Brief Voice (`scripts/generate-morning-brief-voice.py`)
- **Purpose:** Convert morning brief HTML to natural voice
- **Output:** `~/clawd/morning-briefs/morning-brief-YYYY-MM-DD.opus` + transcript
- **Schedule:** Run at 7:30am CST (add to cron)

**Usage:**
```bash
# Generate voice brief (no send)
python3 scripts/generate-morning-brief-voice.py

# Force regeneration even if already sent today
python3 scripts/generate-morning-brief-voice.py --force

# Generate AND send via Telegram (for cron)
python3 scripts/generate-morning-brief-voice.py --send
```

**Cron Setup:**
```bash
30 7 * * * cd ~/clawd && python3 scripts/generate-morning-brief-voice.py --send
```

### 3. Build Update Voice (`systems/voice_build_updates.py`)
- **Purpose:** Monitor build completions and auto-generate voice notifications
- **Input:** `~/clawd/logs/build-status.json`
- **Output:** `~/clawd/build-notifications/build-complete-{id}-{timestamp}.opus`
- **Smart:** Respects work hours (no voice spam during 9am-5pm)

**Usage:**
```bash
# Check for updates (respects context/time)
python3 systems/voice_build_updates.py

# Force check (ignore time restrictions)
python3 systems/voice_build_updates.py --force

# List pending notifications
python3 systems/voice_build_updates.py --list
```

**Cron Setup:**
```bash
*/15 * * * * cd ~/clawd && python3 systems/voice_build_updates.py
```

### 4. Voice Templates (`templates/voice-templates.json`)
- Pre-written templates for common scenarios
- Sections: morning_brief, build_updates, evening_checkin, alerts, progress_updates
- Personality: Professional but friendly (Jarvis-style)

**Example:**
```json
{
  "build_updates": {
    "completed": "Build complete! {system_name} is ready. {key_features}. You can find it at {location}."
  }
}
```

### 5. Testing Suite (`tests/test-voice-system.sh`)
- Comprehensive test suite for all components
- Validates voice generation, templates, formats, integrations
- Includes audio playback test

**Usage:**
```bash
bash tests/test-voice-system.sh
```

---

## 🔌 Integration with Main Agent

### From Chat Sessions

**Generate morning brief voice:**
```python
# In agent code
result = exec("cd ~/clawd && python3 scripts/generate-morning-brief-voice.py --force")
audio_path = "~/clawd/morning-briefs/latest.opus"

# Send via Telegram
message(action="send", target="Ross", filePath=audio_path, 
        caption="Good morning! Here's your voice brief.")
```

**Check for build updates:**
```python
# Run the build update checker
exec("cd ~/clawd && python3 systems/voice_build_updates.py --force")

# Find new notifications
notifications = exec("ls -t ~/clawd/build-notifications/*.opus | head -1")
# Send the latest one
```

### From Smart Context

The voice system integrates with `smart_context.py`:
- **Morning (7-9am):** Auto-generate voice briefs
- **Evening (6-8pm):** Voice summaries welcome
- **Work hours (9am-5pm):** Text only, no voice
- **Night (after 10pm):** Text only, don't disturb

**Check if voice should be used:**
```python
from systems.smart_context import should_use_voice, get_current_context

context = get_current_context()  # 'work', 'morning', 'evening', etc.
use_voice = should_use_voice(user_sent_voice=False)
```

---

## 💰 Cost Tracking

Voice generation costs are logged to `~/clawd/logs/voice-cost-tracking.json`.

**Pricing:** OpenAI TTS-1-HD = $15.00 / 1M characters

**Estimated costs:**
- Morning brief (~500 chars): $0.0075 per brief
- Build update (~200 chars): $0.003 per notification
- Monthly (30 briefs + 10 updates): ~$0.26/month

**View cost summary:**
```bash
python3 systems/auto_voice.py --cost-summary
```

---

## 📝 File Locations

```
~/clawd/
├── systems/
│   ├── auto_voice.py              # Core voice generation
│   ├── voice_build_updates.py     # Build update monitor
│   └── smart_context.py           # Context detection
├── scripts/
│   └── generate-morning-brief-voice.py  # Morning brief voice
├── templates/
│   └── voice-templates.json       # Voice message templates
├── tests/
│   └── test-voice-system.sh       # Test suite
├── morning-briefs/
│   ├── morning-brief-YYYY-MM-DD.opus
│   ├── morning-brief-YYYY-MM-DD.txt
│   └── latest.opus -> (symlink to today)
├── build-notifications/
│   └── build-complete-{id}-{timestamp}.opus
└── logs/
    └── voice-cost-tracking.json   # Cost tracking log
```

---

## 🧪 Testing

Run the full test suite:
```bash
bash tests/test-voice-system.sh
```

**Expected output:**
- ✅ All core components exist
- ✅ Voice generation works
- ✅ Templates are valid
- ✅ Morning brief generates correctly
- ✅ Build updates run without errors
- ✅ Cost tracking functional

---

## 🚀 Quick Start

1. **Test voice generation:**
   ```bash
   python3 systems/auto_voice.py "Test message" test.opus
   afplay test.opus  # macOS
   ```

2. **Generate morning brief:**
   ```bash
   python3 scripts/generate-morning-brief-voice.py --force
   afplay ~/clawd/morning-briefs/latest.opus
   ```

3. **Add to cron (7:30am daily):**
   ```bash
   crontab -e
   # Add: 30 7 * * * cd ~/clawd && python3 scripts/generate-morning-brief-voice.py --send
   ```

4. **Add build monitoring (every 15 min):**
   ```bash
   crontab -e
   # Add: */15 * * * * cd ~/clawd && python3 systems/voice_build_updates.py
   ```

---

## 🎙️ Voice Quality Standards

- **Natural pacing:** Not too fast, easy to follow
- **Clear pronunciation:** Technical terms sound correct
- **No robotic artifacts:** Onyx voice is warm and natural
- **Appropriate tone:** Professional but friendly (Jarvis-style)
- **Length:** Keep briefs under 3 minutes

---

## 🔧 Troubleshooting

**"OPENAI_API_KEY not found"**
- Check: `echo $OPENAI_API_KEY`
- Set in `~/.zshrc` or equivalent: `export OPENAI_API_KEY="sk-..."`

**"Voice file too small"**
- Check API response for errors
- Verify OpenAI account has credits
- Test with: `python3 systems/auto_voice.py "Test" test.opus`

**"No module named 'auto_voice'"**
- Ensure you're running from `~/clawd` directory
- Check Python path: scripts add `~/clawd/systems` to path

**Voice quality issues:**
- Try different speeds: `speed=0.9` (slower) or `speed=1.1` (faster)
- Check model: should be `tts-1-hd` (high quality)
- Verify voice: should be `onyx` (deep, authoritative)

---

## 📚 Examples

### Example: Morning Brief (Generated 2026-02-04)

**Text:**
> Good morning, Ross. Here's your morning brief for Wednesday, February 04. Your calendar is clear today—no scheduled events. You're all caught up on tasks. Nothing urgent on the queue. No overnight builds completed. Everything's quiet on the engineering front. Open loops: 3 proposals awaiting approval. One more thing: It's been 3 days since your last workout log - want a reminder system? That's your brief for today. Have a great day!

**Audio:** `morning-briefs/morning-brief-2026-02-04.opus` (128 KB, ~30 seconds)

### Example: Build Completion

**Text:**
> Build complete! Workflow Infrastructure Build is ready. Deliverables include: smart-context.py, memory-auto-context.py, builds.html. You can find it at your workspace.

**Audio:** `build-notifications/build-complete-workflow-systems-*.opus` (60 KB, ~15 seconds)

---

## 🎯 Future Enhancements

- [ ] Auto-send via Telegram (currently manual)
- [ ] Multi-part voice clips (for very long briefs)
- [ ] Voice reactions (acknowledge user voice messages with voice)
- [ ] Custom voice cloning (use Ross's voice instead of Onyx)
- [ ] Voice command parsing (Ross sends voice → system extracts commands)
- [ ] Evening summary voice ("here's what happened today")

---

## 📞 Support

For issues or questions, check:
1. Test suite: `bash tests/test-voice-system.sh`
2. Cost log: `~/clawd/logs/voice-cost-tracking.json`
3. Build log: `~/clawd/logs/voice-system-build.md`
4. This guide: `~/clawd/systems/VOICE_SYSTEM_GUIDE.md`

---

**Built with ❤️ by Voice Automation Subagent**  
**Deadline met: 2026-02-04 12:45 PM CST** 🎉
