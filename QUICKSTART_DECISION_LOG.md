# Decision Log System - Quick Start Guide

**Get started in 5 minutes**

## What is this?

A production-ready decision tracking and ROI feedback loop that:
- ✅ Logs every decision you make on opportunities
- 📊 Tracks conversion rates by source and type
- 💰 Calculates ROI per decision type
- 💡 Generates insights automatically
- 🔮 Predicts outcomes for new opportunities
- 📈 Improves scoring over time based on actual results

## Quick Test Run

```bash
# Generate 30 days of sample data and run all tests
cd ~/clawd
python3 scripts/test_decision_system.py
```

This creates realistic sample data showing how the system works.

## View Results

### Check Conversion Rates
```bash
python3 scripts/decision_log.py conversions
```

**Example Output:**
```
email → golf_coaching
  Conversion rate: 78.6%
  Revenue: $5,775.74
  Decisions: 14

twitter → golf_coaching
  Conversion rate: 65.0%
  Revenue: $4,313.12
  Decisions: 20
```

### See Insights
```bash
python3 scripts/decision_log.py insights
```

**Example Output:**
```
Email converts best
  Email golf_coaching opportunities convert at 78.6% (14 decisions)
  Confidence: 90%

Partnership generates most revenue
  $7,231.16 total from 27 decisions ($314.40 avg)
```

### ROI Analysis
```bash
python3 scripts/decision_log.py roi
```

**Shows:** Total revenue, average per decision, closed deals by type

### Daily Summary
```bash
python3 scripts/decision_summary.py
```

**Generates:**
- JSON: `reports/decision-summaries/decision-summary-YYYY-MM-DD.json`
- Markdown: `reports/decision-summaries/decision-summary-YYYY-MM-DD.md`

## Real-World Usage

### 1. Log a Decision

When you decide to act on an opportunity:

```python
from decision_log import DecisionLog

log = DecisionLog()

# Someone tweets asking about golf coaching
log.log_decision(
    decision_id="dec_001",  # Unique ID
    opportunity_type="golf_coaching",
    opportunity_source="twitter",
    action_taken="Replied with coaching offer and Calendly link",
    opportunity_content="@jarvis Can you help me fix my slice?",
    opportunity_score=87,
    sender="@golfer_mike"
)
```

### 2. Record the Outcome

When you know what happened:

```python
# They booked a session and paid $250
log.record_outcome(
    decision_id="dec_001",
    outcome_type="conversion",
    outcome_status="success",
    revenue_generated=250.00,
    customer_acquired=True,
    deal_closed=True,
    notes="Booked 2-session package via Stripe"
)
```

### 3. Score New Opportunities

Use historical data to score new opportunities:

```python
from opportunity_scorer import OpportunityScorer

scorer = OpportunityScorer()

# New opportunity arrives
new_opp = {
    'type': 'golf_coaching',
    'source': 'email',
    'score': 75,  # Base score
    'content': 'Looking for golf lessons',
    'sender': 'john@example.com'
}

enhanced = scorer.score_opportunity(new_opp)

print(f"Original score: {enhanced['original_score']}")
print(f"Adjusted score: {enhanced['adjusted_score']}")  # Higher because golf coaching converts well!
print(f"Predicted revenue: ${enhanced['predicted_revenue']:.2f}")
print(f"Conversion probability: {enhanced['conversion_probability']:.1f}%")
print(f"Recommendation: {enhanced['recommendation']}")
```

**Example Output:**
```
Original score: 75
Adjusted score: 92  ← Increased because email golf coaching converts at 78.6%!
Predicted revenue: $359.23
Conversion probability: 78.6%
Recommendation: HIGH PRIORITY - Respond immediately, high conversion likelihood
```

## Integration with Opportunity Aggregator

The system works with your existing opportunity aggregator:

```bash
# 1. Aggregator runs (existing)
python3 scripts/opportunity_aggregator.py
# → Creates data/opportunities.json

# 2. Score with historical data (NEW)
python3 scripts/opportunity_scorer.py
# → Creates data/opportunities_scored.json with enhanced scores

# 3. Act on top opportunities
# (Your existing handling code)

# 4. Log decision
# (Use decision_log.py)

# 5. Record outcome when known
# (Use decision_log.py)

# 6. System learns and improves future scores automatically!
```

