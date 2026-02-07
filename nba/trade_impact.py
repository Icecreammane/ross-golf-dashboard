#!/usr/bin/env python3
"""
Trade Impact Analyzer
Calculates how major trades affect player projections and usage rates
"""

import json
from typing import Dict, List, Tuple
from datetime import datetime

# MAJOR TRADES - 2/4/26 Trade Deadline
TRADES = {
    'harden_to_cavs': {
        'date': '2026-02-04',
        'player': 'James Harden',
        'from_team': 'Los Angeles Clippers',
        'to_team': 'Cleveland Cavaliers',
        'impact_level': 'HIGH',
        'affected_players': {
            # Cleveland - usage decreases for existing ball-handlers
            'Donovan Mitchell': {'usage_delta': -5, 'apg_delta': -2, 'impact': 'MED'},
            'Evan Mobley': {'usage_delta': -3, 'apg_delta': -1, 'impact': 'LOW'},
            'Jarrett Allen': {'usage_delta': -2, 'apg_delta': 0, 'impact': 'LOW'},
            # Harden himself - moderate usage in new system
            'James Harden': {'usage_delta': 0, 'apg_delta': 8, 'ppg_delta': 18, 'impact': 'HIGH'},
        }
    },
    'garland_to_clippers': {
        'date': '2026-02-04',
        'player': 'Darius Garland',
        'from_team': 'Cleveland Cavaliers',
        'to_team': 'Los Angeles Clippers',
        'impact_level': 'HIGH',
        'affected_players': {
            # Clippers - Garland becomes primary ball-handler with Harden gone
            'Darius Garland': {'usage_delta': +8, 'ppg_delta': +4, 'apg_delta': +3, 'impact': 'HIGH'},
            'Kawhi Leonard': {'usage_delta': +3, 'apg_delta': -1, 'impact': 'MED'},
            'Paul George': {'usage_delta': +2, 'apg_delta': 0, 'impact': 'LOW'},
            'Norman Powell': {'usage_delta': +2, 'ppg_delta': +2, 'impact': 'LOW'},
        }
    },
    'jjj_to_utah': {
        'date': '2026-02-04',
        'player': 'Jaren Jackson Jr.',
        'from_team': 'Memphis Grizzlies',
        'to_team': 'Utah Jazz',
        'impact_level': 'HIGH',
        'affected_players': {
            # Utah - JJJ adds scoring but reduces touches for others
            'Jaren Jackson Jr.': {'usage_delta': 0, 'ppg_delta': 20, 'rpg_delta': 6, 'bpg_delta': 1.5, 'impact': 'HIGH'},
            'Lauri Markkanen': {'usage_delta': -4, 'ppg_delta': -3, 'impact': 'MED'},
            'Jordan Clarkson': {'usage_delta': -3, 'ppg_delta': -2, 'impact': 'MED'},
            'Walker Kessler': {'usage_delta': -2, 'rpg_delta': -1.5, 'impact': 'LOW'},
        }
    },
    'huerter_saric_to_pistons': {
        'date': '2026-02-04',
        'player': 'Kevin Huerter + Dario Saric',
        'from_team': 'Sacramento Kings',
        'to_team': 'Detroit Pistons',
        'impact_level': 'MED',
        'affected_players': {
            # Detroit - adds shooting and depth
            'Kevin Huerter': {'usage_delta': +3, 'ppg_delta': +3, 'impact': 'MED'},
            'Dario Saric': {'usage_delta': +2, 'ppg_delta': +4, 'rpg_delta': +2, 'impact': 'LOW'},
            'Cade Cunningham': {'usage_delta': -2, 'apg_delta': -1, 'impact': 'LOW'},
            'Jalen Duren': {'usage_delta': -1, 'rpg_delta': -0.5, 'impact': 'LOW'},
        }
    }
}


