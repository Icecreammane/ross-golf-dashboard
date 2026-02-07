#!/bin/bash
# Sub-Agent Framework Test Suite
# Tests all core functionality without actually spawning agents

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

print_test() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_pass() {
    echo -e "${GREEN}✓ $1${NC}"
    ((PASS++))
}

print_fail() {
    echo -e "${RED}✗ $1${NC}"
    ((FAIL++))
}

print_section() {
    echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Test 1: Cost Calculator
test_cost_calculator() {
    print_section "Test 1: Cost Calculator"
    
    print_test "Testing cost estimation..."
    result=$("$PYTHON" "$SCRIPT_DIR/subagent-cost-calculator.py" \
        "Fix the health monitor bug" \
        --hours 1.5 \
        --model "google/gemini-2.0-flash-exp:free" \
        --json 2>/dev/null || echo "{}")
    
    if echo "$result" | grep -q "estimated_cost"; then
        cost=$(echo "$result" | "$PYTHON" -c "import sys, json; print(json.load(sys.stdin).get('estimated_cost', 0))")
        if (( $(echo "$cost > 0" | bc -l) )); then
            print_pass "Cost calculator working (estimated: \$$cost)"
        else
            print_fail "Cost calculator returned zero cost"
        fi
    else
        print_fail "Cost calculator failed"
    fi
    
    print_test "Testing complexity analysis..."
    result=$("$PYTHON" "$SCRIPT_DIR/subagent-cost-calculator.py" \
        "Build complete multi-system integration infrastructure" \
        --hours 10 \
        --model "anthropic/claude-sonnet-4-5" \
        --json 2>/dev/null || echo "{}")
    
    if echo "$result" | grep -q "complexity_multiplier"; then
        multiplier=$(echo "$result" | "$PYTHON" -c "import sys, json; print(json.load(sys.stdin).get('complexity_multiplier', 0))")
        if (( $(echo "$multiplier >= 1.3" | bc -l) )); then
            print_pass "Complexity analysis working (multiplier: ${multiplier}x)"
        else
            print_fail "Complexity multiplier too low for complex task: ${multiplier}x"
        fi
    else
        print_fail "Complexity analysis failed"
    fi
}

# Test 2: Tier Classifier
test_tier_classifier() {
    print_section "Test 2: Tier Classifier"
    
    # Test quick tier
    print_test "Testing quick tier classification..."
    result=$("$PYTHON" "$SCRIPT_DIR/tier-classifier.py" \
        "Fix small bug in auth.py" \
        --json 2>/dev/null || echo "{}")
    
    if echo "$result" | grep -q "tier"; then
        tier=$(echo "$result" | "$PYTHON" -c "import sys, json; print(json.load(sys.stdin).get('tier', ''))")
        if [ "$tier" = "quick" ]; then
            print_pass "Quick tier correctly classified"
        else
            print_fail "Expected quick tier, got: $tier"
        fi
    else
        print_fail "Tier classifier failed"
    fi
    
    # Test deep tier
    print_test "Testing deep tier classification..."
    result=$("$PYTHON" "$SCRIPT_DIR/tier-classifier.py" \
        "Build Spotify integration with full API implementation" \
        --json 2>/dev/null || echo "{}")
    
    tier=$(echo "$result" | "$PYTHON" -c "import sys, json; print(json.load(sys.stdin).get('tier', ''))" 2>/dev/null || echo "")
    if [ "$tier" = "deep" ] || [ "$tier" = "enforcer" ]; then
        print_pass "Complex task classified as $tier tier"
    else
        print_fail "Expected deep/enforcer tier, got: $tier"
    fi
    
    # Test enforcer tier
    print_test "Testing enforcer tier classification..."
    result=$("$PYTHON" "$SCRIPT_DIR/tier-classifier.py" \
        "Build complete infrastructure for multi-system integration with full monitoring" \
        --json 2>/dev/null || echo "{}")
    
    tier=$(echo "$result" | "$PYTHON" -c "import sys, json; print(json.load(sys.stdin).get('tier', ''))" 2>/dev/null || echo "")
    if [ "$tier" = "enforcer" ]; then
        print_pass "Enforcer tier correctly classified"
    else
        print_fail "Expected enforcer tier, got: $tier (acceptable if deep)"
        if [ "$tier" = "deep" ]; then
            print_pass "Deep tier is acceptable for complex tasks"
        fi
    fi
}

# Test 3: Model Selection
test_model_selection() {
    print_section "Test 3: Model Selection"
    
    print_test "Testing model selection for simple task..."
    result=$("$PYTHON" "$SCRIPT_DIR/select-model.py" \
        "Fix typo in documentation" \
        --tier quick \
        --json 2>/dev/null || echo "{}")
    
    if echo "$result" | grep -q "model"; then
        model=$(echo "$result" | "$PYTHON" -c "import sys, json; print(json.load(sys.stdin).get('model', ''))")
        if echo "$model" | grep -qi "gemini"; then
            print_pass "Gemini correctly selected for simple task"
        else
            print_fail "Expected Gemini, got: $model"
        fi
    else
        print_fail "Model selection failed"
    fi
    
    print_test "Testing model selection for complex task..."
    result=$("$PYTHON" "$SCRIPT_DIR/select-model.py" \
        "Design and implement complete system architecture" \
        --tier enforcer \
        --json 2>/dev/null || echo "{}")
    
    model=$(echo "$result" | "$PYTHON" -c "import sys, json; print(json.load(sys.stdin).get('model', ''))" 2>/dev/null || echo "")
    if echo "$model" | grep -qi "sonnet"; then
        print_pass "Sonnet correctly selected for complex task"
    else
        print_fail "Expected Sonnet, got: $model"
    fi
    
    print_test "Testing user override..."
    result=$("$PYTHON" "$SCRIPT_DIR/select-model.py" \
        "Any task" \
        --prefer "anthropic/claude-sonnet-4-5" \
        --json 2>/dev/null || echo "{}")
    
    model=$(echo "$result" | "$PYTHON" -c "import sys, json; print(json.load(sys.stdin).get('model', ''))" 2>/dev/null || echo "")
    if echo "$model" | grep -q "sonnet"; then
        print_pass "User override working"
    else
        print_fail "User override failed"
    fi
}

# Test 4: Spawn Agent (analyze only)
test_spawn_agent() {
    print_section "Test 4: Spawn Agent (Analyze Only)"
    
    print_test "Testing spawn agent analysis..."
    result=$("$PYTHON" "$SCRIPT_DIR/spawn_agent.py" \
        "Build calendar integration" \
        --analyze-only \
        --json 2>/dev/null || echo "{}")
    
    if echo "$result" | grep -q "cost_estimate"; then
        cost=$(echo "$result" | "$PYTHON" -c "import sys, json; print(json.load(sys.stdin)['cost_estimate'].get('estimated_cost', 0))" 2>/dev/null || echo "0")
        tier=$(echo "$result" | "$PYTHON" -c "import sys, json; print(json.load(sys.stdin)['cost_estimate'].get('tier', ''))" 2>/dev/null || echo "")
        
        if (( $(echo "$cost > 0" | bc -l) )); then
            print_pass "Spawn analysis working (tier: $tier, cost: \$$cost)"
        else
            print_fail "Spawn analysis returned zero cost"
        fi
    else
        print_fail "Spawn analysis failed"
    fi
}

# Test 5: Task Templates
test_templates() {
    print_section "Test 5: Task Templates"
    
    print_test "Checking templates file..."
    if [ -f "$SCRIPT_DIR/../subagents/task-templates.json" ]; then
        print_pass "Templates file exists"
        
        print_test "Validating JSON..."
        if "$PYTHON" -m json.tool "$SCRIPT_DIR/../subagents/task-templates.json" >/dev/null 2>&1; then
            print_pass "Templates JSON is valid"
            
            print_test "Checking template count..."
            count=$("$PYTHON" -c "import json; print(len(json.load(open('$SCRIPT_DIR/../subagents/task-templates.json'))))" 2>/dev/null || echo "0")
            if [ "$count" -gt 5 ]; then
                print_pass "Templates loaded ($count templates)"
            else
                print_fail "Too few templates: $count"
            fi
        else
            print_fail "Templates JSON is invalid"
        fi
    else
        print_fail "Templates file missing"
    fi
}

# Test 6: Tracker
test_tracker() {
    print_section "Test 6: Progress Tracker"
    
    print_test "Testing tracker initialization..."
    if "$PYTHON" -c "from track_subagents import SubAgentTracker; t = SubAgentTracker(); print('OK')" 2>/dev/null | grep -q "OK"; then
        print_pass "Tracker imports and initializes"
    else
        print_fail "Tracker import failed"
    fi
    
    print_test "Testing list command..."
    if "$PYTHON" "$SCRIPT_DIR/track-subagents.py" list 2>/dev/null; then
        print_pass "Tracker list command works"
    else
        print_fail "Tracker list command failed"
    fi
    
    print_test "Testing summary command..."
    if "$PYTHON" "$SCRIPT_DIR/track-subagents.py" summary --json 2>/dev/null | grep -q "total"; then
        print_pass "Tracker summary command works"
    else
        print_fail "Tracker summary command failed"
    fi
}

# Test 7: Guardian
test_guardian() {
    print_section "Test 7: Safety Guardian"
    
    print_test "Testing guardian initialization..."
    if "$PYTHON" -c "from subagent_guardian import SubAgentGuardian; g = SubAgentGuardian(); print('OK')" 2>/dev/null | grep -q "OK"; then
        print_pass "Guardian imports and initializes"
    else
        print_fail "Guardian import failed"
    fi
    
    print_test "Testing safety checks..."
    if "$PYTHON" "$SCRIPT_DIR/subagent-guardian.py" check --json 2>/dev/null | grep -q "overall_status"; then
        print_pass "Guardian check command works"
    else
        print_fail "Guardian check command failed"
    fi
    
    print_test "Testing health report..."
    if "$PYTHON" "$SCRIPT_DIR/subagent-guardian.py" report --json 2>/dev/null | grep -q "health_status"; then
        print_pass "Guardian report command works"
    else
        print_fail "Guardian report command failed"
    fi
}

# Test 8: Integration
test_integration() {
    print_section "Test 8: Full Integration Test"
    
    print_test "Testing complete workflow (analyze → estimate → recommend)..."
    
    # Step 1: Classify
    classification=$("$PYTHON" "$SCRIPT_DIR/tier-classifier.py" \
        "Build REST API for user management" \
        --json 2>/dev/null || echo "{}")
    
    tier=$(echo "$classification" | "$PYTHON" -c "import sys, json; print(json.load(sys.stdin).get('tier', 'unknown'))" 2>/dev/null || echo "unknown")
    
    # Step 2: Select model
    model_selection=$("$PYTHON" "$SCRIPT_DIR/select-model.py" \
        "Build REST API for user management" \
        --tier "$tier" \
        --json 2>/dev/null || echo "{}")
    
    model=$(echo "$model_selection" | "$PYTHON" -c "import sys, json; print(json.load(sys.stdin).get('model', 'unknown'))" 2>/dev/null || echo "unknown")
    
    # Step 3: Calculate cost
    cost_estimate=$("$PYTHON" "$SCRIPT_DIR/subagent-cost-calculator.py" \
        "Build REST API for user management" \
        --hours 5 \
        --model "$model" \
        --json 2>/dev/null || echo "{}")
    
    cost=$(echo "$cost_estimate" | "$PYTHON" -c "import sys, json; print(json.load(sys.stdin).get('estimated_cost', 0))" 2>/dev/null || echo "0")
    
    if [ "$tier" != "unknown" ] && [ "$model" != "unknown" ] && (( $(echo "$cost > 0" | bc -l) )); then
        print_pass "Full workflow complete: tier=$tier, model=$model, cost=\$$cost"
    else
        print_fail "Integration test failed: tier=$tier, model=$model, cost=$cost"
    fi
}

# Test 9: Documentation
test_documentation() {
    print_section "Test 9: Documentation"
    
    print_test "Checking guide..."
    if [ -f "$SCRIPT_DIR/../SUBAGENT_GUIDE.md" ]; then
        lines=$(wc -l < "$SCRIPT_DIR/../SUBAGENT_GUIDE.md")
        if [ "$lines" -gt 100 ]; then
            print_pass "Usage guide exists ($lines lines)"
        else
            print_fail "Usage guide too short: $lines lines"
        fi
    else
        print_fail "Usage guide missing"
    fi
    
    print_test "Checking quick reference..."
    if [ -f "$SCRIPT_DIR/../SUBAGENT_REFERENCE.md" ]; then
        print_pass "Quick reference exists"
    else
        print_fail "Quick reference missing"
    fi
}

# Test 10: File Permissions
test_permissions() {
    print_section "Test 10: File Permissions"
    
    for script in spawn-agent.sh spawn_agent.py track-subagents.py subagent-guardian.py tier-classifier.py select-model.py subagent-cost-calculator.py; do
        print_test "Checking $script..."
        if [ -x "$SCRIPT_DIR/$script" ]; then
            print_pass "$script is executable"
        else
            print_fail "$script is not executable"
        fi
    done
}

# Run all tests
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Sub-Agent Framework Test Suite                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

test_cost_calculator
test_tier_classifier
test_model_selection
test_spawn_agent
test_templates
test_tracker
test_guardian
test_integration
test_documentation
test_permissions

# Summary
print_section "Test Summary"

TOTAL=$((PASS + FAIL))
PASS_RATE=$((PASS * 100 / TOTAL))

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✓ ALL TESTS PASSED ($PASS/$TOTAL)                            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}🎉 Sub-agent framework is ready to use!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review SUBAGENT_GUIDE.md"
    echo "  2. Try: ./scripts/spawn-agent.sh --interactive"
    echo "  3. Spawn your first agent!"
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ✗ SOME TESTS FAILED                                       ║${NC}"
    echo -e "${RED}║  Passed: $PASS/$TOTAL ($PASS_RATE%)                                      ║${NC}"
    echo -e "${RED}║  Failed: $FAIL                                               ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Review failures above and fix before using${NC}"
    exit 1
fi
