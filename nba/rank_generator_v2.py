#!/usr/bin/env python3
"""
NBA DFS Rankings Generator v2.0
Expanded to Top 50 with Trade Deadline Adjustments
"""

import json
import csv
import requests
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

# Import our new modules
from nba_stats_integration import NBAStatsAPI
from trade_impact import TradeImpactAnalyzer

class NBADataFetcher:
    """Fetches NBA data from ESPN API"""
    
    def __init__(self):
        self.espn_base = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        }
    
    def get_games_for_date(self, date_str: str) -> List[Dict]:
        """Get games for specific date (format: YYYYMMDD)"""
        url = f"{self.espn_base}/scoreboard?dates={date_str}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('events', [])
        except Exception as e:
            print(f"Error fetching games: {e}")
            return []
    
    def get_teams_playing(self, games: List[Dict]) -> List[str]:
        """Extract list of team abbreviations playing in slate"""
        teams = set()
        
        for game in games:
            for competition in game.get('competitions', []):
                for competitor in competition.get('competitors', []):
                    team = competitor.get('team', {})
                    team_abbr = team.get('abbreviation', '')
                    if team_abbr:
                        teams.add(team_abbr)
        
        return list(teams)


class EnhancedRankingEngine:
    """Enhanced ranking engine with trade adjustments"""
    
    def __init__(self):
        self.stats_api = NBAStatsAPI()
        self.trade_analyzer = TradeImpactAnalyzer()
    
    def get_players_for_teams(self, teams: List[str], min_minutes: float = 15.0) -> List[Dict]:
        """
        Get top players from specific teams playing in slate
        Returns comprehensive player data
        """
        print(f"📊 Fetching season stats for all players...")
        
        # Get all player stats from NBA API
        all_players = self.stats_api.get_top_players_by_fantasy_points(
            min_minutes=min_minutes,
            limit=200  # Get more than we need
        )
        
        # Get advanced stats for enrichment
        print("📈 Fetching advanced stats...")
        advanced_stats = self.stats_api.get_advanced_stats()
        advanced_by_id = {str(p['PLAYER_ID']): p for p in advanced_stats}
        
        # Filter to teams in slate and enrich data
        slate_players = []
        
        for player in all_players:
            if player['team'] in teams:
                player_id = str(player['player_id'])
                
                # Add advanced stats if available
                if player_id in advanced_by_id:
                    adv = advanced_by_id[player_id]
                    player['usage_rate'] = adv.get('USG_PCT', 20.0)
                    player['true_shooting_pct'] = adv.get('TS_PCT', 0.5)
                    player['defensive_rating'] = adv.get('DEF_RATING', 110)
                    player['offensive_rating'] = adv.get('OFF_RATING', 110)
                    player['pace'] = adv.get('PACE', 100)
                    player['pie'] = adv.get('PIE', 0.1)
                else:
                    # Set defaults
                    player['usage_rate'] = 20.0
                    player['true_shooting_pct'] = 0.5
                    player['defensive_rating'] = 110
                    player['offensive_rating'] = 110
                    player['pace'] = 100
                    player['pie'] = 0.1
                
                # Store season stats with different keys
                player['season_ppg'] = player['ppg']
                player['season_rpg'] = player['rpg']
                player['season_apg'] = player['apg']
                player['season_min'] = player.get('min', 0)
                player['season_gp'] = player.get('gp', 0)
                
                slate_players.append(player)
        
        print(f"✓ Found {len(slate_players)} players from slate teams")
        
        return slate_players
    
    def assign_opponents_and_times(self, players: List[Dict], games: List[Dict]) -> List[Dict]:
        """Assign opponent and game time info to each player"""
        # Build team -> opponent/time mapping
        team_info = {}
        
        for game in games:
            game_time = game.get('date')
            
            for competition in game.get('competitions', []):
                competitors = competition.get('competitors', [])
                if len(competitors) == 2:
                    team1 = competitors[0].get('team', {}).get('abbreviation', '')
                    team2 = competitors[1].get('team', {}).get('abbreviation', '')
                    is_home_1 = competitors[0].get('homeAway') == 'home'
                    is_home_2 = competitors[1].get('homeAway') == 'home'
                    
                    team_info[team1] = {
                        'opponent': team2,
                        'game_time': game_time,
                        'is_home': is_home_1
                    }
                    team_info[team2] = {
                        'opponent': team1,
                        'game_time': game_time,
                        'is_home': is_home_2
                    }
        
        # Assign to players
        for player in players:
            team = player.get('team', '')
            if team in team_info:
                info = team_info[team]
                player['opponent'] = info['opponent']
                player['game_time'] = info['game_time']
                player['is_home'] = info['is_home']
            else:
                player['opponent'] = 'Unknown'
                player['game_time'] = ''
                player['is_home'] = False
        
        return players
    
    def calculate_enhanced_projection(self, player: Dict) -> float:
        """
        Calculate fantasy projection with advanced factors
        Formula: Base stats + matchup modifier + home boost + usage boost
        """
        ppg = player.get('ppg', 0) or player.get('season_ppg', 0)
        rpg = player.get('rpg', 0) or player.get('season_rpg', 0)
        apg = player.get('apg', 0) or player.get('season_apg', 0)
        
        # Base fantasy points: PPG*1.0 + RPG*1.2 + APG*1.5
        base_points = (ppg * 1.0) + (rpg * 1.2) + (apg * 1.5)
        
        # Home court advantage
        if player.get('is_home', False):
            base_points *= 1.05
        
        # Usage rate boost (higher usage = more opportunities)
        usage = player.get('usage_rate', 20.0)
        if usage > 28:
            base_points *= 1.10  # High usage players get boost
        elif usage > 25:
            base_points *= 1.05
        
        # Efficiency boost (high TS%)
        ts_pct = player.get('true_shooting_pct', 0.5)
        if ts_pct > 0.60:
            base_points *= 1.03
        
        return base_points
    
    def generate_rankings(self, players: List[Dict]) -> List[Dict]:
        """
        Generate final rankings with all enhancements
        Returns top 50 players
        """
        print("\n🧮 Calculating enhanced projections...")
        
        # Calculate projections
        for player in players:
            player['projected_fantasy_points'] = round(
                self.calculate_enhanced_projection(player), 2
            )
        
        # Apply trade adjustments
        players = self.trade_analyzer.apply_to_rankings(players)
        
        # Sort and take top 50
        players.sort(key=lambda x: x.get('projected_fantasy_points', 0), reverse=True)
        top_50 = players[:50]
        
        # Assign final ranks
        for idx, player in enumerate(top_50, 1):
            player['rank'] = idx
        
        print(f"✅ Generated Top 50 rankings")
        
        return top_50


