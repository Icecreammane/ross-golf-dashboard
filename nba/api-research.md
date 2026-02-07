# NBA API Research

## balldontlie.io
- **Free tier limitations:** 5 req/min, only teams/players/games (no stats, injuries, odds)
- **ALL-STAR ($9.99/mo):** 60 req/min, adds injuries, game player stats
- **GOAT ($39.99/mo):** 600 req/min, full data including betting odds, props

**Verdict:** Free tier too limited for our needs. Would need at least ALL-STAR for injuries.

## NBA Stats API (stats.nba.com)
- **Cost:** Free
- **Data:** Official NBA stats, player stats, team stats, box scores
- **Limitations:** Unofficial, no official docs, rate limits unclear
- **Endpoints:** 
  - `https://stats.nba.com/stats/` various endpoints
  - No authentication required
  
**Verdict:** Worth trying as primary source for stats

## ESPN Hidden API
- **Cost:** Free
- **Data:** Scores, schedules, basic stats
- **Example:** `http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard`

**Verdict:** Good for schedules and game info

## Next Steps:
1. Test NBA Stats API for player stats
2. Test ESPN API for schedules
3. Find injury report source (RotoWire has public pages we could scrape)
