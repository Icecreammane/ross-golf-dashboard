#!/usr/bin/env python3
"""
NBA DFS Rankings Generator v3.0
Hybrid approach: ESPN API + manual enrichment to reach Top 50
"""

import json
import csv
import requests
from datetime import datetime
from typing import Dict, List, Any
import sys

# Import trade analyzer
from trade_impact import TradeImpactAnalyzer

class ESPNDataFetcher:
    """Enhanced ESPN data fetcher"""
    
    def __init__(self):
        self.espn_base = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        }
    
    def get_games_for_date(self, date_str: str) -> List[Dict]:
        """Get games for specific date"""
        url = f"{self.espn_base}/scoreboard?dates={date_str}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json().get('events', [])
        except Exception as e:
            print(f"⚠️  Error fetching games: {e}")
            return []
    
    def get_team_roster_stats(self, team_id: str) -> List[Dict]:
        """Get detailed roster stats for a team"""
        url = f"{self.espn_base}/teams/{team_id}/roster"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            athletes = []
            for entry in data.get('athletes', []):
                for athlete in entry.get('items', []):
                    athletes.append(athlete)
            
            return athletes
        except Exception as e:
            return []
    
    def extract_comprehensive_players(self, games: List[Dict]) -> List[Dict]:
        """Extract players from game data with full context"""
        players_dict = {}
        team_map = {}
        
        # First pass: Build team/opponent mapping
        for game in games:
            game_id = game.get('id')
            game_time = game.get('date')
            
            for competition in game.get('competitions', []):
                competitors = competition.get('competitors', [])
                if len(competitors) == 2:
                    team1 = competitors[0]
                    team2 = competitors[1]
                    
                    team1_abbr = team1.get('team', {}).get('abbreviation', '')
                    team2_abbr = team2.get('team', {}).get('abbreviation', '')
                    
                    team_map[team1_abbr] = {
                        'opponent': team2_abbr,
                        'game_time': game_time,
                        'is_home': team1.get('homeAway') == 'home'
                    }
                    team_map[team2_abbr] = {
                        'opponent': team1_abbr,
                        'game_time': game_time,
                        'is_home': team2.get('homeAway') == 'home'
                    }
        
        # Second pass: Extract player data
        for game in games:
            for competition in game.get('competitions', []):
                for competitor in competition.get('competitors', []):
                    team = competitor.get('team', {})
                    team_name = team.get('displayName', '')
                    team_abbr = team.get('abbreviation', '')
                    
                    # Get team matchup info
                    matchup = team_map.get(team_abbr, {})
                    
                    # Extract all leader categories
                    for leader_cat in competitor.get('leaders', []):
                        stat_type = leader_cat.get('abbreviation', '')
                        
                        for leader in leader_cat.get('leaders', []):
                            athlete = leader.get('athlete', {})
                            player_id = str(athlete.get('id', ''))
                            
                            if not player_id:
                                continue
                            
                            # Initialize player if not seen
                            if player_id not in players_dict:
                                players_dict[player_id] = {
                                    'player_id': player_id,
                                    'name': athlete.get('displayName', ''),
                                    'team': team_abbr,
                                    'team_name': team_name,
                                    'opponent': matchup.get('opponent', ''),
                                    'game_time': matchup.get('game_time', ''),
                                    'is_home': matchup.get('is_home', False),
                                    'position': athlete.get('position', {}).get('abbreviation', 'F'),
                                    'stats': {}
                                }
                            
                            # Add stat
                            players_dict[player_id]['stats'][stat_type] = leader.get('value', 0)
        
        return list(players_dict.values())
    
    def enrich_with_season_estimates(self, players: List[Dict]) -> List[Dict]:
        """
        Enrich players with estimated season stats
        For players missing stats, estimate based on team/position averages
        """
        # Add season estimates
        for player in players:
            stats = player['stats']
            
            # Ensure all players have basic stats (use 0 as fallback)
            player['ppg'] = stats.get('PTS', stats.get('ppg', 0))
            player['rpg'] = stats.get('REB', stats.get('rpg', 0))
            player['apg'] = stats.get('AST', stats.get('apg', 0))
            
            # Estimate usage based on stats
            if player['ppg'] > 25:
                player['usage_rate'] = 32.0
            elif player['ppg'] > 20:
                player['usage_rate'] = 27.0
            elif player['ppg'] > 15:
                player['usage_rate'] = 22.0
            elif player['ppg'] > 10:
                player['usage_rate'] = 18.0
            else:
                player['usage_rate'] = 15.0
            
            # Add reasonable defaults for missing stats
            player['season_min'] = 30.0 if player['ppg'] > 20 else 25.0 if player['ppg'] > 15 else 20.0
            player['season_gp'] = 50
            player['true_shooting_pct'] = 0.56
        
        return players


