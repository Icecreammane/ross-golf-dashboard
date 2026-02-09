"""
Underdog Fantasy Scoring System
Official Underdog NBA scoring format with stat projections
"""
from typing import Dict, List
import json

class UnderdogScoring:
    """
    Underdog Fantasy NBA Scoring Format (Official):
    - Points: 1.0
    - Rebounds: 1.2
    - Assists: 1.5
    - Steals: 3.0
    - Blocks: 3.0
    - Turnovers: -1.0
    """
    
    SCORING = {
        'points': 1.0,
        'rebounds': 1.2,
        'assists': 1.5,
        'steals': 3.0,
        'blocks': 3.0,
        'turnovers': -1.0
    }
    
    def __init__(self):
        self.stat_projections = self._load_stat_projections()
    
    def _load_stat_projections(self) -> Dict:
        """
        Load stat projections for NBA players
        In production: fetch from NBA API or stats database
        For now: realistic projections for top players
        """
        return {
            'Luka Doncic': {'points': 33.5, 'rebounds': 9.2, 'assists': 9.8, 'steals': 1.4, 'blocks': 0.5, 'turnovers': 3.8},
            'Nikola Jokic': {'points': 30.2, 'rebounds': 13.5, 'assists': 10.2, 'steals': 1.2, 'blocks': 0.8, 'turnovers': 3.2},
            'Giannis Antetokounmpo': {'points': 31.8, 'rebounds': 11.2, 'assists': 6.5, 'steals': 1.1, 'blocks': 1.4, 'turnovers': 3.5},
            'Shai Gilgeous-Alexander': {'points': 31.2, 'rebounds': 5.8, 'assists': 6.2, 'steals': 2.1, 'blocks': 0.9, 'turnovers': 2.8},
            'Joel Embiid': {'points': 29.5, 'rebounds': 10.8, 'assists': 5.2, 'steals': 1.0, 'blocks': 1.6, 'turnovers': 3.4},
            'Jayson Tatum': {'points': 28.2, 'rebounds': 8.5, 'assists': 5.8, 'steals': 1.1, 'blocks': 0.6, 'turnovers': 2.5},
            'Kevin Durant': {'points': 27.8, 'rebounds': 6.8, 'assists': 5.2, 'steals': 0.8, 'blocks': 1.2, 'turnovers': 2.8},
            'Stephen Curry': {'points': 26.5, 'rebounds': 4.5, 'assists': 6.2, 'steals': 1.2, 'blocks': 0.4, 'turnovers': 2.9},
            'LeBron James': {'points': 25.8, 'rebounds': 7.2, 'assists': 8.2, 'steals': 1.3, 'blocks': 0.6, 'turnovers': 3.2},
            'Anthony Davis': {'points': 26.2, 'rebounds': 11.2, 'assists': 3.5, 'steals': 1.3, 'blocks': 2.1, 'turnovers': 2.1},
            'Tyrese Haliburton': {'points': 22.5, 'rebounds': 4.2, 'assists': 11.8, 'steals': 1.2, 'blocks': 0.6, 'turnovers': 2.5},
            'Donovan Mitchell': {'points': 26.8, 'rebounds': 4.8, 'assists': 5.2, 'steals': 1.5, 'blocks': 0.4, 'turnovers': 2.8},
            'Damian Lillard': {'points': 25.2, 'rebounds': 4.2, 'assists': 7.2, 'steals': 0.9, 'blocks': 0.3, 'turnovers': 2.6},
            'Trae Young': {'points': 25.8, 'rebounds': 2.8, 'assists': 10.8, 'steals': 1.1, 'blocks': 0.2, 'turnovers': 3.8},
            'Paolo Banchero': {'points': 23.5, 'rebounds': 6.8, 'assists': 5.2, 'steals': 0.9, 'blocks': 0.6, 'turnovers': 2.8},
            'Franz Wagner': {'points': 21.2, 'rebounds': 5.5, 'assists': 5.8, 'steals': 1.2, 'blocks': 0.5, 'turnovers': 2.2},
            'Jalen Brunson': {'points': 24.8, 'rebounds': 3.5, 'assists': 6.8, 'steals': 0.8, 'blocks': 0.2, 'turnovers': 2.1},
            'Darius Garland': {'points': 21.5, 'rebounds': 2.8, 'assists': 8.2, 'steals': 1.2, 'blocks': 0.1, 'turnovers': 2.8},
            'Cade Cunningham': {'points': 22.8, 'rebounds': 4.2, 'assists': 7.5, 'steals': 0.9, 'blocks': 0.4, 'turnovers': 3.2},
            'Scottie Barnes': {'points': 20.5, 'rebounds': 8.2, 'assists': 5.8, 'steals': 1.4, 'blocks': 0.8, 'turnovers': 2.5},
            'Coby White': {'points': 19.8, 'rebounds': 3.8, 'assists': 5.2, 'steals': 1.1, 'blocks': 0.3, 'turnovers': 2.2},
            'Herbert Jones': {'points': 11.2, 'rebounds': 4.8, 'assists': 2.5, 'steals': 1.8, 'blocks': 0.9, 'turnovers': 1.1},
            'Isaiah Stewart': {'points': 11.5, 'rebounds': 8.5, 'assists': 1.2, 'steals': 0.6, 'blocks': 1.1, 'turnovers': 1.2},
            'Keon Ellis': {'points': 10.8, 'rebounds': 3.2, 'assists': 2.8, 'steals': 1.5, 'blocks': 0.4, 'turnovers': 1.0},
            'Jaden McDaniels': {'points': 11.2, 'rebounds': 4.5, 'assists': 1.8, 'steals': 1.2, 'blocks': 1.0, 'turnovers': 1.2},
        }
    
    def calculate_underdog_points(self, player_name: str, custom_stats: Dict = None) -> Dict:
        """
        Calculate Underdog fantasy points for a player
        
        Args:
            player_name: Player name
            custom_stats: Optional dict with stat overrides
        
        Returns:
            Dict with stat breakdown and total Underdog points
        """
        # Get stat projections
        stats = custom_stats if custom_stats else self.stat_projections.get(player_name, {})
        
        # If no stats available, return default
        if not stats:
            stats = {'points': 15.0, 'rebounds': 5.0, 'assists': 3.0, 'steals': 0.8, 'blocks': 0.5, 'turnovers': 2.0}
        
        # Calculate Underdog points
        underdog_pts = (
            stats['points'] * self.SCORING['points'] +
            stats['rebounds'] * self.SCORING['rebounds'] +
            stats['assists'] * self.SCORING['assists'] +
            stats['steals'] * self.SCORING['steals'] +
            stats['blocks'] * self.SCORING['blocks'] +
            stats['turnovers'] * self.SCORING['turnovers']
        )
        
        return {
            'stats': stats,
            'underdog_points': round(underdog_pts, 2),
            'breakdown': {
                'points_contribution': round(stats['points'] * self.SCORING['points'], 2),
                'rebounds_contribution': round(stats['rebounds'] * self.SCORING['rebounds'], 2),
                'assists_contribution': round(stats['assists'] * self.SCORING['assists'], 2),
                'steals_contribution': round(stats['steals'] * self.SCORING['steals'], 2),
                'blocks_contribution': round(stats['blocks'] * self.SCORING['blocks'], 2),
                'turnovers_contribution': round(stats['turnovers'] * self.SCORING['turnovers'], 2)
            }
        }
    
    def enrich_player_with_underdog_scoring(self, player: Dict) -> Dict:
        """
        Add Underdog scoring calculations to player dict
        
        Args:
            player: Player dict with name, salary, etc.
        
        Returns:
            Enhanced player dict with Underdog fantasy points
        """
        scoring_data = self.calculate_underdog_points(player['name'])
        
        # Replace generic projected_points with Underdog-specific calculation
        player['projected_underdog_points'] = scoring_data['underdog_points']
        player['stat_projections'] = scoring_data['stats']
        player['underdog_breakdown'] = scoring_data['breakdown']
        
        # Keep old projected_points for comparison (if exists)
        if 'projected_points' in player:
            player['old_dfs_points'] = player['projected_points']
        
        # Replace projected_points with Underdog scoring
        player['projected_points'] = scoring_data['underdog_points']
        
        return player
    
    def batch_calculate(self, players: List[Dict]) -> List[Dict]:
        """
        Calculate Underdog points for multiple players
        
        Args:
            players: List of player dicts
        
        Returns:
            List of enriched player dicts with Underdog scoring
        """
        return [self.enrich_player_with_underdog_scoring(p) for p in players]
    
    def verify_scoring(self, player_name: str = 'Luka Doncic') -> Dict:
        """
        Test scoring calculation with sample player
        Returns detailed breakdown for verification
        """
        result = self.calculate_underdog_points(player_name)
        
        print(f"\n🏀 Underdog Scoring Test: {player_name}")
        print("=" * 50)
        print(f"Stats Projections:")
        for stat, value in result['stats'].items():
            print(f"  {stat.capitalize()}: {value}")
        print(f"\nUnderdog Points Breakdown:")
        for component, value in result['breakdown'].items():
            print(f"  {component.replace('_', ' ').title()}: {value}")
        print(f"\n✅ Total Underdog Points: {result['underdog_points']}")
        print("=" * 50)
        
        return result
    
    def get_scoring_format(self) -> Dict:
        """Return the official Underdog scoring format"""
        return {
            'format': 'Underdog Fantasy NBA',
            'multipliers': self.SCORING,
            'description': 'Official Underdog Fantasy scoring with exact point values'
        }


# Test function
if __name__ == '__main__':
    scorer = UnderdogScoring()
    
    # Test with Luka Doncic
    print("\n🧪 Testing Underdog Scoring Calculator")
    scorer.verify_scoring('Luka Doncic')
    
    # Test with Jokic
    scorer.verify_scoring('Nikola Jokic')
    
    # Test batch calculation
    mock_players = [
        {'name': 'Luka Doncic', 'salary': 11000},
        {'name': 'Nikola Jokic', 'salary': 10800}
    ]
    
    enriched = scorer.batch_calculate(mock_players)
    print(f"\n✅ Batch calculation complete. {len(enriched)} players processed.")
    for p in enriched:
        print(f"  {p['name']}: {p['projected_underdog_points']} Underdog pts")
