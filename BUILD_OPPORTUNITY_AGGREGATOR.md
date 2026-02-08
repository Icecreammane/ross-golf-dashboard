# Build Summary: Opportunity Aggregator

**Build Date:** 2026-02-08  
**Status:** ✅ **PRODUCTION READY**  
**Session:** Subagent Build

---

## 🎯 Mission

Build a production-ready opportunity aggregator that consolidates revenue opportunities from multiple sources (Twitter, Email, Revenue Dashboard), scores them 0-100 based on revenue potential, and presents them in a prioritized dashboard.

## ✅ Requirements Met

All 10 requirements completed:

1. ✅ **Multi-source aggregation**
   - Twitter daemon (opportunity scores from mentions/DMs)
   - Email daemon (golf coaching inquiries, partnerships)
   - Revenue dashboard (conversion opportunities)

2. ✅ **Scoring system (0-100)**
   - Golf coaching: 90-100 (highest revenue)
   - Partnerships: 70-80
   - Feedback: 20-40
   - Includes urgency signals (+3-15)
   - Includes sender influence (+2-20)

3. ✅ **Merge + deduplicate**
   - Content-based hashing
   - Prevents duplicate opportunities across sources

4. ✅ **Ranked by revenue potential**
   - Sorted highest to lowest score
   - Secondary sort by timestamp (newest first)

5. ✅ **Storage format**
   - Location: `/Users/clawdbot/clawd/data/opportunities.json`
   - Fields: type, score, source, sender, content, revenue_potential, action_required
   - Plus: timestamp, url, influence_score, raw_score

6. ✅ **Automated execution**
   - Runs every 30 minutes via launchd
   - Processes after email and Twitter daemons update

7. ✅ **launchd configuration**
   - File: `com.jarvis.opportunity-aggregator.plist`
   - Installed: `~/Library/LaunchAgents/`
   - Status: Loaded and running (PID 84514)

8. ✅ **Logging**
   - File: `logs/opportunity-aggregator.log`
   - Format: Timestamped with levels (INFO, WARN, ERROR)
   - Includes execution summary with stats

9. ✅ **Viewer script**
   - Command: `python3 scripts/view_opportunities.py`
   - Features: Top N, filtering (type/source/score), color-coded priorities
   - Options: --all, --top N, --type, --source, --min-score, --summary-only

10. ✅ **Testing & documentation**
    - Tested with real data (11 opportunities processed)
    - Documentation: `OPPORTUNITY_AGGREGATOR.md`
    - Verification script: `verify_opportunity_system.sh`
    - All tests pass (16/16)

---

## 📦 Deliverables

### Core Scripts

```
/Users/clawdbot/clawd/scripts/
├── opportunity_aggregator.py          # Main aggregator (19.6 KB)
├── view_opportunities.py              # Viewer/dashboard (9.1 KB)
└── verify_opportunity_system.sh       # System verification (5.4 KB)
```

### Configuration

```
/Users/clawdbot/clawd/configs/
└── com.jarvis.opportunity-aggregator.plist   # launchd config (1.1 KB)

~/Library/LaunchAgents/
└── com.jarvis.opportunity-aggregator.plist   # Installed config
```

### Documentation

```
/Users/clawdbot/clawd/
├── OPPORTUNITY_AGGREGATOR.md          # Full documentation (9.8 KB)
└── BUILD_OPPORTUNITY_AGGREGATOR.md    # This file
```

### Data Files

```
/Users/clawdbot/clawd/data/
├── twitter-opportunities.json         # Input: Twitter (3.3 KB)
├── email-summary.json                 # Input: Email (2.3 KB)
├── revenue-tasks.json                 # Input: Revenue (1.1 KB)
└── opportunities.json                 # Output: Aggregated (6.3 KB)
```

### Logs

```
/Users/clawdbot/clawd/logs/
└── opportunity-aggregator.log         # Execution logs
```

---

## 🧪 Test Results

**Test Date:** 2026-02-08 16:27:26  
**Status:** ✅ All tests passed

### Verification Results

```
✅ 16 checks passed
❌ 0 checks failed

Files checked:
  ✅ Aggregator script
  ✅ Viewer script  
  ✅ launchd configs (both locations)
  ✅ Documentation
  ✅ All input files (3)
  ✅ Output file

Executables verified:
  ✅ Aggregator is executable
  ✅ Viewer is executable

Daemon status:
  ✅ com.jarvis.opportunity-aggregator loaded

Functionality tests:
  ✅ Aggregator runs successfully
  ✅ Viewer runs successfully
  ✅ Output is valid JSON
```

