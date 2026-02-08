# Revenue Forecast - Quick Start

**Get revenue forecasting running in 2 minutes**

## 1. Initialize with Mock Data

```bash
python3 ~/clawd/scripts/revenue-forecast set-mock 150 5
```
*Sets $150 MRR with 5 customers as starting point*

## 2. Sync Data

```bash
python3 ~/clawd/scripts/revenue-forecast sync
```
*Fetches current data and calculates initial metrics*

## 3. Check Status

```bash
python3 ~/clawd/scripts/revenue-forecast status
```

**You'll see:**
- Current MRR vs target
- Growth rates (daily/weekly)
- Projected target date
- Customers needed

## 4. View Scenarios

```bash
python3 ~/clawd/scripts/revenue-forecast scenarios
```

**Shows:** "What if I add 1 golf student?" projections

## 5. Generate Dashboard

```bash
python3 ~/clawd/scripts/revenue-forecast dashboard
```

**Creates:** `data/revenue_forecast_widget.json`

## Daily Commands

```bash
# Morning routine
revenue-forecast sync          # Update data
revenue-forecast brief         # Get one-sentence update
revenue-forecast dashboard     # Refresh widget

# Check anytime
revenue-forecast status        # Full status
revenue-forecast scenarios     # What-if projections
revenue-forecast history 7     # Last 7 days trend
```

## Add to Morning Brief

```python
from daemons.revenue_forecast import RevenueForecast

forecast = RevenueForecast()
update = forecast.generate_daily_update()
# Returns: "📈 Revenue: $165/500 MRR (33%) - Hit $500 on Apr 15"
```

## Dashboard Widget

**File:** `daemons/revenue_forecast/widget.html`

Open in browser or embed:
```html
<iframe src="daemons/revenue_forecast/widget.html" 
        width="420" height="500"></iframe>
```

## Switch to Real Stripe Data

1. Install package:
   ```bash
   pip3 install stripe
   ```

2. Add to `.env`:
   ```bash
   STRIPE_API_KEY=sk_live_...
   ```

3. Update config (`daemons/revenue_forecast/config.json`):
   ```json
   {
     "stripe_enabled": true,
     "mock_mode": false
   }
   ```

4. Sync:
   ```bash
   revenue-forecast sync
   ```

## Automation

**Add to crontab:**
```bash
# Daily sync at 9 AM
0 9 * * * cd ~/clawd && python3 scripts/revenue-forecast sync

# Update dashboard hourly
0 * * * * cd ~/clawd && python3 scripts/revenue-forecast dashboard
```

**Or add to HEARTBEAT.md:**
```markdown
- Revenue tracking (once daily)
  - Run: revenue-forecast sync
  - If changed >5%, notify me
```

## Common Questions

**Q: "No revenue data available"**  
A: Run `revenue-forecast sync` first

**Q: How often should I sync?**  
A: Daily is fine. Stripe MRR doesn't change much hourly.

**Q: Can I track multiple targets?**  
A: Not yet - coming in v2. Current: one target in config.

**Q: Days to target shows -1?**  
A: Growth rate is negative/zero. Need positive momentum.

## Full Docs

See `daemons/revenue_forecast/README.md` for:
- Complete API reference
- Database schema
- Python integration
- Production setup guide

## Test Suite

```bash
python3 ~/clawd/daemons/revenue_forecast/test.py
```

Runs all tests with mock data. Should see:
```
✅ ALL TESTS PASSED
```

---

**Need help?** `revenue-forecast help`