def export_to_csv(rankings: List[Dict], output_path: str):
    """Export rankings to CSV with trade impact column"""
    print(f"\n💾 Exporting to CSV: {output_path}")
    
    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = [
            'Rank',
            'Player',
            'Team',
            'vs',
            'Position',
            'Home',
            'Proj FP',
            'PPG',
            'RPG',
            'APG',
            'Min/G',
            'Usage%',
            'Trade Impact',
            'Trade Notes'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for player in rankings:
            writer.writerow({
                'Rank': player['rank'],
                'Player': player['name'],
                'Team': player['team'],
                'vs': player.get('opponent', ''),
                'Position': player.get('position', 'F'),
                'Home': 'Y' if player.get('is_home', False) else 'N',
                'Proj FP': player['projected_fantasy_points'],
                'PPG': round(player.get('ppg', 0) or player.get('season_ppg', 0), 1),
                'RPG': round(player.get('rpg', 0) or player.get('season_rpg', 0), 1),
                'APG': round(player.get('apg', 0) or player.get('season_apg', 0), 1),
                'Min/G': round(player.get('season_min', 0), 1),
                'Usage%': round(player.get('usage_rate', 0), 1),
                'Trade Impact': player.get('trade_impact', 'None'),
                'Trade Notes': player.get('trade_notes', '')
            })
    
    print(f"✓ CSV exported successfully")


def generate_markdown_report(rankings: List[Dict], output_path: str):
    """Generate comprehensive markdown report"""
    with open(output_path, 'w') as f:
        f.write("# NBA DFS Rankings Report - Top 50\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %I:%M %p CST')}\n")
        f.write(f"**Slate:** Thursday 2/6/26 (8 games)\n\n")
        
        # Trade deadline summary
        f.write("## ⚡ Trade Deadline Adjustments\n\n")
        analyzer = TradeImpactAnalyzer()
        f.write(analyzer.get_trade_summary())
        f.write("\n---\n\n")
        
        # Top 50 table
        f.write("## Top 50 Players\n\n")
        f.write("| Rank | Player | Team | vs | Pos | Home | Proj FP | PPG | RPG | APG | Usage | Trade |\n")
        f.write("|------|--------|------|----|----|------|---------|-----|-----|-----|-------|-------|\n")
        
        for player in rankings:
            home_indicator = "✓" if player.get('is_home') else ""
            trade_icon = "🔥" if player.get('trade_impact') == 'HIGH' else "⚠️" if player.get('trade_impact') == 'MED' else ""
            
            f.write(f"| {player['rank']} | {player['name']} | {player['team']} | {player.get('opponent', '')} | "
                   f"{player.get('position', 'F')} | {home_indicator} | {player['projected_fantasy_points']} | "
                   f"{player.get('ppg', 0):.1f} | {player.get('rpg', 0):.1f} | {player.get('apg', 0):.1f} | "
                   f"{player.get('usage_rate', 0):.1f}% | {trade_icon} |\n")
        
        # Trade-impacted players section
        f.write("\n## 🔄 Trade-Impacted Players\n\n")
        
        for impact_level in ['HIGH', 'MED', 'LOW']:
            impacted = [p for p in rankings if p.get('trade_impact') == impact_level]
            if impacted:
                f.write(f"\n### {impact_level} Impact ({len(impacted)} players)\n\n")
                for player in impacted:
                    f.write(f"- **#{player['rank']} {player['name']}** ({player['team']}) - {player['projected_fantasy_points']} FP\n")
                    if player.get('trade_notes'):
                        f.write(f"  *{player['trade_notes']}*\n")
        
        # Position breakdown
        f.write("\n## Position Breakdown\n\n")
        by_position = {}
        for player in rankings:
            pos = player.get('position', 'F')
            if pos not in by_position:
                by_position[pos] = []
            by_position[pos].append(player)
        
        for pos in ['G', 'F', 'C']:
            if pos in by_position:
                f.write(f"\n### Top {pos} ({len(by_position[pos])} players)\n\n")
                for player in by_position[pos][:10]:
                    f.write(f"- **{player['name']}** ({player['team']}) - {player['projected_fantasy_points']} FP\n")


def main():
    print("🏀 NBA Rankings Generator v2.0 - Top 50 with Trade Adjustments")
    print("=" * 70)
    
    # Fetch games for Thursday 2/6/26
    fetcher = NBADataFetcher()
    print("\n📥 Fetching game data for Thursday 2/6/26...")
    games = fetcher.get_games_for_date('20260206')
    
    if not games:
        print("❌ No games found for this date")
        return
    
    print(f"✓ Found {len(games)} games")
    
    # Get teams playing
    teams = fetcher.get_teams_playing(games)
    print(f"✓ Teams in slate: {', '.join(sorted(teams))}")
    
    # Generate rankings
    engine = EnhancedRankingEngine()
    
    # Get players from slate teams (15+ MPG minimum)
    players = engine.get_players_for_teams(teams, min_minutes=15.0)
    
    # Assign opponent/time info
    players = engine.assign_opponents_and_times(players, games)
    
    # Generate final rankings
    rankings = engine.generate_rankings(players)
    
    # Save JSON output
    json_path = "/Users/clawdbot/clawd/nba/rankings.json"
    print(f"\n💾 Saving JSON to {json_path}...")
    with open(json_path, 'w') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'slate_date': '2026-02-06',
            'num_games': len(games),
            'num_players': len(rankings),
            'version': '2.0',
            'includes_trade_adjustments': True,
            'rankings': rankings
        }, f, indent=2)
    print("✓ JSON saved")
    
    # Export to CSV
    csv_path = "/Users/clawdbot/clawd/nba/rankings.csv"
    export_to_csv(rankings, csv_path)
    
    # Generate markdown report
    md_path = "/Users/clawdbot/clawd/nba/rankings-report.md"
    print(f"\n📝 Generating report to {md_path}...")
    generate_markdown_report(rankings, md_path)
    print("✓ Report generated")
    
    print("\n" + "=" * 70)
    print("✅ Top 50 Rankings generation complete!")
    print(f"\nTop 10 Players:")
    for player in rankings[:10]:
        trade_marker = " 🔥" if player.get('trade_impact') == 'HIGH' else " ⚠️" if player.get('trade_impact') == 'MED' else ""
        print(f"  {player['rank']}. {player['name']} ({player['team']}) - {player['projected_fantasy_points']} FP{trade_marker}")
    
    # Show trade-impacted players
    high_impact = [p for p in rankings if p.get('trade_impact') == 'HIGH']
    if high_impact:
        print(f"\n🔥 High-Impact Trade Adjustments ({len(high_impact)} players):")
        for p in high_impact:
            print(f"  • {p['name']} - {p.get('trade_notes', '')}")


if __name__ == "__main__":
    main()
