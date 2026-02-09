# Caption Optimizer - Quick Start

**Get optimized social captions in 60 seconds**

---

## ⚡ 60-Second Setup

```bash
# 1. Make sure Ollama is running
ollama list

# 2. Pull the model (if needed)
ollama pull qwen2.5:14b

# 3. Test it
~/clawd/scripts/optimize-caption "Just launched my new product"
```

**Done!** You'll get 3 caption variations in <2s.

---

## 🎯 Daily Usage

### Most Common: Text Only

```bash
optimize-caption "Your rough idea here"
```

**Example:**
```bash
optimize-caption "Launched my golf coaching app after 6 months"
```

**Output:** 3 variations (viral, professional, casual) with hashtags

### With Image

```bash
optimize-caption "Caption idea" --image ~/photo.jpg
```

**Example:**
```bash
optimize-caption "New swing analysis feature" --image ~/golf-screenshot.png
```

### Pick Specific Tones

```bash
optimize-caption "Idea" --tones viral professional
```

---

## 📊 Learning System (Optional but Powerful)

### Track What Works

After posting, log the engagement:

```bash
optimize-caption --log-engagement post_001 viral --likes 142 --retweets 28
```

### See What's Working

```bash
optimize-caption --stats
```

**Output:**
```
Best performing tone: viral
  viral        - Likes: 127.3  Retweets: 23.5
  professional - Likes: 89.1   Retweets: 12.3
  casual       - Likes: 156.2  Retweets: 18.7
```

System automatically uses best-performing tone in future suggestions.

---

## 🔗 Integrate with Social Scheduler

One command optimizes your entire queue:

```bash
optimize-caption --integrate-scheduler
```

This optimizes all unposted items in `~/clawd/data/social-posts-queue.json`

---

## 🎨 Tone Guide

**Viral** 🔥  
Max engagement, controversial, punchy  
→ Use for: Growth, reach, hot takes

**Professional** 💼  
Authoritative, credible, valuable  
→ Use for: B2B, thought leadership, expertise

**Casual** 💬  
Relatable, personal, conversational  
→ Use for: Personal brand, stories, authenticity

---

## 🏃 Real Workflow

**Morning content routine (5 min):**

```bash
# Generate today's captions
optimize-caption "Golf tip: rotation beats arm strength"
optimize-caption "Built a new feature over the weekend"
optimize-caption "Productivity tip: time blocking"

# Pick best variations
# Post via scheduler or manually
# Done!
```

---

## 🐛 Troubleshooting

**"Ollama not running"**
```bash
ollama serve &
```

**"Model not found"**
```bash
ollama pull qwen2.5:14b
```

**Slow (>3s)**
- First run is slower (cold start)
- Run again, should be <2s
- Check: `ollama list` (model loaded?)

---

## 📖 Full Docs

See `CAPTION_OPTIMIZER.md` for:
- Complete API reference
- Advanced features
- Customization options
- Integration guides
- Best practices

---

## 🎯 Pro Tips

1. **Be specific in input:** "Launched app, 500 users" beats "app update"
2. **Log consistently:** 20+ posts with engagement = good learning data
3. **Match tone to platform:** Viral for Twitter, Professional for LinkedIn
4. **Test both:** Generate all 3, see what resonates with YOUR audience

---

**Need help?** Run test suite: `python3 ~/clawd/scripts/test_caption_optimizer.py`
