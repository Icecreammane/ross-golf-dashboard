#!/usr/bin/env python3
"""
NBA Underdog Fantasy - LIVE Projections
Pulls current season stats from NBA.com via nba_api
Calculates fresh Underdog projections
"""

import json
from datetime import datetime
from pathlib import Path
from nba_api.stats.endpoints import leaguedashplayerstats

class LiveUnderdogProjector:
    """Live projections using current season stats"""
    
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
    
    def __init__(self):
        self.workspace = Path.home() / 'clawd'
        self.output_file = self.workspace / 'nba' / 'rankings-live.json'
    
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
        """Load today's slate (salary caps)"""
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
    
    def generate_projections(self):
        """Generate live projections"""
        stats_df = self.get_current_stats()
        if stats_df is None:
            return []
        
        slate = self.load_today_slate()
        
        projections = []
        
        for idx, row in stats_df.iterrows():
            name = row['PLAYER_NAME']
            team = row['TEAM_ABBREVIATION']
            
            # Find in slate for salary
            slate_player = slate.get(name)
            if not slate_player:
                continue  # Only include players in today's slate
            
            salary = slate_player['salary']
            position = slate_player.get('position', 'F')
            
            # Get stats
            ppg = float(row.get('PTS', 0) or 0)
            rpg = float(row.get('REB', 0) or 0)
            apg = float(row.get('AST', 0) or 0)
            threes = float(row.get('FG3M', 0) or 0)
            stl = float(row.get('STL', 0) or 0)
            blk = float(row.get('BLK', 0) or 0)
            to = float(row.get('TOV', 0) or 0)
            
            # Calculate
            projection = self.calculate_projection(ppg, rpg, apg, threes, stl, blk, to)
            ceiling = round(projection * 1.25, 1)
            floor = round(projection * 0.75, 1)
            value = round((ceiling / salary) * 1000, 2)
            
            projections.append({
                'rank': 0,  # Will renumber
                'name': name,
                'team': team,
                'position': position,
                'salary': salary,
                'projected_underdog': projection,
                'ppg': round(ppg, 1),
                'rpg': round(rpg, 1),
                'apg': round(apg, 1),
                'ceiling': ceiling,
                'floor': floor,
                'value': value
            })
        
        # Sort and renumber
        projections.sort(key=lambda x: x['projected_underdog'], reverse=True)
        for i, p in enumerate(projections):
            p['rank'] = i + 1
        
        return projections
    
    def save(self, projections):
        """Save projections"""
        output = {
            'generated_at': datetime.now().isoformat(),
            'slate_date': '2026-02-09',
            'source': 'NBA.com (nba_api)',
            'scoring_system': 'Underdog Fantasy',
            'num_players': len(projections),
            'projections': projections
        }
        
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"✅ Saved {len(projections)} LIVE projections")
        return output


def main():
    projector = LiveUnderdogProjector()
    projections = projector.generate_projections()
    projector.save(projections)
    
    if projections:
        print("\n=== TOP 15 TODAY ===")
        for p in projections[:15]:
            print(f"{p['rank']:2d}. {p['name']:25s} {p['team']} ${p['salary']:5d} - {p['projected_underdog']:5.1f} FP | {p['ppg']:5.1f} PPG {p['rpg']:5.1f} RPG {p['apg']:5.1f} APG")


if __name__ == '__main__':
    main()
