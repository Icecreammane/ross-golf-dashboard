#!/usr/bin/env python3
"""
NBA DFS Rankings Generator
Pulls stats, matchup data, and generates player rankings for DFS optimization
"""

import json
import requests
from datetime import datetime
from typing import Dict, List, Any
import time

class NBADataFetcher:
    """Fetches NBA data from multiple free sources"""
    
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
    
    def extract_team_leaders(self, games: List[Dict]) -> List[Dict]:
        """Extract team leader stats from game data"""
        players = []
        
        for game in games:
            game_id = game.get('id')
            game_time = game.get('date')
            
            for competition in game.get('competitions', []):
                for competitor in competition.get('competitors', []):
                    team = competitor.get('team', {})
                    team_name = team.get('displayName', '')
                    is_home = competitor.get('homeAway') == 'home'
                    
                    # Get opponent
                    opponents = [c for c in competition.get('competitors', []) 
                                if c.get('homeAway') != competitor.get('homeAway')]
                    opp_name = opponents[0].get('team', {}).get('displayName', '') if opponents else ''
                    
                    # Extract leader data
                    for leader_cat in competitor.get('leaders', []):
                        for leader in leader_cat.get('leaders', []):
                            athlete = leader.get('athlete', {})
                            players.append({
                                'player_id': athlete.get('id'),
                                'name': athlete.get('displayName', ''),
                                'team': team_name,
                                'opponent': opp_name,
                                'game_id': game_id,
                                'game_time': game_time,
                                'is_home': is_home,
                                'position': athlete.get('position', {}).get('abbreviation', ''),
                                'stat_type': leader_cat.get('abbreviation', ''),
                                'stat_value': leader.get('value', 0)
                            })
        
        return players

class RankingEngine:
    """Calculates player rankings based on multiple factors"""
    
    def __init__(self):
        self.weights = {
            'ppg': 1.0,
            'rpg': 0.8,
            'apg': 0.9,
            'usage': 1.2,  # High usage = more opportunities
            'matchup': 1.0,  # Good matchup multiplier
        }
    
    def aggregate_player_stats(self, player_data: List[Dict]) -> Dict[str, Dict]:
        """Aggregate stats by player"""
        players = {}
        
        for entry in player_data:
            player_id = entry['player_id']
            if not player_id:
                continue
                
            if player_id not in players:
                players[player_id] = {
                    'id': player_id,
                    'name': entry['name'],
                    'team': entry['team'],
                    'opponent': entry['opponent'],
                    'position': entry['position'],
                    'game_time': entry['game_time'],
                    'is_home': entry['is_home'],
                    'stats': {}
                }
            
            # Store stat
            stat_type = entry['stat_type']
            stat_value = entry['stat_value']
            players[player_id]['stats'][stat_type] = stat_value
        
        return players
    
    def calculate_fantasy_score(self, stats: Dict[str, float]) -> float:
        """Calculate baseline fantasy projection"""
        ppg = stats.get('PTS', 0)
        rpg = stats.get('REB', 0)
        apg = stats.get('AST', 0)
        
        # Basic fantasy scoring: 1pt = 1, 1reb = 1.2, 1ast = 1.5
        return (ppg * 1.0) + (rpg * 1.2) + (apg * 1.5)
    
    def rank_players(self, players: Dict[str, Dict]) -> List[Dict]:
        """Generate ranked list of players"""
        rankings = []
        
        for player_id, player_data in players.items():
            stats = player_data['stats']
            base_score = self.calculate_fantasy_score(stats)
            
            # Apply modifiers
            final_score = base_score
            
            # Home court advantage (small boost)
            if player_data['is_home']:
                final_score *= 1.05
            
            rankings.append({
                'rank': 0,  # Will assign after sorting
                'player_id': player_id,
                'name': player_data['name'],
                'team': player_data['team'],
                'opponent': player_data['opponent'],
                'position': player_data['position'],
                'game_time': player_data['game_time'],
                'is_home': player_data['is_home'],
                'projected_fantasy_points': round(final_score, 2),
                'ppg': stats.get('PTS', 0),
                'rpg': stats.get('REB', 0),
                'apg': stats.get('AST', 0),
            })
        
        # Sort by projected points
        rankings.sort(key=lambda x: x['projected_fantasy_points'], reverse=True)
        
        # Assign ranks
        for idx, player in enumerate(rankings, 1):
            player['rank'] = idx
        
        return rankings

