#!/bin/bash
# Quick script to regenerate NBA rankings on demand

echo "🏀 Updating NBA Rankings..."
echo ""

cd ~/clawd/nba || exit 1

# Run the ranking generator
python3 rank_generator.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Rankings updated successfully!"
    echo ""
    echo "📂 Files generated:"
    echo "   - rankings.json (data for apps)"
    echo "   - rankings-report.md (human-readable)"
    echo ""
    echo "📖 View report: cat ~/clawd/nba/rankings-report.md"
else
    echo "❌ Error generating rankings"
    exit 1
fi
