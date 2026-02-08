# Revenue Forecasting Daemon

**Production-ready revenue tracking and forecasting system**

## Overview

Tracks Monthly Recurring Revenue (MRR) from Stripe, calculates growth trends, projects target achievement dates, and provides actionable scenarios. Includes automated daily updates and dashboard visualization.

## Features

✅ **Stripe Integration** - Automatic MRR tracking from Stripe API  
✅ **Mock Mode** - Test with generated data when Stripe isn't configured  
✅ **Historical Trends** - 30-day growth analysis with daily/weekly rates  
✅ **Smart Projections** - "When will I hit $500 MRR?" answered automatically  
✅ **Scenario Modeling** - "What if I add 1 golf student?" instant answers  
✅ **Daily Updates** - One-sentence brief for morning dashboard  
✅ **SQLite Storage** - Persistent trend data with efficient queries  
✅ **Dashboard Widget** - Beautiful progress visualization  
✅ **CLI Tools** - Easy command-line access to all features  
✅ **Production Ready** - Error handling, validation, comprehensive tests

## Quick Start

### 1. Initialize with Mock Data

```bash
# Set initial baseline (for testing without Stripe)
python3 ~/clawd/scripts/revenue-forecast set-mock 150 5
# Arguments: MRR_dollars customer_count
```

### 2. Sync Current Data

```bash
# Fetch current MRR and update metrics
python3 ~/clawd/scripts/revenue-forecast sync
```

### 3. Check Status

```bash
# View current status and projections
python3 ~/clawd/scripts/revenue-forecast status
```

### 4. Generate Dashboard

```bash
# Create widget data for dashboard integration
python3 ~/clawd/scripts/revenue-forecast dashboard
```

## CLI Commands

### `revenue-forecast status`
Shows current revenue status, growth rates, and target projections.

**Output:**
```
💰 Revenue Forecast Status
Current MRR:     $165.00
Target MRR:      $500.00
Progress:        33.0% 🎯
Gap:             $335.00

📊 Growth Metrics:
Daily Rate:      +0.50%
Weekly Rate:     +3.20%
30-day Proj:     $180.00

🎯 Target Date:    April 15, 2026 (67 days)
Customers Needed: 12 more (at $29/mo avg)
```

### `revenue-forecast sync`
Fetches current MRR from Stripe (or mock data) and updates metrics.

**Use:** Run daily via cron or heartbeat to keep data fresh.

### `revenue-forecast scenarios`
Shows "what-if" scenarios based on config.

**Output:**
```
📈 Forecast Scenarios

📈 1 Golf Student: Hit $500 in 55 days (March 10, 2026)
   New MRR: $194.00

📈 2 Golf Students: Hit $500 in 42 days (February 25, 2026)
   New MRR: $223.00

✅ Enterprise Client: You'd hit $500 immediately!
   New MRR: $364.00
```

### `revenue-forecast brief`
Generates one-sentence update for morning brief integration.

**Output:**
```
📈 Revenue: $165/500 MRR (33%) - Hit $500 on Apr 15
```

### `revenue-forecast history [days]`
Shows historical MRR trend (default: 30 days).

### `revenue-forecast dashboard`
Generates JSON data file for dashboard widget.

**File:** `data/revenue_forecast_widget.json`

### `revenue-forecast set-mock <mrr> <customers>`
Sets mock data baseline for testing without Stripe.

**Example:**
```bash
revenue-forecast set-mock 200 8
# Sets $200 MRR with 8 customers
```

## Configuration

**File:** `daemons/revenue_forecast/config.json`

```json
{
  "target_mrr": 500,
  "database_path": "data/revenue_forecast.db",
  "stripe_enabled": false,
  "mock_mode": true,
  "scenarios": [
    {
      "name": "1 Golf Student",
      "monthly_value": 29,
      "description": "Add 1 more golf student"
    }
  ],
  "morning_brief_integration": true
}
```

**Key Settings:**
- `target_mrr`: Revenue goal in dollars
- `stripe_enabled`: Enable Stripe API (requires `stripe` package + API key)
- `mock_mode`: Use generated data for testing
- `scenarios`: Define "what-if" scenarios to calculate

## Stripe Integration

### Setup (Production)

1. **Install Stripe package:**
   ```bash
   pip3 install stripe
   ```

2. **Set API key:**
   ```bash
   # In .env
   STRIPE_API_KEY=sk_live_...
   ```

3. **Enable in config:**
   ```json
   {
     "stripe_enabled": true,
     "mock_mode": false
   }
   ```

4. **Sync data:**
   ```bash
   revenue-forecast sync
   ```

### How It Works

- Fetches all active subscriptions from Stripe
- Normalizes to monthly recurring value (handles yearly, weekly, etc.)
- Counts unique customers
- Stores snapshot in database
- Updates growth calculations

## Database Schema

**Tables:**

### `mrr_snapshots`
Raw MRR data points over time.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| timestamp | DATETIME | When recorded |
| mrr_cents | INTEGER | MRR in cents |
| customer_count | INTEGER | Number of customers |
| source | TEXT | Data source (stripe/mock/manual) |
| notes | TEXT | Optional notes |

### `growth_metrics`
Calculated growth rates and projections (one per day).

| Column | Type | Description |
|--------|------|-------------|
| date | DATE | Calculation date |
| daily_growth_rate | REAL | % change per day |
| weekly_growth_rate | REAL | % change week-over-week |
| monthly_projection_cents | INTEGER | Projected MRR in 30 days |
| days_to_target | INTEGER | Days until target reached |
| customers_needed | INTEGER | Customers needed to hit target |

