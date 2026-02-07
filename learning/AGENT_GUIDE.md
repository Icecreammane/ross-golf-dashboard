# 🤖 Agent Integration Guide

## Quick Start for Main Agent

### Step 1: Import the Module

```python
from learning.agent_integration import OutcomeLearner
```

### Step 2: Create a Learner Instance

```python
# At the start of a conversation session
learner = OutcomeLearner(session_id="main-session")
```

### Step 3: Use in Your Workflow

## Pattern: Smart Suggestions

**Before making a suggestion, check if the category is well-received:**

```python
# Check if Ross typically values this type of suggestion
guidance = learner.should_suggest_category('productivity')

if guidance['recommend'] and guidance['confidence'] > 0.6:
    # Ross typically likes this category - suggest away!
    suggestion_id = learner.suggest(
        text="Let's build automated backups",
        category="productivity",
        confidence="high",
        context="Ross mentioned wanting more security"
    )
    
    # Tell Ross
    print(f"💡 Suggestion: Let's build automated backups")
else:
    # Ross doesn't usually implement this category
    # Either skip or phrase more carefully
    print(f"ℹ️  {guidance['reason']}")
```

## Pattern: Auto-Track Responses

**After Ross responds, automatically detect and track:**

```python
# Ross says something
ross_message = "yeah let's do that"

# Try to detect and track
if learner.track_pending(ross_message):
    # Automatically detected and tracked!
    print("✅ Outcome tracked")
else:
    # No clear response detected, or no pending suggestion
    pass
```

## Pattern: Manual Tracking

**For complex situations, manually track:**

```python
# Later, when you observe Ross actually using the feature
learner.mark(
    suggestion_id=123,
    status="implemented",
    result="success",
    notes="Ross uses this daily now"
)
```

## Pattern: Weekly Check-In

**Add to heartbeat routine:**

```python
def heartbeat():
    # ... other checks ...
    
    # Every Sunday at 9am, show weekly summary
    if is_sunday() and hour == 9:
        summary = learner.weekly_summary(days=7)
        send_message(summary)
        
        # Get insights
        insights = learner.get_insights()
        if insights['insights']:
            send_message("\n💡 What I learned:")
            for insight in insights['insights']:
                send_message(f"  • {insight}")
```

## Pattern: Category Guidance

**Adapt suggestions based on learned patterns:**

```python
def should_i_suggest(category: str, topic: str) -> bool:
    """Decide if a suggestion is worth making."""
    
    guidance = learner.should_suggest_category(category)
    
    # High confidence + recommended = definitely suggest
    if guidance['recommend'] and guidance['confidence'] > 0.7:
        return True
    
    # Low confidence or not recommended = skip
    if not guidance['recommend'] or guidance['confidence'] < 0.4:
        return False
    
    # Medium confidence = suggest but less aggressively
    return random.random() < guidance['confidence']
```

## Complete Example Workflow

