# Outreach Optimization Guide

Complete guide to the self-optimizing outreach system.

---

## How It Works

The system uses **evolutionary A/B testing** to continuously improve your outreach messages:

1. **Generate** 10 variations for each product/audience
2. **Test** by sending each variation to balanced samples
3. **Track** opens, replies, and conversions
4. **Learn** which approaches work best
5. **Evolve** new variations based on winners
6. **Repeat** → messages get 3-5x better over weeks

---

## The Four Engines

### 1. Message Generator
**File:** `sales/message_generator.py`

Generates 10 different approaches:
- Direct approach
- Personal story first
- Question-led
- Problem-focused
- Solution-focused
- Social proof
- Scarcity/urgency
- Curiosity hook
- Compliment-first
- Value proposition

**Usage:**
```python
from sales.message_generator import MessageGenerator

generator = MessageGenerator()

variations = generator.generate_variations(
    product="FitTrack",
    target_audience="indie makers",
    pain_point="forget to track workouts",
    benefit="never miss a workout again",
    lead_context={"name": "Alex", "achievement": "building in public"}
)

# Returns 10 personalized variations ready to send
```

### 2. Response Tracker
**File:** `sales/response_tracker.py`

Tracks outcomes for every message:
- When sent
- When opened (if detectable)
- When replied
- When converted (signup/purchase)
- Time to reply

**Usage:**
```python
from sales.response_tracker import ResponseTracker

tracker = ResponseTracker()

# Log a send
tracker.log_send(
    message_id="msg_001",
    lead="username",
    variation="personal_story_v1",
    approach="personal_story",
    message_content="Full message text..."
)

# Log outcomes
tracker.log_reply("msg_001")
tracker.log_signup("msg_001")

# Get metrics
metrics = tracker.get_metrics(approach="personal_story")
print(f"Reply rate: {metrics['reply_rate']*100:.1f}%")
```

### 3. Learning Engine
**File:** `sales/learning_engine.py`

