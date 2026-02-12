# NBA DawgBowl Rankings Optimizer v2.0

**Professional-grade DFS projection system** for Underdog Fantasy, built to Drew Dinkmeyer/ETR standards.

---

## 🎯 What This System Does

This optimizer generates elite-level DFS projections using:

1. **Real STL/BLK data** (not estimates) - Phase 1
2. **Recent form weighting** (60/40 split: 60% last 5-10 games, 40% season avg) - Phase 2
3. **Usage rate multipliers** (ceiling/floor adjustments) - Phase 3
4. **Minutes consistency checks** (flags variance & trends) - Phase 4
5. **Enhanced matchup analysis** (position defense + pace factors) - Phase 5

### Output Files

- **JSON rankings** - Complete player data with all metrics
- **Underdog CSV** - Upload-ready format for Underdog Fantasy
- **Validation report** - Accuracy metrics vs actual results

---

## 🚀 Quick Start

### Generate Feb 20th Rankings

```bash
cd ~/clawd/nba
python3 run_feb20_optimizer.py
```

This will:
1. Load the Feb 20th slate (or create sample if missing)
2. Fetch real-time stats from NBA.com API
3. Calculate projections using all 5 phases
4. Export rankings to JSON + CSV
5. Print summary report with top plays

### Validate System Accuracy

```bash
python3 validate_optimizer.py
```

Tests the optimizer on the last 3 slates with real game results. Shows:
- Mean Absolute Error (MAE)
- Hit Rate (projections within ceiling/floor)
- Best/worst predictions

### Test CSV Export Format

```bash
python3 test_csv_format.py
```

Validates that the CSV export is compatible with Underdog Fantasy upload.

---

## 📊 Core Features

### Phase 1: Real Defensive Stats
- **No more estimates!** Pulls actual STL/BLK per game from NBA.com
- Season averages + advanced metrics (usage rate, pace, efficiency)

### Phase 2: Recent Form Weighting
- **60/40 split**: 60% weight on last 5-10 games, 40% on season average
- Smart handling when limited game samples exist
- Form confidence score based on data availability

### Phase 3: Usage Rate Multipliers
- **Ceiling boost** for high-usage stars (30%+ usage = 1.35x ceiling)
- **Floor penalty** for variance (high usage = more bust risk)
- Drew Dinkmeyer method: usage 25%+ gets significant ceiling bump

### Phase 4: Minutes Consistency
- Variance analysis over last 10 games
- **Flags**:
  - `CONSISTENT` - Reliable minutes (< 15% variance)
  - `MODERATE_VARIANCE` - Some inconsistency (15-25%)
  - `HIGH_VARIANCE` - Risky (> 25% variance)
  - `TRENDING_UP/DOWN` - Minutes increasing/decreasing
- Consistency score impacts final projection confidence

### Phase 5: Enhanced Matchup Analysis
- **Opponent defense quality** (elite/good/average/poor/worst)
- **Pace factors** (high pace = more possessions = higher projections)
- Combined multiplier applied to base projection

---

## 📁 File Structure

```
~/clawd/nba/
├── dawgbowl_optimizer.py         # Core optimizer engine
├── run_feb20_optimizer.py        # Run for Feb 20th slate
├── validate_optimizer.py         # Accuracy validation
├── test_csv_format.py            # CSV format checker
├── DAWGBOWL_README.md           # This file
├── dawgbowl_rankings_2026-02-20.json   # Output: Full rankings
├── underdog_rankings_2026-02-20.csv    # Output: Underdog upload
└── validation_report.json        # Output: Accuracy metrics
```

---

## 🎓 How to Use Rankings

### Top Plays
Sort by **Projection** for overall best plays on the slate.

### Value Plays
Sort by **Value** (projection per $1K salary) for salary-saving options.

### Ceiling Plays (Tournaments)
Sort by **Ceiling** for GPP/tournament upside plays.

### Safe Plays (Cash Games)
- Filter by **Consistency Flag**: `CONSISTENT`
- Sort by **Floor** for safe floor plays
- Check **Form Confidence**: 0.80+ is ideal

### Red Flags
- `HIGH_VARIANCE` in consistency flag
- `TRENDING_DOWN` in consistency flag
- Low form confidence (< 0.60)
- Matchup multiplier < 0.95 (tough matchup)

---

## 📈 Understanding the Metrics

### Projection
Main fantasy points projection using Underdog scoring:
- Points: 1.0
- Rebounds: 1.2
- Assists: 1.5
- 3PM: 1.0
- Steals: 2.0
- Blocks: 2.0
- Turnovers: -0.5

### Ceiling
Upper range projection (tournament upside). Influenced by:
- Usage rate (higher = bigger ceiling)
- Consistency (variance lowers ceiling confidence)

### Floor
Lower range projection (minimum expected output). Influenced by:
- Usage rate (higher = more variance = lower floor)
- Consistency (inconsistent minutes = lower floor)

### Value
Projection per $1,000 salary. Higher = better value.
- Elite: 6.0+
- Great: 5.0-6.0
- Good: 4.0-5.0
- Average: 3.0-4.0
- Poor: < 3.0

