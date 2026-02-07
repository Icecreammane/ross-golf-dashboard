# Voice Command Setup Guide

How to enable and use Jarvis voice commands across all platforms.

---

## QUICK START

Voice commands work **right now** via text input. Just type commands in Telegram:

```
Jarvis, what's my MRR?
Jarvis, find 5 leads
Jarvis, am I on track?
```

Jarvis parses natural language and responds conversationally.

---

## PLATFORM INTEGRATION

### Telegram (Text-Based)
**Status:** ✅ Working now

Simply type commands with "Jarvis" prefix:
```
You: Jarvis what's my MRR
Jarvis: Currently $47 MRR. $3 to hit your first $50. That's 94% there. Keep building.
```

### iOS Siri Shortcuts (True Voice)
**Status:** 🚧 Coming soon

1. Create Siri Shortcut
2. Set phrase: "Ask Jarvis [command]"
3. Action: Send message to Jarvis Telegram bot
4. Enable "Show when run" = OFF for seamless execution

Example:
```
"Hey Siri, ask Jarvis what's my MRR"
→ Siri sends to Telegram
→ Jarvis responds via notification
```

### macOS Voice Control
**Status:** 🚧 Coming soon

Use macOS dictation + keyboard shortcut:
1. System Settings → Accessibility → Voice Control
2. Add custom command: "Jarvis [dictation]"
3. Action: Run shell script:
   ```bash
   python3 ~/clawd/scripts/voice_command.sh "$phrase"
   ```

---

## TESTING COMMANDS

### Method 1: Direct Telegram
Just type in your Jarvis Telegram chat:
```
Jarvis, what should I work on?
```

### Method 2: Terminal
```bash
cd ~/clawd
python3 voice/response_generator.py "Jarvis what's my MRR"
```

### Method 3: Test Script
```bash
# Test parsing only
python3 voice/command_parser.py "Jarvis find 5 leads"

# Test full execution
python3 voice/mode_router.py "Jarvis log workout bench press 185"
```

---

## ADDING CUSTOM COMMANDS

### Step 1: Add Pattern to Parser

Edit `voice/command_parser.py`:

```python
self.patterns = {
    # ... existing patterns ...
    
    "your_new_intent": [
        r"your regex pattern here",
        r"alternative pattern",
    ]
}

self.intent_categories["your_new_intent"] = "status"  # or action, logging, guidance
```

### Step 2: Add Router Handler

Edit `voice/mode_router.py`:

```python
routing_map = {
    # ... existing routes ...
    
    "your_new_intent": {
        "handler": "your_handler",
        "action": "your_action",
        "params": {},
        "requires_api": False,
        "estimated_time": 1
    }
}
```

### Step 3: Add Response Generator

Edit `voice/response_generator.py`:

```python
generators = {
    # ... existing generators ...
    
    "your_new_intent": self._generate_your_response,
}

def _generate_your_response(self, result: Dict, context: Dict) -> str:
    return "Your natural language response here"
```

### Step 4: Test It

```bash
python3 voice/response_generator.py "Jarvis your new command"
```

---

## TROUBLESHOOTING

### "Could not parse command"
- Check spelling of wake word ("Jarvis")
- Try simpler phrasing
- Use examples from `voice_commands.md`
- Check parser patterns in `command_parser.py`

### Command parsed but no response
- Check router has handler for that intent
- Verify handler is implemented in `mode_router.py`
- Check logs: `cat ~/clawd/logs/voice-commands.log`

### Response too generic
- Edit response generator for that intent
- Add context-specific variations
- Check if result data is being passed correctly

### Want to add wake word alternatives
Edit `command_parser.py`:
```python
# Change this line:
text = re.sub(r'^(?:hey |hi )?jarvis,? ', '', text)

# To:
text = re.sub(r'^(?:hey |hi )?(?:jarvis|assistant|ai),? ', '', text)
```

---

## ADVANCED: VOICE INPUT PIPELINE

For true voice-to-text in future:

```
[iOS/macOS Voice] 
    ↓
[Speech-to-Text]
    ↓
[Command Parser]
    ↓
[Mode Router]
    ↓
[Response Generator]
    ↓
[Text-to-Speech] (optional)
    ↓
[Spoken Response]
```

**Current implementation:** Text input → Parser → Router → Response → Text output

**Future implementation:** Voice input → STT → Parser → Router → Response → TTS → Voice output

---

## PERFORMANCE

- **Parse time:** < 10ms (regex matching)
- **Route time:** < 5ms (dictionary lookup)
- **Execute time:** Varies by handler (1-5 seconds)
- **Generate time:** < 5ms (template strings)

Total latency (text to response): **< 5 seconds**

---

## LOGS

Voice command logs stored at:
```
~/clawd/memory/voice-commands.jsonl
```

Each entry:
```json
{
  "timestamp": 1707253200,
  "command": "Jarvis what's my MRR",
  "intent": "get_mrr",
  "confidence": 0.9,
  "response": "Currently $47 MRR...",
  "execution_time": 0.234
}
```

View recent commands:
```bash
tail -20 ~/clawd/memory/voice-commands.jsonl | jq
```

---

## EXAMPLES

### Morning Routine
```
Jarvis, am I on track?
Jarvis, what should I work on?
Jarvis, activate build mode
```

### Mid-Day Check
```
Jarvis, how's the launch going?
Jarvis, what's my MRR?
Jarvis, am I procrastinating?
```

### End of Day
```
Jarvis, log win deployed feature X
Jarvis, log workout 45 minutes strength training
Jarvis, check progress
```

---

## INTEGRATION WITH MODES

Voice commands automatically integrate with existing Jarvis modes:

- **Sales Mode:** "Jarvis find leads" activates and executes
- **Build Mode:** "Jarvis activate build mode" switches context
- **Accountability:** "Jarvis am I procrastinating" checks patterns

No separate setup needed - it just works.

---

## NEXT STEPS

1. ✅ Test commands via Telegram (works now)
2. 🚧 Set up iOS Siri Shortcuts (optional, for true voice)
3. 🚧 Configure macOS Voice Control (optional, for desktop voice)
4. 💡 Add custom commands for your workflow
5. 📊 Review logs to see what works best

**Start simple:** Use text-based commands in Telegram today. Add voice later when you want hands-free operation.

---

**Questions? Just ask Jarvis:** *"Jarvis, how do voice commands work?"* 😉
