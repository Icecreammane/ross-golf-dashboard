#!/usr/bin/env python3
"""
Quick integration test - verifies all components are working
"""

import sys
import json
from pathlib import Path

print("Smart Escalation System - Integration Test\n")
print("=" * 60)

# Test 1: Check Ollama
print("\n1. Checking Ollama...")
try:
    import requests
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    if response.status_code == 200:
        models = response.json().get("models", [])
        model_names = [m["name"] for m in models]
        print(f"   ✓ Ollama running with {len(models)} models")
        
        required = ["qwen2.5:14b", "llama3.1:8b"]
        for model in required:
            if any(model in name for name in model_names):
                print(f"   ✓ {model} available")
            else:
                print(f"   ✗ {model} NOT FOUND - run: ollama pull {model}")
    else:
        print("   ✗ Ollama not responding")
except Exception as e:
    print(f"   ✗ Ollama error: {e}")
    print("   → Start Ollama: ollama serve")

# Test 2: Load engine
print("\n2. Loading Smart Escalation Engine...")
try:
    from smart_escalation_engine import get_engine
    engine = get_engine()
    print("   ✓ Engine loaded successfully")
except Exception as e:
    print(f"   ✗ Engine failed to load: {e}")
    sys.exit(1)

# Test 3: Load middleware
print("\n3. Loading Telegram Middleware...")
try:
    from telegram_escalation_middleware import get_middleware
    middleware = get_middleware()
    print("   ✓ Middleware loaded successfully")
except Exception as e:
    print(f"   ✗ Middleware failed to load: {e}")
    sys.exit(1)

# Test 4: Check config
print("\n4. Checking configuration...")
config_file = Path.home() / "clawd" / "config" / "escalation_config.json"
if config_file.exists():
    config = json.loads(config_file.read_text())
    print(f"   ✓ Config loaded")
    print(f"   ✓ Enabled: {config.get('enabled', False)}")
    print(f"   ✓ Telegram: {config.get('telegram', {}).get('enabled', False)}")
else:
    print("   ✗ Config file not found")

# Test 5: Check directories
print("\n5. Checking directories...")
workspace = Path.home() / "clawd"
memory_dir = workspace / "memory"

if memory_dir.exists():
    print(f"   ✓ Memory directory exists: {memory_dir}")
else:
    print(f"   ! Creating memory directory: {memory_dir}")
    memory_dir.mkdir(parents=True, exist_ok=True)

# Test 6: Quick routing test (without actual LLM call)
print("\n6. Testing routing logic...")
try:
    # Create a mock complexity score
    from smart_escalation_engine import ComplexityScore
    
    # Low complexity - should stay local
    low_score = ComplexityScore(
        overall=15,
        factual_vs_reasoning=10,
        data_retrieval=20,
        decision_making=5,
        time_sensitivity=10,
        reversibility=10,
        confidence=90
    )
    
    should_escalate = low_score.should_escalate()
    if not should_escalate:
        print("   ✓ Low complexity correctly routes to LOCAL")
    else:
        print("   ✗ Low complexity incorrectly escalates")
    
    # High complexity - should escalate
    high_score = ComplexityScore(
        overall=85,
        factual_vs_reasoning=80,
        data_retrieval=70,
        decision_making=90,
        time_sensitivity=50,
        reversibility=80,
        confidence=40
    )
    
    should_escalate = high_score.should_escalate()
    if should_escalate:
        print("   ✓ High complexity correctly routes to CLOUD")
    else:
        print("   ✗ High complexity failed to escalate")
    
except Exception as e:
    print(f"   ✗ Routing logic error: {e}")

# Test 7: Check cost tracking
print("\n7. Checking cost tracking...")
try:
    savings = engine.get_cost_savings()
    print(f"   ✓ Cost tracking initialized")
    print(f"   → Total queries: {savings.get('total_queries', 0)}")
    print(f"   → Cost saved: ${savings.get('cost_saved', 0):.4f}")
except Exception as e:
    print(f"   ✗ Cost tracking error: {e}")

print("\n" + "=" * 60)
print("\n✅ System Integration Test Complete")
print("\nNext steps:")
print("  1. Test with real query: python3 test_escalation.py 'What time is it?'")
print("  2. Run benchmark: python3 test_escalation.py --benchmark")
print("  3. View dashboard: python3 escalation_dashboard.py")
print("  4. Integrate with Telegram gateway (see SMART_ESCALATION_SYSTEM.md)")
print()
