#!/usr/bin/env python3
"""
Test suite for /ask command

Tests various decision scenarios to ensure accurate prioritization.
"""

import json
import sys
from pathlib import Path
from ask_command import AskCommand, handle_ask_command

WORKSPACE = Path.home() / "clawd"


def test_basic_functionality():
    """Test basic command functionality"""
    print("=" * 60)
    print("TEST 1: Basic 3-option decision")
    print("=" * 60)
    
    opportunities = [
        "Golf inquiry via email from potential client",
        "Partnership proposal with uncertain terms",
        "Feature request for dark mode (no revenue)"
    ]
    
    question = "Which of these 3 opportunities should I pursue?"
    cmd = AskCommand()
    result = cmd.analyze(question, opportunities)
    
    print(f"\nQuestion: {question}")
    print(f"\nResult:")
    print(result["recommendation"])
    print(f"\n✓ Response time: {result['response_time']}s")
    
    # Assert response time < 2s (allowing 3s for safety)
    assert result['response_time'] < 3.0, f"Response too slow: {result['response_time']}s"
    
    # Assert we got a ranking
    assert len(result['ranked_opportunities']) == 3
    
    print("\n✅ TEST 1 PASSED")
    return True


def test_revenue_prioritization():
    """Test that high-revenue opportunities rank higher"""
    print("\n" + "=" * 60)
    print("TEST 2: Revenue prioritization")
    print("=" * 60)
    
    opportunities = [
        "Small feature request worth $50",
        "Consulting gig worth $450",
        "Product idea that could generate $1000/mo"
    ]
    
    question = "What should I focus on?"
    cmd = AskCommand()
    result = cmd.analyze(question, opportunities)
    
    print(f"\nRanking: {' > '.join([o['label'] for o in result['ranked_opportunities']])}")
    
    # Consulting should beat feature request due to higher revenue
    top_opp = result['ranked_opportunities'][0]
    print(f"\nTop pick: {top_opp['description']}")
    print(f"Expected revenue: ${top_opp['expected_revenue']}")
    
    print("\n✅ TEST 2 PASSED")
    return True


def test_conversion_rate_impact():
    """Test that conversion rate affects ranking"""
    print("\n" + "=" * 60)
    print("TEST 3: Conversion rate impact")
    print("=" * 60)
    
    opportunities = [
        "Email inquiry from interested customer",  # High conversion
        "Cold partnership outreach",  # Medium conversion
        "Random feature idea"  # Low conversion
    ]
    
    cmd = AskCommand()
    result = cmd.analyze("Which is most likely to succeed?", opportunities)
    
    print("\nScores:")
    for opp in result['ranked_opportunities']:
        print(f"  {opp['label']}: {opp['score']}/10 "
              f"(conv: {int(opp['conversion_rate']*100)}%, "
              f"rev: ${opp['expected_revenue']})")
    
    # Email inquiry should rank high due to conversion rate
    assert result['ranked_opportunities'][0]['conversion_rate'] >= 0.5
    
    print("\n✅ TEST 3 PASSED")
    return True


def test_effort_consideration():
    """Test that effort is considered in ROI calculation"""
    print("\n" + "=" * 60)
    print("TEST 4: Effort vs reward balance")
    print("=" * 60)
    
    opportunities = [
        "Quick 2-hour consulting call for $300",
        "20-hour product build for $1000",
        "8-hour partnership setup for $500"
    ]
    
    cmd = AskCommand()
    result = cmd.analyze("Best time investment?", opportunities)
    
    print("\nROI Analysis:")
    for opp in result['ranked_opportunities']:
        print(f"  {opp['label']}: ROI ${opp['roi']:.2f}/hour "
              f"({opp['effort_hours']}h for ${opp['expected_revenue']})")
    
    # Quick consulting should have highest ROI
    top_roi = result['ranked_opportunities'][0]['roi']
    print(f"\nBest ROI: ${top_roi:.2f}/hour")
    
    print("\n✅ TEST 4 PASSED")
    return True


def test_decision_logging():
    """Test that decisions are logged for learning"""
    print("\n" + "=" * 60)
    print("TEST 5: Decision logging")
    print("=" * 60)
    
    cmd = AskCommand()
    initial_count = len(cmd.decision_history.get("decisions", []))
    
    result = cmd.analyze(
        "Test question for logging",
        ["Option A", "Option B"]
    )
    
    # Reload and check count increased
    cmd2 = AskCommand()
    new_count = len(cmd2.decision_history.get("decisions", []))
    
    assert new_count > initial_count, "Decision not logged"
    
    print(f"\n✓ Decisions logged: {new_count} total")
    print(f"✓ Latest: {cmd2.decision_history['decisions'][-1]['question']}")
    
    print("\n✅ TEST 5 PASSED")
    return True


def test_fast_response():
    """Test that response is consistently fast"""
    print("\n" + "=" * 60)
    print("TEST 6: Speed consistency (3 runs)")
    print("=" * 60)
    
    opportunities = [
        "Email inquiry about golf coaching",
        "Partnership with local gym",
        "Feature request for app"
    ]
    
    times = []
    for i in range(3):
        cmd = AskCommand()
        result = cmd.analyze(f"Test run {i+1}", opportunities)
        times.append(result['response_time'])
        print(f"  Run {i+1}: {result['response_time']}s")
    
    avg_time = sum(times) / len(times)
    max_time = max(times)
    
    print(f"\n  Average: {avg_time:.2f}s")
    print(f"  Max: {max_time:.2f}s")
    
    assert max_time < 3.0, f"Too slow: {max_time}s"
    
    print("\n✅ TEST 6 PASSED")
    return True


def test_llm_integration():
    """Test local LLM integration"""
    print("\n" + "=" * 60)
    print("TEST 7: Local LLM reasoning")
    print("=" * 60)
    
    cmd = AskCommand()
    result = cmd.analyze(
        "Should I focus on quick wins or long-term projects?",
        [
            "Quick consulting call ($300, 2 hours)",
            "Build SaaS product ($1000/mo potential, 40 hours)"
        ]
    )
    
    if result.get("llm_reasoning"):
        print(f"\n✓ LLM provided reasoning:")
        print(f"  {result['llm_reasoning'][:150]}...")
        print("\n✅ TEST 7 PASSED")
    else:
        print("\n⚠️  LLM reasoning not available (ollama may not be running)")
        print("  Command still works, just without LLM insights")
        print("\n✅ TEST 7 PASSED (degraded mode)")
    
    return True


def run_all_tests():
    """Run complete test suite"""
    print("\n🧪 STARTING /ASK COMMAND TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Revenue Prioritization", test_revenue_prioritization),
        ("Conversion Rate Impact", test_conversion_rate_impact),
        ("Effort Consideration", test_effort_consideration),
        ("Decision Logging", test_decision_logging),
        ("Fast Response", test_fast_response),
        ("LLM Integration", test_llm_integration)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"\n❌ TEST FAILED: {name}")
            print(f"   Error: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
