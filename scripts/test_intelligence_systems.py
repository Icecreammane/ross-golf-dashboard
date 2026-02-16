#!/usr/bin/env python3
"""
Comprehensive Test Suite for All 6 Intelligence Systems
Run this to verify all systems are operational
"""

import sys
from pathlib import Path

WORKSPACE = Path("/Users/clawdbot/clawd")
sys.path.insert(0, str(WORKSPACE / "scripts"))

def test_all_systems():
    """Test all 6 intelligence systems"""
    print("=" * 60)
    print("JARVIS INTELLIGENCE SYSTEMS - FULL TEST SUITE")
    print("=" * 60)
    print()
    
    results = []
    
    # 1. Context Telepathy
    print("1️⃣  Testing Context Telepathy Engine...")
    try:
        from context_telepathy import ContextTelepathy
        engine = ContextTelepathy()
        engine.log_interaction("query", "workout", {"time": "evening"})
        predictions = engine.predict_next_need()
        print(f"   ✅ Context Telepathy: {len(engine.patterns.get('temporal_patterns', []))} patterns tracked")
        results.append(("Context Telepathy", True))
    except Exception as e:
        print(f"   ❌ Context Telepathy FAILED: {e}")
        results.append(("Context Telepathy", False))
    print()
    
    # 2. Instant Recall
    print("2️⃣  Testing Instant Recall System...")
    try:
        from instant_recall import InstantRecall
        recall = InstantRecall()
        count = recall.rebuild_index()
        search_results = recall.search("workout", limit=3)
        print(f"   ✅ Instant Recall: {count} entries indexed, {len(search_results)} search results")
        results.append(("Instant Recall", True))
    except Exception as e:
        print(f"   ❌ Instant Recall FAILED: {e}")
        results.append(("Instant Recall", False))
    print()
    
    # 3. Decision Engine
    print("3️⃣  Testing Decision Confidence Scoring...")
    try:
        from decision_engine import DecisionEngine
        engine = DecisionEngine()
        score = engine.score_decision("update documentation", {"reversible": True})
        print(f"   ✅ Decision Engine: {score['confidence']:.0%} confidence, {score['recommendation']}")
        results.append(("Decision Engine", True))
    except Exception as e:
        print(f"   ❌ Decision Engine FAILED: {e}")
        results.append(("Decision Engine", False))
    print()
    
    # 4. Personality Evolution
    print("4️⃣  Testing Personality Learning Loop...")
    try:
        from personality_evolution import PersonalityEvolution
        personality = PersonalityEvolution()
        personality.log_interaction("Test message 🔥", "Great!", {"work": True})
        tone = personality.get_recommended_tone({"work_related": True})
        print(f"   ✅ Personality Evolution: {personality.model['learning_stats']['total_interactions']} interactions logged")
        results.append(("Personality Evolution", True))
    except Exception as e:
        print(f"   ❌ Personality Evolution FAILED: {e}")
        results.append(("Personality Evolution", False))
    print()
    
    # 5. Proactive Intelligence
    print("5️⃣  Testing Proactive Intelligence Agent...")
    try:
        from proactive_intel import ProactiveIntel
        intel = ProactiveIntel()
        findings = intel.run_research_cycle()
        print(f"   ✅ Proactive Intel: {len(findings['opportunities'])} opportunities found")
        results.append(("Proactive Intelligence", True))
    except Exception as e:
        print(f"   ❌ Proactive Intelligence FAILED: {e}")
        results.append(("Proactive Intelligence", False))
    print()
    
    # 6. Execution Optimizer
    print("6️⃣  Testing Execution Speed Optimizer...")
    try:
        from parallel_builder import ExecutionOptimizer
        optimizer = ExecutionOptimizer()
        templates = optimizer.get_template_list()
        subtasks = optimizer.decompose_task("Build API")
        print(f"   ✅ Execution Optimizer: {len(templates)} templates, {len(subtasks)} subtasks generated")
        results.append(("Execution Optimizer", True))
    except Exception as e:
        print(f"   ❌ Execution Optimizer FAILED: {e}")
        results.append(("Execution Optimizer", False))
    print()
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for system, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {system}")
    
    print()
    passed = sum(1 for _, p in results if p)
    total = len(results)
    print(f"Result: {passed}/{total} systems operational ({passed/total*100:.0%})")
    
    if passed == total:
        print("\n🎉 ALL SYSTEMS OPERATIONAL! Jarvis is 10x smarter!")
    else:
        print("\n⚠️  Some systems need attention")
    
    return passed == total


if __name__ == "__main__":
    success = test_all_systems()
    sys.exit(0 if success else 1)
