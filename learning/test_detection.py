#!/usr/bin/env python3
"""Test the auto-detection of Ross's responses."""

from agent_integration import OutcomeLearner

def test_detection():
    """Test various response patterns."""
    
    learner = OutcomeLearner()
    
    test_cases = [
        # Positive responses
        ("yes let's do it", "implemented"),
        ("yeah that sounds good", "implemented"),
        ("sure, go for it", "implemented"),
        ("absolutely, build it", "implemented"),
        ("ok let's try", "implemented"),
        ("perfect idea", "implemented"),
        
        # Negative responses  
        ("no thanks", "rejected"),
        ("nah not interested", "rejected"),
        ("skip this one", "rejected"),
        ("not worth it", "rejected"),
        ("pass", "rejected"),
        
        # Deferred responses
        ("maybe later", "deferred"),
        ("let's wait on this", "deferred"),
        ("not now, maybe eventually", "deferred"),
        ("come back to this", "deferred"),
        ("not yet", "deferred"),
        
        # Ambiguous (should return None)
        ("interesting", None),
        ("hmm", None),
        ("tell me more", None),
        ("what do you think?", None),
    ]
    
    print("🧪 Testing Response Auto-Detection\n")
    print("="*70)
    
    passed = 0
    failed = 0
    
    for message, expected in test_cases:
        result = learner.detect_response(message)
        status = "✅" if result == expected else "❌"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} '{message}'")
        print(f"   Expected: {expected} | Got: {result}")
        print()
    
    print("="*70)
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    print(f"   Success rate: {passed / len(test_cases) * 100:.1f}%\n")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed - review detection patterns")

if __name__ == "__main__":
    test_detection()