class TradeImpactAnalyzer:
    """Analyzes trade impacts on player projections"""
    
    def __init__(self):
        self.trades = TRADES
        self.impact_scores = {
            'HIGH': 1.0,
            'MED': 0.6,
            'LOW': 0.3,
            'NONE': 0.0
        }
    
    def get_player_impact(self, player_name: str) -> Tuple[str, Dict]:
        """
        Check if player is affected by trades
        Returns: (impact_level, adjustments_dict)
        """
        for trade_key, trade_data in self.trades.items():
            affected = trade_data.get('affected_players', {})
            
            if player_name in affected:
                impact_data = affected[player_name]
                return (impact_data.get('impact', 'NONE'), impact_data)
        
        return ('NONE', {})
    
    def apply_trade_adjustments(self, player: Dict) -> Dict:
        """
        Apply trade impact adjustments to player projection
        Modifies player dict in-place and returns it
        """
        player_name = player.get('name', '')
        impact_level, adjustments = self.get_player_impact(player_name)
        
        if impact_level == 'NONE':
            player['trade_impact'] = 'None'
            player['trade_notes'] = ''
            return player
        
        # Apply stat adjustments
        original_ppg = player.get('ppg', 0) or player.get('season_ppg', 0)
        original_rpg = player.get('rpg', 0) or player.get('season_rpg', 0)
        original_apg = player.get('apg', 0) or player.get('season_apg', 0)
        
        # Apply deltas
        ppg_delta = adjustments.get('ppg_delta', 0)
        rpg_delta = adjustments.get('rpg_delta', 0)
        apg_delta = adjustments.get('apg_delta', 0)
        usage_delta = adjustments.get('usage_delta', 0)
        bpg_delta = adjustments.get('bpg_delta', 0)
        
        # Update stats
        if ppg_delta != 0:
            player['ppg'] = max(0, original_ppg + ppg_delta)
            player['trade_adjusted_ppg'] = ppg_delta
        
        if rpg_delta != 0:
            player['rpg'] = max(0, original_rpg + rpg_delta)
            player['trade_adjusted_rpg'] = rpg_delta
        
        if apg_delta != 0:
            player['apg'] = max(0, original_apg + apg_delta)
            player['trade_adjusted_apg'] = apg_delta
        
        if bpg_delta != 0:
            bpg = player.get('season_bpg', 0)
            player['season_bpg'] = max(0, bpg + bpg_delta)
        
        if usage_delta != 0:
            usage = player.get('usage_rate', 20.0)
            player['usage_rate'] = max(0, usage + usage_delta)
            player['trade_adjusted_usage'] = usage_delta
        
        # Recalculate fantasy projection with trade adjustments
        adjusted_ppg = player.get('ppg', original_ppg)
        adjusted_rpg = player.get('rpg', original_rpg)
        adjusted_apg = player.get('apg', original_apg)
        
        # Standard DFS formula: (ppg × 1.0) + (rpg × 1.2) + (apg × 1.5)
        new_projection = (adjusted_ppg * 1.0) + (adjusted_rpg * 1.2) + (adjusted_apg * 1.5)
        
        # Add blocks/steals bonus if available
        if 'season_bpg' in player:
            new_projection += player['season_bpg'] * 2.0  # Blocks worth 2 FP
        if 'season_spg' in player:
            new_projection += player['season_spg'] * 2.0  # Steals worth 2 FP
        
        player['projected_fantasy_points'] = round(new_projection, 2)
        player['trade_impact'] = impact_level
        
        # Build trade notes
        notes = []
        if ppg_delta > 0:
            notes.append(f"+{ppg_delta:.1f} PPG")
        elif ppg_delta < 0:
            notes.append(f"{ppg_delta:.1f} PPG")
        
        if rpg_delta > 0:
            notes.append(f"+{rpg_delta:.1f} RPG")
        elif rpg_delta < 0:
            notes.append(f"{rpg_delta:.1f} RPG")
        
        if apg_delta > 0:
            notes.append(f"+{apg_delta:.1f} APG")
        elif apg_delta < 0:
            notes.append(f"{apg_delta:.1f} APG")
        
        if usage_delta > 0:
            notes.append(f"+{usage_delta}% usage")
        elif usage_delta < 0:
            notes.append(f"{usage_delta}% usage")
        
        player['trade_notes'] = ", ".join(notes) if notes else "Role change"
        
        return player
    
    def get_trade_summary(self) -> str:
        """Generate summary of all trades for reporting"""
        summary = "# Trade Deadline Impact Summary\n\n"
        summary += f"**Updated:** {datetime.now().strftime('%Y-%m-%d %I:%M %p CST')}\n\n"
        
        for trade_key, trade_data in self.trades.items():
            summary += f"## {trade_data['player']}\n"
            summary += f"**{trade_data['from_team']} → {trade_data['to_team']}**\n"
            summary += f"Impact Level: {trade_data['impact_level']}\n\n"
            
            affected = trade_data.get('affected_players', {})
            summary += "### Affected Players:\n"
            for player_name, impact_data in affected.items():
                summary += f"- **{player_name}** ({impact_data['impact']} impact)\n"
                
                deltas = []
                if 'ppg_delta' in impact_data:
                    deltas.append(f"PPG: {impact_data['ppg_delta']:+.1f}")
                if 'rpg_delta' in impact_data:
                    deltas.append(f"RPG: {impact_data['rpg_delta']:+.1f}")
                if 'apg_delta' in impact_data:
                    deltas.append(f"APG: {impact_data['apg_delta']:+.1f}")
                if 'usage_delta' in impact_data:
                    deltas.append(f"Usage: {impact_data['usage_delta']:+d}%")
                
                if deltas:
                    summary += f"  {', '.join(deltas)}\n"
            
            summary += "\n"
        
        return summary
    
    def apply_to_rankings(self, rankings: List[Dict]) -> List[Dict]:
        """
        Apply trade impacts to entire rankings list
        Returns updated rankings with trade adjustments
        """
        print("\n🔄 Applying trade deadline adjustments...")
        
        high_impact = 0
        med_impact = 0
        low_impact = 0
        
        for player in rankings:
            self.apply_trade_adjustments(player)
            
            impact = player.get('trade_impact', 'None')
            if impact == 'HIGH':
                high_impact += 1
            elif impact == 'MED':
                med_impact += 1
            elif impact == 'LOW':
                low_impact += 1
        
        # Re-sort by updated projections
        rankings.sort(key=lambda x: x.get('projected_fantasy_points', 0), reverse=True)
        
        # Update ranks
        for idx, player in enumerate(rankings, 1):
            player['rank'] = idx
        
        print(f"✓ Trade impacts applied:")
        print(f"  • {high_impact} HIGH impact players")
        print(f"  • {med_impact} MED impact players")
        print(f"  • {low_impact} LOW impact players")
        
        return rankings


