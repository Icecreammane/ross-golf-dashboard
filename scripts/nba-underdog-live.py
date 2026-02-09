#!/usr/bin/env python3
"""
NBA Underdog Fantasy - LIVE Projections
Pulls current season stats from NBA.com via nba_api
Calculates fresh Underdog projections for ALL 526+ players
Exports CSV
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from nba_api.stats.endpoints import leaguedashplayerstats

class LiveUnderdogProjector:
    """Live projections using current season stats"""
    
    # Dawg Bowl Qualifier Scoring
    SCORING = {
        'pts': 1.0,
        'reb': 1.2,
        'ast': 1.5,
        '3pm': 0.0,  # Not in Dawg Bowl
        'stl': 3.0,  # Changed from 2.0
        'blk': 3.0,  # Changed from 2.0
        'to': -1.0   # Changed from -0.5
    }
    
    def __init__(self):
        self.workspace = Path.home() / 'clawd'
        self.output_json = self.workspace / 'nba' / 'dawgbowl-rankings.json'
        self.output_csv = self.workspace / 'nba' / 'dawgbowl-rankings.csv'
    
    def get_current_stats(self):
        """Fetch live stats from NBA.com"""
        print("📊 Fetching live season stats from NBA.com...")
        
        try:
            stats = leaguedashplayerstats.LeagueDashPlayerStats(
                season='2025-26',
                season_type_all_star='Regular Season',
                per_mode_detailed='PerGame'
            )
            
            df = stats.get_data_frames()[0]
            print(f"✅ Got {len(df)} players with current season stats\n")
            return df
        
        except Exception as e:
            print(f"❌ Error fetching stats: {e}")
            return None
    
    def load_today_slate(self):
        """Load today's slate (salary caps, positions)"""
        slate_file = self.workspace / 'data' / 'nba-slate-2026-02-09.json'
        
        if slate_file.exists():
            with open(slate_file) as f:
                data = json.load(f)
                return {p['name']: p for p in data.get('players', [])}
        
        return {}
    
    def calculate_projection(self, ppg, rpg, apg, threes, stl, blk, to):
        """Calculate Underdog projection"""
        projection = (
            (ppg * self.SCORING['pts']) +
            (rpg * self.SCORING['reb']) +
            (apg * self.SCORING['ast']) +
            (threes * self.SCORING['3pm']) +
            (stl * self.SCORING['stl']) +
            (blk * self.SCORING['blk']) +
            (to * self.SCORING['to'])
        )
        return round(projection, 2)
    
    def estimate_salary(self, ppg, position):
        """Estimate salary for players not in slate"""
        # Rough salary estimation based on PPG and position
        base = ppg * 300
        if position == 'C':
            base *= 1.1
        elif position == 'PG':
            base *= 1.05
        return max(3500, min(11000, int(base)))
    
    def generate_projections(self):
        """Generate live projections for ALL players"""
        stats_df = self.get_current_stats()
        if stats_df is None:
            return []
        
        slate = self.load_today_slate()
        
        projections = []
        
        for idx, row in stats_df.iterrows():
            name = row['PLAYER_NAME']
            team = row['TEAM_ABBREVIATION']
            
            # Get stats
            ppg = float(row.get('PTS', 0) or 0)
            rpg = float(row.get('REB', 0) or 0)
            apg = float(row.get('AST', 0) or 0)
            threes = float(row.get('FG3M', 0) or 0)
            stl = float(row.get('STL', 0) or 0)
            blk = float(row.get('BLK', 0) or 0)
            to = float(row.get('TOV', 0) or 0)
            gp = int(row.get('GP', 0) or 0)
            
            # Skip if minimal games played
            if gp < 5:
                continue
            
            # Find in slate for salary/position, or estimate
            slate_player = slate.get(name)
            if slate_player:
                salary = slate_player['salary']
                position = slate_player.get('position', 'F')
            else:
                position = 'F'  # Default position
                salary = self.estimate_salary(ppg, position)
            
            # Calculate
            projection = self.calculate_projection(ppg, rpg, apg, threes, stl, blk, to)
            ceiling = round(projection * 1.25, 1)
            floor = round(projection * 0.75, 1)
            value = round((ceiling / salary) * 1000, 2) if salary > 0 else 0
            
            projections.append({
                'rank': 0,  # Will renumber
                'name': name,
                'team': team,
                'position': position,
                'salary': salary,
                'projected_underdog': projection,
                'ceiling': ceiling,
                'floor': floor,
                'value': value,
                'ppg': round(ppg, 1),
                'rpg': round(rpg, 1),
                'apg': round(apg, 1),
                'threes': round(threes, 1),
                'stl': round(stl, 2),
                'blk': round(blk, 2),
                'to': round(to, 1),
                'gp': gp
            })
        
        # Sort and renumber
        projections.sort(key=lambda x: x['projected_underdog'], reverse=True)
        for i, p in enumerate(projections):
            p['rank'] = i + 1
        
        return projections
    
    def save_json(self, projections):
        """Save JSON"""
        output = {
            'generated_at': datetime.now().isoformat(),
            'slate_date': '2026-02-09',
            'source': 'NBA.com (nba_api)',
            'scoring_system': 'Dawg Bowl Qualifier #5',
            'scoring': {
                'points': 1.0,
                'assists': 1.5,
                'rebounds': 1.2,
                'blocks': 3.0,
                'steals': 3.0,
                'turnovers': -1.0
            },
            'num_players': len(projections),
            'projections': projections
        }
        
        self.output_json.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_json, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"✅ Saved {len(projections)} projections to JSON")
    
    def save_csv(self, projections):
        """Save simple CSV with just rank, name, team, and points"""
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.output_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['rank', 'name', 'team', 'projected_points'])
            for p in projections:
                writer.writerow([p['rank'], p['name'], p['team'], p['projected_underdog']])
        
        print(f"✅ Exported {len(projections)} players to CSV (rank, name, team, points)")
    
    def save(self, projections):
        """Save both formats"""
        self.save_json(projections)
        self.save_csv(projections)
        return projections


def main():
    projector = LiveUnderdogProjector()
    projections = projector.generate_projections()
    projector.save(projections)
    
    if projections:
        print(f"\n=== TOP 15 ({len(projections)} Total Players) ===")
        for p in projections[:15]:
            print(f"{p['rank']:3d}. {p['name']:25s} {p['team']} ${p['salary']:5d} - {p['projected_underdog']:6.1f} FP | {p['ppg']:5.1f} PPG {p['rpg']:5.1f} RPG {p['apg']:5.1f} APG | Value: {p['value']}")
        
        print(f"\n📊 Download CSV: ~/clawd/nba/dawgbowl-rankings.csv")


if __name__ == '__main__':
    main()
