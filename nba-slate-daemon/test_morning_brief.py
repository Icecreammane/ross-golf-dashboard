#!/usr/bin/env python3
"""
Test script to generate a sample morning brief
"""
import sys
sys.path.insert(0, '/Users/clawdbot/clawd/nba-slate-daemon')

from scrapers.injury_scraper import InjuryScraper
from scrapers.underdog_scraper import UnderdogScraper
from ranking_engine import RankingEngine
from datetime import datetime
import os

print("Generating sample morning brief...")

# Fetch data
injury_scraper = InjuryScraper()
underdog_scraper = UnderdogScraper()
ranking_engine = RankingEngine()

injuries = injury_scraper.get_all_injuries()
players = underdog_scraper.fetch_slate_players()
ranked_df = ranking_engine.rank_players(players)
ranked_df = ranking_engine.assign_tiers(ranked_df)
recs = ranking_engine.generate_recommendations(ranked_df)

# Generate brief
brief = f"""# NBA DFS Morning Brief - February 9, 2026
Generated at {datetime.now().strftime('%I:%M %p CT')}

## 🌟 Top 5 Stars (Play Everyone)
"""

for i, player in enumerate(recs.get('top_stars', [])[:5], 1):
    brief += f"{i}. **{player['name']}** ({player['team']}) - ${player['salary']:,}\n"
    brief += f"   - Ceiling: {player['ceiling']} | Floor: {player['floor']} | Value: {player['value']}\n"
    brief += f"   - Ownership: {player['ownership_pct']}%\n\n"

brief += "\n## 💰 Top 5 Value Plays\n"
for i, player in enumerate(recs.get('top_value', [])[:5], 1):
    brief += f"{i}. **{player['name']}** ({player['team']}) - ${player['salary']:,}\n"
    brief += f"   - Ceiling: {player['ceiling']} | Value: {player['value']} | Ownership: {player['ownership_pct']}%\n\n"

brief += "\n## 🔥 2 Recommended Stacks\n"
for i, stack in enumerate(recs.get('recommended_stacks', [])[:2], 1):
    brief += f"{i}. **{stack['team']} Stack** - ${stack['total_salary']:,}\n"
    brief += f"   - Players: {', '.join(stack['players'])}\n"
    brief += f"   - Combined Ceiling: {stack['combined_ceiling']} | Upside: {stack['combined_upside']}\n\n"

brief += "\n## 🚫 3 Fades (Avoid)\n"
for i, player in enumerate(recs.get('top_fades', [])[:3], 1):
    brief += f"{i}. **{player['name']}** ({player['team']}) - ${player['salary']:,}\n"
    brief += f"   - Reason: Poor value ({player['value']}) or risky floor ({player['floor']})\n\n"

brief += "\n## 🏥 Injury News Summary\n"
injury_count = injuries.get('count', 0)
brief += f"Total injury reports: {injury_count}\n\n"

for injury in injuries.get('injuries', [])[:5]:
    brief += f"- **{injury['headline']}**\n"
    brief += f"  {injury['description'][:150]}...\n\n"

brief += "\n---\n"
brief += "Dashboard updates live throughout the day at http://localhost:5051\n"
brief += "Final rankings lock at 11:59pm CT\n"

# Save brief
output_file = '/Users/clawdbot/clawd/data/nba-morning-brief-2026-02-09.md'
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, 'w') as f:
    f.write(brief)

print(f"\n✅ Morning brief saved to {output_file}")
print("\nPreview:")
print("="*60)
print(brief[:500] + "...\n")
