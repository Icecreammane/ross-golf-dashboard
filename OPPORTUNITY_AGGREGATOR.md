# Opportunity Aggregator

**Production-ready opportunity scoring and aggregation system for Ross's Mac mini.**

## 🎯 Overview

The Opportunity Aggregator consolidates revenue opportunities from multiple sources, scores them based on potential value, and presents them in a prioritized dashboard.

### Features

✅ **Multi-source aggregation:**
- Twitter daemon (mentions, DMs)
- Email daemon (coaching inquiries, partnerships)
- Revenue dashboard (conversion tasks)

✅ **Smart scoring (0-100):**
- Golf coaching: 90-100 (highest revenue potential)
- Partnerships: 70-80
- Fitness coaching: 50-70
- Product feedback: 20-40
- Considers urgency signals and sender influence

✅ **Automatic deduplication:**
- Content-based hashing
- Prevents duplicate opportunities

✅ **Priority ranking:**
- Sorts by revenue potential (highest first)
- Color-coded display (high/medium/low)

✅ **Automated execution:**
- Runs every 30 minutes via launchd
- Processes data after source daemons update

## 📁 Files

```
/Users/clawdbot/clawd/
├── scripts/
│   ├── opportunity_aggregator.py      # Main aggregator
│   └── view_opportunities.py          # Viewer/dashboard
├── configs/
│   └── com.jarvis.opportunity-aggregator.plist  # launchd config
├── data/
│   ├── twitter-opportunities.json     # Input: Twitter data
│   ├── email-summary.json             # Input: Email data
│   ├── revenue-tasks.json             # Input: Revenue tasks
│   └── opportunities.json             # Output: Aggregated opportunities
└── logs/
    └── opportunity-aggregator.log     # Execution logs
```

## 🚀 Installation

The system is already installed and running!

To verify:
```bash
launchctl list | grep opportunity-aggregator
```

To reload (if needed):
```bash
launchctl unload ~/Library/LaunchAgents/com.jarvis.opportunity-aggregator.plist
launchctl load ~/Library/LaunchAgents/com.jarvis.opportunity-aggregator.plist
```

## 📊 Usage

### View Top Opportunities

```bash
# View top 10 opportunities (default)
python3 ~/clawd/scripts/view_opportunities.py

# View top 5
python3 ~/clawd/scripts/view_opportunities.py --top 5

# View all opportunities
python3 ~/clawd/scripts/view_opportunities.py --all

# Summary only (no details)
python3 ~/clawd/scripts/view_opportunities.py --summary-only
```

### Filter Opportunities

```bash
# Filter by type
python3 ~/clawd/scripts/view_opportunities.py --type golf_coaching
python3 ~/clawd/scripts/view_opportunities.py --type partnership
python3 ~/clawd/scripts/view_opportunities.py --type product_feedback

# Filter by source
python3 ~/clawd/scripts/view_opportunities.py --source twitter
python3 ~/clawd/scripts/view_opportunities.py --source email
python3 ~/clawd/scripts/view_opportunities.py --source revenue_dashboard

# Filter by minimum score
python3 ~/clawd/scripts/view_opportunities.py --min-score 80

# Combine filters
python3 ~/clawd/scripts/view_opportunities.py --type golf_coaching --min-score 90
```

### Manual Run

```bash
# Run aggregator manually (useful for testing)
python3 ~/clawd/scripts/opportunity_aggregator.py
```

## 📈 Scoring System

### Revenue Potential Ranges

| Opportunity Type | Score Range | Revenue Estimate |
|-----------------|-------------|------------------|
| Golf Coaching | 90-100 | $200-1000 |
| Coaching (general) | 90-100 | $100-500 |
| Partnership | 70-80 | $100-800 |
| Fitness Coaching | 50-70 | $50-300 |
| Product Feedback | 20-40 | $0-50 |
| General | 10-30 | $0-100 |

### Score Modifiers

**Urgency boost (+3-15):**
- Keywords: "asap", "urgent", "quickly", "soon", "need", "deadline"
- Multiple urgency signals increase boost

**Sender influence (+2-20):**
- Twitter followers:
  - 50,000+: +20
  - 10,000+: +15
  - 5,000+: +10
  - 1,000+: +5
  - <1,000: +2
- Email: +10 for verified addresses

**Revenue dashboard:**
- Score calculated from `revenue_potential` field
- $300+: 85-100
- $100-300: 70-85
- $0-100: 50-70

## 🎨 Output Format

### Stored Data (opportunities.json)

```json
{
  "last_updated": "2026-02-08T22:27:15Z",
  "total_opportunities": 11,
  "opportunities": [
    {
      "type": "golf_coaching",
      "score": 100,
      "source": "email",
      "sender": "John Smith",
      "content": "Hi Ross, I came across your golf training...",
      "revenue_potential": "$500-1000",
      "action_required": "Reply with coaching offer and availability",
      "timestamp": "2024-02-08T10:30:00+00:00",
      "subject": "Golf coaching inquiry - URGENT"
    }
  ],
  "summary": {
    "high_priority": 6,
    "medium_priority": 3,
    "low_priority": 2,
    "by_type": { "golf_coaching": 3, "partnership": 2 },
    "by_source": { "email": 3, "twitter": 4, "revenue_dashboard": 4 }
  }
}
```

### Priority Levels

- 🔥 **HIGH (80-100):** Immediate attention required
- ⚡ **MEDIUM (50-79):** Review within 24-48h
- 💡 **LOW (<50):** Low priority or informational

## 🔧 Configuration

### Scheduling (launchd)

Current schedule: **Every 30 minutes**

