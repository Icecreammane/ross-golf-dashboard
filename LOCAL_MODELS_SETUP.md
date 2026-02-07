# Local Models Setup - Ollama Integration

**Goal:** Run models locally on Mac Mini to reduce API costs and increase privacy.

**Status:** Installing Ollama now...

---

## Installation Steps

### 1. Install Ollama
```bash
brew install ollama
```

### 2. Start Ollama Service
```bash
# Start in background (runs on port 11434)
ollama serve
```

Or use launchd for auto-start:
```bash
# Create service file
cat > ~/Library/LaunchAgents/com.ollama.ollama.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ollama.ollama</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/ollama</string>
        <string>serve</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# Load and start
launchctl load ~/Library/LaunchAgents/com.ollama.ollama.plist
```

### 3. Download Models

**For Coding:**
```bash
ollama pull codestral:22b       # Mistral's code specialist (22B params)
ollama pull deepseek-coder:6.7b # Fast code model (smaller)
```

**For General Tasks:**
```bash
ollama pull llama3.1:8b         # Fast general model
ollama pull qwen2.5:14b         # Strong reasoning (14B)
```

**For Experiments:**
```bash
ollama pull phi3:medium         # Microsoft, efficient (14B)
ollama pull gemma2:9b           # Google, balanced
```

---

## Model Recommendations by Mac Specs

### If 16GB RAM:
- Start with 7B-8B models (fast, reliable)
- `llama3.1:8b`, `deepseek-coder:6.7b`, `gemma2:9b`

### If 32GB RAM:
- Use 14B-22B models (better quality)
- `codestral:22b`, `qwen2.5:14b`, `phi3:medium`

### If 64GB+ RAM:
- Run 33B-70B models (near-cloud quality)
- `deepseek-coder:33b`, `llama3.1:70b`

---

## Clawdbot Configuration

Add to `~/.clawdbot/clawdbot.json`:

```json
{
  "agents": {
    "defaults": {
      "models": {
        "ollama/codestral:22b": {
          "alias": "local-coder",
          "provider": "openai",
          "baseURL": "http://localhost:11434/v1",
          "apiKey": "ollama"
        },
        "ollama/llama3.1:8b": {
          "alias": "local-fast",
          "provider": "openai",
          "baseURL": "http://localhost:11434/v1",
          "apiKey": "ollama"
        },
        "ollama/qwen2.5:14b": {
          "alias": "local-brain",
          "provider": "openai",
          "baseURL": "http://localhost:11434/v1",
          "apiKey": "ollama"
        }
      }
    }
  }
}
```

---

## Use Cases (Experiment & Learn)

### Definitely Try Local For:
- ✅ **Content drafts** - tweets, posts, emails (fast iteration)
- ✅ **Code review** - analyze existing code, suggest improvements
- ✅ **Research & summaries** - web research, document analysis
- ✅ **Experimentation** - try 10 variations, pick best (free!)
- ✅ **Privacy-sensitive** - personal data, financial info

### Keep on Cloud For (Initially):
- ❌ **Production builds** - Codex still better quality
- ❌ **Revenue-critical** - Opus reasoning for landing pages
- ❌ **Strategic planning** - Opus for deep thinking
- ❌ **Multimodal** - Gemini for images/video

### Test & Compare:
- 🔬 **Landing page copy** - local vs Opus, which converts better?
- 🔬 **Tweet generation** - local vs Sonnet, which performs better?
- 🔬 **Code fixes** - local vs Codex, speed vs quality?

---

## Routing Strategy (Updated)

### Phase 1: Conservative (Now)
- Use local for **non-critical content** only
- Cloud for everything else
- Measure quality differences

### Phase 2: Expand (Week 2)
- If local performs well → expand to code review
- Still keep production builds on Codex
- Track cost savings

### Phase 3: Optimize (Week 3+)
- Data-driven decisions on what stays local vs cloud
- Hybrid approach: local first-pass → cloud polish
- Aim for 50% cost reduction

---

## Cost Comparison

### Current (All Cloud):
- Codex: $2-4/build
- Opus: $3-5/build
- Sonnet: $0.50-1/build
- **Monthly:** ~$200

### With Local (50/50 Split):
- Local: $0/build (hardware cost amortized)
- Cloud (critical only): ~$100/month
- **Savings:** $1,200/year

### Break-Even:
- Ollama: Free
- Hardware: Already have Mac Mini
- **Immediate ROI**

---

## Monitoring & Quality Tracking

Create `local-model-results.md`:
- Track tasks run locally vs cloud
- Compare quality (subjective 1-10 rating)
- Measure speed (seconds per task)
- Calculate cost savings

**Weekly review:** What's working locally? What needs cloud?

---

## Next Steps

1. ✅ Install Ollama (in progress)
2. ⏳ Start Ollama service
3. ⏳ Pull initial models (codestral:22b, llama3.1:8b)
4. ⏳ Configure Clawdbot
5. ⏳ Update autonomous_check.py routing
6. ⏳ Test with simple task (generate tweet)
7. ⏳ Document results

---

*Setup started: 2026-02-07 10:32 CST*  
*Goal: Reduce API costs, increase privacy, experiment freely*
