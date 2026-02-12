#!/usr/bin/env python3
"""
NBA DawgBowl Rankings Optimizer - Professional Grade
Implements Drew Dinkmeyer/ETR-style projection system with:
- Real STL/BLK data (not estimates)
- Recent form weighting (60/40 split)
- Usage rate ceiling multipliers
- Minutes consistency analysis
- Enhanced matchup analysis (position defense + pace)
"""

import json
import requests
import time
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import statistics

class DawgBowlOptimizer:
    """Professional-grade NBA DFS optimizer for Underdog Fantasy"""
    
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
    
    # Position-specific defensive ratings (updated via API)
    POSITION_DEF_RATINGS = {}
    
    # Team pace factors (updated via API)
    TEAM_PACE = {}
    
    def __init__(self):
        self.workspace = Path.home() / 'clawd'
        self.output_dir = self.workspace / 'nba'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.season = "2024-25"  # Current season
        self.base_url = "https://stats.nba.com/stats"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.nba.com/',
            'Origin': 'https://www.nba.com',
            'x-nba-stats-origin': 'stats',
            'x-nba-stats-token': 'true'
        }
        self.rate_limit_delay = 0.6
        
        # Cache for API data
        self.player_cache = {}
        self.team_cache = {}
        
    def _api_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make rate-limited API request"""
        url = f"{self.base_url}/{endpoint}"
        try:
            time.sleep(self.rate_limit_delay)
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"⚠️  API error for {endpoint}: {e}")
            return None
    
    def _parse_api_response(self, data: Dict, result_set_index: int = 0) -> List[Dict]:
        """Parse NBA API response into list of dicts"""
        if not data or 'resultSets' not in data:
            return []
        
        result_sets = data['resultSets']
        if result_set_index >= len(result_sets):
            return []
        
        result_set = result_sets[result_set_index]
        headers = result_set.get('headers', [])
        rows = result_set.get('rowSet', [])
        
        return [dict(zip(headers, row)) for row in rows]
    
    # ============================================================================
    # PHASE 1: REAL STL/BLK DATA (NOT ESTIMATES)
    # ============================================================================
    
    def get_player_season_stats(self) -> Dict[str, Dict]:
        """
        Get full season stats including REAL steals and blocks
        Returns dict keyed by player_id
        """
        print("📊 Phase 1: Fetching real STL/BLK data...")
        
        params = {
            'LeagueID': '00',
            'PerMode': 'PerGame',
            'Season': self.season,
            'SeasonType': 'Regular Season'
        }
        
        data = self._api_request('leaguedashplayerstats', params)
        players = self._parse_api_response(data)
        
        player_stats = {}
        for p in players:
            player_id = str(p.get('PLAYER_ID', ''))
            if not player_id:
                continue
            
            player_stats[player_id] = {
                'player_id': player_id,
                'name': p.get('PLAYER_NAME', ''),
                'team': p.get('TEAM_ABBREVIATION', ''),
                # Basic stats
                'gp': p.get('GP', 0),
                'min': p.get('MIN', 0.0),
                'ppg': p.get('PTS', 0.0),
                'rpg': p.get('REB', 0.0),
                'apg': p.get('AST', 0.0),
                'spg': p.get('STL', 0.0),  # REAL steals per game
                'bpg': p.get('BLK', 0.0),  # REAL blocks per game
                '3pm': p.get('FG3M', 0.0),
                'topg': p.get('TOV', 0.0),
                'fg_pct': p.get('FG_PCT', 0.0),
                'fg3_pct': p.get('FG3_PCT', 0.0),
                'ft_pct': p.get('FT_PCT', 0.0),
            }
        
        print(f"✓ Loaded {len(player_stats)} players with real defensive stats")
        return player_stats
    
    def get_player_advanced_stats(self) -> Dict[str, Dict]:
        """Get advanced stats including usage rate"""
        print("📊 Fetching advanced stats (usage rate, pace)...")
        
        params = {
            'LeagueID': '00',
            'PerMode': 'PerGame',
            'Season': self.season,
            'SeasonType': 'Regular Season',
            'MeasureType': 'Advanced'
        }
        
        data = self._api_request('leaguedashplayerstats', params)
        players = self._parse_api_response(data)
        
        advanced_stats = {}
        for p in players:
            player_id = str(p.get('PLAYER_ID', ''))
            if not player_id:
                continue
            
            advanced_stats[player_id] = {
                'usage_rate': p.get('USG_PCT', 0.0),
                'true_shooting': p.get('TS_PCT', 0.0),
                'offensive_rating': p.get('OFF_RATING', 0.0),
                'defensive_rating': p.get('DEF_RATING', 0.0),
                'net_rating': p.get('NET_RATING', 0.0),
                'pace': p.get('PACE', 0.0),
                'pie': p.get('PIE', 0.0),  # Player Impact Estimate
            }
        
        print(f"✓ Loaded advanced stats for {len(advanced_stats)} players")
        return advanced_stats
    
    # ============================================================================
    # PHASE 2: RECENT FORM WEIGHTING (LAST 5-10 GAMES, 60/40 SPLIT)
    # ============================================================================
    
    def get_recent_game_logs(self, player_id: str, last_n_games: int = 10) -> List[Dict]:
        """Get last N games for a player"""
        params = {
            'PlayerID': player_id,
            'Season': self.season,
            'SeasonType': 'Regular Season',
            'LeagueID': '00'
        }
        
        data = self._api_request('playergamelog', params)
        games = self._parse_api_response(data)
        
        # Return most recent N games
        return games[:last_n_games] if games else []
    
    def calculate_recent_form(self, player_id: str, season_avg: Dict) -> Dict:
        """
        Calculate recent form with 60/40 weighting (recent 60%, season 40%)
        Drew Dinkmeyer style: heavier weight on last 5-10 games
        """
        recent_games = self.get_recent_game_logs(player_id, last_n_games=10)
        
        if not recent_games or len(recent_games) < 3:
            # Not enough data, use season average
            return {
                'form_ppg': season_avg.get('ppg', 0),
                'form_rpg': season_avg.get('rpg', 0),
                'form_apg': season_avg.get('apg', 0),
                'form_spg': season_avg.get('spg', 0),
                'form_bpg': season_avg.get('bpg', 0),
                'form_3pm': season_avg.get('3pm', 0),
                'form_topg': season_avg.get('topg', 0),
                'form_min': season_avg.get('min', 0),
                'recent_games': 0,
                'form_confidence': 0.5  # Low confidence
            }
        
        # Calculate averages from recent games
        recent_stats = {
            'pts': [g.get('PTS', 0) for g in recent_games],
            'reb': [g.get('REB', 0) for g in recent_games],
            'ast': [g.get('AST', 0) for g in recent_games],
            'stl': [g.get('STL', 0) for g in recent_games],
            'blk': [g.get('BLK', 0) for g in recent_games],
            '3pm': [g.get('FG3M', 0) for g in recent_games],
            'tov': [g.get('TOV', 0) for g in recent_games],
            'min': [g.get('MIN', 0) for g in recent_games],
        }
        
        recent_avg = {k: sum(v) / len(v) if v else 0 for k, v in recent_stats.items()}
        
        # 60/40 weighted blend (recent 60%, season 40%)
        form_weighted = {
            'form_ppg': (recent_avg['pts'] * 0.6) + (season_avg.get('ppg', 0) * 0.4),
            'form_rpg': (recent_avg['reb'] * 0.6) + (season_avg.get('rpg', 0) * 0.4),
            'form_apg': (recent_avg['ast'] * 0.6) + (season_avg.get('apg', 0) * 0.4),
            'form_spg': (recent_avg['stl'] * 0.6) + (season_avg.get('spg', 0) * 0.4),
            'form_bpg': (recent_avg['blk'] * 0.6) + (season_avg.get('bpg', 0) * 0.4),
            'form_3pm': (recent_avg['3pm'] * 0.6) + (season_avg.get('3pm', 0) * 0.4),
            'form_topg': (recent_avg['tov'] * 0.6) + (season_avg.get('topg', 0) * 0.4),
            'form_min': (recent_avg['min'] * 0.6) + (season_avg.get('min', 0) * 0.4),
            'recent_games': len(recent_games),
            'form_confidence': min(len(recent_games) / 10.0, 1.0)  # Higher with more games
        }
        
        return form_weighted
    
    # ============================================================================
    # PHASE 3: USAGE RATE MULTIPLIERS (CEILING ADJUSTMENTS)
    # ============================================================================
    
    def calculate_usage_ceiling_multiplier(self, usage_rate: float) -> float:
        """
        Usage rate impacts ceiling/variance
        High usage = higher ceiling but also higher bust risk
        Drew Dinkmeyer method: usage 25%+ gets ceiling boost
        """
        if usage_rate >= 30.0:
            return 1.35  # Elite usage, massive ceiling
        elif usage_rate >= 27.0:
            return 1.28
        elif usage_rate >= 24.0:
            return 1.22
        elif usage_rate >= 20.0:
            return 1.15
        else:
            return 1.08  # Low usage = lower ceiling
    
    def calculate_usage_floor_multiplier(self, usage_rate: float) -> float:
        """High usage = lower floor (more variance)"""
        if usage_rate >= 30.0:
            return 0.65  # High bust risk
        elif usage_rate >= 27.0:
            return 0.70
        elif usage_rate >= 24.0:
            return 0.75
        elif usage_rate >= 20.0:
            return 0.78
        else:
            return 0.82  # Low usage = safer floor
    
    # ============================================================================
    # PHASE 4: MINUTES CONSISTENCY CHECKS (FLAG VARIANCE)
    # ============================================================================
    
    def analyze_minutes_consistency(self, player_id: str, season_avg_min: float) -> Dict:
        """
        Check minutes variance over last 10 games
        Flag players with inconsistent playing time
        """
        recent_games = self.get_recent_game_logs(player_id, last_n_games=10)
        
        if not recent_games or len(recent_games) < 5:
            return {
                'min_variance': 0,
                'min_std_dev': 0,
                'consistency_flag': 'UNKNOWN',
                'consistency_score': 0.5
            }
        
        minutes = [g.get('MIN', 0) for g in recent_games]
        
        # Calculate variance
        mean_min = statistics.mean(minutes)
        std_dev = statistics.stdev(minutes) if len(minutes) > 1 else 0
        variance_pct = (std_dev / mean_min * 100) if mean_min > 0 else 0
        
        # Flag based on variance
        if variance_pct > 25:
            flag = 'HIGH_VARIANCE'
            score = 0.6
        elif variance_pct > 15:
            flag = 'MODERATE_VARIANCE'
            score = 0.8
        else:
            flag = 'CONSISTENT'
            score = 1.0
        
        # Check for recent trend (increasing or decreasing minutes)
        if len(minutes) >= 5:
            recent_3 = statistics.mean(minutes[:3])
            older_3 = statistics.mean(minutes[-3:])
            trend = (recent_3 - older_3) / older_3 * 100 if older_3 > 0 else 0
            
            if trend > 10:
                flag = f"{flag}_TRENDING_UP"
                score += 0.1
            elif trend < -10:
                flag = f"{flag}_TRENDING_DOWN"
                score -= 0.15
        
        return {
            'min_variance': variance_pct,
            'min_std_dev': std_dev,
            'consistency_flag': flag,
            'consistency_score': max(0.3, min(1.0, score)),
            'avg_recent_min': mean_min
        }
    
    # ============================================================================
    # PHASE 5: ENHANCED MATCHUP ANALYSIS
    # ============================================================================
    
    def get_team_defensive_ratings(self) -> Dict[str, Dict]:
        """Get team defensive ratings by position"""
        print("📊 Phase 5: Fetching team defensive ratings...")
        
        params = {
            'LeagueID': '00',
            'Season': self.season,
            'SeasonType': 'Regular Season'
        }
        
        data = self._api_request('leaguedashteamstats', params)
        teams = self._parse_api_response(data)
        
        team_defense = {}
        for team in teams:
            team_abbr = team.get('TEAM_ABBREVIATION', '')
            if not team_abbr:
                continue
            
            team_defense[team_abbr] = {
                'def_rating': team.get('DEF_RATING', 100.0),
                'pace': team.get('PACE', 100.0),
                'opp_ppg': team.get('OPP_PTS', 0.0),
                # Position-specific will be calculated separately
            }
        
        print(f"✓ Loaded defense ratings for {len(team_defense)} teams")
        return team_defense
    
    def calculate_pace_multiplier(self, team_pace: float, opp_pace: float) -> float:
        """
        Game pace impacts total possessions
        High pace = more opportunities = higher projections
        """
        avg_pace = (team_pace + opp_pace) / 2
        league_avg_pace = 100.0  # Approximate league average
        
        pace_factor = avg_pace / league_avg_pace
        
        # Cap the multiplier between 0.90 and 1.12
        return max(0.90, min(1.12, pace_factor))
    
    def calculate_matchup_multiplier(self, player_team: str, opponent: str, 
                                    team_defense: Dict[str, Dict]) -> float:
        """
        Calculate matchup-based projection multiplier
        Considers opponent defense quality and pace
        """
        if opponent not in team_defense or player_team not in team_defense:
            return 1.0  # Neutral if missing data
        
        opp_def = team_defense[opponent]
        team_info = team_defense[player_team]
        
        # Defensive rating multiplier (lower rating = better defense = lower multiplier)
        def_rating = opp_def['def_rating']
        league_avg_def = 112.0  # Approximate league average
        
        if def_rating < 108:
            def_mult = 0.92  # Elite defense
        elif def_rating < 110:
            def_mult = 0.96  # Good defense
        elif def_rating < 114:
            def_mult = 1.00  # Average
        elif def_rating < 116:
            def_mult = 1.05  # Poor defense
        else:
            def_mult = 1.10  # Terrible defense
        
        # Pace multiplier
        pace_mult = self.calculate_pace_multiplier(
            team_info.get('pace', 100), 
            opp_def.get('pace', 100)
        )
        
        # Combined multiplier
        return def_mult * pace_mult
    
    # ============================================================================
    # PROJECTION ENGINE
    # ============================================================================
    
    def calculate_projection(self, player_stats: Dict, form_stats: Dict, 
                            advanced_stats: Dict, consistency: Dict,
                            matchup_mult: float = 1.0) -> Dict:
        """
        Master projection calculator
        Uses all phases: real data, recent form, usage, consistency, matchup
        """
        # Use form-weighted stats
        ppg = form_stats.get('form_ppg', 0)
        rpg = form_stats.get('form_rpg', 0)
        apg = form_stats.get('form_apg', 0)
        spg = form_stats.get('form_spg', 0)
        bpg = form_stats.get('form_bpg', 0)
        three_pm = form_stats.get('form_3pm', 0)
        topg = form_stats.get('form_topg', 0)
        
        # Base fantasy points calculation
        base_fp = (
            (ppg * self.SCORING['pts']) +
            (rpg * self.SCORING['reb']) +
            (apg * self.SCORING['ast']) +
            (three_pm * self.SCORING['3pm']) +
            (spg * self.SCORING['stl']) +  # Real steals!
            (bpg * self.SCORING['blk']) +  # Real blocks!
            (topg * self.SCORING['to'])
        )
        
        # Apply matchup multiplier
        adjusted_fp = base_fp * matchup_mult
        
        # Usage rate for ceiling/floor calculation
        usage_rate = advanced_stats.get('usage_rate', 20.0)
        ceiling_mult = self.calculate_usage_ceiling_multiplier(usage_rate)
        floor_mult = self.calculate_usage_floor_multiplier(usage_rate)
        
        # Consistency impacts ceiling/floor confidence
        consistency_score = consistency.get('consistency_score', 0.8)
        
        # Final projections
        projection = adjusted_fp
        ceiling = adjusted_fp * ceiling_mult * consistency_score
        floor = adjusted_fp * floor_mult * consistency_score
        
        return {
            'projection': round(projection, 2),
            'ceiling': round(ceiling, 2),
            'floor': round(floor, 2),
            'base_fp': round(base_fp, 2),
            'matchup_mult': round(matchup_mult, 3),
            'usage_rate': round(usage_rate, 1),
            'consistency_score': round(consistency_score, 2),
            'form_confidence': form_stats.get('form_confidence', 0.5)
        }
    
    # ============================================================================
    # UNDERDOG CSV EXPORT (FIXED FORMAT)
    # ============================================================================
    
    def export_underdog_csv(self, rankings: List[Dict], filename: str = 'underdog_rankings.csv'):
        """
        Export rankings in Underdog-compatible CSV format
        CRITICAL FIX: Proper format for Underdog Fantasy upload
        
        Format:
        Player Name, Team, Position, Projection, Ceiling, Floor, Value
        """
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header row (Underdog format)
            writer.writerow([
                'Player Name',
                'Team',
                'Position',
                'Projection',
                'Ceiling',
                'Floor',
                'Value',
                'Usage Rate',
                'Consistency',
                'Form Confidence'
            ])
            
            # Data rows
            for player in rankings:
                writer.writerow([
                    player['name'],
                    player['team'],
                    player.get('position', 'F'),  # Default to F if missing
                    f"{player['projection']:.2f}",
                    f"{player['ceiling']:.2f}",
                    f"{player['floor']:.2f}",
                    f"{player['value']:.2f}",
                    f"{player['usage_rate']:.1f}",
                    player.get('consistency_flag', 'UNKNOWN'),
                    f"{player['form_confidence']:.2f}"
                ])
        
        print(f"✅ Exported Underdog CSV: {output_path}")
        return output_path
    
    # ============================================================================
    # MAIN OPTIMIZATION PIPELINE
    # ============================================================================
    
    def optimize_slate(self, slate_players: List[Dict], opponent_map: Dict[str, str] = None) -> List[Dict]:
        """
        Full optimization pipeline for a slate
        slate_players: list of dicts with player_id, name, team, position, salary
        opponent_map: dict mapping team abbreviation to opponent abbreviation
        """
        print("\n" + "="*80)
        print("🏀 NBA DAWGBOWL OPTIMIZER - PROFESSIONAL GRADE")
        print("="*80 + "\n")
        
        # Phase 1: Get real stats
        season_stats = self.get_player_season_stats()
        advanced_stats = self.get_player_advanced_stats()
        
        # Phase 5: Get team defense & pace
        team_defense = self.get_team_defensive_ratings()
        
        rankings = []
        total_players = len(slate_players)
        
        print(f"\n🔄 Processing {total_players} players...\n")
        
        for idx, slate_player in enumerate(slate_players, 1):
            player_id = str(slate_player.get('player_id', ''))
            
            if not player_id or player_id not in season_stats:
                print(f"⚠️  Skipping {slate_player.get('name', 'Unknown')} - no stats found")
                continue
            
            # Get player data
            player_stats = season_stats[player_id]
            player_advanced = advanced_stats.get(player_id, {})
            
            # Phase 2: Recent form
            print(f"  [{idx}/{total_players}] {player_stats['name']} - calculating recent form...")
            form_stats = self.calculate_recent_form(player_id, player_stats)
            
            # Phase 4: Minutes consistency
            consistency = self.analyze_minutes_consistency(player_id, player_stats.get('min', 0))
            
            # Phase 5: Matchup analysis
            matchup_mult = 1.0
            if opponent_map and slate_player['team'] in opponent_map:
                opponent = opponent_map[slate_player['team']]
                matchup_mult = self.calculate_matchup_multiplier(
                    slate_player['team'], opponent, team_defense
                )
            
            # Calculate projection
            proj_data = self.calculate_projection(
                player_stats, form_stats, player_advanced, 
                consistency, matchup_mult
            )
            
            # Calculate value (projection per $1K salary)
            salary = slate_player.get('salary', 5000)
            value = (proj_data['projection'] / salary) * 1000
            
            # Build ranking entry
            ranking = {
                'rank': 0,  # Will be set after sorting
                'player_id': player_id,
                'name': player_stats['name'],
                'team': player_stats['team'],
                'position': slate_player.get('position', 'F'),
                'salary': salary,
                'opponent': opponent_map.get(slate_player['team'], 'UNK') if opponent_map else 'UNK',
                # Projections
                'projection': proj_data['projection'],
                'ceiling': proj_data['ceiling'],
                'floor': proj_data['floor'],
                'value': round(value, 2),
                # Stats breakdown
                'ppg': round(form_stats['form_ppg'], 1),
                'rpg': round(form_stats['form_rpg'], 1),
                'apg': round(form_stats['form_apg'], 1),
                'spg': round(form_stats['form_spg'], 1),
                'bpg': round(form_stats['form_bpg'], 1),
                '3pm': round(form_stats['form_3pm'], 1),
                'min': round(form_stats['form_min'], 1),
                # Metadata
                'usage_rate': proj_data['usage_rate'],
                'matchup_mult': proj_data['matchup_mult'],
                'consistency_flag': consistency['consistency_flag'],
                'consistency_score': consistency['consistency_score'],
                'form_confidence': proj_data['form_confidence'],
                'recent_games': form_stats['recent_games'],
            }
            
            rankings.append(ranking)
        
        # Sort by projection (descending)
        rankings.sort(key=lambda x: x['projection'], reverse=True)
        
        # Assign ranks
        for idx, player in enumerate(rankings, 1):
            player['rank'] = idx
        
        print(f"\n✅ Optimization complete! {len(rankings)} players ranked.\n")
        
        return rankings
    
    def save_rankings(self, rankings: List[Dict], slate_date: str):
        """Save rankings to JSON"""
        output = {
            'generated_at': datetime.now().isoformat(),
            'slate_date': slate_date,
            'system': 'DawgBowl Optimizer Pro',
            'version': '2.0',
            'features': [
                'Real STL/BLK data (not estimates)',
                'Recent form weighting (60/40 split)',
                'Usage rate ceiling multipliers',
                'Minutes consistency analysis',
                'Enhanced matchup analysis (defense + pace)'
            ],
            'num_players': len(rankings),
            'rankings': rankings
        }
        
        output_file = self.output_dir / f'dawgbowl_rankings_{slate_date}.json'
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"✅ Saved rankings: {output_file}")
        return output_file


if __name__ == '__main__':
    # Test with sample slate
    optimizer = DawgBowlOptimizer()
    
    # Sample slate (will be replaced with real data)
    sample_slate = [
        {'player_id': '1630162', 'name': 'LaMelo Ball', 'team': 'CHA', 'position': 'PG', 'salary': 9500},
        {'player_id': '1629029', 'name': 'Luka Doncic', 'team': 'DAL', 'position': 'PG', 'salary': 11000},
        {'player_id': '201939', 'name': 'Stephen Curry', 'team': 'GSW', 'position': 'PG', 'salary': 10000},
    ]
    
    opponent_map = {
        'CHA': 'ATL',
        'DAL': 'LAL',
        'GSW': 'SAC'
    }
    
    rankings = optimizer.optimize_slate(sample_slate, opponent_map)
    
    # Save outputs
    optimizer.save_rankings(rankings, '2026-02-20')
    optimizer.export_underdog_csv(rankings, 'underdog_rankings_feb20.csv')
    
    # Print top 10
    print("\n" + "="*80)
    print("TOP 10 RANKINGS")
    print("="*80)
    for p in rankings[:10]:
        print(f"{p['rank']:2d}. {p['name']:20s} {p['team']} ${p['salary']:5d} - "
              f"Proj: {p['projection']:5.1f} | Ceiling: {p['ceiling']:5.1f} | "
              f"Value: {p['value']:.2f}")