Analyzes results and identifies patterns:
- Winner (best performing approach)
- Losers (underperformers to eliminate)
- Insights (what's working and why)
- Recommendations (what to do next)

**Usage:**
```python
from sales.learning_engine import LearningEngine

engine = LearningEngine()

# Generate report after 50+ sends
report = engine.generate_report(min_sends=50)
print(report)

# Output:
# Winner: personal_story (41.2% reply rate)
# Insights: Personal approach converts 2.7x better
# Recommendations: Generate 3 new variations based on personal_story
```

### 4. Evolution Engine
**File:** `sales/evolution_engine.py`

Generates new variations from winners:
- Amplify what works
- Create hybrids
- Mutate for variation
- Test extreme versions

**Usage:**
```python
from sales.evolution_engine import EvolutionEngine

engine = EvolutionEngine()

# Check if ready to evolve
decision = engine.should_evolve()

if decision["should_evolve"]:
    # Generate generation 2 variations
    evolved = engine.evolve_messages(
        product="FitTrack",
        audience="indie makers",
        pain_point="forget workouts",
        benefit="never miss a workout",
        generation=2
    )
    
    # Test these new variations against gen 1 winners
```

---

## Integration with Sales Mode

The system integrates seamlessly with existing sales workflows.

### Method 1: Automatic (Recommended)

When you activate sales mode, it automatically:
1. Generates variations for each lead
2. Picks which variation to send (balanced A/B)
3. Tracks sends and outcomes
4. Learns and evolves after thresholds

### Method 2: Manual Control

```python
# In your sales script
from sales.message_generator import MessageGenerator
from sales.response_tracker import ResponseTracker

generator = MessageGenerator()
tracker = ResponseTracker()

# For each lead
variations = generator.generate_variations(
    product=YOUR_PRODUCT,
    target_audience=AUDIENCE,
    pain_point=PAIN,
    benefit=BENEFIT,
    lead_context={"name": lead.name, "achievement": lead.bio}
)

# Pick variation to send
selected = generator.pick_variation(variations, strategy="random")

# Send message (your sending logic)
send_dm(lead.username, selected["message"])

# Log it
tracker.log_send(
    message_id=f"msg_{timestamp}",
    lead=lead.username,
    variation=selected["variation_id"],
    approach=selected["approach"],
    message_content=selected["message"]
)

# Later, when they reply:
tracker.log_reply(message_id)
```

---

## Data Requirements

### Minimum for insights:
- **10 sends** per variation = early signals
- **20 sends** per variation = reliable patterns
- **50 total sends** = confident learning

### When to evolve:
- **After 50-100 sends**: First evolution
- **Every 100 sends**: Subsequent evolutions
- **Or when winner hits 40%+ reply rate**: Test bolder versions

---

## Metrics Explained

### Reply Rate
Most important metric. % of messages that get a response.
- **< 10%**: Something's wrong - rethink approach entirely
- **10-20%**: Normal, room for improvement
- **20-30%**: Good performance
- **30-40%**: Excellent
- **40%+**: Exceptional - capture and replicate this!

### Open Rate
Less reliable (hard to track), but useful when available.
- High opens + low replies = message doesn't deliver on promise
- Low opens = subject line or targeting issue

### Conversion Rate
% that lead to actual signups/sales.
- Ultimately what matters
- But reply rate is leading indicator

### Time to Reply
How long before they respond.
- Faster replies = higher interest
- Track by approach to see what creates urgency

---

## Dashboard

**File:** `sales/outreach_dashboard.html`

Open in browser to see:
- Real-time metrics
- Leaderboard of approaches
- Current insights
- Actionable recommendations

**View dashboard:**
```bash
open ~/clawd/sales/outreach_dashboard.html
```

Updates automatically every 30 seconds when open.

---

## Evolution Strategies

### Week 1: Baseline Testing
- Send 10 original variations
- Balance sends across all approaches
- Collect 50-100 data points
- No premature optimization

### Week 2: First Evolution
- Identify winner (likely 2-3x better than worst)
- Generate 8 new variations based on winner
- Keep 2 best from week 1 as control
- Test new vs. old

### Week 3: Double Down
- If gen 2 beats gen 1: Evolve again
- If gen 1 still wins: Amplify original winner more
- Eliminate bottom 30% performers entirely

### Week 4: Optimization
- By now, best messages are 3-5x better than originals
- Test small tweaks to winning formula
- Maintain 80/20: 80% winning approach, 20% experiments

---

## When to Trust the Data

### Trust it when:
- ✅ 50+ total sends
- ✅ At least 10 sends per variation
- ✅ Clear winner (2x+ better than average)
- ✅ Consistent across multiple days

### Don't trust it when:
- ❌ < 20 total sends
- ❌ Only 1-2 sends per variation
- ❌ All variations performing identically (sample size too small)
- ❌ Wild day-to-day swings (wait for stability)

---

## Adding New Variations

### Step 1: Edit Message Generator

```python
# In sales/message_generator.py

def _generate_your_new_approach(self, product, audience, pain, benefit, context) -> str:
    lead_name = context.get("name", "there")
    
    msg = f"Hey {lead_name},\n\n"
    msg += "Your unique hook here...\n\n"
    msg += f"Something about {product} and {benefit}.\n\n"
    msg += "Call to action?\n\n"
    msg += "- Ross"
    
    return msg
```

### Step 2: Add to Approaches Dictionary

```python
self.approaches = {
    # ... existing approaches ...
    "your_new_approach": self._generate_your_new_approach,
}
```

### Step 3: Test It

```bash
python3 sales/message_generator.py
```

---

## CLI Quick Reference

### Generate variations
```bash
python3 sales/message_generator.py
```

### View metrics
```bash
python3 sales/response_tracker.py
```

### Generate learning report
```bash
python3 sales/learning_engine.py
```

### Check if ready to evolve
```bash
python3 sales/evolution_engine.py
```

---

## Common Patterns We've Learned

Based on testing across products:

### What Usually Works:
- **Personal stories** (builds connection)
- **Specific problem focus** (shows you understand)
- **Question-led** (creates engagement)
- **Short messages** (< 100 words)
- **One clear CTA** (not multiple asks)

### What Usually Fails:
- **Generic pitches** (no personalization)
- **Scarcity tactics** (feels manipulative)
- **Feature dumps** (nobody cares about features)
- **Long messages** (> 200 words)
- **Multiple CTAs** (confusing)

---

## Troubleshooting

### "Not enough data" errors
**Solution:** Keep sending. Need minimum 50 sends.

### All variations performing the same
**Solution:** Sample size too small OR targeting is off (no message will work on wrong audience).

### Winner not improving in evolution
**Solution:** You've hit local maximum. Try completely different approaches, not just variations of winner.

### Reply rate dropped after evolution
**Solution:** Small sample variance. Send 20+ of new gen before comparing.

### Dashboard not updating
**Solution:** Refresh browser. Data updates when new entries are added to responses.jsonl.

---

## Best Practices

1. **Test on consistent audience** - Don't switch target audiences mid-test
2. **Send at consistent times** - Time of day affects open/reply rates
3. **Track external factors** - Product launches, holidays affect results
4. **Don't over-optimize** - 30-40% reply rate is amazing, don't chase 100%
5. **Keep controls** - Always send some of proven winner alongside tests
6. **Document context** - Note what's happening when performance shifts

---

## Future Enhancements

Coming soon:
- Subject line A/B testing
- Follow-up sequence optimization
- Sentiment analysis of replies
- Automated lead scoring based on reply quality
- Multi-variate testing (approach + timing + audience)

---

## Success Stories

Once you have data, document what works:

```markdown
## What Works for FitTrack + Indie Makers

Winner: Personal story approach
Reply rate: 41.2%
Key elements:
- Opens with personal struggle
- Shows vulnerability
- Quick turnaround story (2 weeks to build)
- Invites without pressuring

Sample message:
[paste actual winning message]

Avoid:
- Direct pitches (13% reply rate)
- Scarcity tactics (18% reply rate)
```

---

**The system learns. You win. Start testing today.** 🚀