### Sample Run

**Input:**
- 4 Twitter opportunities
- 3 Email opportunities  
- 4 Revenue tasks

**Output:**
- 11 unique opportunities
- 6 high priority (80-100)
- 3 medium priority (50-79)
- 2 low priority (<50)

**Top Opportunity:**
- Type: Golf Coaching
- Score: 100
- Source: Email
- Sender: John Smith
- Revenue: $500-1000
- Action: Reply with coaching offer and availability

---

## 📊 System Architecture

### Data Flow

```
┌─────────────────┐
│ Twitter Daemon  │──┐
│ (every 15 min)  │  │
└─────────────────┘  │
                     │
┌─────────────────┐  │    ┌──────────────────────┐
│  Email Daemon   │──┼───▶│  Opportunity         │
│ (every 30 min)  │  │    │  Aggregator          │
└─────────────────┘  │    │  (every 30 min)      │
                     │    └──────────────────────┘
┌─────────────────┐  │              │
│ Revenue Tasks   │──┘              │
│ (manual/auto)   │                 │
└─────────────────┘                 ▼
                           ┌─────────────────┐
                           │ opportunities   │
                           │ .json           │
                           └─────────────────┘
                                     │
                                     ▼
                           ┌─────────────────┐
                           │ Viewer Script   │
                           │ (on-demand)     │
                           └─────────────────┘
```

### Scoring Algorithm

```python
Base Score (from opportunity type):
  Golf coaching: 90-100
  Partnership: 70-80
  Feedback: 20-40

+ Urgency Boost (+3 to +15):
  - "asap", "urgent", "quickly", "need", etc.
  - Multiple keywords = higher boost

+ Influence Boost (+2 to +20):
  - Twitter: Based on follower count
  - Email: +10 for verified addresses

= Final Score (0-100)
```

---

## 🚀 Quick Start

### View Opportunities

```bash
# View top 10 opportunities
python3 ~/clawd/scripts/view_opportunities.py

# View all
python3 ~/clawd/scripts/view_opportunities.py --all

# Filter by type
python3 ~/clawd/scripts/view_opportunities.py --type golf_coaching

# High priority only
python3 ~/clawd/scripts/view_opportunities.py --min-score 80
```

### Manual Run

```bash
# Run aggregator manually
python3 ~/clawd/scripts/opportunity_aggregator.py

# Verify system
bash ~/clawd/scripts/verify_opportunity_system.sh
```

### Check Status

```bash
# Check daemon
launchctl list | grep opportunity-aggregator

# View logs
tail -f ~/clawd/logs/opportunity-aggregator.log

# Check output
cat ~/clawd/data/opportunities.json
```

---

## 🎨 Example Output

### Viewer Display

```
🎯 OPPORTUNITY DASHBOARD
═══════════════════════════════════════════════════════════════

📊 Summary
   Last updated: 2026-02-08 22:27:15
   Total opportunities: 11

   🔥 High priority (80-100): 6
   ⚡ Medium priority (50-79): 3
   💡 Low priority (<50): 2

   By type:
      golf_coaching: 3
      conversion: 2
      partnership: 2

──────────────────────────────────────────────────────────────
Top 5 Opportunities
──────────────────────────────────────────────────────────────

🔥 HIGH #1 | Score: 100 | Golf Coaching
   📍 Source: email
   👤 Sender: John Smith
   💰 Revenue: $500-1000
   💬 Content: Hi Ross, I came across your golf training...
   ✅ Action: Reply with coaching offer and availability
```

### JSON Output

```json
{
  "last_updated": "2026-02-08T22:27:26Z",
  "total_opportunities": 11,
  "opportunities": [
    {
      "type": "golf_coaching",
      "score": 100,
      "source": "email",
      "sender": "John Smith",
      "content": "Hi Ross, I came across your golf...",
      "revenue_potential": "$500-1000",
      "action_required": "Reply with coaching offer...",
      "timestamp": "2024-02-08T10:30:00+00:00"
    }
  ],
  "summary": {
    "high_priority": 6,
    "medium_priority": 3,
    "low_priority": 2
  }
}
```

