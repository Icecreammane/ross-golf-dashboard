# Smart Escalation System

**Status:** Production-ready  
**Created:** 2026-02-08  
**Purpose:** Intelligent LLM routing to reduce cloud costs while maintaining quality

---

## Overview

The Smart Escalation System intercepts user queries and intelligently routes them to either:
- **Local LLM (Llama)** - Fast, free, for simple queries
- **Cloud LLM (Sonnet)** - Powerful, for complex reasoning

Users don't notice the routing - they just get faster responses for simple questions and normal responses for complex ones. The system tracks cost savings in real-time.

---

## Architecture

```
User Message (Telegram)
         ↓
[Telegram Escalation Middleware]
         ↓
[Smart Escalation Engine]
    ↓           ↓
[Score Query]  [Gather Context]
    ↓
[Complexity Analysis]
• Overall: 0-100
• Factual vs Reasoning
• Data Retrieval
• Decision Making
• Time Sensitivity
• Reversibility
• Local Confidence
    ↓
[Routing Decision]
    ↓         ↓
  LOCAL     CLOUD
    ↓         ↓
 Llama    Sonnet
    ↓         ↓
  Response  (normal flow)
    ↓
[Log Decision + Track Savings]
    ↓
  User
```

---

## Components

### 1. **Smart Escalation Engine** (`smart_escalation_engine.py`)
Core routing logic. Scores queries, generates local responses, logs decisions.

**Key Features:**
- Multi-dimensional complexity scoring (0-100)
- Local LLM response generation with context
- Automatic escalation when confidence < 70%
- Cost tracking (tokens saved, $ saved)
- Decision logging to `memory/escalation.log`

**Models:**
- Scoring: `qwen2.5:14b` (strong reasoning)
- Response: `llama3.1:8b` (fast execution)

### 2. **Telegram Middleware** (`telegram_escalation_middleware.py`)
Intercepts Telegram messages before they reach main agent.

**Integration Points:**
- Hooks into Telegram message handler
- Returns either local response OR forwards to cloud
- Transparent to user
- Can be toggled per-user

### 3. **CLI Testing Tool** (`test_escalation.py`)
Test and benchmark the routing system.

**Usage:**
```bash
# Test a single query
python3 test_escalation.py "What time is it?"

# Interactive mode
python3 test_escalation.py --interactive

# Show statistics
python3 test_escalation.py --stats

# Run benchmark suite
python3 test_escalation.py --benchmark
```

### 4. **Dashboard** (`escalation_dashboard.py`)
Real-time stats and trends.

**Usage:**
```bash
# Show dashboard
python3 escalation_dashboard.py

# Watch mode (auto-refresh)
python3 escalation_dashboard.py --watch

# Last 48 hours
python3 escalation_dashboard.py --hours 48
```

---

## Routing Logic

### Complexity Thresholds

| Range | Complexity | Routing | Examples |
|-------|------------|---------|----------|
| 0-20 | Factual | LOCAL | "What time is it?", "Show today's memory" |
| 21-50 | Light reasoning | LOCAL (if confidence > 70%) | "Explain TCP vs UDP", "Summarize yesterday" |
| 51-100 | High complexity | CLOUD | "Design a distributed system", "Strategic planning" |

### Escalation Triggers
Query escalates to cloud if ANY of:
- Overall complexity > 50
- Local confidence < 70%
- Decision making > 70 AND reversibility > 70 (critical decisions)
- Local model returns "ESCALATE_NEEDED"

---

## Configuration

**File:** `config/escalation_config.json`

```json
{
  "enabled": true,
  "models": {
    "scoring": "qwen2.5:14b",
    "response": "llama3.1:8b"
  },
  "thresholds": {
    "complexity_escalate": 50,
    "confidence_minimum": 70,
    "critical_decision_threshold": 70
  },
  "telegram": {
    "enabled": true,
    "show_routing_info": false,
    "skip_commands": true,
    "skip_media": true
  }
}
```

