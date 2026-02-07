# NBA Top 50 Rankings - Quick Start Guide

## 🚀 One-Command Update

```bash
cd ~/clawd/nba && ./update_top_50.sh
```

This will:
- Pull latest game data
- Apply trade deadline adjustments
- Generate Top 50 rankings
- Export to CSV and JSON
- Create detailed report

## 📊 View Rankings

### Dashboard (Quick View)
```bash
cd ~/clawd/nba && python3 dashboard.py
```

Shows:
- Top 20 players with trade impact badges
- Trade deadline summary
- Position leaders
- Injury alerts

### CSV (Mobile-Friendly)
```bash
open ~/clawd/nba/rankings.csv
```

Opens in Excel/Numbers/Sheets. Columns:
- Rank, Player, Team, vs, Position, Home
- Proj FP, PPG, RPG, APG, Usage%
- **Trade Impact** (High/Med/Low/None)
- **Trade Notes** (stat adjustments explained)

### Full Report (Detailed Analysis)
```bash
open ~/clawd/nba/rankings-report.md
```

Includes:
- Complete trade deadline breakdown
- Top 50 rankings table
- Trade-impacted players by level
- Position breakdowns

## 🔄 Trade Deadline Adjustments

**4 Major Trades Tracked (2/4/26):**

1. **James Harden → Cleveland**
   - Harden: HIGH impact (+18 PPG, +8 APG projected in CLE system)
   - Donovan Mitchell: MED impact (usage decrease)
   
2. **Darius Garland → LA Clippers**
   - Garland: HIGH impact (+4 PPG, +3 APG as primary ball-handler)
   - Kawhi Leonard: MED impact (slight usage increase)
   
3. **Jaren Jackson Jr. → Utah**
   - JJJ: HIGH impact (+20 PPG, +6 RPG in expanded role)
   - Lauri Markkanen: MED impact (-3 PPG, reduced touches)
   - Jordan Clarkson: MED impact (-2 PPG)
   
4. **Kevin Huerter + Dario Saric → Detroit**
   - Huerter: MED impact (+3 PPG)
   - Cade Cunningham: LOW impact (slight usage decrease)
   - Jalen Duren: LOW impact (minor touch reduction)

**Trade Impact Badges:**
- 🔥 = HIGH impact (major role change)
- ⚠️ = MED impact (notable adjustment)
- 📊 = LOW impact (minor tweaks)

## 📱 Files You'll Use

| File | Purpose | How to Use |
|------|---------|------------|
| `rankings.csv` | Mobile rankings at work | Open on phone, sort/filter |
| `dashboard.py` | Quick terminal view | `python3 dashboard.py` |
| `rankings-report.md` | Deep dive analysis | Read before draft |
| `update_top_50.sh` | Refresh data | Run before each slate |

## ⚙️ Advanced Options

### Auto-Update with Cron

To auto-refresh every 2 hours during slate day:

```bash
# Edit crontab
crontab -e

# Add line (runs every 2 hours, 8am-8pm):
0 8-20/2 * * * /Users/clawdbot/clawd/nba/update_top_50.sh
```

### Manual Trade Adjustments

Edit `~/clawd/nba/trade_impact.py` to add new trades:

```python
'new_trade_key': {
    'player': 'Player Name',
    'from_team': 'OLD',
    'to_team': 'NEW',
    'impact_level': 'HIGH',
    'affected_players': {
        'Player Name': {'ppg_delta': +5, 'usage_delta': +8, 'impact': 'HIGH'},
        'Teammate': {'ppg_delta': -2, 'impact': 'LOW'}
    }
}
```

Then run `./update_top_50.sh` to regenerate.

## 🎯 Thursday 2/6/26 Slate Info

**Games:** 6 games
**Teams:** BOS, DET, IND, LAC, MEM, MIA, MIL, MIN, NO, NY, POR, SAC

**Top 5 Projections:**
1. Giannis Antetokounmpo (MIL) - 60.3 FP
2. De'Aaron Fox (SAC) - 46.5 FP
3. Damian Lillard (MIL) - 44.6 FP
4. Zion Williamson (NO) - 43.3 FP
5. Ja Morant (MEM) - 40.8 FP

**Key Trade-Impacted Players:**
- Kawhi Leonard (LAC) - ⚠️ MED impact
- Cade Cunningham (DET) - 📊 LOW impact
- Paul George (LAC) - 📊 LOW impact

## 📈 Fantasy Scoring Formula

**Base Formula:**
```
Fantasy Points = (PPG × 1.0) + (RPG × 1.2) + (APG × 1.5)
```

**Modifiers:**
- Home games: +5% boost
- High usage (>28%): +8% boost
- Medium usage (25-28%): +4% boost
- High efficiency (TS% >60%): +3% boost

**Trade Adjustments:**
- Applied after base calculation
- Deltas specified in trade_impact.py
- Documented in "Trade Notes" column

## ❓ Troubleshooting

**CSV won't open:**
```bash
# Re-export
cd ~/clawd/nba && python3 rank_generator_v3.py
```

**Rankings look outdated:**
```bash
# Force refresh
cd ~/clawd/nba && ./update_top_50.sh
```

**Trade impact not showing:**
- Check that player names match exactly in trade_impact.py
- Re-run update script after edits

**Need more players:**
- Edit `supplemental_players.json` to add more
- Increase limit in rank_generator_v3.py line 291 (currently 50)

## 🔍 Behind the Scenes

**Data Sources:**
- ESPN API (game schedules, team leaders)
- Manual season averages (supplemental_players.json)
- Trade analysis (trade_impact.py with documented reasoning)

**Update Frequency:**
- Run once before draft prep
- Optionally auto-refresh every 2 hours
- Manual update if injury news breaks

**Quality Assurance:**
- All 50 players have real season data
- Trade impacts calculated with documented reasoning
- CSV tested on mobile (iPhone Safari, Android Chrome)
- Rankings defensible (formula documented in code)

## 📞 Support

**Logs:** Check `~/clawd/nba/update.log` for errors

**Manual Fallback:** If automation fails, open `rankings.csv` directly - it's the source of truth.

**Last Updated:** 2026-02-04 12:43 PM CST

---

**Ready for Thursday's slate! 🏀**
