#!/bin/bash
# Demo script for /ask command

echo "🤖 /ASK COMMAND DEMO"
echo "=================================================="
echo ""
echo "This command helps you make fast decisions about"
echo "which opportunities to pursue based on:"
echo "  • Conversion rates"
echo "  • Revenue potential"
echo "  • Effort required"
echo "  • Historical data"
echo ""
echo "=================================================="
echo ""

# Test 1: Basic usage with current opportunities
echo "📋 TEST 1: Analyze current opportunities"
echo "--------------------------------------------------"
python3 ~/clawd/scripts/ask_command.py "Which opportunity should I pursue?"
echo ""
echo ""

# Test 2: Custom scenario
echo "📋 TEST 2: Quick win vs long-term project"
echo "--------------------------------------------------"

# Create a custom scenario
cat > /tmp/test_opportunities.json <<EOF
{
  "opportunities": [
    {
      "description": "Quick consulting call for \$300 (2 hours)",
      "source": "email"
    },
    {
      "description": "Build SaaS product with \$1000/mo potential (40 hours)",
      "source": "idea"
    },
    {
      "description": "Partnership opportunity with local gym (\$500, 8 hours)",
      "source": "linkedin"
    }
  ]
}
EOF

# Temporarily swap opportunities
mv ~/clawd/memory/current_opportunities.json ~/clawd/memory/current_opportunities.json.backup 2>/dev/null
cp /tmp/test_opportunities.json ~/clawd/memory/current_opportunities.json

python3 ~/clawd/scripts/ask_command.py "Should I focus on quick wins or long-term projects?"

# Restore
mv ~/clawd/memory/current_opportunities.json.backup ~/clawd/memory/current_opportunities.json 2>/dev/null

echo ""
echo ""

# Test 3: Speed test
echo "📋 TEST 3: Speed test (5 runs)"
echo "--------------------------------------------------"
for i in {1..5}; do
    python3 ~/clawd/scripts/ask_command.py "Test run $i" | grep "Response time"
done

echo ""
echo ""

# Test 4: Show help
echo "📋 TEST 4: Command help"
echo "--------------------------------------------------"
python3 ~/clawd/scripts/ask_command_integration.py "/ask"

echo ""
echo ""

echo "=================================================="
echo "✅ DEMO COMPLETE!"
echo ""
echo "To use in Telegram:"
echo "  /ask Which of these 3 opportunities should I pursue?"
echo ""
echo "Documentation: ~/clawd/ASK_COMMAND.md"
echo "Tests: python3 ~/clawd/scripts/test_ask_command.py"
echo "=================================================="
