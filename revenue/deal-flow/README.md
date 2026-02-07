# Deal Flow Pipeline

Your personal money-making opportunity scanner. Tracks arbitrage deals, affiliate programs, Florida real estate, and side hustles.

## Quick Start

1. **View Dashboard**
   ```bash
   open ~/clawd/revenue/deal-flow/dashboard.html
   ```

2. **Update Opportunities**
   ```bash
   python3 ~/clawd/revenue/deal-flow/scraper.py
   ```

3. **Mobile Access**
   - Bookmark the dashboard.html file on your phone
   - Opens in Safari/Chrome, fully mobile-optimized

## What's Included

### 📊 Dashboard (`dashboard.html`)
- Visual overview of all opportunities
- Filter by type: Arbitrage, Affiliate, Real Estate, Side Hustle
- Sort by ROI (return/effort ratio)
- Each deal shows:
  - Effort score (1-10)
  - Return potential ($)
  - Viral potential 🔥
  - Requirements
  - Next steps

### 💾 Database (`opportunities.json`)
- Currently loaded with 15+ opportunities
- Each opportunity scored and categorized
- Auto-calculated stats and ROI

### 🔍 Scraper (`scraper.py`)
- Adds new opportunities
- Updates existing data
- Recalculates stats

## How to Use

### Adding Opportunities Manually

Edit `opportunities.json` and add entries like:

```json
{
  "id": "df016",
  "type": "arbitrage",
  "title": "Your Opportunity Title",
  "description": "What it is and how it works",
  "source": "Where you found it",
  "effortScore": 5,
  "returnPotential": 1000,
  "timeframe": "1-2 weeks",
  "requirements": ["What you need", "To get started"],
  "status": "active",
  "viralPotential": 7,
  "nextSteps": [
    "First action",
    "Second action"
  ],
  "dateAdded": "2026-01-30"
}
```

### Opportunity Types

- **arbitrage** - Buy low, sell high (flipping, marketplace deals)
- **affiliate** - Promote products for commission
- **real-estate** - Florida properties under $300k
- **side-hustle** - Service-based income (coaching, consulting)

### Status Levels

- `active` - Ready to execute now
- `research` - Needs more investigation
- `dream` - Long-term goal

### ROI Scoring

The dashboard automatically calculates ROI:
- **Excellent ROI** (⭐) - Return/Effort > 200
- **Good ROI** (✓) - Return/Effort > 100
- **Fair ROI** - Return/Effort < 100

Lower effort + higher return = better ROI!

## Automation

### Daily Auto-Refresh (via cron)

Run the scraper daily at 8 AM:

```bash
crontab -e
```

Add this line:
```
0 8 * * * cd /Users/clawdbot/clawd/revenue/deal-flow && python3 scraper.py
```

## Next Steps

1. **Review all opportunities** - Click through each deal, expand "Next Steps"
2. **Pick 2-3 to start** - Focus on high ROI, low effort deals
3. **Execute** - Follow the next steps for each opportunity
4. **Track progress** - Update status as you execute
5. **Add new deals** - As you discover opportunities, add them to the database

## Tips

- **Start with arbitrage** - Fastest cash, lowest risk
- **Build affiliate in parallel** - Compounds over time
- **Real estate is the endgame** - Save for down payment while building side income
- **Sort by ROI** - Best bang for your buck
- **Check viral potential** - 🔥 High viral = potential for exponential growth

---

**Goal:** Find and execute opportunities that get you to $500 MRR and $50k Florida fund. Let's make it happen! 💰
