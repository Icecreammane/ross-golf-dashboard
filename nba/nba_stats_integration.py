#!/usr/bin/env python3
"""
NBA Stats API Integration
Pulls deeper roster data, season averages, usage rates, and pace stats
Uses stats.nba.com API (free, no key required)
"""

import json
import requests
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

class NBAStatsAPI:
    """Interface to stats.nba.com API for deeper player data"""
    
    def __init__(self):
        self.base_url = "https://stats.nba.com/stats"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://www.nba.com',
            'Referer': 'https://www.nba.com/',
            'Connection': 'keep-alive',
            'x-nba-stats-origin': 'stats',
            'x-nba-stats-token': 'true'
        }
        self.season = "2025-26"
        self.rate_limit_delay = 0.6  # Seconds between requests to avoid rate limiting
    
    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make API request with rate limiting and error handling"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            time.sleep(self.rate_limit_delay)
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"⚠️  API request failed for {endpoint}: {e}")
            return None
    
    def get_league_leaders(self, stat_category: str = 'PTS', limit: int = 100) -> List[Dict]:
        """
        Get league leaders for a specific stat category
        Categories: PTS, REB, AST, FG_PCT, FT_PCT, FG3_PCT, STL, BLK
        """
        params = {
            'LeagueID': '00',
            'PerMode': 'PerGame',
            'Scope': 'S',
            'Season': self.season,
            'SeasonType': 'Regular Season',
            'StatCategory': stat_category
        }
        
        data = self._make_request('leagueLeaders', params)
        
        if not data or 'resultSet' not in data:
            return []
        
        result_set = data['resultSet']
        headers = result_set.get('headers', [])
        rows = result_set.get('rowSet', [])
        
        # Convert to dict format
        players = []
        for row in rows[:limit]:
            player_dict = dict(zip(headers, row))
            players.append(player_dict)
        
        return players
    
    def get_player_stats(self, season_type: str = 'Regular Season') -> List[Dict]:
        """
        Get all player stats for current season
        Returns comprehensive stats including usage rate, pace, etc.
        """
        params = {
            'LeagueID': '00',
            'PerMode': 'PerGame',
            'Season': self.season,
            'SeasonType': season_type
        }
        
        data = self._make_request('leaguedashplayerstats', params)
        
        if not data or 'resultSets' not in data:
            return []
        
        result_set = data['resultSets'][0]
        headers = result_set.get('headers', [])
        rows = result_set.get('rowSet', [])
        
        # Convert to dict format
        players = []
        for row in rows:
            player_dict = dict(zip(headers, row))
            players.append(player_dict)
        
        return players
    
    def get_advanced_stats(self) -> List[Dict]:
        """
        Get advanced stats including usage rate, true shooting %, PIE, etc.
        """
        params = {
            'LeagueID': '00',
            'PerMode': 'PerGame',
            'Season': self.season,
            'SeasonType': 'Regular Season',
            'MeasureType': 'Advanced'
        }
        
        data = self._make_request('leaguedashplayerstats', params)
        
        if not data or 'resultSets' not in data:
            return []
        
        result_set = data['resultSets'][0]
        headers = result_set.get('headers', [])
        rows = result_set.get('rowSet', [])
        
        # Convert to dict format
        players = []
        for row in rows:
            player_dict = dict(zip(headers, row))
            players.append(player_dict)
        
        return players
    
    def get_team_roster(self, team_id: str) -> List[Dict]:
        """Get full roster for a specific team"""
        params = {
            'LeagueID': '00',
            'Season': self.season,
            'TeamID': team_id
        }
        
        data = self._make_request('commonteamroster', params)
        
        if not data or 'resultSets' not in data:
            return []
        
        result_set = data['resultSets'][0]
        headers = result_set.get('headers', [])
        rows = result_set.get('rowSet', [])
        
        # Convert to dict format
        players = []
        for row in rows:
            player_dict = dict(zip(headers, row))
            players.append(player_dict)
        
        return players
    
    def enrich_player_data(self, existing_players: List[Dict]) -> Dict[str, Dict]:
        """
        Enrich existing player data with season averages and advanced stats
        Returns dict keyed by player_id with enriched data
        """
        print("📊 Fetching comprehensive player stats...")
        
        # Get all player stats
        basic_stats = self.get_player_stats()
        advanced_stats = self.get_advanced_stats()
        
        # Index by player ID
        basic_by_id = {}
        advanced_by_id = {}
        
        print(f"✓ Retrieved {len(basic_stats)} players with basic stats")
        print(f"✓ Retrieved {len(advanced_stats)} players with advanced stats")
        
        for player in basic_stats:
            player_id = str(player.get('PLAYER_ID', ''))
            if player_id:
                basic_by_id[player_id] = player
        
        for player in advanced_stats:
            player_id = str(player.get('PLAYER_ID', ''))
            if player_id:
                advanced_by_id[player_id] = player
        
        # Enrich existing players
        enriched = {}
        for player in existing_players:
            player_id = str(player.get('player_id', ''))
            
            if player_id in basic_by_id:
                basic = basic_by_id[player_id]
                advanced = advanced_by_id.get(player_id, {})
                
                enriched[player_id] = {
                    **player,  # Keep existing data
                    # Season averages (full, not just leaders)
                    'season_ppg': basic.get('PTS', player.get('ppg', 0)),
                    'season_rpg': basic.get('REB', player.get('rpg', 0)),
                    'season_apg': basic.get('AST', player.get('apg', 0)),
                    'season_spg': basic.get('STL', 0),
                    'season_bpg': basic.get('BLK', 0),
                    'season_fg_pct': basic.get('FG_PCT', 0),
                    'season_fg3_pct': basic.get('FG3_PCT', 0),
                    'season_ft_pct': basic.get('FT_PCT', 0),
                    'season_min': basic.get('MIN', 0),
                    'season_gp': basic.get('GP', 0),
                    # Advanced stats
                    'usage_rate': advanced.get('USG_PCT', 0),
                    'true_shooting_pct': advanced.get('TS_PCT', 0),
                    'offensive_rating': advanced.get('OFF_RATING', 0),
                    'defensive_rating': advanced.get('DEF_RATING', 0),
                    'net_rating': advanced.get('NET_RATING', 0),
                    'pie': advanced.get('PIE', 0),  # Player Impact Estimate
                    'pace': advanced.get('PACE', 0),
                }
            else:
                enriched[player_id] = player
        
        return enriched
    
    def get_top_players_by_fantasy_points(self, min_minutes: float = 15.0, limit: int = 100) -> List[Dict]:
        """
        Get top players ranked by estimated fantasy points
        Filters out low-minute players
        """
        print("🔍 Fetching top fantasy performers...")
        
        basic_stats = self.get_player_stats()
        
        # Calculate fantasy points for each player
        players_with_fp = []
        for player in basic_stats:
            min_per_game = player.get('MIN', 0)
            
            # Filter by minutes played
            if min_per_game < min_minutes:
                continue
            
            ppg = player.get('PTS', 0)
            rpg = player.get('REB', 0)
            apg = player.get('AST', 0)
            
            # Standard DFS scoring
            fantasy_points = (ppg * 1.0) + (rpg * 1.2) + (apg * 1.5)
            
            players_with_fp.append({
                'player_id': player.get('PLAYER_ID'),
                'name': player.get('PLAYER_NAME'),
                'team': player.get('TEAM_ABBREVIATION'),
                'position': 'F',  # Would need separate call for actual position
                'ppg': ppg,
                'rpg': rpg,
                'apg': apg,
                'min': min_per_game,
                'gp': player.get('GP', 0),
                'fantasy_points': round(fantasy_points, 2)
            })
        
        # Sort by fantasy points
        players_with_fp.sort(key=lambda x: x['fantasy_points'], reverse=True)
        
        print(f"✓ Found {len(players_with_fp)} players with {min_minutes}+ MPG")
        
        return players_with_fp[:limit]


def test_api():
    """Test the NBA Stats API integration"""
    print("🏀 Testing NBA Stats API Integration\n")
    
    api = NBAStatsAPI()
    
    # Test 1: Get top scorers
    print("Test 1: Top 10 Scorers")
    print("-" * 50)
    leaders = api.get_league_leaders('PTS', limit=10)
    for i, player in enumerate(leaders, 1):
        name = player.get('PLAYER', 'Unknown')
        pts = player.get('PTS', 0)
        team = player.get('TEAM', '')
        print(f"{i}. {name} ({team}) - {pts:.1f} PPG")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Get top fantasy players
    print("Test 2: Top 15 Fantasy Players (15+ MPG)")
    print("-" * 50)
    top_players = api.get_top_players_by_fantasy_points(min_minutes=15.0, limit=15)
    for i, player in enumerate(top_players, 1):
        print(f"{i}. {player['name']} ({player['team']}) - {player['fantasy_points']} FP")
        print(f"   {player['ppg']:.1f} PPG, {player['rpg']:.1f} RPG, {player['apg']:.1f} APG")
    
    print("\n" + "="*50)
    print("✅ API integration test complete!")


if __name__ == "__main__":
    test_api()