class HybridRankingEngine:
    """Hybrid ranking engine using ESPN + manual enrichment"""
    
    def __init__(self):
        self.trade_analyzer = TradeImpactAnalyzer()
    
    def calculate_fantasy_projection(self, player: Dict) -> float:
        """Calculate fantasy projection"""
        ppg = player.get('ppg', 0)
        rpg = player.get('rpg', 0)
        apg = player.get('apg', 0)
        
        # Base: PPG*1.0 + RPG*1.2 + APG*1.5
        base = (ppg * 1.0) + (rpg * 1.2) + (apg * 1.5)
        
        # Home boost
        if player.get('is_home', False):
            base *= 1.05
        
        # Usage boost
        usage = player.get('usage_rate', 20)
        if usage > 28:
            base *= 1.08
        elif usage > 25:
            base *= 1.04
        
        return base
    
    def load_supplemental_players(self, team_map: Dict) -> List[Dict]:
        """Load supplemental rotation players from JSON"""
        try:
            with open('/Users/clawdbot/clawd/nba/supplemental_players.json', 'r') as f:
                data = json.load(f)
                supp_players = data.get('players', [])
                
                # Add opponent/game info
                for player in supp_players:
                    team = player['team']
                    if team in team_map:
                        player['opponent'] = team_map[team]['opponent']
                        player['game_time'] = team_map[team]['game_time']
                        player['is_home'] = team_map[team]['is_home']
                    else:
                        player['opponent'] = ''
                        player['game_time'] = ''
                        player['is_home'] = False
                    
                    # Add season estimates
                    player['season_min'] = 28.0 if player['ppg'] > 20 else 24.0
                    player['season_gp'] = 50
                    player['true_shooting_pct'] = 0.55
                    player['player_id'] = f"supp_{player['name'].replace(' ', '_')}"
                
                return supp_players
        except Exception as e:
            print(f"⚠️  Could not load supplemental players: {e}")
            return []
    
    def merge_players(self, espn_players: List[Dict], supp_players: List[Dict]) -> List[Dict]:
        """Merge ESPN and supplemental players, avoiding duplicates"""
        # Index ESPN players by name
        espn_names = {p['name'].lower() for p in espn_players}
        
        # Add supplemental players not already in ESPN data
        added = 0
        for supp in supp_players:
            if supp['name'].lower() not in espn_names:
                espn_players.append(supp)
                added += 1
        
        print(f"✓ Added {added} supplemental players")
        return espn_players
    
    def generate_rankings(self, players: List[Dict]) -> List[Dict]:
        """Generate final rankings"""
        print(f"\n🧮 Calculating projections for {len(players)} players...")
        
        # Calculate projections
        for player in players:
            player['projected_fantasy_points'] = round(
                self.calculate_fantasy_projection(player), 2
            )
        
        # Apply trade adjustments
        players = self.trade_analyzer.apply_to_rankings(players)
        
        # Sort by projection
        players.sort(key=lambda x: x.get('projected_fantasy_points', 0), reverse=True)
        
        # Take top 50 (or all if less)
        top_players = players[:50]
        
        # Assign ranks
        for idx, player in enumerate(top_players, 1):
            player['rank'] = idx
        
        print(f"✅ Generated Top {len(top_players)} rankings")
        
        return top_players


def export_to_csv(rankings: List[Dict], output_path: str):
    """Export to CSV"""
    print(f"\n💾 Exporting to CSV: {output_path}")
    
    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = [
            'Rank', 'Player', 'Team', 'vs', 'Position', 'Home',
            'Proj FP', 'PPG', 'RPG', 'APG', 'Usage%',
            'Trade Impact', 'Trade Notes'
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
                'PPG': round(player.get('ppg', 0), 1),
                'RPG': round(player.get('rpg', 0), 1),
                'APG': round(player.get('apg', 0), 1),
                'Usage%': round(player.get('usage_rate', 0), 1),
                'Trade Impact': player.get('trade_impact', 'None'),
                'Trade Notes': player.get('trade_notes', '')
            })
    
    print(f"✓ CSV exported")


