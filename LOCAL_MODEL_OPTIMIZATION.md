# Local Model Optimization Strategy

**Hardware:** Mac mini M4, 16GB RAM, 256GB storage  
**Goal:** Maximize local model usage, save Claude/GPT for strategic work  
**Created:** February 12, 2026

---

## Current Setup

**Models installed (Ollama):**
- `llama3.1:8b` (local-fast) - 8B params, fast, basic quality
- `qwen2.5:14b` (local-brain) - 14B params, good quality, moderate speed

**Current usage:**
- Heartbeats: Qwen 2.5 14B ✅
- Everything else: Claude Sonnet 4.5

**Cost:** ~$150-200/month on Claude

---

## Optimized Setup (Recommended)

### Phase 1: Add Better Local Model (Now)

**Install Qwen 2.5 32B (Q4 quantization):**
```bash
ollama pull qwen2.5:32b-instruct-q4_K_M
```

**Why this model:**
- 32B params = significantly smarter than 14B
- Q4 quantization = fits in 16GB RAM
- Speed: ~10-15 tokens/sec (usable)
- Quality: Near Claude Haiku level
- Alias: `local-smart`

**Expected performance:**
- Code generation: Excellent
- Content writing: Very good
- Reasoning: Good (not Claude Sonnet, but close to Haiku)
- Speed: Slower than 14B, but still responsive

---

## Usage Strategy (What Runs Where)

### Run Locally (Qwen 2.5 32B)

**1. Code Generation (90% of coding tasks)**
- Automation scripts
- Data analysis
- API integrations
- Simple web apps
- Test scripts
- Utility functions

**Savings:** ~$20-30/month

**2. Content Generation (all drafts)**
- Social media posts
- Email drafts
- Blog content
- Product descriptions (Notion templates, golf coaching)
- Marketing copy (first pass)
- Documentation

**Savings:** ~$30-40/month

**3. Research & Summarization**
- Competitor analysis
- Market research
- Document summarization
- Meeting notes
- Technical docs

**Savings:** ~$10-15/month

**4. Data Processing**
- CSV/JSON parsing
- Log analysis
- Report generation
- Analytics summaries

**Savings:** ~$5-10/month

**5. Background Tasks (Overnight)**
- Memory indexing (persistent_memory.py)
- Pattern analysis
- Learning loop
- Content pre-generation
- Proactive research

**Savings:** ~$20-30/month

**6. Routine Automation**
- Heartbeats ✅ (already local)
- Health checks
- Status updates
- Task queue maintenance
- Daily summaries

**Savings:** ~$15-20/month

**7. Interactive Development**
- Live coding sessions (vibe-coding)
- Debugging help
- Stack Overflow replacement
- Quick syntax checks

**Savings:** ~$10-15/month

---

### Keep on Claude Sonnet/GPT (Strategic Work)

**When to use cloud models:**

1. **Strategic Planning**
   - Weekend build strategy
   - Product roadmap
   - Business decisions
   - Architecture design

2. **Complex Reasoning**
   - Multi-step problem solving
   - Tradeoff analysis
   - Risk assessment
   - Decision frameworks

3. **High-Stakes Content**
   - Customer-facing final copy
   - Important emails (executives, clients)
   - Landing page copy (after local draft)
   - Product launch messaging

4. **Deep Analysis**
   - Psychological insights (dating advice)
   - Career strategy
   - Financial planning
   - Life optimization

5. **Real-Time Strategic Conversations**
   - Like this conversation
   - Planning sessions
   - Brainstorming
   - Problem-solving

**Usage estimate:** ~20-30% of current volume  
**Cost:** ~$30-50/month (down from $150-200)

---

## Implementation Steps

### Step 1: Install Better Local Model (5 min)
```bash
# Install Qwen 2.5 32B (quantized for 16GB RAM)
ollama pull qwen2.5:32b-instruct-q4_K_M

# Test it
ollama run qwen2.5:32b-instruct-q4_K_M "Write a Python function to parse CSV files"

# Verify it's fast enough for your needs
```

### Step 2: Update Clawdbot Config (2 min)
```bash
# Add new model alias
# I'll handle this via config.patch
```

### Step 3: Route Tasks to Local Models (10 min)
Update scripts to use local models:
- `scripts/generate_social_posts.py` → Use local-smart
- `scripts/proactive_research.py` → Use local-smart
- `scripts/opportunity_drafter.py` → Use local-smart
- Background automation → Use local-smart
- Interactive coding → Use local-smart

