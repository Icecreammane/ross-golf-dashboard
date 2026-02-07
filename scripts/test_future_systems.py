#!/usr/bin/env python3
"""
Test script for Future Systems
Verifies all systems import and basic functionality works
"""

import sys
from pathlib import Path

# Add workspace to path
workspace = Path(__file__).parent.parent
sys.path.insert(0, str(workspace))

def test_accountability():
    """Test Pattern Tracking system"""
    print("🧠 Testing Predictive Accountability...")
    
    try:
        from accountability.pattern_tracker import PatternTracker
        tracker = PatternTracker(str(workspace))
        
        # Test logging
        entry = tracker.quick_log("test_action", 5, "revenue_task")
        assert entry["action"] == "test_action"
        assert entry["duration"] == 300  # 5 min = 300 sec
        
        print("✅ Pattern Tracker: Working")
    except Exception as e:
        print(f"❌ Pattern Tracker: {e}")
        return False
    
    try:
        from accountability.pattern_analyzer import PatternAnalyzer
        analyzer = PatternAnalyzer(str(workspace))
        
        # Test analysis (may have no data yet)
        report = analyzer.generate_weekly_report(days=1)
        assert "Pattern Analysis" in report
        
        print("✅ Pattern Analyzer: Working")
    except Exception as e:
        print(f"❌ Pattern Analyzer: {e}")
        return False
    
    try:
        from accountability.predictor import ProcrastinationPredictor
        predictor = ProcrastinationPredictor(str(workspace))
        
        # Test prediction
        prediction = predictor.predict_procrastination()
        assert "risk_level" in prediction
        
        print("✅ Predictor: Working")
    except Exception as e:
        print(f"❌ Predictor: {e}")
        return False
    
    try:
        from accountability.intervention_engine import InterventionEngine
        engine = InterventionEngine(str(workspace))
        
        # Test status
        stats = engine.get_effectiveness_stats()
        assert "total_interventions" in stats
        
        print("✅ Intervention Engine: Working")
    except Exception as e:
        print(f"❌ Intervention Engine: {e}")
        return False
    
    return True

def test_voice():
    """Test Voice Command system"""
    print("\n🎙️  Testing Voice Commands...")
    
    try:
        from voice.command_parser import VoiceCommandParser
        parser = VoiceCommandParser()
        
        # Test parsing
        result = parser.parse("Jarvis what's my MRR")
        assert result is not None
        assert result.intent == "get_mrr"
        
        print("✅ Command Parser: Working")
    except Exception as e:
        print(f"❌ Command Parser: {e}")
        return False
    
    try:
        from voice.mode_router import ModeRouter
        router = ModeRouter(str(workspace))
        
        # Test routing
        from voice.command_parser import VoiceCommandParser
        parser = VoiceCommandParser()
        parsed = parser.parse("Jarvis find 5 leads")
        
        routing = router.route(parsed)
        assert routing["handler"] == "sales_mode"
        
        print("✅ Mode Router: Working")
    except Exception as e:
        print(f"❌ Mode Router: {e}")
        return False
    
    try:
        from voice.response_generator import ResponseGenerator
        generator = ResponseGenerator()
        
        # Test response generation
        response = generator.generate("get_mrr", {"mrr": 47}, {})
        assert "47" in response or "$47" in response
        
        print("✅ Response Generator: Working")
    except Exception as e:
        print(f"❌ Response Generator: {e}")
        return False
    
    return True

def test_outreach():
    """Test Self-Optimizing Outreach system"""
    print("\n📧 Testing Self-Optimizing Outreach...")
    
    try:
        from sales.message_generator import MessageGenerator
        generator = MessageGenerator(str(workspace))
        
        # Test variation generation
        variations = generator.generate_variations(
            product="TestProduct",
            target_audience="test users",
            pain_point="test problem",
            benefit="test benefit"
        )
        
        assert len(variations) == 10
        assert all("message" in v for v in variations)
        
        print("✅ Message Generator: Working")
    except Exception as e:
        print(f"❌ Message Generator: {e}")
        return False
    
    try:
        from sales.response_tracker import ResponseTracker
        tracker = ResponseTracker(str(workspace))
        
        # Test tracking
        metrics = tracker.get_metrics()
        assert "send_count" in metrics
        
        print("✅ Response Tracker: Working")
    except Exception as e:
        print(f"❌ Response Tracker: {e}")
        return False
    
    try:
        from sales.learning_engine import LearningEngine
        engine = LearningEngine(str(workspace))
        
        # Test analysis (may have insufficient data)
        analysis = engine.analyze_results(min_sends=1)
        assert "status" in analysis or "winner" in analysis
        
        print("✅ Learning Engine: Working")
    except Exception as e:
        print(f"❌ Learning Engine: {e}")
        return False
    
    try:
        from sales.evolution_engine import EvolutionEngine
        engine = EvolutionEngine(str(workspace))
        
        # Test evolution check
        decision = engine.should_evolve()
        assert "should_evolve" in decision
        
        print("✅ Evolution Engine: Working")
    except Exception as e:
        print(f"❌ Evolution Engine: {e}")
        return False
    
    return True

def main():
    print("="*60)
    print("🚀 Future Systems Test Suite")
    print("="*60)
    
    results = []
    
    results.append(("Predictive Accountability", test_accountability()))
    results.append(("Voice Commands", test_voice()))
    results.append(("Self-Optimizing Outreach", test_outreach()))
    
    print("\n" + "="*60)
    print("📊 Test Results")
    print("="*60)
    
    for system, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{system:<30} {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All systems operational! Ready for activation.\n")
        return 0
    else:
        print("\n⚠️  Some systems failed. Check errors above.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