**Per-User Overrides:**
```json
{
  "user_overrides": {
    "8412148376": {
      "enabled": true,
      "name": "Ross"
    }
  }
}
```

---

## Telegram Integration

### Current State
**Middleware ready, needs gateway integration.**

### Integration Steps

1. **Locate Telegram handler** in Clawdbot gateway
2. **Add middleware import:**
   ```python
   from telegram_escalation_middleware import intercept_telegram_message
   ```

3. **Hook before forwarding to agent:**
   ```python
   # Before sending message to main agent:
   result = intercept_telegram_message({
       "text": message.text,
       "user_id": message.from_user.id,
       "chat_type": message.chat.type,
       "timestamp": datetime.now().isoformat(),
       "message_id": message.message_id,
       "has_media": bool(message.photo or message.video or message.document),
       "has_file": bool(message.document),
       "from_bot": message.from_user.is_bot,
       "reply_to": message.reply_to_message.message_id if message.reply_to_message else None
   })
   
   if result["action"] == "respond_local":
       # Send local response immediately (no cloud call)
       await message.reply_text(result["response"])
       
       # Log savings
       print(f"Local response: {result['metadata']['tokens_saved']} tokens saved, "
             f"${result['metadata']['cost_saved']:.6f} saved")
       
       return  # Don't forward to cloud
   
   # Otherwise, forward to main agent as normal
   forward_to_main_agent(message)
   ```

4. **Test with simple queries:**
   ```
   "What time is it?" → Should get instant local response
   "Design a distributed system" → Should escalate to cloud
   ```

### Fallback Behavior
If middleware errors, it **always escalates** to cloud (safe default).

---

## Logging & Analytics

### Decision Log
**File:** `memory/escalation.log` (JSONL format)

Each line is a decision:
```json
{
  "timestamp": "2026-02-08T15:30:00",
  "route": "local",
  "query": "What time is it?",
  "reason": "Local handling",
  "complexity": {
    "overall": 15,
    "factual_vs_reasoning": 5,
    "confidence": 95
  },
  "response_time_ms": 245,
  "tokens_saved": 50,
  "cost_saved": 0.000375
}
```

### Cost Savings Log
**File:** `memory/escalation_cost_savings.json`

Running totals:
```json
{
  "total_queries": 1250,
  "local_queries": 875,
  "cloud_queries": 375,
  "tokens_saved": 125000,
  "cost_saved": 2.375,
  "local_percentage": 70.0,
  "started": "2026-02-08T10:00:00",
  "last_updated": "2026-02-08T15:30:00"
}
```

---

## Performance

### Expected Results

| Query Type | Route | Response Time | Tokens Saved | Cost Saved |
|------------|-------|---------------|--------------|------------|
| "What time is it?" | Local | 200-500ms | ~50 | $0.0004 |
| "Summarize today" | Local | 500-1500ms | ~200 | $0.0015 |
| "Design system architecture" | Cloud | Normal | 0 | $0 |

### Estimated Impact

**Assumptions:**
- 100 queries/day
- 60% are low-complexity (can be local)
- Avg tokens per query: 150 input + 300 output

**Savings:**
- Queries/month: 3,000
- Local queries: 1,800 (60%)
- Tokens saved: ~810,000/month
- **Cost saved: ~$12-15/month**

**ROI:** Setup time < 1 hour, ongoing savings automatic.

---

## Testing & Validation

### Smoke Test
```bash
# 1. Test engine directly
cd ~/clawd/scripts
python3 smart_escalation_engine.py

# 2. Test CLI
python3 test_escalation.py "What time is it?"
python3 test_escalation.py "Should I invest in Bitcoin?"

# 3. Run benchmark
python3 test_escalation.py --benchmark

# 4. Check stats
python3 test_escalation.py --stats

# 5. View dashboard
python3 escalation_dashboard.py
```

