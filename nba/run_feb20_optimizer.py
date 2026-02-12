#!/usr/bin/env python3
"""
Run DawgBowl Optimizer for Feb 20th slate
Loads slate data, runs optimization, exports rankings + CSV
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from dawgbowl_optimizer import DawgBowlOptimizer

def load_slate_data(slate_date: str = '2026-02-20') -> tuple:
    """
    Load slate data for the specified date
    Returns (slate_players, opponent_map, games_info)
    """
    workspace = Path.home() / 'clawd'
    
    # Try multiple slate file formats
    possible_files = [
        workspace / 'data' / f'nba-slate-{slate_date}.json',
        workspace / 'nba' / f'slate_{slate_date}.json',
        workspace / 'nba' / 'slate_feb20.json',
    ]
    
    slate_file = None
    for f in possible_files:
        if f.exists():
            slate_file = f
            break
    
    if not slate_file:
        print(f"⚠️  No slate file found for {slate_date}")
        print(f"Creating sample slate structure...")
        return create_sample_slate()
    
    print(f"📂 Loading slate from: {slate_file}")
    
    with open(slate_file) as f:
        slate_data = json.load(f)
    
    # Parse slate format
    if 'players' in slate_data:
        players = slate_data['players']
    elif 'lineup' in slate_data:
        players = slate_data['lineup']
    else:
        players = slate_data.get('data', [])
    
    # Build opponent map from games
    opponent_map = {}
    if 'games' in slate_data:
        for game in slate_data['games']:
            home = game.get('home_team', '')
            away = game.get('away_team', '')
            if home and away:
                opponent_map[home] = away
                opponent_map[away] = home
    
    # Get games info for context
    games_info = slate_data.get('games', [])
    
    print(f"✓ Loaded {len(players)} players from {len(games_info)} games")
    
    return players, opponent_map, games_info


def create_sample_slate():
    """Create sample slate if no file exists (for testing)"""
    print("📝 Creating sample Feb 20th slate...")
    
    # Top players likely to be on Feb 20th slates
    sample_players = [
        {'player_id': '1629029', 'name': 'Luka Doncic', 'team': 'DAL', 'position': 'PG', 'salary': 11000},
        {'player_id': '203507', 'name': 'Giannis Antetokounmpo', 'team': 'MIL', 'position': 'PF', 'salary': 10500},
        {'player_id': '1628369', 'name': 'Jayson Tatum', 'team': 'BOS', 'position': 'SF', 'salary': 9800},
        {'player_id': '1630162', 'name': 'LaMelo Ball', 'team': 'CHA', 'position': 'PG', 'salary': 9500},
        {'player_id': '201939', 'name': 'Stephen Curry', 'team': 'GSW', 'position': 'PG', 'salary': 10000},
        {'player_id': '1629630', 'name': 'Tyrese Haliburton', 'team': 'IND', 'position': 'PG', 'salary': 9200},
        {'player_id': '203081', 'name': 'Damian Lillard', 'team': 'MIL', 'position': 'PG', 'salary': 8800},
        {'player_id': '203999', 'name': 'Nikola Jokic', 'team': 'DEN', 'position': 'C', 'salary': 11200},
        {'player_id': '1629027', 'name': 'Trae Young', 'team': 'ATL', 'position': 'PG', 'salary': 9400},
        {'player_id': '1630169', 'name': 'Anthony Edwards', 'team': 'MIN', 'position': 'SG', 'salary': 9600},
        {'player_id': '203076', 'name': 'Anthony Davis', 'team': 'LAL', 'position': 'PF', 'salary': 10200},
        {'player_id': '203954', 'name': 'Joel Embiid', 'team': 'PHI', 'position': 'C', 'salary': 10800},
        {'player_id': '1630163', 'name': 'Tyrese Maxey', 'team': 'PHI', 'position': 'PG', 'salary': 8500},
        {'player_id': '1628368', 'name': 'De\'Aaron Fox', 'team': 'SAC', 'position': 'PG', 'salary': 9100},
        {'player_id': '203897', 'name': 'Devin Booker', 'team': 'PHX', 'position': 'SG', 'salary': 9300},
    ]
    
    opponent_map = {
        'DAL': 'LAL', 'LAL': 'DAL',
        'MIL': 'CHA', 'CHA': 'MIL',
        'BOS': 'ATL', 'ATL': 'BOS',
        'GSW': 'SAC', 'SAC': 'GSW',
        'IND': 'DEN', 'DEN': 'IND',
        'MIN': 'PHX', 'PHX': 'MIN',
        'PHI': 'NYK', 'NYK': 'PHI',
    }
    
    games_info = [
        {'home_team': 'LAL', 'away_team': 'DAL', 'time': '10:00 PM ET'},
        {'home_team': 'MIL', 'away_team': 'CHA', 'time': '8:00 PM ET'},
        {'home_team': 'BOS', 'away_team': 'ATL', 'time': '7:30 PM ET'},
        {'home_team': 'GSW', 'away_team': 'SAC', 'time': '10:30 PM ET'},
        {'home_team': 'IND', 'away_team': 'DEN', 'time': '7:00 PM ET'},
        {'home_team': 'MIN', 'away_team': 'PHX', 'time': '8:00 PM ET'},
        {'home_team': 'PHI', 'away_team': 'NYK', 'time': '7:30 PM ET'},
    ]
    
    return sample_players, opponent_map, games_info


def print_summary_report(rankings: List[Dict], games_info: List[Dict]):
    """Print summary report with confidence scores"""
    print("\n" + "="*80)
    print("🏀 DAWGBOWL RANKINGS REPORT - FEB 20TH")
    print("="*80)
    print(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Players Ranked: {len(rankings)}")
    
    if games_info:
        print(f"\nGames ({len(games_info)}):")
        for game in games_info:
            print(f"  • {game.get('away_team', 'UNK')} @ {game.get('home_team', 'UNK')} - {game.get('time', 'TBD')}")
    
    print("\n" + "-"*80)
    print("TOP 20 PLAYERS")
    print("-"*80)
    print(f"{'Rank':<5} {'Player':<22} {'Team':<5} {'Opp':<5} {'Sal':<7} {'Proj':<7} {'Ceil':<7} {'Floor':<7} {'Value':<6} {'Conf'}")
    print("-"*80)
    
    for p in rankings[:20]:
        conf_emoji = "🟢" if p['form_confidence'] >= 0.8 else "🟡" if p['form_confidence'] >= 0.6 else "🔴"
        print(f"{p['rank']:<5} {p['name'][:20]:<22} {p['team']:<5} {p['opponent']:<5} "
              f"${p['salary']:<6} {p['projection']:<7.1f} {p['ceiling']:<7.1f} "
              f"{p['floor']:<7.1f} {p['value']:<6.2f} {conf_emoji}")
    
    print("\n" + "-"*80)
    print("VALUE PLAYS (Top 10 by Value)")
    print("-"*80)
    
    value_plays = sorted(rankings, key=lambda x: x['value'], reverse=True)[:10]
    for p in value_plays:
        print(f"{p['name']:22s} {p['team']} ${p['salary']:5d} - Value: {p['value']:.2f} | Proj: {p['projection']:.1f}")
    
    print("\n" + "-"*80)
    print("CONSISTENCY FLAGS")
    print("-"*80)
    
    high_variance = [p for p in rankings if 'HIGH_VARIANCE' in p['consistency_flag']]
    if high_variance:
        print(f"\n⚠️  High Variance ({len(high_variance)} players):")
        for p in high_variance[:5]:
            print(f"  • {p['name']} ({p['team']}) - {p['consistency_flag']}")
    
    trending_down = [p for p in rankings if 'TRENDING_DOWN' in p['consistency_flag']]
    if trending_down:
        print(f"\n📉 Trending Down ({len(trending_down)} players):")
        for p in trending_down[:5]:
            print(f"  • {p['name']} ({p['team']}) - {p['consistency_flag']}")
    
    print("\n" + "="*80)
    print("✅ REPORT COMPLETE")
    print("="*80 + "\n")


def main():
    slate_date = '2026-02-20'
    
    print("\n" + "="*80)
    print("🏀 NBA DAWGBOWL OPTIMIZER - FEB 20TH")
    print("="*80 + "\n")
    
    # Load slate
    slate_players, opponent_map, games_info = load_slate_data(slate_date)
    
    if not slate_players:
        print("❌ No players to process")
        sys.exit(1)
    
    # Initialize optimizer
    optimizer = DawgBowlOptimizer()
    
    # Run optimization
    rankings = optimizer.optimize_slate(slate_players, opponent_map)
    
    if not rankings:
        print("❌ Optimization failed")
        sys.exit(1)
    
    # Save outputs
    json_file = optimizer.save_rankings(rankings, slate_date)
    csv_file = optimizer.export_underdog_csv(rankings, f'underdog_rankings_{slate_date}.csv')
    
    # Print summary report
    print_summary_report(rankings, games_info)
    
    print(f"\n📁 Output files:")
    print(f"  • JSON: {json_file}")
    print(f"  • CSV:  {csv_file}")
    print(f"\n✅ Ready to upload to Underdog Fantasy!")


if __name__ == '__main__':
    main()
