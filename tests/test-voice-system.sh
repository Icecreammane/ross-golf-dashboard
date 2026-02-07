#!/bin/bash
# Voice System Testing Suite
# Tests voice generation, formats, templates, and integrations

set -e  # Exit on error

WORKSPACE="$HOME/clawd"
TEST_OUTPUT="$WORKSPACE/tests/voice-test-output"
LOG_FILE="$WORKSPACE/logs/voice-system-test.log"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

echo "🧪 Voice System Test Suite"
echo "=========================="
echo ""

# Setup test directory
mkdir -p "$TEST_OUTPUT"
mkdir -p "$WORKSPACE/logs"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') | $1" >> "$LOG_FILE"
}

# Test result functions
pass_test() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    log "PASS: $1"
    ((TESTS_PASSED++))
}

fail_test() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    log "FAIL: $1"
    ((TESTS_FAILED++))
}

warn_test() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
    log "WARN: $1"
}

# Clear previous log
> "$LOG_FILE"
log "Voice System Test Suite Started"

echo "1️⃣  Testing Core Voice Generation Module"
echo "----------------------------------------"

# Test 1: Check if auto-voice.py exists and is executable
if [ -f "$WORKSPACE/systems/auto-voice.py" ]; then
    pass_test "auto-voice.py exists"
else
    fail_test "auto-voice.py not found"
fi

# Test 2: Check OpenAI API key
if [ -n "$OPENAI_API_KEY" ]; then
    pass_test "OpenAI API key is set"
else
    fail_test "OpenAI API key not found in environment"
fi

# Test 3: Generate a test voice clip
echo ""
echo "Generating test voice clip..."
TEST_TEXT="This is a test of the automated voice system. If you can hear this, voice generation is working correctly."

if python3 "$WORKSPACE/systems/auto-voice.py" "$TEST_TEXT" "$TEST_OUTPUT/test-voice.opus" > /dev/null 2>&1; then
    if [ -f "$TEST_OUTPUT/test-voice.opus" ]; then
        FILE_SIZE=$(stat -f%z "$TEST_OUTPUT/test-voice.opus" 2>/dev/null || stat -c%s "$TEST_OUTPUT/test-voice.opus")
        if [ "$FILE_SIZE" -gt 1000 ]; then
            pass_test "Voice generation works (${FILE_SIZE} bytes)"
        else
            fail_test "Generated file too small (${FILE_SIZE} bytes)"
        fi
    else
        fail_test "Voice file not created"
    fi
else
    fail_test "Voice generation script error"
fi

# Test 4: Verify file format
if command -v file > /dev/null 2>&1; then
    FILE_TYPE=$(file "$TEST_OUTPUT/test-voice.opus")
    if [[ "$FILE_TYPE" == *"Ogg"* ]] || [[ "$FILE_TYPE" == *"Opus"* ]]; then
        pass_test "Output format is valid Opus/Ogg"
    else
        warn_test "File format might be incorrect: $FILE_TYPE"
    fi
fi

echo ""
echo "2️⃣  Testing Voice Templates"
echo "----------------------------------------"

# Test 5: Check if voice-templates.json exists
if [ -f "$WORKSPACE/templates/voice-templates.json" ]; then
    pass_test "voice-templates.json exists"
    
    # Test 6: Validate JSON syntax
    if python3 -c "import json; json.load(open('$WORKSPACE/templates/voice-templates.json'))" 2>/dev/null; then
        pass_test "voice-templates.json is valid JSON"
        
        # Test 7: Check for required template sections
        REQUIRED_SECTIONS=("morning_brief" "build_updates" "evening_checkin" "alerts")
        for section in "${REQUIRED_SECTIONS[@]}"; do
            if python3 -c "import json; data = json.load(open('$WORKSPACE/templates/voice-templates.json')); exit(0 if '$section' in data else 1)"; then
                pass_test "Template section '$section' exists"
            else
                fail_test "Template section '$section' missing"
            fi
        done
    else
        fail_test "voice-templates.json has invalid JSON syntax"
    fi
else
    fail_test "voice-templates.json not found"
fi

echo ""
echo "3️⃣  Testing Morning Brief Voice Generation"
echo "----------------------------------------"

