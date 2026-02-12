#!/usr/bin/env python3
"""
DawgBowl Optimizer System Status
Check that all components are ready for Feb 20th
"""

import sys
from pathlib import Path
from datetime import datetime
import importlib.util


def check_file_exists(file_path: Path, description: str) -> bool:
    """Check if a file exists"""
    if file_path.exists():
        print(f"✓ {description}: {file_path.name}")
        return True
    else:
        print(f"✗ {description}: MISSING")
        return False


def check_module_imports() -> bool:
    """Check that all required modules can be imported"""
    print("\n📦 Checking Python modules...")
    
    required = ['json', 'requests', 'csv', 'statistics']
    all_ok = True
    
    for module in required:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"✗ {module} - MISSING")
            all_ok = False
    
    return all_ok


def check_optimizer() -> bool:
    """Check that the optimizer module loads"""
    print("\n🔧 Checking optimizer module...")
    
    try:
        from dawgbowl_optimizer import DawgBowlOptimizer
        optimizer = DawgBowlOptimizer()
        print("✓ DawgBowlOptimizer loaded successfully")
        print(f"  Season: {optimizer.season}")
        print(f"  Output dir: {optimizer.output_dir}")
        return True
    except Exception as e:
        print(f"✗ Failed to load optimizer: {e}")
        return False


def check_api_access() -> bool:
    """Quick check if NBA API is accessible"""
    print("\n🌐 Checking NBA API access...")
    
    try:
        import requests
        response = requests.get(
            'https://stats.nba.com/stats/leaguedashplayerstats',
            params={'LeagueID': '00', 'Season': '2024-25', 'SeasonType': 'Regular Season', 'PerMode': 'PerGame'},
            headers={
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'https://www.nba.com/'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✓ NBA API accessible")
            print(f"  Response size: {len(response.content):,} bytes")
            return True
        else:
            print(f"⚠️  NBA API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ NBA API check failed: {e}")
        return False


def check_slate_data() -> bool:
    """Check if Feb 20th slate data exists"""
    print("\n📊 Checking slate data...")
    
    workspace = Path.home() / 'clawd'
    possible_files = [
        workspace / 'nba' / 'slate_feb20.json',
        workspace / 'nba' / 'slate_2026-02-20.json',
        workspace / 'data' / 'nba-slate-2026-02-20.json',
    ]
    
    for slate_file in possible_files:
        if slate_file.exists():
            print(f"✓ Slate file found: {slate_file}")
            return True
    
    print("⚠️  No slate file found (will use sample data)")
    print("  To add real slate data:")
    print("  1. Copy slate_template.json")
    print("  2. Fill in actual players/salaries")
    print("  3. Save as slate_feb20.json")
    return False


def system_status():
    """Run full system status check"""
    print("="*80)
    print("🏀 NBA DAWGBOWL OPTIMIZER - SYSTEM STATUS")
    print("="*80)
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target Slate: February 20, 2026")
    print(f"Deadline: February 19, 2026")
    
    workspace = Path.home() / 'clawd' / 'nba'
    
    # Check core files
    print("\n📁 Checking core files...")
    core_files = [
        (workspace / 'dawgbowl_optimizer.py', 'Main optimizer'),
        (workspace / 'run_feb20_optimizer.py', 'Feb 20th runner'),
        (workspace / 'validate_optimizer.py', 'Validation script'),
        (workspace / 'test_csv_format.py', 'CSV tester'),
        (workspace / 'slate_template.json', 'Slate template'),
        (workspace / 'DAWGBOWL_README.md', 'Documentation'),
    ]
    
    files_ok = all(check_file_exists(f, desc) for f, desc in core_files)
    
    # Check modules
    modules_ok = check_module_imports()
    
    # Check optimizer
    optimizer_ok = check_optimizer()
    
    # Check API
    api_ok = check_api_access()
    
    # Check slate data
    slate_ok = check_slate_data()
    
    # Check existing outputs
    print("\n📊 Checking existing outputs...")
    output_files = list(workspace.glob('dawgbowl_rankings_*.json'))
    csv_files = list(workspace.glob('underdog_rankings_*.csv'))
    
    if output_files:
        print(f"✓ Found {len(output_files)} ranking file(s)")
        latest = max(output_files, key=lambda f: f.stat().st_mtime)
        print(f"  Latest: {latest.name}")
    else:
        print("⚠️  No ranking files yet")
    
    if csv_files:
        print(f"✓ Found {len(csv_files)} CSV export(s)")
    else:
        print("⚠️  No CSV exports yet")
    
    # Overall status
    print("\n" + "="*80)
    print("SYSTEM STATUS SUMMARY")
    print("="*80 + "\n")
    
    checks = [
        ("Core files", files_ok),
        ("Python modules", modules_ok),
        ("Optimizer module", optimizer_ok),
        ("NBA API access", api_ok),
        ("Slate data", slate_ok or True),  # Optional
    ]
    
    passed = sum(1 for _, ok in checks if ok)
    total = len(checks)
    
    for check, ok in checks:
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"{check:20s} {status}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✅ SYSTEM READY FOR FEB 20TH!")
        print("\nNext steps:")
        print("  1. Run validation: python3 validate_optimizer.py")
        print("  2. Generate rankings: python3 run_feb20_optimizer.py")
        print("  3. Test CSV format: python3 test_csv_format.py")
        print("  4. Upload to Underdog Fantasy")
    elif passed >= total - 1:
        print("\n🟡 SYSTEM MOSTLY READY")
        print("Review warnings above, but core functionality should work.")
    else:
        print("\n❌ SYSTEM NOT READY")
        print("Fix critical issues before running optimizer.")
    
    print("\n" + "="*80 + "\n")
    
    return passed == total


if __name__ == '__main__':
    success = system_status()
    sys.exit(0 if success else 1)
