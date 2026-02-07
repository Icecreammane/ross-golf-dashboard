#!/bin/bash
# Productivity Stack Aliases
# Source this file in your shell config: source ~/clawd/scripts/productivity_aliases.sh

# Decision Framework - Kill overthinking
alias decide='python3 ~/clawd/scripts/decision_framework.py'
alias decide-quick='python3 ~/clawd/scripts/decision_framework.py --quick'

# Revenue Queue - Always know what to work on
alias revenue-queue='python3 ~/clawd/scripts/revenue_queue.py'
alias nexttask='python3 ~/clawd/scripts/revenue_queue.py next'
alias tasks='python3 ~/clawd/scripts/revenue_queue.py list'
alias suggest='python3 ~/clawd/scripts/revenue_queue.py suggest'

# Launch Accountability - Ship more, build less
alias launch-accountability='python3 ~/clawd/scripts/launch_accountability.py'
alias pressure='python3 ~/clawd/scripts/launch_accountability.py pressure'
alias launch-status='python3 ~/clawd/scripts/launch_accountability.py status'

echo "✅ Productivity stack aliases loaded"
echo "   decide, nexttask, tasks, pressure, launch-status"