### Form Confidence
0.0-1.0 score based on recent game sample size.
- 1.0 = Full 10 games of data
- 0.5 = Limited data (< 3 games)
- Higher = more reliable projection

### Consistency Score
0.3-1.0 score based on minutes variance.
- 1.0+ = Rock solid minutes
- 0.8-1.0 = Consistent
- 0.6-0.8 = Some variance
- < 0.6 = High risk

---

## 🔧 Customization

### Change Season
Edit `dawgbowl_optimizer.py`:
```python
self.season = "2024-25"  # Change to current season
```

### Adjust Form Weighting
Edit `calculate_recent_form()` method:
```python
# Current: 60/40 split (recent 60%, season 40%)
'form_ppg': (recent_avg['pts'] * 0.6) + (season_avg.get('ppg', 0) * 0.4),

# More aggressive (70/30):
'form_ppg': (recent_avg['pts'] * 0.7) + (season_avg.get('ppg', 0) * 0.3),
```

### Change Usage Multipliers
Edit `calculate_usage_ceiling_multiplier()` method to adjust ceiling boosts.

### Modify Matchup Impact
Edit `calculate_matchup_multiplier()` to tweak defense/pace effects.

---

## 🧪 Validation & Testing

### Expected Accuracy Benchmarks

Based on industry standards (Drew Dinkmeyer, ETR, 4for4):

| Metric | Excellent | Good | Acceptable |
|--------|-----------|------|------------|
| MAE | < 5.0 FP | < 7.0 FP | < 10.0 FP |
| RMSE | < 6.5 FP | < 9.0 FP | < 12.0 FP |
| Hit Rate | > 70% | > 60% | > 50% |

**MAE** = Mean Absolute Error (average projection error)  
**RMSE** = Root Mean Square Error (penalizes large misses)  
**Hit Rate** = % of actuals within ceiling/floor range

### Running Validation

```bash
python3 validate_optimizer.py
```

This tests on the last 3 slates and shows:
- Per-date accuracy metrics
- Overall system grade
- Best/worst predictions
- Detailed error analysis

---

## 🐛 Troubleshooting

### "No slate file found"
The optimizer will create a sample slate. To use real data:
1. Create `~/clawd/nba/slate_feb20.json`
2. Format: `{"players": [...], "games": [...]}`

### "API request failed"
- NBA.com API can be rate-limited
- Script uses 0.6s delay between requests
- If issues persist, try again in a few minutes

### CSV Upload Fails on Underdog
Run format tester:
```bash
python3 test_csv_format.py
```

Common issues:
- Special characters in player names
- Incorrect column headers
- Non-UTF-8 encoding

---

## 📊 Example Output

### Rankings Report
```
TOP 20 PLAYERS
--------------------------------------------------------------------------------
Rank  Player                 Team  Opp   Sal     Proj    Ceil    Floor   Value  Conf
--------------------------------------------------------------------------------
1     Luka Doncic           DAL   LAL   $11000  62.5    78.1    46.9    5.68   🟢
2     Nikola Jokic          DEN   SAC   $11200  61.2    76.5    45.9    5.46   🟢
3     Giannis Antetokounmpo MIL   CHA   $10500  58.9    73.6    44.2    5.61   🟡
...
```

### Value Plays
```
VALUE PLAYS (Top 10 by Value)
--------------------------------------------------------------------------------
Tyrese Maxey          PHI $8500 - Value: 6.24 | Proj: 53.0
Tyrese Haliburton     IND $9200 - Value: 6.12 | Proj: 56.3
De'Aaron Fox           SAC $9100 - Value: 5.89 | Proj: 53.6
...
```

### Consistency Flags
```
⚠️  High Variance (3 players):
  • Joel Embiid (PHI) - HIGH_VARIANCE_TRENDING_DOWN
  • Kawhi Leonard (LAC) - HIGH_VARIANCE
  • Zion Williamson (NOP) - MODERATE_VARIANCE_TRENDING_UP
```

---

## 🎯 Feb 20th Deadline Checklist

- [x] Phase 1: Real STL/BLK data ✅
- [x] Phase 2: Recent form weighting (60/40) ✅
- [x] Phase 3: Usage rate multipliers ✅
- [x] Phase 4: Minutes consistency checks ✅
- [x] Phase 5: Enhanced matchup analysis ✅
- [x] Underdog CSV export (FIXED FORMAT) ✅
- [x] Validation system ✅
- [ ] Run validation on recent slates
- [ ] Load Feb 20th slate data
- [ ] Generate final rankings
- [ ] Test CSV upload on Underdog

**Deadline**: Feb 19th (1 day buffer before Feb 20th DawgBowl)

---

## 📚 References

**Industry Standard Systems:**
- Drew Dinkmeyer (DailyFantasyNerd) - Usage rate methodology
- Establish The Run (ETR) - Recent form weighting
- 4for4 - Ceiling/floor variance modeling

**Data Sources:**
- stats.nba.com API (official NBA stats)
- Real-time game logs
- Advanced metrics (usage, pace, efficiency)

---

## 🤝 Support

Questions? Issues?
- Check validation report for accuracy metrics
- Run test scripts to diagnose problems
- Review recent slates to ensure data availability

---

**Built for Feb 20th DawgBowl. Good luck! 🏀**
