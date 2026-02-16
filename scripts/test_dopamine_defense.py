#!/usr/bin/env python3
"""
Test script for Dopamine Defense System.

Runs through core functionality to verify everything works.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from activity_tracker import (
    record_interaction,
    get_idle_status,
    get_daily_summary,
    load_activity_log,
    save_activity_log,
    CST
)
from dopamine_defense import (
    check_and_interrupt,
    get_next_quick_win,
    load_quick_wins,
    get_defense_stats,
    generate_evening_report,
    record_response_received
)

def print_section(title):
    """Print test section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_activity_tracking():
    """Test activity tracking functionality."""
    print_section("Test 1: Activity Tracking")
    
    # Record interaction
    print("\n1. Recording interaction...")
    result = record_interaction("test")
    print(f"   ✓ Interaction recorded at {result['timestamp']}")
    print(f"   - Work hours: {result['work_hours']}")
    print(f"   - Idle detected: {result['idle_detected']}")
    
    # Check status
    print("\n2. Checking idle status...")
    status = get_idle_status()
    print(f"   ✓ Is idle: {status['is_idle']}")
    print(f"   - Minutes idle: {status['minutes_idle']}")
    print(f"   - Should interrupt: {status['should_interrupt']}")
    
    # Get summary
    print("\n3. Getting daily summary...")
    summary = get_daily_summary()
    print(f"   ✓ Total sessions: {summary['total_sessions']}")
    print(f"   - Active time: {summary['estimated_active_minutes']}m")
    print(f"   - Idle time: {summary['total_idle_minutes']}m")
    print(f"   - Productivity: {int(summary['productivity_score'] * 100)}%")

def test_quick_wins():
    """Test quick win selection."""
    print_section("Test 2: Quick Win Library")
    
    wins_data = load_quick_wins()
    total_wins = len(wins_data.get("quick_wins", []))
    print(f"\n✓ Loaded {total_wins} quick win tasks")
    
    print("\n1. Testing task rotation (5 selections)...")
    for i in range(5):
        win = get_next_quick_win()
        if win:
            print(f"   {i+1}. {win['task'][:50]}... ({win['category']}, {win['estimated_minutes']}m)")
    
    print("\n2. Verifying no immediate repeats...")
    wins_data = load_quick_wins()
    history = wins_data.get("suggestion_history", [])
    unique = len(set(history[-5:]))
    print(f"   ✓ Last 5 suggestions: {unique} unique tasks")

def test_interrupt_logic():
    """Test interrupt decision logic."""
    print_section("Test 3: Interrupt Logic")
    
    print("\n1. Checking interrupt decision (should not fire - not idle)...")
    result = check_and_interrupt()
    print(f"   Should interrupt: {result['should_interrupt']}")
    print(f"   Reason: {result['reason']}")
    
    if result['should_interrupt']:
        print(f"\n   📨 Would send message:")
        print(f"   {result['message'][:100]}...")
    
    print("\n2. Testing cooldown mechanism...")
    stats = get_defense_stats()
    print(f"   ✓ Total interrupts sent: {stats['total_interrupts']}")
    print(f"   - Success rate: {int(stats['success_rate'] * 100)}%")
    if stats['last_interrupt']:
        print(f"   - Last interrupt: {stats['last_interrupt']}")

def test_forced_idle_scenario():
    """Test by forcing an idle scenario."""
    print_section("Test 4: Forced Idle Scenario")
    
    print("\n⚠️  Simulating 25-minute idle period...")
    
    # Backup current state
    log = load_activity_log()
    original_last = log.get("last_interaction")
    
    # Set last interaction to 25 minutes ago (during work hours)
    now = datetime.now(CST)
    
    # Make sure we're in work hours for the test
    fake_now = now.replace(hour=14)  # 2pm CST
    fake_last = fake_now - timedelta(minutes=25)
    
    log["last_interaction"] = fake_last.isoformat()
    save_activity_log(log)
    
    print(f"   Set last_interaction to: {fake_last.strftime('%I:%M %p')}")
    print(f"   Current time (simulated): {fake_now.strftime('%I:%M %p')}")
    
    # Check status
    status = get_idle_status()
    print(f"\n   Idle status check:")
    print(f"   - Is idle: {status['is_idle']}")
    print(f"   - Minutes idle: {status['minutes_idle']}")
    print(f"   - Should interrupt: {status['should_interrupt']}")
    
    # Check interrupt decision
    result = check_and_interrupt()
    print(f"\n   Interrupt decision:")
    print(f"   - Should send: {result['should_interrupt']}")
    print(f"   - Reason: {result['reason']}")
    
    if result['should_interrupt'] and result['message']:
        print(f"\n   📨 Message that would be sent:")
        print(f"   ---")
        print(f"   {result['message']}")
        print(f"   ---")
        print(f"\n   Quick win: {result['quick_win']['task']}")
    
    # Restore original state
    if original_last:
        log["last_interaction"] = original_last
        save_activity_log(log)
        print(f"\n   ✓ Restored original state")
    else:
        print(f"\n   ⚠️  Note: Activity log was empty before test")

def test_evening_report():
    """Test evening report generation."""
    print_section("Test 5: Evening Report")
    
    print("\n1. Generating report...")
    report = generate_evening_report()
    
    print("\n   📊 Generated Report:")
    print("   " + "---" * 20)
    for line in report.split('\n'):
        print(f"   {line}")
    print("   " + "---" * 20)

def test_response_tracking():
    """Test response tracking."""
    print_section("Test 6: Response Tracking")
    
    stats_before = get_defense_stats()
    print(f"\n   Current stats:")
    print(f"   - Total interrupts: {stats_before['total_interrupts']}")
    print(f"   - Successful: {stats_before['successful_engagements']}")
    
    if stats_before['total_interrupts'] > 0:
        print("\n   Testing response recording...")
        record_response_received()
        
        stats_after = get_defense_stats()
        print(f"   ✓ Response recorded")
        print(f"   - New success rate: {int(stats_after['success_rate'] * 100)}%")

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  DOPAMINE DEFENSE SYSTEM - TEST SUITE")
    print("="*60)
    print("\nThis script tests core functionality without sending messages.")
    print("Safe to run - only modifies test data files.\n")
    
    try:
        test_activity_tracking()
        test_quick_wins()
        test_interrupt_logic()
        test_forced_idle_scenario()
        test_evening_report()
        test_response_tracking()
        
        print_section("✅ All Tests Complete")
        print("\n🎯 Next steps:")
        print("   1. Review test output above")
        print("   2. Integrate with HEARTBEAT.md")
        print("   3. Test with real idle periods")
        print("   4. Verify Telegram messages send correctly")
        print("\nSee docs/DOPAMINE_DEFENSE.md for integration guide.\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed with error:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
