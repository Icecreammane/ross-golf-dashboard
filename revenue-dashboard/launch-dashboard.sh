#!/bin/bash
# Quick launcher for Revenue Dashboard

echo "🚀 Launching Revenue Dashboard..."
echo ""

# Check if files exist
if [ ! -f "index.html" ]; then
    echo "❌ Error: index.html not found"
    echo "Make sure you're in the revenue-dashboard/ directory"
    exit 1
fi

# Option 1: Try to open in default browser
echo "📊 Opening dashboard in your default browser..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open index.html
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open index.html
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    start index.html
else
    echo "⚠️  Couldn't detect OS. Please open index.html manually."
fi

echo ""
echo "✅ Dashboard opened!"
echo ""
echo "💡 Tips:"
echo "  - Update data.json to change your numbers"
echo "  - Refresh browser (⌘R / Ctrl+R) after updating"
echo "  - Read README.md for full documentation"
echo ""
echo "📈 Your mission: $0 → $500 MRR → Florida"
echo ""
