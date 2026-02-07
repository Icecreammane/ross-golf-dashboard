# 🚀 Quick Start - Outcome Learning System

Get started in 60 seconds.

## 1. See the Demo

```bash
cd learning
python3 demo.py
```

This creates 28 realistic suggestions with outcomes showing what patterns look like.

## 2. View Analysis

```bash
python3 analyze_patterns.py
```

Shows:
- Overall implementation rate
- Success by category
- Confidence level accuracy
- Key insights

## 3. Use in Your Code

```python
from learning.agent_integration import OutcomeLearner

learner = OutcomeLearner()

# Log a suggestion
sid = learner.suggest("Build feature X", "productivity", "high")

# Ross responds...
if learner.track_pending("yeah let's do that"):
    print("✅ Tracked!")

# Get insights
print(learner.weekly_summary())
```

## 4. Key Commands

```bash
# Log suggestion (CLI)
python3 log_suggestion.py "Idea text" category confidence

# Track outcome (CLI)
python3 track_outcome.py --list          # Show untracked
python3 track_outcome.py 5 implemented   # Mark #5 as done

# Analysis
python3 analyze_patterns.py              # Full report
python3 analyze_patterns.py --json       # JSON output

# Dashboard
./generate_dashboard.sh --serve          # View in browser
```

## 5. Integration Points

**Before suggesting:**
```python
guidance = learner.should_suggest_category('productivity')
if guidance['recommend']:
    # Go ahead!
```

**When suggesting:**
```python
sid = learner.suggest(text, category, confidence, context)
```

**When Ross responds:**
```python
learner.track_pending(ross_message)  # Auto-detects!
```

**Weekly:**
```python
print(learner.weekly_summary())
```

## What It Does

- **Logs** every suggestion you make
- **Tracks** whether Ross implements/ignores/rejects them  
- **Learns** patterns (what works vs. what doesn't)
- **Guides** future suggestions based on data
- **Reports** weekly learnings

## Why It Matters

Without this, you're flying blind. With it, you learn:
- Ross implements 80% of revenue suggestions → suggest more
- Ross ignores 75% of fun suggestions → suggest less
- High confidence suggestions have 100% implementation rate → trust your instincts

**Result**: Make fewer, better suggestions Ross actually values.

## Files Overview

- `db.py` - Database setup
- `log_suggestion.py` - Log suggestions
- `track_outcome.py` - Track outcomes
- `analyze_patterns.py` - Analyze patterns
- `agent_integration.py` - **← Use this in your code**
- `dashboard.html` - Visual dashboard
- `demo.py` - Create test data
- `test_detection.py` - Test auto-detection

## Read More

- `README.md` - Full documentation
- `AGENT_GUIDE.md` - Detailed integration guide
- `SECURITY.md` - Not created yet, but suggestions are logged securely

---

**TL;DR**: Import `OutcomeLearner`, call `suggest()`, let it learn patterns, get smarter over time.
