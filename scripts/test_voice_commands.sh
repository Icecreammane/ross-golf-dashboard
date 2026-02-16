#!/bin/bash
# Test Voice Commands
# Validates voice command router functionality

WORKSPACE="$HOME/clawd"
ROUTER="$WORKSPACE/scripts/voice_command_router.py"

echo "🎤 Testing Voice Command Router"
echo "================================"
echo ""

# Test fitness commands
echo "1. Testing Fitness Commands:"
echo "   Command: 'Log bench press 185 pounds 8 reps'"
python3 "$ROUTER" "Log bench press 185 pounds 8 reps" | grep -E "(Intent|Confidence|Result)"
echo ""

echo "   Command: 'I just ate chicken breast 300 calories'"
python3 "$ROUTER" "I just ate chicken breast 300 calories" | grep -E "(Intent|Confidence|Result)"
echo ""

# Test life admin commands
echo "2. Testing Life Admin Commands:"
echo "   Command: 'Add milk to shopping list'"
python3 "$ROUTER" "Add milk to shopping list" | grep -E "(Intent|Confidence|Result)"
echo ""

echo "   Command: 'What's my calendar tomorrow'"
python3 "$ROUTER" "What's my calendar tomorrow" | grep -E "(Intent|Confidence|Result)"
echo ""

# Test general queries
echo "3. Testing General Queries:"
echo "   Command: 'What's the weather like'"
python3 "$ROUTER" "What's the weather like" | grep -E "(Intent|Confidence)"
echo ""

echo "================================"
echo "✅ Voice command testing complete!"
echo ""
echo "📊 Data written to:"
echo "   - $WORKSPACE/data/fitness_data.json"
echo "   - $WORKSPACE/data/shopping_list.json"
echo "   - $WORKSPACE/logs/voice-commands.log"
