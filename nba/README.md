# NBA DFS Rankings Engine

Automated player rankings system for NBA DFS optimization. Built for the Thursday 2/6/26 slate (8 games).

## 🚀 Quick Start

**Generate rankings:**
```bash
./update_rankings.sh
```

**Or run Python directly:**
```bash
python3 rank_generator.py
```

## 📊 Output Files

### rankings.json
Complete data in JSON format. Includes:
- Player rankings with projected fantasy points
- Team matchups
- Home/away status
- Season averages (PPG, RPG, APG)

**Use for:** Apps, further analysis, data exports

### rankings-report.md
Human-readable markdown report. Includes:
- Top 50 players ranked by projected fantasy points
- Position-specific breakdowns (G, F, C)
- Matchup details

**Use for:** Quick review, sharing with humans

## 🧮 Ranking Algorithm

**Fantasy Points Formula:**
```
FP = (PPG × 1.0) + (RPG × 1.2) + (APG × 1.5)
```

**Modifiers:**
- Home court advantage: +5%
- (Future: Matchup quality, injuries, pace, usage)

## 📅 Thursday 2/6/26 Slate

**8 Games:**
1. WSH @ DET (7:00 PM EST)
2. BKN @ ORL (7:00 PM EST)
3. UTAH @ ATL (7:30 PM EST)
4. CHI @ TOR (7:30 PM EST)
5. CHA @ HOU (8:00 PM EST)
6. SA @ DAL (8:30 PM EST)
7. GS @ PHX (10:00 PM EST)
8. PHI @ LAL (10:00 PM EST)

## 🔄 Data Sources

### Current (v1.0)
- **ESPN API** - Game schedules, team leaders, season stats
  - Free, reliable, no authentication
  - Updates: Real-time

### Planned
- **NBA Stats API** - Full player statistics
- **Injury Reports** - RotoWire/ESPN scraping
- **Vegas Lines** - Game totals for pace indicators
- **Defensive Ratings** - Matchup quality analysis

## 📈 Future Enhancements

**v1.1 - Enhanced Stats**
- [ ] Full season averages from NBA Stats API
- [ ] Last 7 days trending (hot/cold players)
- [ ] Usage rate indicators

**v1.2 - Matchup Analysis**
- [ ] Defensive ratings by position
- [ ] Pace factors (Vegas game totals)
- [ ] Historical performance vs opponent

**v1.3 - Injury Intel**
- [ ] Injury status tracking
- [ ] Opportunity boosts for replacements
- [ ] GTD (game-time decision) flags

**v1.4 - DFS Optimization**
- [ ] Salary data integration (DraftKings, FanDuel)
- [ ] Value rankings (FP per $1000)
- [ ] Lineup optimizer
- [ ] Stack recommendations

## 🛠️ Tech Stack

- **Python 3** - Core ranking engine
- **requests** - HTTP client for APIs
- **json** - Data serialization
- **Bash** - Automation scripts

## 📝 Usage Examples

**View top 10 players:**
```bash
cat rankings.json | jq '.rankings[:10]'
```

**See top guards:**
```bash
cat rankings.json | jq '.rankings[] | select(.position=="G") | {rank, name, projected_fantasy_points}' | head -20
```

**Check home games only:**
```bash
cat rankings.json | jq '.rankings[] | select(.is_home==true) | {rank, name, team}'
```

## 🐛 Known Limitations

1. **Limited stat depth:** Currently only using team leader stats (PPG/RPG/APG). Full player stats coming in v1.1.

2. **No injury data:** Manual injury checking still needed. Auto-tracking coming in v1.3.

3. **No salaries:** Rankings are pure fantasy points, not value-based. Salary integration in v1.4.

4. **Simple matchup logic:** Only using home/away. Defensive ratings coming in v1.2.

## 🔍 Validation

Test against tonight's games (2/4/26) to validate projections vs actual performance.

## 📞 Support

Questions? Check:
- Build log: `~/clawd/memory/nba-rankings-build.md`
- API research: `~/clawd/nba/api-research.md`

---
**Built:** 2026-02-04  
**For:** Thursday 2/6/26 slate  
**Status:** ✅ Operational
