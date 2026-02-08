#!/bin/bash
# Quick demo of smart escalation system

echo "======================================================================"
echo "Smart Escalation System - Live Demo"
echo "======================================================================"
echo ""

echo "Testing system health..."
python3 test_system_integration.py
echo ""

echo "======================================================================"
echo "Demo Query 1: Simple factual question (should route LOCAL)"
echo "======================================================================"
python3 test_escalation.py "What is the current date and time?" --no-response
echo ""

echo "======================================================================"
echo "Demo Query 2: Complex decision (should route CLOUD)"
echo "======================================================================"
python3 test_escalation.py "Should I invest my life savings in cryptocurrency or stick with index funds? Provide detailed financial analysis." --no-response
echo ""

echo "======================================================================"
echo "Current Statistics:"
echo "======================================================================"
python3 test_escalation.py --stats
echo ""

echo "======================================================================"
echo "Demo complete! Run 'python3 test_escalation.py --interactive' to try"
echo "your own queries."
echo "======================================================================"
