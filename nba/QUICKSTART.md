# NBA Rankings - Quick Start

## 🎯 What Ross Needs to Know

This system ranks NBA players for Thursday's 8-game slate (2/6/26) to help with DFS decisions.

## 📱 Commands

### View Dashboard (Best for quick review)
```bash
cd ~/clawd/nba && python3 dashboard.py
```

### Update Rankings
```bash
cd ~/clawd/nba && ./update_rankings.sh
```

### Read Full Report
```bash
cat ~/clawd/nba/rankings-report.md
```

## 🏆 Top Plays (Current)

**Guards:**
1. Luka Doncic (LAL) - 48.8 FP
2. Cade Cunningham (DET) - 42.0 FP
3. Tyrese Maxey (PHI) - 39.1 FP

**Forwards:**
1. Jalen Johnson (ATL) - 50.2 FP
2. Paolo Banchero (ORL) - 41.2 FP
3. Victor Wembanyama (SA) - 37.3 FP

**Centers:**
1. Alex Sarr (WSH) - 26.7 FP
2. Alperen Sengun (HOU) - 21.8 FP
3. Jalen Duren (DET) - 13.5 FP

## 🚨 Update Injuries

Edit `injuries.json` with latest injury reports:
```bash
nano ~/clawd/nba/injuries.json
```

## 📊 Data Files

- **rankings.json** - Raw data (for apps/analysis)
- **rankings-report.md** - Human-readable report
- **injuries.json** - Manual injury tracking

## 🔄 How Often to Update

- **Morning of game day:** Get fresh data
- **2 hours before games:** Final injury updates
- **After lineup news:** Re-run if major changes

## 💡 Tips

1. **Home court matters:** +5% boost already applied
2. **Check injuries manually:** System doesn't auto-track yet (coming soon)
3. **High usage players:** Prioritize guards/forwards with high AST and PTS
4. **Game pace:** Higher projected totals = more fantasy points (check Vegas lines separately)

## 🐛 Issues?

- **No data?** Check internet connection, ESPN API might be down
- **Old rankings?** Run `./update_rankings.sh`
- **Need help?** Check `README.md` for details

## 📅 Games Thursday 2/6/26

| Time (EST) | Away | Home |
|------------|------|------|
| 7:00 PM | WSH | DET |
| 7:00 PM | BKN | ORL |
| 7:30 PM | UTAH | ATL |
| 7:30 PM | CHI | TOR |
| 8:00 PM | CHA | HOU |
| 8:30 PM | SA | DAL |
| 10:00 PM | GS | PHX |
| 10:00 PM | PHI | LAL |

---
**Last Updated:** 2026-02-04  
**System Status:** ✅ Operational
