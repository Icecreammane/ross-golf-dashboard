# Decision Log & ROI Feedback Loop System

**Production-ready decision tracking and learning system**

## Overview

The Decision Log System tracks every decision made on opportunities, records outcomes, calculates conversion rates, generates insights, and predicts future outcomes based on historical data.

### Key Features

1. **Decision Logging** - Log every decision with full context
2. **Outcome Tracking** - Record results (revenue, conversions, timing)
3. **Conversion Analytics** - Calculate rates by source and type
4. **ROI Analysis** - Track revenue per decision type
5. **Insight Generation** - Auto-generate insights from patterns
6. **Predictive Scoring** - Score new opportunities based on past performance
7. **Daily Summaries** - Automated reporting
8. **Integration** - Works with existing opportunity aggregator

## Components

### 1. `decision_log.py` - Core Decision Logger

**Purpose:** Tracks decisions and outcomes in SQLite database

**Database Schema:**
- `decisions` - Every decision made (what, when, who, why)
- `outcomes` - Results of decisions (revenue, conversion, timing)
- `conversion_metrics` - Aggregated conversion rates
- `insights` - Generated insights from patterns
- `predictions` - ML-based predictions for opportunities

**Key Methods:**
```python
from decision_log import DecisionLog

log = DecisionLog()

# Log a decision
log.log_decision(
    decision_id="dec_12345",
    opportunity_type="golf_coaching",
    opportunity_source="twitter",
    action_taken="Replied with coaching offer",
    opportunity_content="Can you help fix my slice?",
    opportunity_score=85,
    sender="@golfer123"
)

# Record outcome
log.record_outcome(
    decision_id="dec_12345",
    outcome_type="conversion",
    outcome_status="success",
    revenue_generated=250.00,
    customer_acquired=True,
    deal_closed=True,
    notes="2-session coaching package"
)

# Get conversion rates
rates = log.get_conversion_rates()

# Calculate ROI by type
roi = log.calculate_roi_by_type()

# Generate insights
insights = log.generate_insights()

# Predict outcome for new opportunity
prediction = log.predict_outcome({
    'type': 'golf_coaching',
    'source': 'email',
    'content': '...'
})
```

**CLI Usage:**
```bash
# Daily summary
python3 scripts/decision_log.py summary

# View insights
python3 scripts/decision_log.py insights

# Conversion rates
python3 scripts/decision_log.py conversions

# ROI analysis
python3 scripts/decision_log.py roi
```

### 2. `opportunity_scorer.py` - Enhanced Scoring

**Purpose:** Scores opportunities using historical decision data

**Features:**
- Adjusts scores based on actual conversion rates
- Predicts revenue using past outcomes
- Provides confidence scores
- Generates reasoning for scores

**Usage:**
```python
from opportunity_scorer import OpportunityScorer

scorer = OpportunityScorer()

# Score single opportunity
enhanced = scorer.score_opportunity({
    'type': 'golf_coaching',
    'source': 'twitter',
    'score': 85,
    'content': 'Need golf lessons',
    'sender': '@golfer'
})

# Returns:
# {
#   'original_score': 85,
#   'adjusted_score': 92,  # Increased based on high historical conversion
#   'predicted_revenue': 350.50,
#   'conversion_probability': 75.5,
#   'recommendation': 'HIGH PRIORITY - Respond immediately',
#   'reasoning': 'Score increased from 85 to 92 based on strong historical performance...'
# }

# Score batch of opportunities
opportunities = [...list of opportunities...]
scored = scorer.score_opportunities_batch(opportunities)

# Generate full scoring report
report = scorer.generate_scoring_report(opportunities)
```

**CLI Usage:**
```bash
# Score all opportunities from aggregator
python3 scripts/opportunity_scorer.py

# Output: opportunities_scored.json with enhanced scores
```

**Integration with Opportunity Aggregator:**

The scorer reads from `data/opportunities.json` (output of opportunity_aggregator.py) and writes enhanced scores to `data/opportunities_scored.json`.

### 3. `decision_summary.py` - Daily Reporting

**Purpose:** Generate comprehensive daily and weekly summaries

**Features:**
- Daily decision activity reports
- Revenue tracking
- Insight summaries
- Conversion rate trends
- Markdown and JSON output

