#!/usr/bin/env python3
"""
NBA Underdog Fantasy Projections - Live
Pulls current season stats, calculates daily projections using Underdog scoring
"""

import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class UnderdogNBAProjector:
    """Generate live Underdog Fantasy NBA projections"""
    
    # Underdog Fantasy Scoring
    SCORING = {
        'pts': 1.0,
        'reb': 1.2,
        'ast': 1.5,
        '3pm': 1.0,
        'stl': 2.0,
        'blk': 2.0,
        'to': -0.5
    }
    
    # Defensive efficiency multipliers (worse defense = higher projection)
    DEFENSE_MULTIPLIERS = {
        'excellent': 0.85,   # Strong defense reduces projection
        'good': 0.92,
        'average': 1.0,
        'poor': 1.08,
        'worst': 1.15
    }
    
    def __init__(self):
        self.workspace = Path.home() / 'clawd'
        self.output_file = self.workspace / 'nba' / 'rankings-live.json'
        self.season = "2025-26"
    
    def get_season_stats(self) -> Dict[str, Any]:
        """Fetch current season stats from stats.nba.com"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
                'Referer': 'https://www.nba.com/'
            }
            
            params = {
                'LeagueID': '00',
                'PerMode': 'PerGame',
                'Season': self.season,
                'SeasonType': 'Regular Season'
            }
            
            url = 'https://stats.nba.com/stats/leaguedashplayerstats'
            response = requests.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_stats(data)
            else:
                print(f"⚠️  API returned {response.status_code}")
                return {}
        
        except Exception as e:
            print(f"❌ Error fetching stats: {e}")
            return {}
    
    def _parse_stats(self, data: Dict) -> Dict[str, Any]:
        """Parse stats.nba.com response"""
        if 'resultSets' not in data or not data['resultSets']:
            return {}
        
        result_set = data['resultSets'][0]
        headers = result_set.get('headers', [])
        rows = result_set.get('rowSet', [])
        
        players = {}
        for row in rows:
            player_dict = dict(zip(headers, row))
            player_id = player_dict.get('PLAYER_ID')
            
            if player_id:
                players[str(player_id)] = {
                    'name': player_dict.get('PLAYER_NAME', 'Unknown'),
                    'team': player_dict.get('TEAM_ABBREVIATION', ''),
                    'ppg': float(player_dict.get('PTS', 0) or 0),
                    'rpg': float(player_dict.get('REB', 0) or 0),
                    'apg': float(player_dict.get('AST', 0) or 0),
                    '3pm': float(player_dict.get('FG3M', 0) or 0),
                    'gp': int(player_dict.get('GP', 0) or 0),
                    'min': float(player_dict.get('MIN', 0) or 0)
                }
        
        return players
    
    def load_today_slate(self) -> List[Dict]:
        """Load today's slate data"""
        slate_file = self.workspace / 'data' / 'nba-slate-2026-02-09.json'
        
        if slate_file.exists():
            with open(slate_file) as f:
                data = json.load(f)
                return data.get('players', [])
        
        return []
    
    def estimate_stl_blk(self, player: Dict) -> tuple:
        """Estimate steals and blocks based on position and MPG"""
        min_per_game = player.get('min', 0)
        
        # Rough estimates based on position/role
        # This would be better with actual defensive stats
        base_stl = (min_per_game / 30) * 1.2
        base_blk = (min_per_game / 30) * 0.8
        
        return base_stl, base_blk
    
    def calculate_projection(self, player: Dict, opponent_def_mult: float = 1.0) -> float:
        """Calculate Underdog projection for a player"""
        ppg = player.get('ppg', 0)
        rpg = player.get('rpg', 0)
        apg = player.get('apg', 0)
        three_pm = player.get('3pm', 0)
        stl, blk = self.estimate_stl_blk(player)
        to = player.get('apg', 0) * 0.2  # Rough TO estimate
        
        # Base calculation
        projection = (
            (ppg * self.SCORING['pts']) +
            (rpg * self.SCORING['reb']) +
            (apg * self.SCORING['ast']) +
            (three_pm * self.SCORING['3pm']) +
            (stl * self.SCORING['stl']) +
            (blk * self.SCORING['blk']) +
            (to * self.SCORING['to'])
        )
        
        # Apply opponent defense multiplier
        projection *= opponent_def_mult
        
        return round(projection, 2)
    
    def generate_projections(self) -> List[Dict]:
        """Generate projections for today's slate"""
        print("📊 Pulling season stats...")
        season_stats = self.get_season_stats()
        
        if not season_stats:
            print("⚠️  Using pre-computed data fallback")
            slate = self.load_today_slate()
        else:
            slate = self.load_today_slate()
        
        print(f"📊 Loaded {len(season_stats)} season stats, {len(slate)} players in slate")
        
        projections = []
        
        for player in slate:
            player_id = str(player.get('id', ''))
            
            # Get season stats if available, otherwise use slate defaults
            if player_id in season_stats:
                stats = season_stats[player_id]
            else:
                stats = {
                    'ppg': player.get('stat_projections', {}).get('points', 0),
                    'rpg': player.get('stat_projections', {}).get('rebounds', 0),
                    'apg': player.get('stat_projections', {}).get('assists', 0),
                    '3pm': player.get('stat_projections', {}).get('3pm', 0.5),
                    'min': player.get('stat_projections', {}).get('min', 25)
                }
            
            # Calculate projection
            projection = self.calculate_projection(stats)
            
            # Build result
            result = {
                'rank': len(projections) + 1,
                'name': player.get('name', 'Unknown'),
                'team': player.get('team', ''),
                'position': player.get('position', 'F'),
                'salary': player.get('salary', 5000),
                'projected_underdog': round(projection, 1),
                'ppg': stats.get('ppg', 0),
                'rpg': stats.get('rpg', 0),
                'apg': stats.get('apg', 0),
                'ceiling': round(projection * 1.25, 1),
                'floor': round(projection * 0.75, 1),
                'value': round((projection * 1.25 / player.get('salary', 5000)) * 1000, 2)
            }
            
            projections.append(result)
        
        # Sort by projection
        projections.sort(key=lambda x: x['projected_underdog'], reverse=True)
        
        # Re-rank
        for i, p in enumerate(projections):
            p['rank'] = i + 1
        
        return projections
    
    def save_projections(self, projections: List[Dict]):
        """Save to file"""
        output = {
            'generated_at': datetime.now().isoformat(),
            'slate_date': '2026-02-09',
            'scoring_system': 'Underdog Fantasy',
            'num_players': len(projections),
            'projections': projections
        }
        
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"✅ Saved {len(projections)} projections to {self.output_file}")
        return output


def main():
    projector = UnderdogNBAProjector()
    projections = projector.generate_projections()
    projector.save_projections(projections)
    
    print("\n=== TOP 15 PLAYERS ===")
    for p in projections[:15]:
        print(f"{p['rank']:2d}. {p['name']:25s} {p['team']} ${p['salary']:5d} - {p['projected_underdog']:5.1f} FP")


if __name__ == '__main__':
    main()