To change interval, edit `~/Library/LaunchAgents/com.jarvis.opportunity-aggregator.plist`:

```xml
<key>StartInterval</key>
<integer>1800</integer>  <!-- 1800 seconds = 30 minutes -->
```

Then reload:
```bash
launchctl unload ~/Library/LaunchAgents/com.jarvis.opportunity-aggregator.plist
launchctl load ~/Library/LaunchAgents/com.jarvis.opportunity-aggregator.plist
```

### Scoring Adjustments

Edit `/Users/clawdbot/clawd/scripts/opportunity_aggregator.py`:

```python
# Adjust revenue scoring ranges (line ~40)
REVENUE_SCORING = {
    'golf_coaching': (90, 100),    # Increase range for higher priority
    'partnership': (70, 80),
    # ...
}

# Adjust urgency keywords (line ~53)
URGENCY_KEYWORDS = [
    'asap', 'urgent', 'quickly',   # Add more keywords
    # ...
]
```

After changes, test:
```bash
python3 ~/clawd/scripts/opportunity_aggregator.py
```

## 📝 Logs

### View Logs

```bash
# Tail live logs
tail -f ~/clawd/logs/opportunity-aggregator.log

# View last 50 lines
tail -n 50 ~/clawd/logs/opportunity-aggregator.log

# Search for errors
grep ERROR ~/clawd/logs/opportunity-aggregator.log
```

### Log Format

```
2026-02-08 16:27:15,040 [INFO] 🎯 OPPORTUNITY AGGREGATOR STARTING
2026-02-08 16:27:15,040 [INFO]    Time: 2026-02-08 16:27:15
2026-02-08 16:27:15,041 [INFO]   ✅ Twitter: partnership from @fitness_coach_pro (score: 80)
2026-02-08 16:27:15,041 [INFO]   ✅ Email: golf_coaching from John Smith (score: 100)
```

## 🧪 Testing

### Test with Current Data

```bash
# Run aggregator
python3 ~/clawd/scripts/opportunity_aggregator.py

# View results
python3 ~/clawd/scripts/view_opportunities.py --all
```

### Add Test Data

```bash
# Twitter opportunities
echo '[{"id": "test_123", "type": "mention", "sender": "test_user", "content": "Looking for golf coaching ASAP!", "score": 50, "opportunity_type": "coaching", "author_followers": 5000}]' > ~/clawd/data/twitter-opportunities.json

# Email opportunities
echo '[{"sender": "Test User", "subject": "Partnership inquiry", "preview": "Would like to partner on fitness project", "importance_reason": "keyword: partner", "timestamp": "2024-02-08T12:00:00Z", "from_email": "test@example.com"}]' > ~/clawd/data/email-summary.json

# Run aggregator
python3 ~/clawd/scripts/opportunity_aggregator.py

# View results
python3 ~/clawd/scripts/view_opportunities.py
```

## 🛠️ Troubleshooting

### Daemon Not Running

```bash
# Check status
launchctl list | grep opportunity-aggregator

# Check for errors
tail -n 100 ~/clawd/logs/opportunity-aggregator.log

# Reload daemon
launchctl unload ~/Library/LaunchAgents/com.jarvis.opportunity-aggregator.plist
launchctl load ~/Library/LaunchAgents/com.jarvis.opportunity-aggregator.plist
```

### No Opportunities Found

Check that source files exist and contain data:
```bash
ls -lh ~/clawd/data/twitter-opportunities.json
ls -lh ~/clawd/data/email-summary.json
ls -lh ~/clawd/data/revenue-tasks.json

# Check file contents
cat ~/clawd/data/twitter-opportunities.json
```

### Score Seems Wrong

1. Check scoring configuration in `opportunity_aggregator.py`
2. Verify urgency keywords are being detected
3. Check sender influence calculation
4. Review logs for score calculation details

## 📊 Integration with Other Systems

### Twitter Daemon
- **Source:** `/Users/clawdbot/clawd/daemons/twitter_daemon.py`
- **Output:** `data/twitter-opportunities.json`
- **Schedule:** Every 15 minutes
- Opportunity aggregator runs after Twitter daemon updates

### Email Daemon
- **Source:** `/Users/clawdbot/clawd/scripts/email_daemon.py`
- **Output:** `data/email-summary.json`
- **Schedule:** Every 30 minutes
- Aggregator processes new email opportunities

### Revenue Dashboard
- **Source:** Manual or automated task creation
- **File:** `data/revenue-tasks.json`
- **Format:** Tasks with `revenue_potential` field

## 🔐 Security

- No external API calls (reads local files only)
- No sensitive data in output
- Logs contain only opportunity metadata
- Safe to run automatically

## 📚 Quick Reference

```bash
# View dashboard
python3 ~/clawd/scripts/view_opportunities.py

# Run manually
python3 ~/clawd/scripts/opportunity_aggregator.py

# Check daemon status
launchctl list | grep opportunity-aggregator

# View logs
tail -f ~/clawd/logs/opportunity-aggregator.log

# Filter high-priority golf coaching
python3 ~/clawd/scripts/view_opportunities.py --type golf_coaching --min-score 90
```

## ✅ Production Status

**Status:** ✅ Production-ready

- [x] Aggregates from 3 sources
- [x] Scores 0-100 based on revenue potential
- [x] Considers urgency and influence
- [x] Merges and deduplicates
- [x] Ranks by revenue potential
- [x] Stores in opportunities.json
- [x] Runs every 30 minutes
- [x] launchd configuration installed
- [x] Logging enabled
- [x] Viewer script with filters
- [x] Tested and documented

---

**Last Updated:** 2026-02-08
**Version:** 1.0.0
**Status:** Production