```python
from learning.agent_integration import OutcomeLearner

class SmartAgent:
    def __init__(self):
        self.learner = OutcomeLearner(session_id="main")
        self.pending_suggestion = None
    
    def make_suggestion(self, idea: str, category: str):
        """Make a smart suggestion based on learned patterns."""
        
        # Check if this category is typically well-received
        guidance = self.learner.should_suggest_category(category)
        
        if not guidance['recommend'] and guidance['sample_size'] >= 5:
            # Ross has rejected this category multiple times
            print(f"⚠️  Skipping: {guidance['reason']}")
            return
        
        # Adjust confidence based on category history
        if guidance['confidence'] > 0.8:
            confidence = "high"
        elif guidance['confidence'] > 0.5:
            confidence = "medium"
        else:
            confidence = "low"
        
        # Log the suggestion
        self.pending_suggestion = self.learner.suggest(
            text=idea,
            category=category,
            confidence=confidence,
            context=f"Based on {guidance['sample_size']} prior {category} suggestions"
        )
        
        # Present to Ross
        print(f"💡 {idea}")
        if confidence == "low":
            print(f"   (Just an idea - I know you don't usually implement {category} suggestions)")
    
    def handle_ross_response(self, message: str):
        """Handle Ross's response to any suggestion."""
        
        # Try auto-detection
        if self.learner.track_pending(message):
            print("✅ Tracked your response")
            self.pending_suggestion = None
    
    def weekly_review(self):
        """Run weekly review and learning."""
        
        print("\n" + "="*60)
        print("📊 WEEKLY LEARNING SUMMARY")
        print("="*60 + "\n")
        
        # Show summary
        print(self.learner.weekly_summary(days=7))
        print()
        
        # Show insights
        insights = self.learner.get_insights()
        print("💡 What I learned about you this week:\n")
        for insight in insights['insights']:
            print(f"  • {insight}")
        
        print("\n" + "="*60 + "\n")
        
        # Show category guidance
        print("🎯 Recommendation: Focus on these categories:\n")
        for category in ['productivity', 'revenue', 'learning', 'fun', 'infrastructure']:
            guidance = self.learner.should_suggest_category(category)
            if guidance['recommend'] and guidance['sample_size'] >= 3:
                emoji = "✅" if guidance['confidence'] > 0.7 else "⚠️"
                print(f"  {emoji} {category:14s}: {guidance['reason']}")
        
        print()

# Usage
agent = SmartAgent()

# Make suggestions intelligently
agent.make_suggestion("Build automated backups", "productivity")

# Ross responds
agent.handle_ross_response("yeah let's do that")

# Weekly review
agent.weekly_review()
```

## Key Functions Reference

### `OutcomeLearner` Class

#### `suggest(text, category, confidence, context)`
Log a suggestion. Returns suggestion ID.

**Categories**: `productivity`, `fun`, `revenue`, `infrastructure`, `learning`, `health`, `social`, `other`

**Confidence**: `high`, `medium`, `low`

#### `detect_response(user_message)`
Auto-detect if message indicates implemented/rejected/deferred.

Returns: `'implemented'`, `'rejected'`, `'deferred'`, or `None`

#### `track_pending(user_message)`
Try to track the pending suggestion based on user message.

Returns: `True` if tracked, `False` otherwise

#### `mark(suggestion_id, status, result, notes)`
Manually track a suggestion outcome.

**Status**: `implemented`, `ignored`, `deferred`, `rejected`, `in_progress`

**Result**: `success`, `failure`, `partial`, `unknown`

#### `should_suggest_category(category)`
Check if suggestions in this category are well-received.

Returns dict with:
- `recommend`: bool
- `confidence`: float (0-1)
- `reason`: string explanation
- `sample_size`: int
- `data`: category stats (if available)

#### `get_insights()`
Get current learning insights.

Returns dict with:
- `stats`: overall statistics
- `insights`: list of human-readable insights
- `by_category`: category breakdown

#### `weekly_summary(days=7)`
Generate a summary for the last N days.

Returns: formatted string

---

## Tips for Integration

1. **Start Early**: Begin logging suggestions from day 1, even if tracking is imperfect
2. **Be Consistent**: Use consistent categories so patterns emerge
3. **Trust the Data**: After 10+ suggestions per category, the patterns are meaningful
4. **Adapt Over Time**: Ross's preferences may change - recent data matters more
5. **Don't Overfit**: A few rejections doesn't mean never suggest that category again
6. **Use Context**: The `context` field helps you remember WHY you suggested something

## Testing

Run the demo to see it in action:

```bash
cd learning
python3 demo.py
python3 analyze_patterns.py
```

## Monitoring

Add to daily heartbeat:

```python
# Check if we have untracked suggestions
from learning.track_outcome import get_latest_suggestions

untracked = get_latest_suggestions(limit=5)
if len(untracked) > 3:
    print(f"⚠️  {len(untracked)} suggestions need outcome tracking")
```

---

**The goal**: Make fewer, better suggestions that Ross actually values.
