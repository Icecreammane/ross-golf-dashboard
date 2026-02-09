"""
Underdog Fantasy data scraper
Fetches player salaries, projections, and contest details
"""
import requests
from typing import List, Dict
import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from underdog_scoring import UnderdogScoring

class UnderdogScraper:
    def __init__(self):
        self.base_url = "https://api.underdogfantasy.com/beta/v3"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.scorer = UnderdogScoring()
    
    def fetch_slate_players(self, date: str = "2026-02-09") -> List[Dict]:
        """
        Fetch players available for the slate
        Note: This is a mock implementation - actual Underdog API may differ
        """
        try:
            # Underdog API endpoint (may need authentication for real use)
            url = f"{self.base_url}/players"
            params = {'date': date, 'sport': 'basketball'}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            # If API not accessible, return mock data structure
            if response.status_code != 200:
                return self._generate_mock_slate()
            
            data = response.json()
            return self._parse_underdog_players(data)
            
        except Exception as e:
            print(f"Error fetching Underdog data: {e}")
            return self._generate_mock_slate()
    
    def _parse_underdog_players(self, data: Dict) -> List[Dict]:
        """Parse Underdog API response"""
        players = []
        for player in data.get('players', []):
            players.append({
                'id': player.get('id'),
                'name': player.get('name'),
                'team': player.get('team'),
                'position': player.get('position'),
                'salary': player.get('salary', 5000),
                'projected_points': player.get('projection', 20.0),
                'ownership_pct': player.get('ownership', 10.0),
                'adp': player.get('adp', 50)
            })
        return players
    
    def _generate_mock_slate(self) -> List[Dict]:
        """Generate mock slate data for testing with Underdog scoring"""
        # Top NBA players with realistic salaries for Feb 9, 2026
        # Note: projected_points will be REPLACED by Underdog scoring calculations
        mock_players = [
            {'name': 'Luka Doncic', 'team': 'DAL', 'position': 'PG', 'salary': 11000, 'ownership_pct': 35.2, 'adp': 1},
            {'name': 'Nikola Jokic', 'team': 'DEN', 'position': 'C', 'salary': 10800, 'ownership_pct': 32.1, 'adp': 2},
            {'name': 'Giannis Antetokounmpo', 'team': 'MIL', 'position': 'PF', 'salary': 10500, 'ownership_pct': 28.5, 'adp': 3},
            {'name': 'Shai Gilgeous-Alexander', 'team': 'OKC', 'position': 'PG', 'salary': 10200, 'ownership_pct': 25.3, 'adp': 4},
            {'name': 'Joel Embiid', 'team': 'PHI', 'position': 'C', 'salary': 10000, 'ownership_pct': 22.8, 'adp': 5},
            {'name': 'Jayson Tatum', 'team': 'BOS', 'position': 'SF', 'salary': 9800, 'ownership_pct': 24.1, 'adp': 6},
            {'name': 'Kevin Durant', 'team': 'PHX', 'position': 'PF', 'salary': 9500, 'ownership_pct': 20.5, 'adp': 7},
            {'name': 'Stephen Curry', 'team': 'GSW', 'position': 'PG', 'salary': 9300, 'ownership_pct': 26.8, 'adp': 8},
            {'name': 'LeBron James', 'team': 'LAL', 'position': 'SF', 'salary': 9000, 'ownership_pct': 18.2, 'adp': 9},
            {'name': 'Anthony Davis', 'team': 'LAL', 'position': 'C', 'salary': 8800, 'ownership_pct': 19.8, 'adp': 10},
            # Mid-tier value plays
            {'name': 'Tyrese Haliburton', 'team': 'IND', 'position': 'PG', 'salary': 8200, 'ownership_pct': 15.2, 'adp': 12},
            {'name': 'Donovan Mitchell', 'team': 'CLE', 'position': 'SG', 'salary': 8000, 'ownership_pct': 14.5, 'adp': 13},
            {'name': 'Damian Lillard', 'team': 'MIL', 'position': 'PG', 'salary': 7800, 'ownership_pct': 12.8, 'adp': 15},
            {'name': 'Trae Young', 'team': 'ATL', 'position': 'PG', 'salary': 7500, 'ownership_pct': 11.2, 'adp': 16},
            {'name': 'Paolo Banchero', 'team': 'ORL', 'position': 'PF', 'salary': 7200, 'ownership_pct': 9.5, 'adp': 18},
            # Value plays
            {'name': 'Franz Wagner', 'team': 'ORL', 'position': 'SF', 'salary': 6800, 'ownership_pct': 8.2, 'adp': 22},
            {'name': 'Jalen Brunson', 'team': 'NYK', 'position': 'PG', 'salary': 6500, 'ownership_pct': 7.8, 'adp': 24},
            {'name': 'Darius Garland', 'team': 'CLE', 'position': 'PG', 'salary': 6200, 'ownership_pct': 6.5, 'adp': 26},
            {'name': 'Cade Cunningham', 'team': 'DET', 'position': 'PG', 'salary': 6000, 'ownership_pct': 5.8, 'adp': 28},
            {'name': 'Scottie Barnes', 'team': 'TOR', 'position': 'SF', 'salary': 5800, 'ownership_pct': 5.2, 'adp': 30},
            # Punts/deep value
            {'name': 'Coby White', 'team': 'CHI', 'position': 'PG', 'salary': 5200, 'ownership_pct': 4.2, 'adp': 35},
            {'name': 'Herbert Jones', 'team': 'NOP', 'position': 'SF', 'salary': 5000, 'ownership_pct': 3.8, 'adp': 38},
            {'name': 'Isaiah Stewart', 'team': 'DET', 'position': 'C', 'salary': 4800, 'ownership_pct': 3.2, 'adp': 42},
            {'name': 'Keon Ellis', 'team': 'SAC', 'position': 'SG', 'salary': 4500, 'ownership_pct': 2.5, 'adp': 48},
            {'name': 'Jaden McDaniels', 'team': 'MIN', 'position': 'SF', 'salary': 4200, 'ownership_pct': 2.1, 'adp': 52},
        ]
        
        # Add IDs and calculate Underdog scoring for all players
        players_with_ids = [{'id': i, **player} for i, player in enumerate(mock_players)]
        
        # Apply Underdog scoring calculations
        players_with_scoring = self.scorer.batch_calculate(players_with_ids)
        
        return players_with_scoring
    
    def fetch_vegas_lines(self) -> Dict:
        """Fetch Vegas betting lines for games"""
        # Mock Vegas data - in production, use OddsAPI or similar
        return {
            'DAL vs LAL': {'total': 225.5, 'spread': 'DAL -3.5'},
            'DEN vs PHX': {'total': 228.0, 'spread': 'DEN -2.5'},
            'MIL vs BOS': {'total': 232.5, 'spread': 'BOS -1.5'},
            'OKC vs GSW': {'total': 230.0, 'spread': 'OKC -4.5'},
        }
