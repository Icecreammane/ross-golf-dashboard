# 🧠 Outcome Learning System

**Learn what Ross actually values by tracking suggestion outcomes.**

## Overview

This system logs every suggestion the agent makes, tracks whether Ross implements them, measures outcomes, and learns patterns to improve future suggestions.

## Quick Start

### 1. Initialize Database
```bash
cd learning
python3 db.py
```

### 2. Log a Suggestion
```bash
python3 log_suggestion.py "Build a dashboard" productivity high "We need visibility into patterns"
```

### 3. Track Outcome
```bash
# List recent untracked suggestions
python3 track_outcome.py --list

# Mark one as implemented
python3 track_outcome.py 1 implemented success "Ross loved it!"
```

### 4. Analyze Patterns
```bash
python3 analyze_patterns.py
```

### 5. View Dashboard
```bash
# Generate dashboard data
python3 analyze_patterns.py --json > dashboard_data.json

# Serve the dashboard
python3 -m http.server 8000

# Open: http://localhost:8000/dashboard.html?data=dashboard_data.json
```

## Agent Integration

The main agent should use `agent_integration.py` for easy integration:

```python
from learning.agent_integration import OutcomeLearner

learner = OutcomeLearner(session_id="main-chat")

# Before making a suggestion, check if category is well-received
guidance = learner.should_suggest_category('productivity')
if guidance['recommend']:
    # Make the suggestion
    suggestion_id = learner.suggest(
        text="Let's build a notification system",
        category="productivity",
        confidence="high",
        context="Ross mentioned wanting alerts"
    )
    
    # Later, when Ross responds...
    if learner.detect_response(ross_message):
        # Automatically tracked!
        pass

# Get weekly summary
print(learner.weekly_summary())

# Get current insights
insights = learner.get_insights()
for insight in insights['insights']:
    print(insight)
```

## Auto-Detection

The system automatically detects Ross's responses:

**Positive (→ implemented):**
- "yes", "yeah", "sure", "ok", "sounds good"
- "let's do it", "go for it", "build it"
- "absolutely", "definitely", "perfect"

**Negative (→ rejected):**
- "no", "nah", "nope", "not now"
- "skip", "pass", "ignore", "forget it"
- "not interested", "waste of time"

**Deferred (→ deferred):**
- "later", "maybe", "eventually", "someday"
- "let's wait", "hold off", "come back to"
- "not yet", "not priority"

## Database Schema

### `suggestions` table
- `id`: Primary key
- `timestamp`: Unix timestamp
- `text`: Suggestion text
- `category`: productivity, fun, revenue, infrastructure, learning, health, social, other
- `confidence`: high, medium, low
- `context`: Why this was suggested
- `session_id`: Optional session identifier

### `outcomes` table
- `id`: Primary key
- `suggestion_id`: Foreign key to suggestions
- `status`: implemented, ignored, deferred, rejected, in_progress
- `result`: success, failure, partial, unknown
- `notes`: Additional context
- `timestamp`: Unix timestamp

### `patterns` table
- Cached pattern insights updated by `analyze_patterns.py --update-cache`

## Learning Patterns

The system learns:

1. **Category Success Rate**: Which types of suggestions Ross implements most
2. **Confidence Accuracy**: How accurate the agent's confidence levels are
3. **Timing Patterns**: When suggestions are best received (hour/day)
4. **Success Factors**: What implemented suggestions actually work
5. **Ross's Priorities**: What topics he cares about vs. ignores

## Files

- `db.py` - Database utilities
- `log_suggestion.py` - Log suggestions (CLI & module)
- `track_outcome.py` - Track outcomes (CLI & module)
- `analyze_patterns.py` - Pattern analysis (CLI & module)
- `agent_integration.py` - Easy agent integration
- `dashboard.html` - Visual dashboard
- `suggestions.db` - SQLite database (created on first run)

## Usage Examples

### CLI Usage
```bash
# Log a suggestion
python3 log_suggestion.py "Add email notifications" productivity high

# List untracked suggestions
python3 track_outcome.py --list

# Track an outcome
python3 track_outcome.py 5 implemented success "Working great!"

# Analyze patterns
python3 analyze_patterns.py

# Get JSON output
python3 analyze_patterns.py --json

# Update pattern cache
python3 analyze_patterns.py --update-cache
```

### Python Module Usage
```python
# Simple functions
from learning.agent_integration import suggest, check_category, get_summary

# Log a suggestion
suggestion_id = suggest("Build feature X", "productivity", "high")

# Check if category is good
result = check_category("fun")
print(result['recommend'])  # True/False
print(result['reason'])

# Get weekly summary
print(get_summary(days=7))
```

### Advanced Usage
```python
from learning.agent_integration import OutcomeLearner

learner = OutcomeLearner()

# Make a suggestion
sid = learner.suggest("Try this approach", "productivity", "medium")

# Later, when Ross responds...
learner.mark(sid, "implemented", "success", "Worked perfectly")

# Get insights
insights = learner.get_insights()
print(insights['stats'])  # Overall statistics
print(insights['by_category'])  # Category breakdown

# Check if a category is recommended
guidance = learner.should_suggest_category('revenue')
if guidance['recommend'] and guidance['confidence'] > 0.7:
    print("High confidence that Ross will value this category")
```

## Integration with Main Agent

Add to the main agent's workflow:

1. **Before suggesting**: Check `should_suggest_category()` to see if Ross typically values this type
2. **When suggesting**: Call `suggest()` to log it
3. **After Ross responds**: Use `detect_response()` or `track_pending()` to auto-track
4. **Periodically**: Run `weekly_summary()` in heartbeats
5. **Weekly**: Review insights with `get_insights()`

## Success Metrics

Track these over time:
- Implementation rate trending up (agent learning what works)
- Confidence accuracy improving (better at predicting)
- Category distribution matching Ross's actual priorities
- Success rate of implemented suggestions staying high

## Maintenance

**Daily**: Auto-track outcomes as conversations happen

**Weekly**: 
- Review `weekly_summary()`
- Update patterns: `python3 analyze_patterns.py --update-cache`
- Review dashboard

**Monthly**:
- Deep analysis of patterns
- Adjust suggestion strategy based on learnings
- Clean up old data if needed (keep at least 3 months for patterns)

## Future Enhancements

Potential additions:
- Time-based patterns (best time to suggest)
- Topic clustering (what themes work together)
- Context analysis (what surrounding context predicts success)
- Ross's mood detection
- Suggestion fatigue detection (too many suggestions = lower acceptance)
- A/B testing different phrasing approaches

---

Built to make the agent actually learn what Ross values, not just suggest blindly.
