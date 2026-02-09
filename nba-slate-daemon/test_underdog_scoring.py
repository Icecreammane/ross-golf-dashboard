#!/usr/bin/env python3
"""
Comprehensive test suite for Underdog scoring integration
Verifies all 7 requirements from the task
"""

import sys
import json
import requests
from underdog_scoring import UnderdogScoring
from scrapers.underdog_scraper import UnderdogScraper
from ranking_engine import RankingEngine

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

def print_test(name, passed, details=""):
    status = f"{GREEN}✅ PASS{RESET}" if passed else f"{RED}❌ FAIL{RESET}"
    print(f"{status} | {name}")
    if details:
        print(f"        {details}")

def test_requirement_1():
    """Requirement 1: Replace generic DFS scoring with Underdog's exact format"""
    print(f"\n{BOLD}{BLUE}TEST 1: Underdog Scoring Format{RESET}")
    print("=" * 70)
    
    scorer = UnderdogScoring()
    format_info = scorer.get_scoring_format()
    
    expected_scoring = {
        'points': 1.0,
        'rebounds': 1.2,
        'assists': 1.5,
        'steals': 3.0,
        'blocks': 3.0,
        'turnovers': -1.0
    }
    
    all_correct = True
    for stat, expected_value in expected_scoring.items():
        actual_value = scorer.SCORING.get(stat)
        correct = actual_value == expected_value
        all_correct = all_correct and correct
        print_test(
            f"{stat.capitalize()}: {expected_value}",
            correct,
            f"Actual: {actual_value}"
        )
    
    return all_correct

def test_requirement_2():
    """Requirement 2: Recalculate all player projections using Underdog scoring"""
    print(f"\n{BOLD}{BLUE}TEST 2: Player Projections Recalculated{RESET}")
    print("=" * 70)
    
    scraper = UnderdogScraper()
    players = scraper.fetch_slate_players()
    
    # Verify all players have Underdog scoring
    all_have_scoring = all('projected_underdog_points' in p for p in players)
    print_test(
        f"All {len(players)} players have Underdog points",
        all_have_scoring
    )
    
    # Verify stat projections exist
    all_have_stats = all('stat_projections' in p for p in players)
    print_test(
        f"All {len(players)} players have stat projections",
        all_have_stats
    )
    
    # Manual verification for sample player
    sample = players[0]
    scorer = UnderdogScoring()
    manual_calc = scorer.calculate_underdog_points(sample['name'])
    calculated_pts = sample['projected_underdog_points']
    expected_pts = manual_calc['underdog_points']
    
    matches = abs(calculated_pts - expected_pts) < 0.01
    print_test(
        f"Manual verification: {sample['name']}",
        matches,
        f"Expected: {expected_pts}, Got: {calculated_pts}"
    )
    
    return all_have_scoring and all_have_stats and matches

def test_requirement_3():
    """Requirement 3: Update dashboard to show projected Underdog points per player"""
    print(f"\n{BOLD}{BLUE}TEST 3: Dashboard Shows Underdog Points{RESET}")
    print("=" * 70)
    
    try:
        # Test API endpoint
        response = requests.get('http://localhost:5051/api/players', timeout=5)
        data = response.json()
        
        api_working = response.status_code == 200
        print_test("Dashboard API responding", api_working)
        
        if api_working:
            players = data.get('players', [])
            has_underdog_field = all('projected_underdog_points' in p for p in players[:5])
            print_test(
                "Players have projected_underdog_points field",
                has_underdog_field
            )
            
            has_breakdown = all('underdog_breakdown' in p for p in players[:5])
            print_test(
                "Players have underdog_breakdown field",
                has_breakdown
            )
            
            return api_working and has_underdog_field and has_breakdown
    except Exception as e:
        print_test("Dashboard API check", False, str(e))
        return False

def test_requirement_4():
    """Requirement 4: Update ranking algorithm to optimize for Underdog scoring"""
    print(f"\n{BOLD}{BLUE}TEST 4: Ranking Algorithm Uses Underdog Scoring{RESET}")
    print("=" * 70)
    
    scraper = UnderdogScraper()
    players = scraper.fetch_slate_players()
    
    ranking_engine = RankingEngine()
    ranked_df = ranking_engine.rank_players(players)
    
    # Verify rankings use projected_points (which is now Underdog points)
    uses_projections = 'projected_points' in ranked_df.columns
    print_test("Rankings use projected_points field", uses_projections)
    
    # Verify ceiling/floor calculations use Underdog points
    sample_row = ranked_df.iloc[0]
    projected = sample_row['projected_points']
    ceiling = sample_row['ceiling']
    floor = sample_row['floor']
    
    # Ceiling should be higher than projection
    ceiling_valid = ceiling > projected
    print_test(
        f"Ceiling calculation valid",
        ceiling_valid,
        f"Projected: {projected}, Ceiling: {ceiling}"
    )
    
    # Floor should be lower than projection
    floor_valid = floor < projected
    print_test(
        f"Floor calculation valid",
        floor_valid,
        f"Projected: {projected}, Floor: {floor}"
    )
    
    # Value should be calculated from ceiling
    value = sample_row['value']
    expected_value = (ceiling / sample_row['salary']) * 1000
    value_valid = abs(value - expected_value) < 0.01
    print_test(
        f"Value calculation uses Underdog-based ceiling",
        value_valid,
        f"Expected: {expected_value:.2f}, Got: {value}"
    )
    
    return uses_projections and ceiling_valid and floor_valid and value_valid

