#!/bin/bash
# Test the NBA rankings system end-to-end

echo "🧪 Testing NBA Rankings System"
echo "=" 50

echo ""
echo "1️⃣  Testing data fetch..."
python3 -c "
from rank_generator import NBADataFetcher
fetcher = NBADataFetcher()
games = fetcher.get_games_for_date('20260205')
print(f'   ✓ Fetched {len(games)} games')
"

echo ""
echo "2️⃣  Testing ranking generation..."
python3 rank_generator.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✓ Rankings generated successfully"
else
    echo "   ❌ Failed to generate rankings"
    exit 1
fi

echo ""
echo "3️⃣  Checking output files..."
if [ -f "rankings.json" ]; then
    echo "   ✓ rankings.json exists"
    num_players=$(cat rankings.json | python3 -c "import json, sys; print(len(json.load(sys.stdin)['rankings']))")
    echo "   ✓ Contains $num_players players"
else
    echo "   ❌ rankings.json not found"
    exit 1
fi

if [ -f "rankings-report.md" ]; then
    echo "   ✓ rankings-report.md exists"
else
    echo "   ❌ rankings-report.md not found"
    exit 1
fi

echo ""
echo "4️⃣  Testing dashboard..."
python3 dashboard.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✓ Dashboard loads successfully"
else
    echo "   ❌ Dashboard failed"
    exit 1
fi

echo ""
echo "=" 50
echo "✅ All tests passed!"
echo ""
echo "System is operational and ready for Thursday's slate."