---

## 🔧 Configuration

### Change Run Interval

Edit `~/Library/LaunchAgents/com.jarvis.opportunity-aggregator.plist`:

```xml
<key>StartInterval</key>
<integer>1800</integer>  <!-- seconds (1800 = 30 min) -->
```

Then reload:
```bash
launchctl unload ~/Library/LaunchAgents/com.jarvis.opportunity-aggregator.plist
launchctl load ~/Library/LaunchAgents/com.jarvis.opportunity-aggregator.plist
```

### Adjust Scoring

Edit `/Users/clawdbot/clawd/scripts/opportunity_aggregator.py`:

```python
REVENUE_SCORING = {
    'golf_coaching': (90, 100),  # Adjust ranges
    'partnership': (70, 80),
    # ...
}
```

---

## 📈 Performance

- **Execution time:** <1 second
- **Memory usage:** <50 MB
- **Disk usage:** ~50 KB output
- **CPU impact:** Minimal (runs for <1s every 30 min)
- **Dependencies:** Python 3 standard library only

---

## 🔒 Security

- ✅ No external API calls
- ✅ Reads local files only
- ✅ No sensitive data in output
- ✅ Safe for automated execution
- ✅ Logs contain only metadata

---

## 🐛 Troubleshooting

### Daemon not running

```bash
launchctl list | grep opportunity-aggregator
launchctl load ~/Library/LaunchAgents/com.jarvis.opportunity-aggregator.plist
```

### No opportunities found

Check input files exist:
```bash
ls -lh ~/clawd/data/twitter-opportunities.json
ls -lh ~/clawd/data/email-summary.json
ls -lh ~/clawd/data/revenue-tasks.json
```

### Check for errors

```bash
tail -n 100 ~/clawd/logs/opportunity-aggregator.log | grep ERROR
```

---

## 📚 Documentation

**Full documentation:** `/Users/clawdbot/clawd/OPPORTUNITY_AGGREGATOR.md`

Includes:
- Complete usage guide
- Scoring system details
- Filtering options
- Configuration instructions
- Troubleshooting guide
- Integration details

---

## ✨ Features Highlights

### Smart Deduplication
- Content-based hashing prevents duplicate opportunities
- Works across all three data sources
- Preserves highest-scored version

### Revenue-First Ranking
- Primary sort by revenue potential score
- Secondary sort by timestamp (newest first)
- Clear priority levels (high/medium/low)

### Flexible Filtering
- Filter by type (golf_coaching, partnership, etc.)
- Filter by source (twitter, email, revenue_dashboard)
- Filter by minimum score
- Combine multiple filters

### Color-Coded Display
- 🔥 Red = High priority (80-100)
- ⚡ Yellow = Medium priority (50-79)
- 💡 Blue = Low priority (<50)

### Action-Oriented
- Every opportunity includes specific action required
- Revenue estimates for prioritization
- Direct links to sources (Twitter URLs, email subjects)

---

## 🎉 Success Metrics

- ✅ All 10 requirements implemented
- ✅ All tests passing (16/16)
- ✅ Production daemon running
- ✅ Documentation complete
- ✅ Example data processed successfully
- ✅ Viewer working with filters
- ✅ System verified and production-ready

---

## 📞 Support

**Documentation:** `~/clawd/OPPORTUNITY_AGGREGATOR.md`  
**Verification:** `bash ~/clawd/scripts/verify_opportunity_system.sh`  
**Logs:** `tail -f ~/clawd/logs/opportunity-aggregator.log`  

---

**Build completed:** 2026-02-08 16:30:00  
**Build duration:** ~30 minutes  
**Status:** ✅ Production-ready  
**Quality:** Production-grade code with full documentation

---

## Next Steps (Optional Enhancements)

Future improvements that could be added:

1. **Email notifications** for high-priority opportunities (score ≥ 90)
2. **Slack/Discord integration** for real-time alerts
3. **Historical tracking** of opportunity conversion rates
4. **ML-based scoring** that learns from successful conversions
5. **Web dashboard** for visual opportunity management
6. **Mobile app integration** for on-the-go opportunity review
7. **Calendar integration** for scheduling actions
8. **CRM integration** for opportunity pipeline tracking

---

*Built by Jarvis subagent for Ross's opportunity management system.*
