#!/bin/bash
# Night Shift Build - Runs while Ross sleeps
# Prepares tomorrow's work

echo "🌙 Night Shift Build Started - $(date)"

# Run opportunity research
echo "📊 Running opportunity deep-dive..."
python3 ~/clawd/opportunity_scanner/market_scanner.py > ~/clawd/night_shift_output/opportunities_research.txt 2>&1

# Build 2/11 projections detail
echo "🏀 Building detailed 2/11 projections..."
python3 ~/clawd/nba_projections_model.py > ~/clawd/night_shift_output/2_11_projections.txt 2>&1

# Start Notion template skeleton
echo "📝 Building Notion template skeleton..."
python3 ~/clawd/templates/notion_budget_builder.py > ~/clawd/night_shift_output/notion_template_log.txt 2>&1

echo "✅ Night Shift Complete - Ready for morning!"
echo "Output saved to ~/clawd/night_shift_output/"