**Usage:**
```python
from decision_summary import DecisionSummaryGenerator

generator = DecisionSummaryGenerator()

# Daily summary (defaults to today)
summary = generator.generate_daily_summary()
json_file, md_file = generator.save_summary(summary)

# Specific date
summary = generator.generate_daily_summary('2026-02-08')

# Weekly summary (last 7 days)
weekly = generator.generate_weekly_summary()
```

**CLI Usage:**
```bash
# Today's summary
python3 scripts/decision_summary.py

# Specific date
python3 scripts/decision_summary.py date 2026-02-08

# Weekly summary
python3 scripts/decision_summary.py weekly
```

**Output Files:**
- JSON: `reports/decision-summaries/decision-summary-YYYY-MM-DD.json`
- Markdown: `reports/decision-summaries/decision-summary-YYYY-MM-DD.md`

### 4. `test_decision_system.py` - Test Suite

**Purpose:** Test system with realistic sample data

**Features:**
- Generates 30 days of sample decisions
- Realistic conversion rates by source/type
- Tests all major features
- Creates demo data for evaluation

**Usage:**
```bash
# Run full test suite
python3 scripts/test_decision_system.py
```

**What it tests:**
1. Decision logging
2. Outcome recording
3. Conversion rate calculations
4. ROI analysis
5. Insight generation
6. Prediction engine
7. Opportunity scoring
8. Daily summary generation

## Data Flow

```
1. Opportunity arrives
   ↓
2. opportunity_aggregator.py scores it (base score)
   ↓
3. opportunity_scorer.py enhances score with historical data
   ↓
4. Decision is made and logged via decision_log.log_decision()
   ↓
5. Action is taken (reply, schedule call, etc.)
   ↓
6. Outcome is recorded via decision_log.record_outcome()
   ↓
7. Conversion metrics are auto-updated
   ↓
8. Insights are generated from patterns
   ↓
9. Future opportunities are scored higher/lower based on learning
   ↓
10. Daily summary generated showing performance
```

## Database Schema

**Location:** `data/decision_log.db` (SQLite)

### Tables

**decisions**
```sql
- id (primary key)
- decision_id (unique identifier)
- timestamp (when decision was made)
- opportunity_type (coaching, partnership, etc.)
- opportunity_source (twitter, email, etc.)
- opportunity_content (text of opportunity)
- opportunity_score (original score)
- sender (who sent it)
- action_taken (what we did)
- decision_maker (jarvis, ross, etc.)
- context (JSON metadata)
```

**outcomes**
```sql
- id (primary key)
- decision_id (foreign key to decisions)
- outcome_type (conversion, response, etc.)
- outcome_status (success, failed, pending)
- revenue_generated (USD)
- customer_acquired (boolean)
- deal_closed (boolean)
- response_received (boolean)
- time_to_outcome_hours (time from decision to outcome)
- notes (additional context)
- recorded_at (timestamp)
```

**conversion_metrics** (auto-updated)
```sql
- source_type + opportunity_type (unique key)
- total_decisions
- total_responses
- total_customers
- total_deals_closed
- total_revenue
- avg_time_to_conversion_hours
- conversion_rate (percentage)
- last_updated
```

**insights** (auto-generated)
```sql
- insight_type (conversion, comparison, timing, revenue)
- title (short description)
- description (detailed explanation)
- confidence_score (0.0-1.0)
- data_points (number of samples)
- generated_at (timestamp)
```

**predictions**
```sql
- opportunity_id
- predicted_outcome
- predicted_revenue
- predicted_conversion_probability
- similar_past_decisions (JSON)
- reasoning (explanation)
- predicted_at (timestamp)
```

## Conversion Rate Tracking

The system automatically calculates conversion rates by:

1. **Source Type** (twitter, email, revenue_dashboard)
2. **Opportunity Type** (golf_coaching, partnership, feedback, etc.)
3. **Combination** (twitter + golf_coaching, email + partnership, etc.)

**Example Output:**
```
twitter → golf_coaching: 65.5% (12 decisions, $3,200 revenue)
email → golf_coaching: 75.0% (8 decisions, $2,800 revenue)
twitter → partnership: 33.3% (9 decisions, $1,500 revenue)
```