### Expected Benchmark Results
- Factual queries (4): Local
- Light reasoning (2): Local
- Medium complexity (3): Mixed
- High complexity (4): Cloud

**Target:** >50% local routing

---

## Monitoring

### Daily Check
```bash
python3 escalation_dashboard.py
```

### Watch Mode (Live)
```bash
python3 escalation_dashboard.py --watch
```

### Quick Stats
```bash
python3 test_escalation.py --stats
```

### Logs
```bash
# Recent decisions
tail -20 ~/clawd/memory/escalation.log | jq

# Cost savings
cat ~/clawd/memory/escalation_cost_savings.json | jq
```

---

## Troubleshooting

### Issue: All queries escalating to cloud
**Check:**
1. Is Ollama running? `ollama list`
2. Are models downloaded? Should see `qwen2.5:14b` and `llama3.1:8b`
3. Config enabled? Check `config/escalation_config.json`

**Fix:**
```bash
# Ensure Ollama is running
ollama serve &

# Pull models if missing
ollama pull qwen2.5:14b
ollama pull llama3.1:8b
```

### Issue: Local responses are poor quality
**Adjust thresholds** in `config/escalation_config.json`:
```json
{
  "thresholds": {
    "confidence_minimum": 80  // Increase from 70
  }
}
```

### Issue: Response times too slow
**Switch to faster model** for responses:
```json
{
  "models": {
    "response": "llama3.1:8b"  // Already fastest
  }
}
```

Or adjust Ollama settings:
```bash
# Increase context window
ollama run llama3.1:8b --context 4096
```

---

## Future Enhancements

### Phase 2 (Optional)
- [ ] Learning from user feedback (thumbs up/down on local responses)
- [ ] A/B testing different thresholds
- [ ] Response caching for repeated queries
- [ ] Multi-turn conversation context
- [ ] Integration with Discord, WhatsApp
- [ ] Real-time dashboard web UI
- [ ] Model performance tracking
- [ ] Auto-tuning thresholds based on accuracy

### Phase 3 (Advanced)
- [ ] Hybrid responses (local + cloud refinement)
- [ ] Streaming local responses
- [ ] Multiple local models for different query types
- [ ] GPU acceleration for local inference
- [ ] Cost optimization across multiple cloud providers

---

## Commands Reference

```bash
# Test single query
python3 test_escalation.py "your query here"

# Interactive testing
python3 test_escalation.py --interactive

# Run benchmark
python3 test_escalation.py --benchmark

# Show statistics
python3 test_escalation.py --stats

# Dashboard (static)
python3 escalation_dashboard.py

# Dashboard (live)
python3 escalation_dashboard.py --watch

# Dashboard (last 48h)
python3 escalation_dashboard.py --hours 48

# Test middleware
python3 telegram_escalation_middleware.py "test query" --user-id 12345

# Check cost savings
cat ~/clawd/memory/escalation_cost_savings.json | jq

# View recent decisions
tail -50 ~/clawd/memory/escalation.log | jq
```

---

## Success Metrics

### Week 1 Targets
- [ ] 50%+ queries handled locally
- [ ] <1 second avg response time for local queries
- [ ] Zero user complaints about response quality
- [ ] $5+ cost savings

### Month 1 Targets
- [ ] 60%+ local routing rate
- [ ] $15+ monthly savings
- [ ] Dashboard integrated into daily workflow
- [ ] User satisfaction maintained/improved

---

## Support

**Issues:** Add to `BUILD_SMART_ESCALATION.md` (this document)  
**Logs:** `memory/escalation.log`  
**Config:** `config/escalation_config.json`  
**Stats:** Run `python3 test_escalation.py --stats`

---

**Built:** 2026-02-08  
**Status:** Production-ready, awaiting gateway integration  
**Estimated ROI:** ~$15/month savings for ~1 hour setup