# Test 8: Check if generate-morning-brief-voice.py exists
if [ -f "$WORKSPACE/scripts/generate-morning-brief-voice.py" ]; then
    pass_test "generate-morning-brief-voice.py exists"
    
    # Test 9: Try to generate morning brief (dry run)
    echo "Generating test morning brief voice..."
    if python3 "$WORKSPACE/scripts/generate-morning-brief-voice.py" --force 2>&1 | tee -a "$LOG_FILE"; then
        # Check if output files were created
        if ls "$WORKSPACE/morning-briefs"/*.opus > /dev/null 2>&1; then
            pass_test "Morning brief voice generated"
            
            # Check for transcript
            if ls "$WORKSPACE/morning-briefs"/*.txt > /dev/null 2>&1; then
                pass_test "Morning brief transcript created"
            else
                warn_test "Transcript file not found"
            fi
        else
            fail_test "Morning brief voice file not created"
        fi
    else
        fail_test "Morning brief generation failed"
    fi
else
    fail_test "generate-morning-brief-voice.py not found"
fi

echo ""
echo "4️⃣  Testing Build Update Voice Generator"
echo "----------------------------------------"

# Test 10: Check if voice-build-updates.py exists
if [ -f "$WORKSPACE/systems/voice-build-updates.py" ]; then
    pass_test "voice-build-updates.py exists"
    
    # Test 11: Run build update check (dry run)
    echo "Running build update check..."
    if python3 "$WORKSPACE/systems/voice-build-updates.py" --force 2>&1 | tee -a "$LOG_FILE"; then
        pass_test "Build update script runs without errors"
    else
        fail_test "Build update script encountered errors"
    fi
else
    fail_test "voice-build-updates.py not found"
fi

echo ""
echo "5️⃣  Testing Smart Context Integration"
echo "----------------------------------------"

# Test 12: Check if smart-context.py exists
if [ -f "$WORKSPACE/systems/smart-context.py" ]; then
    pass_test "smart-context.py exists"
    
    # Test 13: Test context detection
    if python3 "$WORKSPACE/systems/smart-context.py" --summary > /dev/null 2>&1; then
        pass_test "Context detection works"
    else
        fail_test "Context detection failed"
    fi
else
    fail_test "smart-context.py not found"
fi

echo ""
echo "6️⃣  Testing Cost Tracking"
echo "----------------------------------------"

# Test 14: Check if cost log exists
if [ -f "$WORKSPACE/logs/voice-cost-tracking.json" ]; then
    pass_test "Cost tracking log exists"
    
    # Test 15: Get cost summary
    if python3 "$WORKSPACE/systems/auto-voice.py" --cost-summary > /dev/null 2>&1; then
        pass_test "Cost summary generation works"
    else
        fail_test "Cost summary failed"
    fi
else
    warn_test "No cost log yet (will be created on first use)"
fi

echo ""
echo "7️⃣  Audio Playback Test (Manual)"
echo "----------------------------------------"

if [ -f "$TEST_OUTPUT/test-voice.opus" ]; then
    echo "🔊 Test audio file generated: $TEST_OUTPUT/test-voice.opus"
    echo ""
    echo "   To play the test audio manually:"
    echo "   • macOS:  afplay $TEST_OUTPUT/test-voice.opus"
    echo "   • Linux:  ffplay -nodisp -autoexit $TEST_OUTPUT/test-voice.opus"
    echo "   • Or send to Telegram and listen there"
    echo ""
    
    # Try to auto-play on macOS
    if command -v afplay > /dev/null 2>&1; then
        echo "   Playing test audio..."
        afplay "$TEST_OUTPUT/test-voice.opus" &
        PLAY_PID=$!
        sleep 5
        kill $PLAY_PID 2>/dev/null || true
        pass_test "Audio playback initiated (macOS)"
    else
        warn_test "Audio playback tool not available (install ffmpeg for testing)"
    fi
fi

echo ""
echo "========================================"
echo "📊 Test Summary"
echo "========================================"
echo -e "${GREEN}Passed:${NC} $TESTS_PASSED"
echo -e "${RED}Failed:${NC} $TESTS_FAILED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "🎉 Voice system is ready to use!"
    echo ""
    echo "Next steps:"
    echo "  1. Test the morning brief: python3 ~/clawd/scripts/generate-morning-brief-voice.py --force"
    echo "  2. Listen to the output: ls -lh ~/clawd/morning-briefs/latest.opus"
    echo "  3. Send to Telegram (via main agent): request morning brief voice"
    echo "  4. Add to cron: 30 7 * * * cd ~/clawd && python3 scripts/generate-morning-brief-voice.py --send"
    log "All tests passed!"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed${NC}"
    echo "Review the log: $LOG_FILE"
    log "Tests completed with $TESTS_FAILED failure(s)"
    exit 1
fi