## What Gets Better Over Time

As you log more decisions and outcomes:

1. **Conversion rates become more accurate**
   - "Email converts 78.6% vs Twitter 65%"
   
2. **Revenue predictions improve**
   - "Golf coaching typically generates $350"
   
3. **Opportunity scoring gets smarter**
   - Automatically boosts scores for high-converting types
   - Lowers scores for low-converting types
   
4. **Insights reveal patterns**
   - "Partnerships take ~15 days to close"
   - "Twitter inquiries convert 2x slower than email"
   
5. **Predictions become more confident**
   - "This looks like your best customers (90% confidence)"

## File Locations

**Scripts:**
- `scripts/decision_log.py` - Core logger
- `scripts/opportunity_scorer.py` - Enhanced scoring
- `scripts/decision_summary.py` - Reporting
- `scripts/test_decision_system.py` - Test suite

**Data:**
- `data/decision_log.db` - SQLite database
- `data/opportunities_scored.json` - Enhanced scores

**Reports:**
- `reports/decision-summaries/` - Daily/weekly summaries

## CLI Commands

```bash
# Daily summary
python3 scripts/decision_summary.py

# Specific date
python3 scripts/decision_summary.py date 2026-02-08

# Weekly summary
python3 scripts/decision_summary.py weekly

# Conversion rates
python3 scripts/decision_log.py conversions

# Insights
python3 scripts/decision_log.py insights

# ROI analysis
python3 scripts/decision_log.py roi

# Score opportunities
python3 scripts/opportunity_scorer.py

# Run tests
python3 scripts/test_decision_system.py
```

## Example Workflow

**Morning:**
```bash
# Check yesterday's performance
python3 scripts/decision_summary.py date 2026-02-07

# See what's working
python3 scripts/decision_log.py insights
```

**Throughout the day:**
```python
# Act on opportunities and log decisions
log.log_decision(...)

# When outcomes happen
log.record_outcome(...)
```

**Before prioritizing new opportunities:**
```bash
# Score new opportunities with historical data
python3 scripts/opportunity_scorer.py

# Check enhanced scores
cat data/opportunities_scored.json
```

**Evening:**
```bash
# Generate today's summary
python3 scripts/decision_summary.py
```

## Key Metrics Tracked

1. **Conversion Rate**
   - % of decisions that convert to customers
   - Broken down by source (twitter, email) and type (coaching, partnership)

2. **Revenue per Decision**
   - Average revenue generated per decision
   - Total revenue by type

3. **Time to Conversion**
   - How long from decision to closed deal
   - Helps set expectations

4. **Response Rate**
   - % of decisions that get any response
   - Even if they don't convert

5. **Deal Closure Rate**
   - % of responses that close
   - Quality of leads by source

## Tips

1. **Log everything** - Even "no" responses are valuable data
2. **Be consistent** - Record outcomes promptly for accurate time tracking
3. **Review weekly** - Check insights to spot trends
4. **Trust predictions** - High confidence scores (0.8+) are reliable
5. **Use adjusted scores** - Better than base scores for prioritization

## Troubleshooting

**"No insights generated"**
→ Need 3-5 decisions per type/source for insights

**"Predictions show 0% confidence"**
→ Not enough historical data yet. Keep logging!

**"Conversion rates seem wrong"**
→ Run `python3 scripts/decision_log.py conversions` to verify outcomes are being recorded

## Next Steps

1. ✅ Run test suite: `python3 scripts/test_decision_system.py`
2. ✅ Review sample reports in `reports/decision-summaries/`
3. ✅ Start logging real decisions as they happen
4. ✅ Record outcomes when known
5. ✅ Watch the system learn and improve!

## Full Documentation

See `DECISION_LOG_SYSTEM.md` for complete documentation including:
- Database schema
- API reference
- Advanced usage
- Automation setup
- Integration patterns

---

**Questions?** Check the logs:
- `logs/decision-log.log`
- `logs/opportunity-scorer.log`

Or examine the database:
```bash
sqlite3 data/decision_log.db
sqlite> SELECT * FROM decisions LIMIT 5;
sqlite> SELECT * FROM conversion_metrics;
```
