#!/bin/bash
# Quick Start for Underdog Contest - Feb 9, 2026
# Run this at 6:00 AM CST

set -e

DAEMON_DIR="/Users/clawdbot/clawd/nba-slate-daemon"
cd "$DAEMON_DIR"

echo "=============================================="
echo "🏀 NBA UNDERDOG CONTEST - QUICK START"
echo "Contest Date: February 9, 2026"
echo "Lock Time: 5:41 PM CST"
echo "=============================================="
echo ""

# Step 1: Verify files exist
echo "📋 Step 1: Verifying files..."
if [ ! -f "real_data_integration.py" ]; then
    echo "❌ Error: real_data_integration.py not found"
    exit 1
fi
if [ ! -f "real_projections_engine.py" ]; then
    echo "❌ Error: real_projections_engine.py not found"
    exit 1
fi
echo "✅ All required files present"
echo ""

# Step 2: Stop any existing daemon
echo "🛑 Step 2: Stopping existing daemon..."
if [ -f "daemon.pid" ]; then
    PID=$(cat daemon.pid)
    if ps -p "$PID" > /dev/null 2>&1; then
        kill "$PID"
        echo "✅ Stopped existing daemon (PID: $PID)"
    fi
fi
echo ""

# Step 3: Run quick test
echo "🧪 Step 3: Running quick health check..."
python3 -c "
from real_projections_engine import RealProjectionsEngine
engine = RealProjectionsEngine()
proj = engine.generate_full_projection('Luka Doncic', 'DAL', 'PG', 228.5)
assert proj['projected_underdog_points'] > 0, 'Projection failed'
print('✅ Projection engine working')
"
echo ""

# Step 4: Start daemon
echo "🚀 Step 4: Starting real data daemon..."
./start_daemon.sh

# Wait for startup
sleep 3

# Step 5: Verify it's running
echo ""
echo "🔍 Step 5: Verifying daemon status..."
if ! curl -s http://localhost:5051/api/status > /dev/null; then
    echo "❌ Daemon not responding on port 5051"
    echo "Check logs: tail -f $DAEMON_DIR/daemon.log"
    exit 1
fi

PLAYER_COUNT=$(curl -s http://localhost:5051/api/players | python3 -c "import sys, json; print(len(json.load(sys.stdin)['players']))")
echo "✅ Daemon running"
echo "✅ $PLAYER_COUNT players loaded"
echo ""

# Step 6: Show top 5 players
echo "🌟 Top 5 Projected Players:"
curl -s http://localhost:5051/api/players | python3 -c "
import sys, json
data = json.load(sys.stdin)
for i, p in enumerate(data['players'][:5], 1):
    print(f\"  {i}. {p['name']} ({p['team']}) - \${p['salary']:,}\")
    print(f\"     Proj: {p['projected_underdog_points']} | Ceiling: {p['ceiling']} | Value: {p['value']}\")
"
echo ""

# Step 7: Show URLs
echo "=============================================="
echo "✅ READY FOR CONTEST"
echo "=============================================="
echo ""
echo "📊 Dashboard: http://localhost:5051"
echo "📁 Data API: http://localhost:5051/api/players"
echo "📥 CSV Export: http://localhost:5051/api/export/csv"
echo ""
echo "📝 Morning brief will generate at 7:30 AM:"
echo "   /Users/clawdbot/clawd/data/nba-morning-brief-2026-02-09.md"
echo ""
echo "🔒 Rankings lock automatically at 11:59 PM"
echo ""
echo "📊 To manually refresh data:"
echo "   curl http://localhost:5051/api/refresh"
echo ""
echo "🛑 To stop daemon:"
echo "   cd $DAEMON_DIR && ./stop_daemon.sh"
echo ""
echo "✅ System is live. Good luck! 🏀💰"
echo "=============================================="