def test_trade_analyzer():
    """Test the trade impact analyzer"""
    print("🔄 Testing Trade Impact Analyzer\n")
    
    analyzer = TradeImpactAnalyzer()
    
    # Test players
    test_players = [
        {'name': 'James Harden', 'team': 'Cleveland Cavaliers', 'ppg': 20, 'rpg': 5, 'apg': 10},
        {'name': 'Darius Garland', 'team': 'Los Angeles Clippers', 'ppg': 18, 'rpg': 3, 'apg': 6},
        {'name': 'Jaren Jackson Jr.', 'team': 'Utah Jazz', 'ppg': 22, 'rpg': 6, 'apg': 2},
        {'name': 'Lauri Markkanen', 'team': 'Utah Jazz', 'ppg': 24, 'rpg': 8, 'apg': 2},
    ]
    
    print("Before Trade Adjustments:")
    print("-" * 60)
    for p in test_players:
        print(f"{p['name']}: {p['ppg']} PPG, {p['rpg']} RPG, {p['apg']} APG")
    
    print("\n" + "="*60 + "\n")
    
    # Apply adjustments
    for player in test_players:
        analyzer.apply_trade_adjustments(player)
    
    print("After Trade Adjustments:")
    print("-" * 60)
    for p in test_players:
        impact = p.get('trade_impact', 'None')
        notes = p.get('trade_notes', '')
        print(f"{p['name']} ({impact} impact): {p['ppg']:.1f} PPG, {p['rpg']:.1f} RPG, {p['apg']:.1f} APG")
        if notes:
            print(f"  → {notes}")
        print(f"  → Projected FP: {p.get('projected_fantasy_points', 0):.1f}")
    
    print("\n" + "="*60 + "\n")
    print(analyzer.get_trade_summary())


if __name__ == "__main__":
    test_trade_analyzer()
