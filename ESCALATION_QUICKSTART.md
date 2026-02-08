# Smart Escalation System - Quick Start

**Status:** ✅ Production-ready  
**Setup Time:** < 5 minutes  
**Monthly Savings:** $15-20 estimated

---

## What Is This?

An intelligent routing layer that sends simple questions to your local LLM (free!) and complex questions to Sonnet (paid). You save money, get faster responses, and never notice the difference.

---

## Quick Commands

```bash
# Test system health
python3 ~/clawd/scripts/test_system_integration.py

# Test a query
python3 ~/clawd/scripts/test_escalation.py "What time is it?"

# Interactive testing
python3 ~/clawd/scripts/test_escalation.py --interactive

# Run benchmark
python3 ~/clawd/scripts/test_escalation.py --benchmark

# View statistics
python3 ~/clawd/scripts/test_escalation.py --stats

# Dashboard (live)
python3 ~/clawd/scripts/escalation_dashboard.py --watch

# Check cost savings
cat ~/clawd/memory/escalation_cost_savings.json | jq
```

---

## How It Works

1. **User asks question** via Telegram
2. **Middleware intercepts** message
3. **Local LLM scores complexity** (0-100)
4. **Routing decision:**
   - Low complexity (0-50) + High confidence (>70%) = **LOCAL** ⚡
   - High complexity (51-100) OR Low confidence (<70%) = **CLOUD** ☁️
5. **Response delivered** (user doesn't know which route)
6. **Savings tracked** automatically

---

## Example Routing

| Query | Complexity | Route | Why |
|-------|------------|-------|-----|
| "What time is it?" | 10 | LOCAL | Pure factual |
| "Explain TCP vs UDP" | 35 | LOCAL | Light reasoning |
| "Should I invest in Bitcoin?" | 75 | CLOUD | High complexity decision |
| "Design distributed system" | 90 | CLOUD | Requires deep expertise |

---

## Current Status

✅ **Core Engine** - Built and tested  
✅ **CLI Tools** - Test, benchmark, stats ready  
✅ **Dashboard** - Real-time monitoring  
✅ **Configuration** - Tunable thresholds  
✅ **Cost Tracking** - Automatic logging  
⏳ **Telegram Integration** - Ready for gateway hookup

---

## Integration (5 minutes)

### Step 1: Verify System
```bash
cd ~/clawd/scripts
python3 test_system_integration.py
```

**Expected:** All checks pass ✓

### Step 2: Test Routing
```bash
python3 test_escalation.py --benchmark
```

**Expected:** 
- Simple queries → LOCAL
- Complex queries → CLOUD
- 50%+ local routing rate

### Step 3: Hook into Telegram Gateway

**Location:** Find Telegram message handler in Clawdbot gateway

**Add this code:**
```python
from telegram_escalation_middleware import intercept_telegram_message

# Before forwarding message to main agent:
result = intercept_telegram_message({
    "text": message.text,
    "user_id": message.from_user.id,
    "chat_type": message.chat.type,
    "timestamp": datetime.now().isoformat(),
    "message_id": message.message_id,
    "has_media": bool(message.photo or message.video),
    "has_file": bool(message.document),
    "from_bot": message.from_user.is_bot
})

if result["action"] == "respond_local":
    # Send local response immediately
    await message.reply_text(result["response"])
    return  # Don't forward to cloud

# Otherwise forward to main agent as normal
```

### Step 4: Test Live
Send these via Telegram:
- "What time is it?" → Should be instant (local)
- "Design a distributed system" → Normal speed (cloud)

### Step 5: Monitor
```bash
# Watch live
python3 escalation_dashboard.py --watch

# Check savings
python3 test_escalation.py --stats
```

---

## Configuration

**File:** `~/clawd/config/escalation_config.json`

**Key settings:**
```json
{
  "enabled": true,
  "thresholds": {
    "complexity_escalate": 50,    // Complexity above this → cloud
    "confidence_minimum": 70       // Confidence below this → cloud
  }
}
```

**Tune for:**
- **More local:** Increase `complexity_escalate` to 60-70
- **More cloud:** Decrease `confidence_minimum` to 60
- **Disable:** Set `"enabled": false`

---

## Monitoring

### Daily Check
```bash
python3 escalation_dashboard.py
```

Look for:
- **Local percentage** > 50%
- **Cost saved** increasing
- **No quality complaints** from users

### Weekly Review
```bash
# View trends
python3 escalation_dashboard.py --hours 168

# Export logs
tail -500 ~/clawd/memory/escalation.log > weekly_review.jsonl
```

---

## Troubleshooting

### Problem: All queries escalate to cloud
**Fix:**
```bash
# Check Ollama
ollama list

# Pull models if missing
ollama pull qwen2.5:14b
ollama pull llama3.1:8b

# Restart Ollama
killall ollama
ollama serve &
```

### Problem: Local responses are poor
**Fix:** Increase confidence threshold in config:
```json
{"thresholds": {"confidence_minimum": 80}}
```

### Problem: Response times slow
**Fix:** Already using fastest models (llama3.1:8b)
- Ensure no other heavy processes running
- Consider running Ollama with more RAM

---

## Success Metrics

### Week 1 Goals
- ✅ System integrated and running
- ✅ 50%+ local routing rate
- ✅ <1s response time for local queries
- ✅ $5+ saved

### Month 1 Goals
- ✅ 60%+ local routing rate
- ✅ $15+ monthly savings
- ✅ Zero quality issues
- ✅ Dashboard in daily workflow

---

## Files Reference

| File | Purpose |
|------|---------|
| `scripts/smart_escalation_engine.py` | Core routing logic |
| `scripts/telegram_escalation_middleware.py` | Telegram integration hook |
| `scripts/test_escalation.py` | CLI testing tool |
| `scripts/escalation_dashboard.py` | Stats and monitoring |
| `scripts/test_system_integration.py` | System health check |
| `config/escalation_config.json` | Configuration |
| `memory/escalation.log` | Decision log (JSONL) |
| `memory/escalation_cost_savings.json` | Cost tracking |
| `SMART_ESCALATION_SYSTEM.md` | Full documentation |

---

## Support

**Test system:** `python3 test_system_integration.py`  
**View logs:** `tail -50 ~/clawd/memory/escalation.log | jq`  
**Check config:** `cat ~/clawd/config/escalation_config.json | jq`  
**Get stats:** `python3 test_escalation.py --stats`

---

**Built:** 2026-02-08  
**Status:** Production-ready  
**Estimated ROI:** $15-20/month for 5min setup
