#!/bin/bash
# jarvis_quick.sh - Quick commands for Ross

set -e

SCRIPTS_DIR="$HOME/clawd/scripts"
WORKSPACE="$HOME/clawd"

case "$1" in
  status)
    echo "📊 Build Status"
    echo "==============="
    python3 "$SCRIPTS_DIR/build_status.py" 2>/dev/null || echo "⚠️  build_status.py not found"
    echo ""
    python3 "$SCRIPTS_DIR/cost_tracker.py" --today
    ;;
    
  cost)
    python3 "$SCRIPTS_DIR/cost_tracker.py" --today
    ;;
    
  week)
    python3 "$SCRIPTS_DIR/cost_tracker.py" --week
    ;;
    
  spawn)
    echo "🚀 Forcing autonomous check..."
    python3 "$SCRIPTS_DIR/autonomous_check.py" --force
    ;;
    
  pause)
    touch "$WORKSPACE/.pause_autonomy"
    echo "⏸️  Autonomy paused"
    echo "   No new builds will spawn until resumed"
    echo "   Run: jarvis_quick resume"
    ;;
    
  resume)
    rm -f "$WORKSPACE/.pause_autonomy"
    echo "▶️  Autonomy resumed"
    echo "   Builds will spawn automatically"
    ;;
    
  clean)
    echo "🧹 Running memory cleanup..."
    python3 "$SCRIPTS_DIR/cleanup_memory.py" "$@"
    ;;
    
  clean-dry)
    echo "🧹 Memory cleanup (dry run)..."
    python3 "$SCRIPTS_DIR/cleanup_memory.py" --dry-run
    ;;
    
  progress)
    echo "📊 Current Progress"
    echo "=================="
    if [ -f "$WORKSPACE/progress-data.json" ]; then
      python3 -c "
import json
with open('$WORKSPACE/progress-data.json', 'r') as f:
    data = json.load(f)
    if data.get('agents'):
        for sid, agent in data['agents'].items():
            print(f\"  {agent['task_name']}: {agent['state']} ({agent['percent']}%)\")
            print(f\"    └─ {agent['message']}\")
    else:
        print('  No active builds')
"
    else
      echo "  No progress data yet"
    fi
    ;;
    
  dashboard)
    echo "🌐 Starting dashboard server..."
    cd "$WORKSPACE"
    python3 -m http.server 8080 &
    SERVER_PID=$!
    echo "   Dashboard running at: http://localhost:8080/org-chart-dashboard.html"
    echo "   Press Ctrl+C to stop"
    echo "   Server PID: $SERVER_PID"
    wait $SERVER_PID
    ;;
    
  logs)
    echo "📋 Recent Jarvis Journal Entries"
    echo "================================="
    tail -n 20 "$WORKSPACE/memory/jarvis-journal.md" 2>/dev/null || echo "No journal entries yet"
    ;;
    
  queue)
    echo "📋 Build Queue"
    echo "=============="
    cat "$WORKSPACE/BUILD_QUEUE.md" 2>/dev/null || echo "No queue file"
    ;;
    
  help|--help|-h)
    cat << 'EOF'
🤖 Jarvis Quick Commands
=========================

Usage: jarvis_quick <command>

Commands:
  status      Show build status + today's costs
  cost        Show today's API costs
  week        Show this week's API costs
  spawn       Force autonomous check (spawn next build)
  pause       Pause autonomous builds
  resume      Resume autonomous builds
  clean       Run memory cleanup (removes old files)
  clean-dry   Preview what would be cleaned (dry run)
  progress    Show current build progress
  dashboard   Start local dashboard server
  logs        Show recent journal entries
  queue       Show build queue
  help        Show this help message

Examples:
  jarvis_quick status       # Quick status check
  jarvis_quick pause        # Stop spawning new builds
  jarvis_quick clean-dry    # See what cleanup would remove
  jarvis_quick dashboard    # View org chart in browser

EOF
    ;;
    
  *)
    echo "❌ Unknown command: $1"
    echo "Run 'jarvis_quick help' for usage"
    exit 1
    ;;
esac