**Metrics Calculated:**
- Conversion rate (% that become customers)
- Average revenue per decision
- Average time to conversion
- Response rate (% that reply)

## ROI Analysis

**Tracks:**
- Total revenue by opportunity type
- Average revenue per decision
- Number of decisions vs. closed deals
- Return on time invested

**Example Output:**
```
golf_coaching (email): $2,800 total, $350 avg/decision, 8 decisions, 6 closed
partnership (twitter): $1,500 total, $167 avg/decision, 9 decisions, 3 closed
```

## Insight Generation

The system auto-generates insights like:

1. **Best Converting Source**
   - "Email converts 1.5x better than Twitter"
   - Based on actual conversion rates

2. **Revenue Leaders**
   - "Golf coaching generates most revenue"
   - "$350 average per decision"

3. **Timing Patterns**
   - "Partnerships take ~15 days on average"
   - "Golf coaching closes in 2-3 days"

4. **Performance Comparisons**
   - "Twitter golf_coaching converts at 65% vs 33% for partnerships"

**Confidence Scores:**
- 0.9+ (90%) = High confidence (10+ data points)
- 0.7-0.9 (70-90%) = Moderate confidence (5-10 data points)
- <0.7 (<70%) = Low confidence (<5 data points)

## Predictive Scoring

**How it works:**

1. New opportunity arrives
2. System finds similar past decisions (same type + source)
3. Calculates:
   - Historical conversion rate
   - Average revenue
   - Average time to close
4. Predicts outcome with confidence score

**Example Prediction:**
```json
{
  "predicted_outcome": "conversion",
  "conversion_probability": 75.5,
  "predicted_revenue": 350.50,
  "avg_time_to_close_days": 2.3,
  "confidence": 0.85,
  "reasoning": "Based on 12 similar golf_coaching opportunities from twitter, we've seen a 65.5% conversion rate with average revenue of $350.50. This is a strong opportunity type. Confidence: high (12 data points).",
  "similar_count": 12
}
```

**Score Adjustment Formula:**
```
adjusted_score = 
  base_score * 0.4 +                      # Original score (40% weight)
  (conversion_rate / 100) * 30 +          # Historical conversion (30% weight)
  min(avg_revenue / 50, 20) +             # Revenue potential (20% weight)
  confidence * 10                          # Prediction confidence (10% weight)
```

## Daily Summaries

**Generated Automatically:**
- Decisions made today
- Outcomes recorded today
- Revenue generated
- Customers acquired
- Top insights
- Conversion rates

**Example Summary:**
```
📊 DECISION PERFORMANCE SUMMARY
Date: 2026-02-08

🎯 Decisions Made: 4
   Types: golf_coaching, partnership
   Sources: twitter, email

📈 Outcomes Recorded: 3
   Revenue: $850.00
   New customers: 2
   Deals closed: 2

🏆 Top Outcome:
   $500.00 from golf_coaching (email)
   Time to close: 1.5 days

💡 Key Insights:
   • Email converts 1.5x better than Twitter
   • Golf coaching generates most revenue
   • Partnerships take ~15 days on average
```

## Integration with Opportunity Aggregator

**How they work together:**

1. **Opportunity Aggregator** (`opportunity_aggregator.py`)
   - Scans Twitter, email, revenue dashboard
   - Scores opportunities 0-100 (base score)
   - Outputs: `data/opportunities.json`

2. **Opportunity Scorer** (`opportunity_scorer.py`)
   - Reads `opportunities.json`
   - Enhances scores with historical data
   - Adjusts based on conversion rates and ROI
   - Outputs: `data/opportunities_scored.json`

3. **Decision Made**
   - Action taken on opportunity
   - Logged via `decision_log.py`

4. **Outcome Recorded**
   - Result tracked (converted, revenue, etc.)
   - Feeds back into conversion metrics

5. **Learning Loop**
   - Future opportunities scored higher/lower
   - Based on actual performance
   - Continuous improvement

**Example Integration:**