def generate_markdown_report(rankings: List[Dict], output_path: str):
    """Generate human-readable markdown report"""
    with open(output_path, 'w') as f:
        f.write("# NBA DFS Rankings Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %I:%M %p CST')}\n\n")
        f.write("## Top 50 Players - Thursday 2/6/26 Slate\n\n")
        f.write("| Rank | Player | Team | vs | Pos | Home | Proj FP | PPG | RPG | APG |\n")
        f.write("|------|--------|------|----|----|------|---------|-----|-----|-----|\n")
        
        for player in rankings[:50]:
            home_indicator = "✓" if player['is_home'] else ""
            f.write(f"| {player['rank']} | {player['name']} | {player['team']} | {player['opponent']} | "
                   f"{player['position']} | {home_indicator} | {player['projected_fantasy_points']} | "
                   f"{player['ppg']:.1f} | {player['rpg']:.1f} | {player['apg']:.1f} |\n")
        
        f.write("\n## Position Breakdown\n\n")
        
        # Group by position
        by_position = {}
        for player in rankings:
            pos = player['position'] or 'UNKNOWN'
            if pos not in by_position:
                by_position[pos] = []
            by_position[pos].append(player)
        
        for pos in ['G', 'F', 'C']:
            if pos in by_position:
                f.write(f"\n### Top {pos} - {len(by_position[pos])} players\n\n")
                for player in by_position[pos][:10]:
                    f.write(f"- **{player['name']}** ({player['team']}) - {player['projected_fantasy_points']} FP\n")

def main():
    print("🏀 NBA Rankings Generator")
    print("=" * 50)
    
    # Fetch data for Thursday 2/6/26
    fetcher = NBADataFetcher()
    print("\n📥 Fetching game data for Thursday 2/6/26...")
    games = fetcher.get_games_for_date('20260205')
    
    if not games:
        print("❌ No games found for this date")
        return
    
    print(f"✓ Found {len(games)} games")
    
    # Extract player data from team leaders
    print("\n📊 Extracting player stats...")
    player_data = fetcher.extract_team_leaders(games)
    print(f"✓ Extracted data for {len(player_data)} player entries")
    
    # Generate rankings
    engine = RankingEngine()
    print("\n🧮 Aggregating player stats...")
    players = engine.aggregate_player_stats(player_data)
    print(f"✓ Found {len(players)} unique players")
    
    print("\n📈 Calculating rankings...")
    rankings = engine.rank_players(players)
    
    # Save JSON output
    json_path = "/Users/clawdbot/clawd/nba/rankings.json"
    print(f"\n💾 Saving JSON to {json_path}...")
    with open(json_path, 'w') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'slate_date': '2026-02-06',
            'num_games': len(games),
            'num_players': len(rankings),
            'rankings': rankings
        }, f, indent=2)
    print("✓ JSON saved")
    
    # Generate markdown report
    md_path = "/Users/clawdbot/clawd/nba/rankings-report.md"
    print(f"\n📝 Generating report to {md_path}...")
    generate_markdown_report(rankings, md_path)
    print("✓ Report generated")
    
    print("\n" + "=" * 50)
    print("✅ Rankings generation complete!")
    print(f"\nTop 10 Players:")
    for player in rankings[:10]:
        print(f"  {player['rank']}. {player['name']} ({player['team']}) - {player['projected_fantasy_points']} FP")

if __name__ == "__main__":
    main()
