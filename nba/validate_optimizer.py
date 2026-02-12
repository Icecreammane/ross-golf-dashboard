#!/usr/bin/env python3
"""
Validate DawgBowl Optimizer Accuracy
Test on recent slates and compare projections to actual results
"""

import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dawgbowl_optimizer import DawgBowlOptimizer


class OptimizerValidator:
    """Validate optimizer accuracy against actual game results"""
    
    def __init__(self):
        self.workspace = Path.home() / 'clawd'
        self.optimizer = DawgBowlOptimizer()
        self.validation_results = []
    
    def get_game_results(self, date: str) -> Dict[str, Dict]:
        """
        Fetch actual game results for a date
        Format: YYYY-MM-DD
        Returns dict keyed by player_id with actual stats
        """
        print(f"📊 Fetching game results for {date}...")
        
        # Convert date format
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        date_param = date_obj.strftime('%m/%d/%Y')
        
        params = {
            'LeagueID': '00',
            'Season': self.optimizer.season,
            'SeasonType': 'Regular Season',
            'DateFrom': date_param,
            'DateTo': date_param
        }
        
        data = self.optimizer._api_request('leaguegamelog', params)
        
        if not data or 'resultSets' not in data:
            print(f"⚠️  No game data found for {date}")
            return {}
        
        games = self.optimizer._parse_api_response(data)
        
        actual_stats = {}
        for game in games:
            player_id = str(game.get('PLAYER_ID', ''))
            if not player_id:
                continue
            
            # Calculate actual fantasy points
            pts = game.get('PTS', 0) or 0
            reb = game.get('REB', 0) or 0
            ast = game.get('AST', 0) or 0
            stl = game.get('STL', 0) or 0
            blk = game.get('BLK', 0) or 0
            three_pm = game.get('FG3M', 0) or 0
            tov = game.get('TOV', 0) or 0
            
            actual_fp = (
                (pts * self.optimizer.SCORING['pts']) +
                (reb * self.optimizer.SCORING['reb']) +
                (ast * self.optimizer.SCORING['ast']) +
                (three_pm * self.optimizer.SCORING['3pm']) +
                (stl * self.optimizer.SCORING['stl']) +
                (blk * self.optimizer.SCORING['blk']) +
                (tov * self.optimizer.SCORING['to'])
            )
            
            actual_stats[player_id] = {
                'player_id': player_id,
                'name': game.get('PLAYER_NAME', ''),
                'team': game.get('TEAM_ABBREVIATION', ''),
                'matchup': game.get('MATCHUP', ''),
                'actual_fp': round(actual_fp, 2),
                'pts': pts,
                'reb': reb,
                'ast': ast,
                'stl': stl,
                'blk': blk,
                '3pm': three_pm,
                'tov': tov,
                'min': game.get('MIN', 0),
            }
        
        print(f"✓ Loaded results for {len(actual_stats)} players")
        return actual_stats
    
    def calculate_accuracy_metrics(self, projections: List[Dict], 
                                   actuals: Dict[str, Dict]) -> Dict:
        """
        Calculate accuracy metrics
        - Mean Absolute Error (MAE)
        - Root Mean Square Error (RMSE)
        - Correlation
        - Hit rate (actual within projection range)
        """
        matched_projections = []
        errors = []
        squared_errors = []
        within_range = 0
        
        for proj in projections:
            player_id = proj['player_id']
            
            if player_id not in actuals:
                continue
            
            actual = actuals[player_id]
            projected_fp = proj['projection']
            actual_fp = actual['actual_fp']
            ceiling = proj['ceiling']
            floor = proj['floor']
            
            # Calculate error
            error = abs(projected_fp - actual_fp)
            errors.append(error)
            squared_errors.append(error ** 2)
            
            # Check if within range
            if floor <= actual_fp <= ceiling:
                within_range += 1
            
            matched_projections.append({
                'player': proj['name'],
                'team': proj['team'],
                'projected': projected_fp,
                'actual': actual_fp,
                'error': error,
                'error_pct': (error / projected_fp * 100) if projected_fp > 0 else 0,
                'within_range': floor <= actual_fp <= ceiling,
                'ceiling': ceiling,
                'floor': floor
            })
        
        if not errors:
            return None
        
        mae = sum(errors) / len(errors)
        rmse = (sum(squared_errors) / len(squared_errors)) ** 0.5
        hit_rate = within_range / len(matched_projections) * 100
        
        # Sort by error for analysis
        matched_projections.sort(key=lambda x: x['error'])
        
        return {
            'mae': mae,
            'rmse': rmse,
            'hit_rate': hit_rate,
            'total_matched': len(matched_projections),
            'projections': matched_projections
        }
    
    def validate_date(self, test_date: str) -> Dict:
        """Validate optimizer for a specific date"""
        print("\n" + "="*80)
        print(f"🔍 VALIDATING: {test_date}")
        print("="*80 + "\n")
        
        # Get actual results
        actuals = self.get_game_results(test_date)
        
        if not actuals:
            print(f"❌ No game data available for {test_date}")
            return None
        
        # Build slate from actual results
        slate_players = []
        opponent_map = {}
        
        for player_id, player_data in actuals.items():
            # Parse opponent from matchup string (e.g., "LAL vs. GSW" or "LAL @ GSW")
            matchup = player_data['matchup']
            opponent = ''
            if ' vs. ' in matchup:
                opponent = matchup.split(' vs. ')[1]
            elif ' @ ' in matchup:
                opponent = matchup.split(' @ ')[1]
            
            slate_players.append({
                'player_id': player_id,
                'name': player_data['name'],
                'team': player_data['team'],
                'position': 'F',  # Default
                'salary': 5000  # Placeholder
            })
            
            if opponent:
                opponent_map[player_data['team']] = opponent
        
        # Run optimizer
        print(f"\n🔄 Running optimizer on {len(slate_players)} players...")
        rankings = self.optimizer.optimize_slate(slate_players, opponent_map)
        
        # Calculate accuracy
        print("\n📊 Calculating accuracy metrics...")
        metrics = self.calculate_accuracy_metrics(rankings, actuals)
        
        if not metrics:
            print("❌ Could not calculate metrics")
            return None
        
        # Print results
        print("\n" + "-"*80)
        print("ACCURACY METRICS")
        print("-"*80)
        print(f"Mean Absolute Error (MAE):     {metrics['mae']:.2f} fantasy points")
        print(f"Root Mean Square Error (RMSE): {metrics['rmse']:.2f} fantasy points")
        print(f"Hit Rate (within ceiling/floor): {metrics['hit_rate']:.1f}%")
        print(f"Total Players Matched:         {metrics['total_matched']}")
        
        # Show best and worst predictions
        projs = metrics['projections']
        
        print("\n" + "-"*80)
        print("BEST PREDICTIONS (lowest error)")
        print("-"*80)
        for p in projs[:5]:
            print(f"{p['player']:22s} {p['team']} - Proj: {p['projected']:5.1f} | "
                  f"Actual: {p['actual']:5.1f} | Error: {p['error']:.1f}")
        
        print("\n" + "-"*80)
        print("WORST PREDICTIONS (highest error)")
        print("-"*80)
        for p in projs[-5:]:
            print(f"{p['player']:22s} {p['team']} - Proj: {p['projected']:5.1f} | "
                  f"Actual: {p['actual']:5.1f} | Error: {p['error']:.1f}")
        
        return {
            'date': test_date,
            'metrics': metrics,
            'summary': {
                'mae': metrics['mae'],
                'rmse': metrics['rmse'],
                'hit_rate': metrics['hit_rate'],
                'total_matched': metrics['total_matched']
            }
        }
    
    def run_validation_suite(self, num_dates: int = 3) -> List[Dict]:
        """
        Run validation on multiple recent dates
        Tests the last N dates with games
        """
        print("\n" + "="*80)
        print("🏀 OPTIMIZER VALIDATION SUITE")
        print("="*80)
        print(f"\nTesting on {num_dates} recent slates...")
        
        # Get recent dates (going back 7 days to find dates with games)
        test_dates = []
        current_date = datetime.now() - timedelta(days=1)  # Start with yesterday
        
        days_checked = 0
        while len(test_dates) < num_dates and days_checked < 14:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Quick check if there were games
            actuals = self.get_game_results(date_str)
            if actuals:
                test_dates.append(date_str)
            
            current_date -= timedelta(days=1)
            days_checked += 1
        
        if not test_dates:
            print("❌ No recent game dates found")
            return []
        
        print(f"\n✓ Found {len(test_dates)} dates with games: {', '.join(test_dates)}\n")
        
        # Run validation on each date
        results = []
        for date in test_dates:
            result = self.validate_date(date)
            if result:
                results.append(result)
                self.validation_results.append(result)
        
        # Print overall summary
        if results:
            print("\n" + "="*80)
            print("OVERALL VALIDATION SUMMARY")
            print("="*80)
            
            avg_mae = sum(r['summary']['mae'] for r in results) / len(results)
            avg_rmse = sum(r['summary']['rmse'] for r in results) / len(results)
            avg_hit_rate = sum(r['summary']['hit_rate'] for r in results) / len(results)
            
            print(f"\nAverage MAE:       {avg_mae:.2f} FP")
            print(f"Average RMSE:      {avg_rmse:.2f} FP")
            print(f"Average Hit Rate:  {avg_hit_rate:.1f}%")
            
            print("\nPer-Date Summary:")
            for r in results:
                print(f"  {r['date']}: MAE={r['summary']['mae']:.2f}, "
                      f"Hit Rate={r['summary']['hit_rate']:.1f}%")
            
            # Grade the system
            if avg_mae < 5.0 and avg_hit_rate > 70:
                grade = "🟢 EXCELLENT"
            elif avg_mae < 7.0 and avg_hit_rate > 60:
                grade = "🟡 GOOD"
            elif avg_mae < 10.0 and avg_hit_rate > 50:
                grade = "🟠 ACCEPTABLE"
            else:
                grade = "🔴 NEEDS IMPROVEMENT"
            
            print(f"\n📊 System Grade: {grade}")
            
            print("\n" + "="*80)
            print("✅ VALIDATION COMPLETE")
            print("="*80 + "\n")
        
        return results
    
    def save_validation_report(self, results: List[Dict]):
        """Save validation results to file"""
        if not results:
            return
        
        output = {
            'validation_run': datetime.now().isoformat(),
            'dates_tested': [r['date'] for r in results],
            'summary': {
                'avg_mae': sum(r['summary']['mae'] for r in results) / len(results),
                'avg_rmse': sum(r['summary']['rmse'] for r in results) / len(results),
                'avg_hit_rate': sum(r['summary']['hit_rate'] for r in results) / len(results),
            },
            'detailed_results': results
        }
        
        output_file = self.workspace / 'nba' / 'validation_report.json'
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"📁 Validation report saved: {output_file}")


def main():
    validator = OptimizerValidator()
    
    # Run validation on last 3 slates
    results = validator.run_validation_suite(num_dates=3)
    
    # Save report
    if results:
        validator.save_validation_report(results)
        print("\n✅ Validation complete! Optimizer is ready for Feb 20th.")
    else:
        print("\n⚠️  Validation could not be completed. Check API access.")


if __name__ == '__main__':
    main()