```python
# 1. Aggregate opportunities
from opportunity_aggregator import OpportunityAggregator
aggregator = OpportunityAggregator()
aggregator.run()  # Creates opportunities.json

# 2. Score with historical data
from opportunity_scorer import OpportunityScorer
scorer = OpportunityScorer()
opportunities = load_opportunities()  # From opportunities.json
scored = scorer.score_opportunities_batch(opportunities)

# 3. Act on top opportunities
for opp in scored[:5]:  # Top 5
    if opp['adjusted_score'] >= 85:
        # Take action (reply, schedule, etc.)
        action_taken = handle_opportunity(opp)
        
        # Log decision
        decision_log.log_decision(
            decision_id=generate_id(),
            opportunity_type=opp['type'],
            opportunity_source=opp['source'],
            action_taken=action_taken,
            # ... other fields
        )

# 4. Later, record outcome
decision_log.record_outcome(
    decision_id="...",
    outcome_type="conversion",
    outcome_status="success",
    revenue_generated=350.00,
    customer_acquired=True,
    deal_closed=True
)

# 5. System learns and adjusts future scores automatically
```

## Usage Examples

### Example 1: Log a Decision

```python
from decision_log import DecisionLog

log = DecisionLog()

# Someone tweets asking about golf coaching
log.log_decision(
    decision_id="dec_twitter_001",
    opportunity_type="golf_coaching",
    opportunity_source="twitter",
    action_taken="Replied with coaching offer and Calendly link",
    opportunity_content="@jarvis Can you help me fix my slice? Saw your swing analysis posts",
    opportunity_score=87,
    sender="@golfer_mike"
)
```

### Example 2: Record an Outcome

```python
# They booked a session and paid
log.record_outcome(
    decision_id="dec_twitter_001",
    outcome_type="conversion",
    outcome_status="success",
    revenue_generated=250.00,
    customer_acquired=True,
    deal_closed=True,
    response_received=True,
    notes="Booked 2-session package via Calendly, paid via Stripe"
)
```

### Example 3: Check Performance

```python
# Get conversion rates
rates = log.get_conversion_rates()
for rate in rates:
    print(f"{rate['source_type']} → {rate['opportunity_type']}: {rate['conversion_rate']:.1f}%")

# Get ROI analysis
roi = log.calculate_roi_by_type()
for item in roi:
    print(f"{item['opportunity_type']}: ${item['total_revenue']:.2f} total, ${item['avg_revenue_per_decision']:.2f} avg")
```

### Example 4: Predict Outcome for New Opportunity

```python
# New email arrives
new_opportunity = {
    'type': 'golf_coaching',
    'source': 'email',
    'content': 'Interested in golf coaching to improve my handicap'
}

prediction = log.predict_outcome(new_opportunity)
print(f"Conversion probability: {prediction['conversion_probability']:.1f}%")
print(f"Predicted revenue: ${prediction['predicted_revenue']:.2f}")
print(f"Reasoning: {prediction['reasoning']}")
```

### Example 5: Generate Daily Summary

```python
from decision_summary import DecisionSummaryGenerator

generator = DecisionSummaryGenerator()

# Today's summary
summary = generator.generate_daily_summary()
print(summary['performance_summary'])

# Save to file
json_file, md_file = generator.save_summary(summary)
```

## Automation

### Daily Summary Cron Job

Add to crontab for daily reports:

```bash
# Daily summary at 11:59 PM
59 23 * * * cd /Users/clawdbot/clawd && python3 scripts/decision_summary.py >> logs/daily-summary.log 2>&1
```

### Weekly Summary

```bash
# Weekly summary every Sunday at 9 PM
0 21 * * 0 cd /Users/clawdbot/clawd && python3 scripts/decision_summary.py weekly >> logs/weekly-summary.log 2>&1
```

### Opportunity Scoring

```bash
# Re-score opportunities after aggregator runs
*/30 * * * * cd /Users/clawdbot/clawd && python3 scripts/opportunity_scorer.py >> logs/opportunity-scorer.log 2>&1
```

## Files and Locations

**Scripts:**
- `scripts/decision_log.py` - Core decision logger
- `scripts/opportunity_scorer.py` - Enhanced scoring with historical data
- `scripts/decision_summary.py` - Daily/weekly reporting
- `scripts/test_decision_system.py` - Test suite with sample data