### `forecast_scenarios`
What-if scenario calculations.

### `daily_updates`
One-sentence briefs for morning dashboard.

## Dashboard Widget

**File:** `daemons/revenue_forecast/widget.html`

Beautiful standalone widget showing:
- Current MRR with progress bar
- 14-day mini chart
- Growth metrics (daily/weekly)
- Target date projection
- Customer count needed

**Integration:**
```html
<iframe src="daemons/revenue_forecast/widget.html" 
        width="420" height="500" frameborder="0"></iframe>
```

**Data Source:** Reads `data/revenue_forecast_widget.json` (generated by CLI)

## Morning Brief Integration

Add to morning brief daemon:

```python
from daemons.revenue_forecast import RevenueForecast

forecast = RevenueForecast()
revenue_update = forecast.generate_daily_update()
# Returns: "📈 Revenue: $165/500 MRR (33%) - Hit $500 on Apr 15"
```

## Automation

### Daily Sync (Cron)

```bash
# Add to crontab
0 9 * * * cd ~/clawd && python3 scripts/revenue-forecast sync && python3 scripts/revenue-forecast brief
```

Or add to heartbeat check:

```python
# In HEARTBEAT.md
- Check revenue data (once daily)
  - Run: revenue-forecast sync
  - If changed > 5%, notify
```

### Dashboard Auto-Update

```bash
# Regenerate widget data every hour
0 * * * * cd ~/clawd && python3 scripts/revenue-forecast dashboard
```

## Testing

**Run test suite:**
```bash
python3 ~/clawd/daemons/revenue_forecast/test.py
```

**Tests:**
- ✅ Database operations (CRUD, queries)
- ✅ Growth rate calculations
- ✅ Scenario projections
- ✅ Stripe integration (mock mode)
- ✅ Daily update generation
- ✅ Dashboard data export
- ✅ End-to-end workflow

**Test with mock data:**
```bash
# Initialize with $150 MRR, 5 customers
revenue-forecast set-mock 150 5

# Sync to populate initial data
revenue-forecast sync

# Check status
revenue-forecast status

# View scenarios
revenue-forecast scenarios
```

## Architecture

```
revenue_forecast/
├── __init__.py           # Package exports
├── config.json           # Configuration
├── schema.sql            # Database schema
├── database.py           # DB operations
├── forecaster.py         # Growth calculations
├── stripe_integration.py # Stripe API + mock
├── cli.py                # Command-line tool
├── widget.html           # Dashboard widget
├── test.py               # Test suite
└── README.md             # This file
```

## Python API

```python
from daemons.revenue_forecast import RevenueForecast, RevenueDatabase

# Initialize
forecast = RevenueForecast()

# Get current metrics
metrics = forecast.update_metrics()
print(f"MRR: ${metrics['current_mrr']}")
print(f"Days to target: {metrics['days_to_target']}")

# Calculate scenarios
scenarios = forecast.generate_all_scenarios()
for s in scenarios:
    print(f"{s['scenario_name']}: {s['days_to_target']} days")

# Generate brief
update = forecast.generate_daily_update()
print(update)

# Get dashboard data
dashboard = forecast.get_dashboard_data()
```

## Calculations Explained

### Daily Growth Rate
Average % change per day over last 7 days.

**Formula:** `((last_mrr - first_mrr) / days) / first_mrr * 100`

### Weekly Growth Rate
Week-over-week % change (last 7 days vs previous 7 days).

**Formula:** `((this_week_avg - prev_week_avg) / prev_week_avg) * 100`

### Days to Target
Days until target MRR reached at current growth rate.

**Formula:** `(target_mrr - current_mrr) / daily_change`

### Customers Needed
Customers needed to hit target (assumes $29/mo average).

**Formula:** `(target_mrr - current_mrr) / avg_customer_value`

### Scenario Projection
What-if calculation: "If I add $X MRR, when do I hit target?"

**Formula:** `(target_mrr - (current_mrr + additional_mrr)) / daily_change`

## Troubleshooting

### "No revenue data available"
**Solution:** Run `revenue-forecast sync` to populate initial data.

### "Insufficient historical data"
**Solution:** Need at least 2 days of data. Run sync daily for a few days.

### "Days to target: -1"
**Meaning:** Growth rate is negative or zero. Won't reach target without positive growth.

### Widget shows "Loading..."
**Solution:** Run `revenue-forecast dashboard` to generate data file.

### Stripe connection fails
**Solution:** Verify `STRIPE_API_KEY` in environment. Check `stripe` package installed.

## Production Checklist

- [ ] Install Stripe package (`pip3 install stripe`)
- [ ] Set `STRIPE_API_KEY` in `.env`
- [ ] Update `config.json` with real target MRR
- [ ] Disable mock mode in config
- [ ] Run initial sync: `revenue-forecast sync`
- [ ] Add daily cron job for sync
- [ ] Integrate with morning brief
- [ ] Add widget to dashboard
- [ ] Test all scenarios
- [ ] Monitor for first week

## Support

**Questions?** Check CLI help:
```bash
revenue-forecast help
```

**Logs:** SQLite database at `data/revenue_forecast.db`

**Widget not loading?** Check `data/revenue_forecast_widget.json` exists

## Roadmap

Future enhancements:
- [ ] Multiple target milestones ($500, $1K, $5K, etc.)
- [ ] Email alerts on milestone progress
- [ ] Churn tracking and projection
- [ ] Customer lifetime value calculations
- [ ] Integration with other revenue sources (non-MRR)
- [ ] Export reports to PDF
- [ ] Slack/Telegram notifications

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-08  
**Production Status:** ✅ Ready