def test_requirement_5():
    """Requirement 5: Test with sample players to verify scores match Underdog's format"""
    print(f"\n{BOLD}{BLUE}TEST 5: Manual Verification with Sample Players{RESET}")
    print("=" * 70)
    
    scorer = UnderdogScoring()
    
    test_cases = [
        {
            'name': 'Test Player 1',
            'stats': {
                'points': 25.0,
                'rebounds': 8.0,
                'assists': 6.0,
                'steals': 2.0,
                'blocks': 1.0,
                'turnovers': 3.0
            },
            'expected': 25.0*1.0 + 8.0*1.2 + 6.0*1.5 + 2.0*3.0 + 1.0*3.0 + 3.0*(-1.0)
        },
        {
            'name': 'Luka Doncic',
            'stats': None,  # Use built-in projections
            'expected': 61.14  # From our test earlier
        }
    ]
    
    all_pass = True
    for case in test_cases:
        result = scorer.calculate_underdog_points(case['name'], case['stats'])
        calculated = result['underdog_points']
        expected = case['expected']
        
        matches = abs(calculated - expected) < 0.01
        all_pass = all_pass and matches
        
        print_test(
            f"{case['name']}",
            matches,
            f"Expected: {expected:.2f}, Got: {calculated:.2f}"
        )
        
        if case['stats']:
            print(f"        Stats: {case['stats']}")
    
    return all_pass

def test_requirement_6():
    """Requirement 6: Update CSV export to show Underdog points"""
    print(f"\n{BOLD}{BLUE}TEST 6: CSV Export Contains Underdog Points{RESET}")
    print("=" * 70)
    
    try:
        response = requests.get('http://localhost:5051/api/export/csv', timeout=5)
        
        csv_working = response.status_code == 200
        print_test("CSV export endpoint working", csv_working)
        
        if csv_working:
            csv_content = response.text
            
            # Check for key Underdog fields in CSV header
            has_underdog_pts = 'projected_underdog_points' in csv_content
            print_test("CSV includes 'projected_underdog_points' column", has_underdog_pts)
            
            has_stat_cols = all(col in csv_content for col in [
                'stat_points', 'stat_rebounds', 'stat_assists',
                'stat_steals', 'stat_blocks', 'stat_turnovers'
            ])
            print_test("CSV includes stat projection columns", has_stat_cols)
            
            # Check it's not empty
            lines = csv_content.strip().split('\n')
            has_data = len(lines) > 1
            print_test(f"CSV contains data ({len(lines)-1} players)", has_data)
            
            return csv_working and has_underdog_pts and has_stat_cols and has_data
    except Exception as e:
        print_test("CSV export check", False, str(e))
        return False

def test_requirement_7():
    """Requirement 7: Re-rank all players based on new scoring"""
    print(f"\n{BOLD}{BLUE}TEST 7: Players Re-ranked with Underdog Scoring{RESET}")
    print("=" * 70)
    
    try:
        response = requests.get('http://localhost:5051/api/players', timeout=5)
        data = response.json()
        players = data.get('players', [])
        
        # Verify players are sorted by overall_rank
        ranks = [p['overall_rank'] for p in players]
        is_sorted = ranks == sorted(ranks)
        print_test("Players sorted by overall_rank", is_sorted)
        
        # Verify ranks are based on Underdog scoring
        # (value rank should use Underdog ceiling calculations)
        sample_players = players[:5]
        for p in sample_players:
            value = p['value']
            ceiling = p['ceiling']
            salary = p['salary']
            expected_value = (ceiling / salary) * 1000
            
            value_correct = abs(value - expected_value) < 0.01
            print_test(
                f"{p['name'][:20]:20} | Value: {value:.2f}",
                value_correct,
                f"Rank: {int(p['overall_rank'])}"
            )
        
        # Verify tier assignments
        has_tiers = all('tier' in p for p in players)
        print_test("All players have tier assignments", has_tiers)
        
        return is_sorted and has_tiers
    except Exception as e:
        print_test("Re-ranking verification", False, str(e))
        return False

def main():
    print(f"\n{BOLD}{'='*70}")
    print(f"  UNDERDOG SCORING INTEGRATION TEST SUITE")
    print(f"{'='*70}{RESET}\n")
    
    results = []
    
    results.append(("Requirement 1: Underdog Scoring Format", test_requirement_1()))
    results.append(("Requirement 2: Recalculate Projections", test_requirement_2()))
    results.append(("Requirement 3: Dashboard Display", test_requirement_3()))
    results.append(("Requirement 4: Ranking Algorithm", test_requirement_4()))
    results.append(("Requirement 5: Sample Verification", test_requirement_5()))
    results.append(("Requirement 6: CSV Export", test_requirement_6()))
    results.append(("Requirement 7: Re-rank Players", test_requirement_7()))
    
    print(f"\n{BOLD}{'='*70}")
    print(f"  TEST SUMMARY")
    print(f"{'='*70}{RESET}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{GREEN}✅ PASS{RESET}" if result else f"{RED}❌ FAIL{RESET}"
        print(f"{status} | {name}")
    
    print(f"\n{BOLD}Results: {passed}/{total} requirements met{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}{BOLD}🎉 ALL TESTS PASSED! Underdog scoring integration complete!{RESET}\n")
        return 0
    else:
        print(f"\n{RED}{BOLD}⚠️  Some tests failed. Review output above.{RESET}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
