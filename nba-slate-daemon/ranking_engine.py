"""
NBA DFS Ranking Algorithm
Calculates ceiling, floor, value, upside for all players
Generates tier recommendations
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime

class RankingEngine:
    def __init__(self):
        self.variance_factors = {
            'PG': 1.15,  # Point guards have higher variance
            'SG': 1.12,
            'SF': 1.10,
            'PF': 1.08,
            'C': 1.05   # Centers more consistent
        }
    
    def calculate_player_metrics(self, player: Dict) -> Dict:
        """Calculate ceiling, floor, value, upside for a player"""
        projected = player['projected_points']
        salary = player['salary']
        position = player['position']
        
        # Variance based on position
        variance = self.variance_factors.get(position, 1.10)
        
        # Ceiling: best case scenario (90th percentile)
        ceiling = projected * variance * 1.25
        
        # Floor: worst case scenario (10th percentile)
        floor = projected * (2 - variance) * 0.75
        
        # Value: ceiling divided by salary (per $1000)
        value = (ceiling / salary) * 1000
        
        # Upside: ceiling minus expected value
        upside = ceiling - projected
        
        # Points per dollar
        ppd = projected / (salary / 1000)
        
        return {
            **player,
            'ceiling': round(ceiling, 2),
            'floor': round(floor, 2),
            'value': round(value, 2),
            'upside': round(upside, 2),
            'ppd': round(ppd, 2),
            'variance': round(variance, 2)
        }
    
    def rank_players(self, players: List[Dict]) -> pd.DataFrame:
        """Rank all players by multiple metrics"""
        # Calculate metrics for all players
        enriched_players = [self.calculate_player_metrics(p) for p in players]
        
        # Convert to DataFrame for easier ranking
        df = pd.DataFrame(enriched_players)
        
        # Add rankings
        df['value_rank'] = df['value'].rank(ascending=False)
        df['ceiling_rank'] = df['ceiling'].rank(ascending=False)
        df['floor_rank'] = df['floor'].rank(ascending=False)
        df['ppd_rank'] = df['ppd'].rank(ascending=False)
        
        # Composite score (weighted average)
        df['composite_score'] = (
            df['value_rank'] * 0.35 +
            df['ceiling_rank'] * 0.25 +
            df['ppd_rank'] * 0.25 +
            df['floor_rank'] * 0.15
        )
        
        df['overall_rank'] = df['composite_score'].rank()
        
        return df.sort_values('overall_rank')
    
    def assign_tiers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Assign players to tiers based on salary and rankings"""
        def determine_tier(row):
            salary = row['salary']
            value = row['value']
            ceiling = row['ceiling']
            ownership = row['ownership_pct']
            
            # Tier 1: Stars - high salary, elite ceiling (play everyone)
            if salary >= 9000 and ceiling >= 42:
                return 'Tier 1: Stars'
            
            # Tier 2: Value plays - high value score, good ceiling
            elif value >= 4.5 and ceiling >= 28:
                return 'Tier 2: Value'
            
            # Tier 3: Punts - low salary, decent floor
            elif salary <= 5500 and row['floor'] >= 15:
                return 'Tier 3: Punts'
            
            # Tier 4: Fades - poor value or high ownership with risk
            elif value < 3.5 or (ownership > 25 and row['floor'] < 25):
                return 'Tier 4: Fades'
            
            else:
                return 'Tier 2: Value'
        
        df['tier'] = df.apply(determine_tier, axis=1)
        return df
    
    def find_stacks(self, df: pd.DataFrame) -> List[Dict]:
        """Identify teams with correlated upside (game stacks)"""
        stacks = []
        
        # Group by team and calculate team metrics
        team_groups = df.groupby('team').agg({
            'upside': 'sum',
            'ceiling': 'sum',
            'value': 'mean',
            'name': lambda x: list(x)
        }).reset_index()
        
        # Sort by combined upside
        team_groups = team_groups.sort_values('upside', ascending=False)
        
        for idx, row in team_groups.head(5).iterrows():
            players = df[df['team'] == row['team']].nlargest(3, 'ceiling')
            stacks.append({
                'team': str(row['team']),
                'players': players['name'].tolist(),
                'combined_ceiling': round(float(players['ceiling'].sum()), 2),
                'combined_upside': round(float(players['upside'].sum()), 2),
                'avg_value': round(float(players['value'].mean()), 2),
                'total_salary': int(players['salary'].sum())
            })
        
        return stacks[:3]  # Top 3 stacks
    
    def find_contrarian_pivots(self, df: pd.DataFrame) -> List[Dict]:
        """Find low-owned players with high upside"""
        # Low ownership (<10%) with high ceiling
        contrarian = df[
            (df['ownership_pct'] < 10) & 
            (df['ceiling'] >= 30) &
            (df['value'] >= 4.0)
        ].nlargest(5, 'upside')
        
        return contrarian[['name', 'team', 'salary', 'ceiling', 'upside', 'ownership_pct', 'value']].to_dict('records')
    
    def generate_recommendations(self, df: pd.DataFrame) -> Dict:
        """Generate full recommendation report"""
        tier1 = df[df['tier'] == 'Tier 1: Stars'].nlargest(5, 'ceiling')
        tier2 = df[df['tier'] == 'Tier 2: Value'].nlargest(5, 'value')
        tier3 = df[df['tier'] == 'Tier 3: Punts'].nlargest(5, 'value')
        tier4 = df[df['tier'] == 'Tier 4: Fades'].nsmallest(5, 'value')
        
        stacks = self.find_stacks(df)
        contrarian = self.find_contrarian_pivots(df)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'top_stars': tier1[['name', 'team', 'salary', 'ceiling', 'floor', 'value', 'ownership_pct']].to_dict('records'),
            'top_value': tier2[['name', 'team', 'salary', 'ceiling', 'floor', 'value', 'ownership_pct']].to_dict('records'),
            'top_punts': tier3[['name', 'team', 'salary', 'ceiling', 'floor', 'value', 'ownership_pct']].to_dict('records'),
            'top_fades': tier4[['name', 'team', 'salary', 'ceiling', 'floor', 'value', 'ownership_pct']].to_dict('records'),
            'recommended_stacks': stacks,
            'contrarian_pivots': contrarian,
            'methodology': {
                'ceiling_calc': 'Projected points × position variance × 1.25 (90th percentile outcome)',
                'floor_calc': 'Projected points × (2 - variance) × 0.75 (10th percentile outcome)',
                'value_calc': '(Ceiling / Salary) × 1000 (points per $1K)',
                'upside_calc': 'Ceiling - Projected points',
                'tier1_criteria': 'Salary >= $9K, Ceiling >= 42 pts',
                'tier2_criteria': 'Value >= 4.5, Ceiling >= 28 pts',
                'tier3_criteria': 'Salary <= $5.5K, Floor >= 15 pts',
                'tier4_criteria': 'Value < 3.5 OR (High ownership + risky floor)',
                'variance_by_position': self.variance_factors
            }
        }