**Data:**
- `data/decision_log.db` - SQLite database (all decisions/outcomes)
- `data/opportunities.json` - Aggregated opportunities (from aggregator)
- `data/opportunities_scored.json` - Enhanced scores (from scorer)

**Reports:**
- `reports/decision-summaries/decision-summary-YYYY-MM-DD.json` - Daily JSON
- `reports/decision-summaries/decision-summary-YYYY-MM-DD.md` - Daily Markdown
- `reports/decision-summaries/weekly-summary-YYYY-WXX.json` - Weekly JSON

**Logs:**
- `logs/decision-log.log` - Decision log operations
- `logs/opportunity-scorer.log` - Scoring operations
- `logs/daily-summary.log` - Summary generation

## Getting Started

### 1. Test the System

Run the test suite to generate sample data:

```bash
cd ~/clawd
python3 scripts/test_decision_system.py
```

This creates 30 days of realistic sample data and tests all features.

### 2. View Results

```bash
# Conversion rates
python3 scripts/decision_log.py conversions

# ROI analysis
python3 scripts/decision_log.py roi

# Insights
python3 scripts/decision_log.py insights

# Daily summary
python3 scripts/decision_summary.py
```

### 3. Review Reports

Check generated reports:

```bash
ls reports/decision-summaries/
cat reports/decision-summaries/decision-summary-*.md
```

### 4. Integrate with Existing System

```python
# In your opportunity handler code:
from decision_log import DecisionLog

log = DecisionLog()

# When you act on an opportunity:
log.log_decision(...)

# When you know the outcome:
log.record_outcome(...)
```

### 5. Use Enhanced Scoring

```bash
# Score opportunities with historical data
python3 scripts/opportunity_scorer.py

# Check enhanced scores
cat data/opportunities_scored.json
```

## Best Practices

1. **Log Every Decision**
   - Don't skip logging even "small" opportunities
   - The system learns from all data points

2. **Record Outcomes Promptly**
   - Record outcomes as soon as you know them
   - Accurate time-to-conversion data improves predictions

3. **Review Insights Weekly**
   - Check weekly summaries for patterns
   - Adjust strategy based on what's working

4. **Trust the Predictions**
   - High-confidence predictions (0.8+) are reliable
   - Low-confidence (<0.5) means not enough data yet

5. **Use Adjusted Scores**
   - `adjusted_score` is better than `original_score`
   - Based on actual performance, not just content

6. **Track Revenue Accurately**
   - Real revenue data makes predictions better
   - Even $0 conversions are valuable data

## Troubleshooting

**Problem:** No insights generated

**Solution:** Need at least 3-5 decisions per type/source combination for insights

---

**Problem:** Predictions show 0% confidence

**Solution:** Not enough historical data for that opportunity type. Make more decisions and record outcomes.

---

**Problem:** Conversion rates seem wrong

**Solution:** Check that outcomes are being recorded. Run `python3 scripts/decision_log.py conversions` to verify.

---

**Problem:** Database locked errors

**Solution:** Close all connections properly. The DecisionLog class has a `.close()` method.

---

**Problem:** Can't find opportunities_scored.json

**Solution:** Run `python3 scripts/opportunity_scorer.py` after opportunities have been aggregated.

## Future Enhancements

Potential improvements:

1. **Machine Learning Models**
   - Train actual ML models on decision data
   - More sophisticated prediction algorithms

2. **A/B Testing**
   - Test different approaches
   - Track which actions convert best

3. **Sentiment Analysis**
   - Analyze opportunity text sentiment
   - Correlate sentiment with conversion

4. **Time-Series Analysis**
   - Track performance trends over time
   - Identify seasonality patterns

5. **Multi-Agent Learning**
   - Share learnings across different decision makers
   - Compare Ross's decisions vs Jarvis's

6. **Real-Time Dashboards**
   - Live conversion tracking
   - Real-time ROI monitoring

## Support

Questions or issues? Check:
1. Test suite output: `python3 scripts/test_decision_system.py`
2. Logs in `logs/decision-log.log`
3. Database: `sqlite3 data/decision_log.db`

---

**Version:** 1.0
**Last Updated:** 2026-02-08
**Status:** Production Ready ✅
