# Model Roster - The Coding Arms

**Command Structure:** Ross → Jarvis → Specialized Builders

**Philosophy:** Right tool for the right job. Cost-effective, quality-focused.

---

## 🎯 Model Selection Guide

### 🤖 Codex (OpenAI GPT-5.2-Codex)
**Alias:** `codex`  
**Use For:**
- All production coding (APIs, integrations, features)
- Full-stack development (frontend + backend)
- Complex algorithmic work
- Code architecture and refactoring
- Bug fixes and optimization

**Why:** Best pure coding model. Strong at production-quality code.

**Cost:** ~$2-4 per build

**Examples:**
- Stripe integration
- Mission Control dashboard
- API wrappers
- Database schemas

---

### 🧠 Opus (Claude Opus 4-5)
**Alias:** `opus`  
**Use For:**
- Strategic planning and architecture
- Complex multi-step builds
- Landing pages with high conversion needs
- Content that needs deep reasoning
- When first-try accuracy is critical

**Why:** Deepest reasoning, best strategic thinking.

**Cost:** ~$3-5 per build

**Examples:**
- Revenue-critical landing pages
- Business strategy documents
- Complex automation workflows

---

### ⚡ Sonnet (Claude Sonnet 4-5)
**Alias:** `sonnet5`  
**Use For:**
- Content generation (tweets, posts, emails)
- Documentation and markdown
- Research and analysis
- Dashboard updates
- Internal tools
- Quick tasks

**Why:** Fast, cost-effective, good quality for most work.

**Cost:** ~$0.50-1 per build

**Examples:**
- Tweet drafts
- Weekly reports
- Dashboard data updates
- Memory logs

---

### 💎 Gemini (Google Gemini API)
**Status:** API configured  
**Use For:**
- Multimodal tasks (image + text)
- Large context windows (1M+ tokens)
- Document analysis and extraction
- Video/audio processing
- Research with massive datasets

**Why:** Best multimodal, huge context window.

**Cost:** ~$1-2 per task

**Examples:**
- Analyze screenshots/images
- Parse long PDF documents
- Extract data from videos
- Research across many sources

---

### 🚀 Grok (xAI Grok API)
**Status:** API configured  
**Use For:**
- Real-time web data (Twitter/X integration)
- Social media analysis
- Trend spotting
- Market research
- Snarky/witty content generation

**Why:** Real-time access to X, fast inference.

**Cost:** ~$1-2 per task

**Examples:**
- Twitter sentiment analysis
- Trending topic research
- Competitive intel from social
- Generate viral tweet ideas

---

## 🎮 Routing Logic (Updated)

### Task arrives → Route to:

**"Build Stripe integration"**  
→ **Codex** (production coding)

**"Create landing page for golf coaching"**  
→ **Codex** (coding) + **Opus** (copy/UX strategy)

**"Generate 7 tweet drafts"**  
→ **Sonnet** (fast content generation)

**"Analyze this dashboard screenshot"**  
→ **Gemini** (multimodal)

**"What's trending on Twitter about side hustles?"**  
→ **Grok** (real-time X data)

**"Write strategic plan for $500 MRR"**  
→ **Opus** (deep reasoning)

**"Update Florida Freedom Dashboard data"**  
→ **Sonnet** (quick task)

---

## 🏗️ Implementation (autonomous_check.py)

**Model selection keywords:**

```python
# Codex (production coding)
if any(word in task for word in [
    "build", "integrate", "api", "feature", 
    "frontend", "backend", "code", "database"
]):
    model = "codex"

# Opus (strategic + revenue-critical)
elif any(word in task for word in [
    "landing page", "strategy", "architecture",
    "revenue", "conversion", "critical"
]):
    model = "opus"

# Gemini (multimodal)
elif any(word in task for word in [
    "analyze image", "screenshot", "video",
    "pdf", "document", "extract data"
]):
    model = "gemini"

# Grok (real-time social)
elif any(word in task for word in [
    "twitter", "trending", "social", "viral",
    "x.com", "sentiment"
]):
    model = "grok"

# Sonnet (default for everything else)
else:
    model = "sonnet5"
```

---

## 💰 Cost Breakdown (Estimated)

**Per Build:**
- Codex: $2-4
- Opus: $3-5
- Sonnet: $0.50-1
- Gemini: $1-2
- Grok: $1-2

**Monthly Target:** <$200/month for full automation

**ROI Threshold:** If a build saves 1+ hour or generates $10+, cost doesn't matter.

---

## 🎯 The Coding Arms Structure

```
Ross (CEO - Sets Direction)
  │
  └─ Jarvis (Chief of Staff - Delegates & Coordinates)
       │
       ├─ Codex (Lead Engineer - Production Coding)
       ├─ Opus (Chief Strategist - Deep Reasoning)
       ├─ Sonnet (Workhorse - Content & Tasks)
       ├─ Gemini (Analyst - Multimodal & Research)
       └─ Grok (Scout - Real-Time Intel)
```

**How It Works:**
1. Ross tells Jarvis what needs to happen
2. Jarvis routes to the right specialist
3. Specialist builds and reports back to Jarvis
4. Jarvis delivers result to Ross
5. Repeat

---

## 🔄 Override Rules

**Manual Override:** Can specify model in BUILD_QUEUE.md
```markdown
- [ ] Build X - Model: codex
```

**Force Specific Model:**
```bash
python3 scripts/autonomous_check.py --model opus
```

**Session Override:** Tell Jarvis directly
```
"Use Codex for this build"
"Let Gemini analyze this image"
```

---

*Updated: 2026-02-07*  
*Next: Update autonomous_check.py with Gemini/Grok routing*