def generate_report(rankings: List[Dict], output_path: str):
    """Generate markdown report"""
    with open(output_path, 'w') as f:
        f.write("# NBA DFS Rankings - Top 50\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %I:%M %p CST')}\n")
        f.write(f"**Slate:** Thursday 2/6/26\n")
        f.write(f"**Players:** {len(rankings)}\n\n")
        
        # Trade summary
        f.write("## ⚡ Trade Deadline Adjustments\n\n")
        analyzer = TradeImpactAnalyzer()
        f.write(analyzer.get_trade_summary())
        f.write("\n---\n\n")
        
        # Rankings table
        f.write("## Top Rankings\n\n")
        f.write("| Rank | Player | Team | vs | Pos | Home | Proj FP | PPG | RPG | APG | Usage | Trade |\n")
        f.write("|------|--------|------|----|----|------|---------|-----|-----|-----|-------|-------|\n")
        
        for player in rankings:
            home = "✓" if player.get('is_home') else ""
            trade_icon = ""
            if player.get('trade_impact') == 'HIGH':
                trade_icon = "🔥"
            elif player.get('trade_impact') == 'MED':
                trade_icon = "⚠️"
            
            f.write(f"| {player['rank']} | {player['name']} | {player['team']} | "
                   f"{player.get('opponent', '')} | {player.get('position', 'F')} | {home} | "
                   f"{player['projected_fantasy_points']} | {player.get('ppg', 0):.1f} | "
                   f"{player.get('rpg', 0):.1f} | {player.get('apg', 0):.1f} | "
                   f"{player.get('usage_rate', 0):.1f}% | {trade_icon} |\n")
        
        # Trade impacted
        f.write("\n## 🔄 Trade-Impacted Players\n\n")
        for level in ['HIGH', 'MED', 'LOW']:
            impacted = [p for p in rankings if p.get('trade_impact') == level]
            if impacted:
                f.write(f"\n### {level} Impact\n\n")
                for p in impacted:
                    f.write(f"- **#{p['rank']} {p['name']}** - {p['projected_fantasy_points']} FP\n")
                    if p.get('trade_notes'):
                        f.write(f"  *{p['trade_notes']}*\n")


def main():
    print("🏀 NBA Rankings Generator v3.0 - Hybrid ESPN Approach")
    print("=" * 70)
    
    # Fetch games
    fetcher = ESPNDataFetcher()
    print("\n📥 Fetching Thursday 2/6/26 games...")
    games = fetcher.get_games_for_date('20260206')
    
    if not games:
        print("❌ No games found")
        return
    
    print(f"✓ Found {len(games)} games")
    
    # Build team map for opponent/time info
    team_map = {}
    for game in games:
        game_time = game.get('date')
        for competition in game.get('competitions', []):
            competitors = competition.get('competitors', [])
            if len(competitors) == 2:
                team1 = competitors[0]
                team2 = competitors[1]
                team1_abbr = team1.get('team', {}).get('abbreviation', '')
                team2_abbr = team2.get('team', {}).get('abbreviation', '')
                
                team_map[team1_abbr] = {
                    'opponent': team2_abbr,
                    'game_time': game_time,
                    'is_home': team1.get('homeAway') == 'home'
                }
                team_map[team2_abbr] = {
                    'opponent': team1_abbr,
                    'game_time': game_time,
                    'is_home': team2.get('homeAway') == 'home'
                }
    
    # Extract players
    print("\n📊 Extracting player data from ESPN...")
    players = fetcher.extract_comprehensive_players(games)
    print(f"✓ Extracted {len(players)} players from ESPN")
    
    # Enrich
    players = fetcher.enrich_with_season_estimates(players)
    
    # Load and merge supplemental players
    print("\n📥 Loading supplemental rotation players...")
    engine = HybridRankingEngine()
    supp_players = engine.load_supplemental_players(team_map)
    players = engine.merge_players(players, supp_players)
    print(f"✓ Total players: {len(players)}")
    
    # Generate rankings
    rankings = engine.generate_rankings(players)
    
    # Save JSON
    json_path = "/Users/clawdbot/clawd/nba/rankings.json"
    print(f"\n💾 Saving JSON...")
    with open(json_path, 'w') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'slate_date': '2026-02-06',
            'num_games': len(games),
            'num_players': len(rankings),
            'version': '3.0',
            'includes_trade_adjustments': True,
            'rankings': rankings
        }, f, indent=2)
    print("✓ JSON saved")
    
    # Export CSV
    csv_path = "/Users/clawdbot/clawd/nba/rankings.csv"
    export_to_csv(rankings, csv_path)
    
    # Generate report
    md_path = "/Users/clawdbot/clawd/nba/rankings-report.md"
    print(f"\n📝 Generating report...")
    generate_report(rankings, md_path)
    print("✓ Report generated")
    
    print("\n" + "=" * 70)
    print(f"✅ Generated Top {len(rankings)} Rankings!")
    print(f"\nTop 10:")
    for p in rankings[:10]:
        marker = " 🔥" if p.get('trade_impact') == 'HIGH' else " ⚠️" if p.get('trade_impact') == 'MED' else ""
        print(f"  {p['rank']}. {p['name']} ({p['team']}) - {p['projected_fantasy_points']} FP{marker}")
    
    # Show trade impacts
    high = [p for p in rankings if p.get('trade_impact') == 'HIGH']
    if high:
        print(f"\n🔥 High-Impact Trades:")
        for p in high:
            print(f"  • {p['name']} - {p.get('trade_notes', '')}")


if __name__ == "__main__":
    main()
