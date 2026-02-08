# Agent Integration: /ask Command

**For:** Main Jarvis agent session  
**Time to integrate:** ~5 minutes  
**Complexity:** Simple (5 lines of code)

---

## How to Integrate

### Option 1: Direct Integration (Recommended)

In your main agent's message processing logic, add this check **before** passing to the LLM:

```python
# Check for /ask command
if message_text.startswith('/ask'):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path.home() / "clawd" / "scripts"))
    from ask_command_integration import process_ask_command
    
    response = process_ask_command(message_text)
    return response  # Send directly to user
```

### Option 2: Using exec Tool

If you can't modify message handling directly, use exec:

```python
if message_text.startswith('/ask'):
    result = exec(
        command=f"cd ~/clawd/scripts && python3 ask_command_integration.py '{message_text}'",
        capture_output=True
    )
    return result.stdout
```

---

## Testing After Integration

### Test 1: Basic Usage
**You type:**
```
/ask Which opportunity should I pursue?
```

**Expected response:**
```
**Ranking:** A > B > C

1. A: Golf swing analysis inquiry via email (67% conversion, $194 expected, 2h effort)
2. B: Partnership proposal for fitness app (30% conversion, $150 expected, 8h effort)
3. C: Feature request: Add dark mode (10% conversion, $0 expected, 4h effort)

⚡ Response time: 0.02s
```

### Test 2: Help
**You type:**
```
/ask
```

**Expected response:**
```
❓ **Usage:** `/ask [your question]`

**Examples:**
• `/ask Which of these 3 opportunities should I pursue?`
• `/ask Should I focus on quick wins or long-term projects?`
• `/ask What's the best ROI option right now?`

💡 I'll analyze based on conversion rates, revenue potential, and effort required.
```

### Test 3: Custom Question
**You type:**
```
/ask Should I focus on quick wins or long-term projects?
```

**Expected response:**
Ranked opportunities with reasoning.

---

## Verification Checklist

After integrating:

1. [ ] `/ask` with no question shows help
2. [ ] `/ask [question]` returns ranked list
3. [ ] Response time shown at bottom
4. [ ] Decision logged to `memory/decision_history.json`
5. [ ] Response time < 2 seconds (should be ~0.02s)

---

## How It Works

When user sends `/ask [question]`:

1. **Agent intercepts** message starting with `/ask`
2. **Calls integration wrapper** (`ask_command_integration.py`)
3. **Wrapper processes** question:
   - Loads current opportunities from `memory/current_opportunities.json`
   - Classifies each opportunity type
   - Scores based on conversion rate, revenue, effort, ROI
   - Ranks by score
   - Optionally queries local LLM for reasoning
4. **Returns formatted response** with ranking
5. **Logs decision** to `memory/decision_history.json`

**Total time:** ~0.02 seconds

---

## Troubleshooting

### "No opportunities found"
**Cause:** No opportunities in `memory/current_opportunities.json`

**Fix:** Add sample opportunities:
```bash
cat > ~/clawd/memory/current_opportunities.json <<EOF
{
  "opportunities": [
    {"description": "Golf inquiry via email", "source": "email"},
    {"description": "Partnership proposal", "source": "linkedin"},
    {"description": "Feature request", "source": "github"}
  ]
}
EOF
```

### Integration not working
**Debug:**
```bash
# Test command directly
python3 ~/clawd/scripts/ask_command_integration.py "/ask test"

# Check for errors
python3 ~/clawd/scripts/test_ask_command.py
```

### Slow response (>2s)
**Should not happen** (current: 0.02s), but if it does:
- Check system load
- LLM timeout is 3s max
- Falls back to score-only if LLM unavailable

---

## Example Integration Code

### In Main Agent Session

```python
def process_message(message_text):
    """Process incoming Telegram message"""
    
    # Check for /ask command
    if message_text.startswith('/ask'):
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path.home() / "clawd" / "scripts"))
        
        from ask_command_integration import process_ask_command
        response = process_ask_command(message_text)
        return response
    
    # Check for other commands
    if message_text.startswith('/lockdown'):
        return handle_lockdown()
    
    # ... other command handling ...
    
    # Default: pass to LLM
    return query_llm(message_text)
```

---

## Command Priority

Add `/ask` handling **before** these:
- General LLM processing
- Heartbeat checks
- Context loading

Add `/ask` handling **after** these:
- `/lockdown` (security)
- `/elevated` (security)
- System commands

**Suggested order:**
1. Security commands (`/lockdown`, `/elevated`)
2. Quick commands (`/ask`, quick actions)
3. Regular message processing

---

## Performance

**Current benchmarks:**
- Classification: 0.001s
- Scoring: 0.01s
- Formatting: 0.005s
- **Total: ~0.02s**

**No impact on:**
- Other commands
- Message processing
- System performance

**Benefits:**
- Instant decision support
- No cloud API calls
- No token cost
- No latency

---

## Maintenance

### Update Opportunities
Opportunities auto-loaded from `memory/current_opportunities.json`.

**Manual update:**
```bash
vim ~/clawd/memory/current_opportunities.json
```

**Auto-populated by:**
- `opportunity_scanner.py`
- `email_daemon.py`
- Manual logging

### Update Conversion Rates
As you track real outcomes, update `memory/conversion_data.json`:

```bash
# After a successful email inquiry converts
vim ~/clawd/memory/conversion_data.json
# Update email_inquiry conversion_rate and avg_revenue
```

**Future:** Auto-update from revenue tracker integration.

### View Decision History
```bash
# Last 10 decisions
cat ~/clawd/memory/decision_history.json | jq '.decisions[-10:]'

# Today's decisions
cat ~/clawd/memory/decision_history.json | jq '.decisions[] | select(.timestamp | startswith("2026-02-08"))'
```

---

## Next Steps

1. **Integrate** (5 lines of code above)
2. **Test** (3 test cases above)
3. **Verify** (checklist above)
4. **Use** regularly for opportunity prioritization
5. **Update** conversion rates based on real outcomes

---

## Documentation

- **Full docs:** `~/clawd/ASK_COMMAND.md`
- **Build summary:** `~/clawd/BUILD_ASK_COMMAND.md`
- **This guide:** `~/clawd/AGENT_ASK_INTEGRATION.md`

---

## Questions?

**Test the command:**
```bash
python3 ~/clawd/scripts/ask_command_integration.py "/ask Which opportunity?"
```

**Run demo:**
```bash
bash ~/clawd/scripts/demo_ask_command.sh
```

**Run tests:**
```bash
python3 ~/clawd/scripts/test_ask_command.py
```

---

**Integration time:** ~5 minutes  
**Complexity:** Simple  
**Benefit:** Instant decision support with no cloud cost  

**Ready to integrate!** 🚀
