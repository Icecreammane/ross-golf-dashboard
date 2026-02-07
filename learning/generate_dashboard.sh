#!/bin/bash
# Generate dashboard data and optionally serve it

cd "$(dirname "$0")"

echo "🧠 Generating dashboard data..."
python3 analyze_patterns.py --json > dashboard_data.json

if [ $? -eq 0 ]; then
    echo "✅ Dashboard data generated: dashboard_data.json"
    echo ""
    echo "To view the dashboard:"
    echo "  python3 -m http.server 8000"
    echo "  Then open: http://localhost:8000/dashboard.html?data=dashboard_data.json"
    echo ""
    
    if [ "$1" == "--serve" ]; then
        echo "Starting web server..."
        python3 -m http.server 8000
    fi
else
    echo "❌ Error generating dashboard data"
    exit 1
fi
