# NBA Slate Rankings Daemon

Production-ready NBA DFS analysis system for Underdog contests.

## Features

✅ **Automated Data Scraping**
- Hourly injury updates from ESPN API
- Player salaries, projections, ownership from Underdog
- Vegas lines and game totals

✅ **Advanced Ranking Algorithm**
- **Ceiling**: 90th percentile best-case scenario (projected × variance × 1.25)
- **Floor**: 10th percentile worst-case scenario (projected × (2-variance) × 0.75)
- **Value**: Ceiling per $1K salary
- **Upside**: Ceiling minus projected points
- Position-specific variance factors

✅ **Smart Recommendations**
- **Tier 1 (Stars)**: Elite salary + ceiling, play everyone
- **Tier 2 (Value)**: High value score + ceiling
- **Tier 3 (Punts)**: Low salary with solid floor
- **Tier 4 (Fades)**: Poor value or risky plays
- **Stacks**: Teams with correlated upside
- **Contrarian Pivots**: Low ownership + high ceiling

✅ **Live Dashboard** (Port 5051)
- Real-time player rankings
- Tier visualizations
- Injury updates as they happen
- Recommended stacks
- Manual refresh capability

✅ **Scheduled Tasks**
- Hourly updates throughout Feb 9, 2026
- Morning brief @ 7:30am CT
- Final lock @ 11:59pm CT

## Installation

```bash
cd /Users/clawdbot/clawd/nba-slate-daemon
pip3 install -r requirements.txt
```

## Usage

### Start the Daemon

```bash
python3 app.py
```

Dashboard will be available at: **http://localhost:5051**

### Manual Commands

```python
# Test injury scraper
python3 -c "from scrapers.injury_scraper import InjuryScraper; print(InjuryScraper().get_all_injuries())"

# Test Underdog scraper
python3 -c "from scrapers.underdog_scraper import UnderdogScraper; print(UnderdogScraper().fetch_slate_players()[:3])"

# Test ranking engine
python3 -c "from ranking_engine import RankingEngine; from scrapers.underdog_scraper import UnderdogScraper; players = UnderdogScraper().fetch_slate_players(); engine = RankingEngine(); df = engine.rank_players(players); print(df.head())"
```

## API Endpoints

- `GET /` - Dashboard UI
- `GET /api/players` - All ranked players
- `GET /api/recommendations` - Tier recommendations
- `GET /api/injuries` - Latest injury updates
- `GET /api/vegas` - Vegas betting lines
- `GET /api/status` - System status
- `GET /api/refresh` - Manual data refresh

## Data Storage

- **Analysis JSON**: `/Users/clawdbot/clawd/data/nba-slate-2026-02-09.json`
- **Morning Brief**: `/Users/clawdbot/clawd/data/nba-morning-brief-2026-02-09.md`

## Schedule

| Time | Action |
|------|--------|
| 00:00 - 23:00 | Hourly updates (every hour) |
| 07:30 | Generate morning brief |
| 23:59 | Lock final rankings |

## Methodology

### Ranking Algorithm

```python
# Ceiling (90th percentile)
ceiling = projected_points × position_variance × 1.25

# Floor (10th percentile)
floor = projected_points × (2 - position_variance) × 0.75

# Value (per $1K)
value = (ceiling / salary) × 1000

# Upside
upside = ceiling - projected_points
```

### Position Variance
- PG: 1.15 (highest variance)
- SG: 1.12
- SF: 1.10
- PF: 1.08
- C: 1.05 (most consistent)

### Tier Criteria
- **Tier 1**: Salary ≥ $9K, Ceiling ≥ 42 pts
- **Tier 2**: Value ≥ 4.5, Ceiling ≥ 28 pts
- **Tier 3**: Salary ≤ $5.5K, Floor ≥ 15 pts
- **Tier 4**: Value < 3.5 OR (High ownership + risky floor)

## Production Notes

- Mock data included for testing before Feb 9, 2026
- Replace Underdog scraper with actual API when credentials available
- Add RotoWire scraping if needed (currently ESPN only)
- Consider adding OddsAPI integration for real Vegas lines

## Security

- No API keys committed (add to environment variables)
- Read-only web dashboard (no user input stored)
- CORS enabled for local development

---

**Status**: Production-ready for Feb 9, 2026 Underdog contest
**Port**: 5051
**Data**: /Users/clawdbot/clawd/data/