### Step 4: Test Quality (Weekend)
During vibe-coding sessions:
- Test local model for code generation
- Compare output quality
- Measure speed
- Adjust if needed

### Step 5: Monitor & Optimize (Ongoing)
Track:
- Response quality vs Claude
- Speed (tokens/sec)
- Cost savings
- Workflow friction

---

## Model Selection Guide

**For your M4 16GB, here are the tiers:**

### Tier 1: Speed (Current - Keep)
- **Llama 3.1 8B** (local-fast)
- Speed: ~30-40 tokens/sec
- Quality: Basic
- Use: Quick lookups, simple tasks

### Tier 2: Balance (Recommended - Add This)
- **Qwen 2.5 32B Q4** (local-smart)
- Speed: ~10-15 tokens/sec
- Quality: Near Haiku level
- Use: Code, content, research (90% of tasks)

### Tier 3: Quality (Optional - Test Later)
- **Llama 3.3 70B Q3**
- Speed: ~3-5 tokens/sec (slow)
- Quality: Near Sonnet 3.5 level
- Use: Complex reasoning when speed doesn't matter

**My recommendation: Add Tier 2 (Qwen 32B Q4) now. Test Tier 3 later if needed.**

---

## Expected Results

### Before Optimization
- Local models: 10% of tasks (just heartbeats)
- Claude: 90% of tasks
- Cost: ~$150-200/month

### After Optimization
- Local models: 70-80% of tasks
- Claude: 20-30% of tasks (strategic only)
- Cost: ~$30-50/month

**Savings: $100-150/month = $1,200-1,800/year**

---

## Quality Checkpoints

**Test these scenarios with local model:**

1. **Code generation:** "Write a Flask API endpoint for Stripe checkout"
2. **Content:** "Write 3 social media posts about golf coaching"
3. **Research:** "Summarize the top 5 golf coaching apps and their pricing"
4. **Analysis:** "Review this code and suggest improvements"

**If local model quality is 85%+ of Claude Haiku → full send.**  
**If quality is < 80% → adjust, use smaller model, or keep more on Claude.**

---

## Specialized Models (Future Optimization)

**For specific tasks, consider:**

- **Code:** `deepseek-coder:33b` (best coding model at this size)
- **Writing:** `qwen2.5:32b` (already recommended)
- **Chat:** `llama3.3:70b` (if you want smarter conversations)
- **Instruction:** `mistral:7b` (fast, good at following instructions)

**My take:** Start with Qwen 2.5 32B. It's good at everything. Specialize later if needed.

---

## Weekend Integration

**This fits perfectly with weekend builds:**

**Saturday (Golf Coaching Site):**
- Local model generates initial code
- Local model writes copy drafts
- Claude reviews architecture
- Claude polishes customer-facing copy

**Saturday (Notion Templates):**
- Local model writes descriptions
- Local model generates marketing copy
- Claude refines positioning

**Sunday (Product Launch System):**
- Local model generates boilerplate code
- Local model creates templates
- Claude designs system architecture

**Vibe-coding experience:**
- You describe feature
- Local model writes code in real-time
- Fast iteration (no API latency)
- Claude reviews final product

---

## Monitoring Dashboard

**Track these metrics:**

1. **Cost savings:**
   - Claude API calls: Before vs After
   - Monthly spend: Target < $50

2. **Quality:**
   - Local model success rate (% of tasks that don't need revision)
   - User satisfaction (your feedback)

3. **Speed:**
   - Average response time
   - Tokens per second

4. **Usage distribution:**
   - % tasks on local vs cloud
   - Task categorization

**Create simple tracker:** `memory/local-model-stats.json`

---

## Rollback Plan

**If local models aren't good enough:**

1. **Keep heartbeats local** (no quality issues there)
2. **Move code generation back to Claude Haiku** (cheaper than Sonnet)
3. **Keep strategic work on Sonnet** (no change)
4. **Partial optimization:** Still save ~$50-80/month

**But I'm confident Qwen 2.5 32B will handle 70-80% of tasks well.**

---

## Next Steps

**Right now (Ross at work, I handle):**
1. Install Qwen 2.5 32B Q4
2. Update Clawdbot config with new alias
3. Test quality on sample tasks
4. Document performance

**Tonight (8pm session):**
1. Show you local model in action
2. Test during credential rotation
3. Get your quality approval

**This weekend (during builds):**
1. Use local model for all coding
2. Measure speed and quality
3. Adjust routing as needed

---

**Status:** Ready to optimize  
**Next:** Install Qwen 2.5 32B and configure routing  
**Goal:** Save $100-150/month while maintaining quality
