#!/usr/bin/env python3
"""
Test Script for Real NBA Data Integration
Verifies all components work correctly before contest lock
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from real_data_integration import RealDataIntegrator, RealNBADataFetcher, RealInjuryDataFetcher, RealVegasLinesFetcher
from real_projections_engine import RealProjectionsEngine
from underdog_scoring import UnderdogScoring
import json
from datetime import datetime

def test_injury_data():
    """Test 1: Verify injury data fetching"""
    print("\n" + "=" * 60)
    print("TEST 1: Injury Data Integration")
    print("=" * 60)
    
    fetcher = RealInjuryDataFetcher()
    injury_data = fetcher.get_injury_report()
    
    print(f"✅ Fetched {injury_data['count']} injury reports")
    
    # Show sample injuries
    if injury_data['injuries']:
        print("\nSample injury reports:")
        for injury in injury_data['injuries'][:5]:
            print(f"  - {injury['player']} ({injury['team']}): {injury['status']}")
    
    return injury_data['count'] > 0

def test_vegas_lines():
    """Test 2: Verify Vegas lines fetching"""
    print("\n" + "=" * 60)
    print("TEST 2: Vegas Lines Integration")
    print("=" * 60)
    
    fetcher = RealVegasLinesFetcher()
    lines = fetcher.get_vegas_lines()
    
    print(f"✅ Fetched {len(lines)} game lines")
    
    # Show sample lines
    for matchup, data in list(lines.items())[:3]:
        print(f"  {matchup}")
        print(f"    Total: {data['total']} | Spread: {data['spread']}")
    
    return len(lines) > 0

def test_nba_data():
    """Test 3: Verify NBA game/roster data"""
    print("\n" + "=" * 60)
    print("TEST 3: NBA Game & Roster Data")
    print("=" * 60)
    
    fetcher = RealNBADataFetcher()
    games = fetcher.get_games_for_date("2026-02-09")
    
    print(f"✅ Found {len(games)} games on Feb 9, 2026")
    
    # Show games
    for game in games:
        print(f"  {game['away_team']} @ {game['home_team']}")
    
    return len(games) > 0

def test_underdog_scoring():
    """Test 4: Verify Underdog scoring calculations"""
    print("\n" + "=" * 60)
    print("TEST 4: Underdog Scoring Accuracy")
    print("=" * 60)
    
    scorer = UnderdogScoring()
    
    # Test with known player
    test_player = 'Luka Doncic'
    result = scorer.calculate_underdog_points(test_player)
    
    print(f"\n📊 Sample Calculation: {test_player}")
    print(f"  Stats: {result['stats']}")
    print(f"  Underdog Points: {result['underdog_points']}")
    
    # Verify calculation manually
    expected = (
        result['stats']['points'] * 1.0 +
        result['stats']['rebounds'] * 1.2 +
        result['stats']['assists'] * 1.5 +
        result['stats']['steals'] * 3.0 +
        result['stats']['blocks'] * 3.0 +
        result['stats']['turnovers'] * -1.0
    )
    
    print(f"  Expected: {round(expected, 2)}")
    print(f"  ✅ Match: {abs(result['underdog_points'] - expected) < 0.1}")
    
    return abs(result['underdog_points'] - expected) < 0.1

def test_projection_engine():
    """Test 5: Verify full projection engine"""
    print("\n" + "=" * 60)
    print("TEST 5: Real Projections Engine")
    print("=" * 60)
    
    engine = RealProjectionsEngine()
    
    # Test single projection
    projection = engine.generate_full_projection(
        player_name='Nikola Jokic',
        team='DEN',
        position='C',
        game_total=230.0,
        injury_status='active'
    )
    
    print(f"\n📈 Sample Projection: Nikola Jokic")
    print(f"  Salary: ${projection['salary']:,}")
    print(f"  Projected Underdog Points: {projection['projected_underdog_points']}")
    print(f"  Ceiling: {projection['ceiling']} | Floor: {projection['floor']}")
    print(f"  Value: {projection['value']} pts/$1K")
    print(f"  Game Total: {projection['game_total']}")
    
    # Verify key fields exist
    required_fields = ['name', 'team', 'salary', 'projected_underdog_points', 
                      'ceiling', 'floor', 'value', 'upside']
    missing = [f for f in required_fields if f not in projection]
    
    if missing:
        print(f"  ❌ Missing fields: {missing}")
        return False
    
    print("  ✅ All required fields present")
    return True

def test_full_slate_generation():
    """Test 6: Generate complete slate with real data"""
    print("\n" + "=" * 60)
    print("TEST 6: Full Slate Generation (Real Data)")
    print("=" * 60)
    
    engine = RealProjectionsEngine()
    projections = engine.generate_slate_projections("2026-02-09")
    
    print(f"\n✅ Generated {len(projections)} player projections")
    
    # Show top 10 by projected points
    print("\n🌟 Top 10 Projected Players (Underdog Scoring):")
    for i, player in enumerate(projections[:10], 1):
        print(f"  {i}. {player['name']} ({player['team']}) - ${player['salary']:,}")
        print(f"     Proj: {player['projected_underdog_points']} | Ceiling: {player['ceiling']} | Value: {player['value']}")
    
    # Save to test file
    output_path = '/Users/clawdbot/clawd/data/test-real-slate-feb-9.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump({
            'test_run': True,
            'generated_at': datetime.now().isoformat(),
            'player_count': len(projections),
            'projections': projections
        }, f, indent=2)
    
    print(f"\n💾 Test data saved to: {output_path}")
    
    return len(projections) > 0

def test_sample_players():
    """Test 7: Verify specific player accuracy"""
    print("\n" + "=" * 60)
    print("TEST 7: Sample Player Accuracy Check")
    print("=" * 60)
    
    engine = RealProjectionsEngine()
    
    test_cases = [
        {'name': 'Luka Doncic', 'team': 'DAL', 'pos': 'PG', 'total': 228.5},
        {'name': 'Nikola Jokic', 'team': 'DEN', 'pos': 'C', 'total': 230.0},
        {'name': 'Stephen Curry', 'team': 'GSW', 'pos': 'PG', 'total': 227.0},
    ]
    
    all_passed = True
    
    for test in test_cases:
        proj = engine.generate_full_projection(
            player_name=test['name'],
            team=test['team'],
            position=test['pos'],
            game_total=test['total']
        )
        
        # Sanity checks
        checks = {
            'Has positive projection': proj['projected_underdog_points'] > 0,
            'Ceiling > Projection': proj['ceiling'] > proj['projected_underdog_points'],
            'Projection > Floor': proj['projected_underdog_points'] > proj['floor'],
            'Reasonable salary': 4000 <= proj['salary'] <= 12000,
            'Reasonable value': 2.0 <= proj['value'] <= 8.0
        }
        
        print(f"\n🧪 {test['name']}")
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}")
            if not passed:
                all_passed = False
    
    return all_passed

def run_all_tests():
    """Run comprehensive test suite"""
    print("\n" + "🏀" * 30)
    print("NBA UNDERDOG REAL DATA INTEGRATION - TEST SUITE")
    print("Contest Date: February 9, 2026")
    print("Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("🏀" * 30)
    
    tests = [
        ("Injury Data", test_injury_data),
        ("Vegas Lines", test_vegas_lines),
        ("NBA Games Data", test_nba_data),
        ("Underdog Scoring", test_underdog_scoring),
        ("Projection Engine", test_projection_engine),
        ("Full Slate Generation", test_full_slate_generation),
        ("Sample Player Accuracy", test_sample_players),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ {test_name} FAILED with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 60)
    print(f"Result: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED - Ready for contest!")
        print("✅ System verified for Feb 9, 2026 5:41pm lock")
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed - Review before contest")
    
    print("=" * 60)
    
    return passed_count == total_count


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
