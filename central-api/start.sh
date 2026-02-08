#!/bin/bash
# Start Central API server

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Run ./setup.sh first"
    exit 1
fi

# Load environment
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  .env file not found. Using defaults."
fi

echo "🚀 Starting Central API on port 3003..."
echo "📚 API docs: http://localhost:3003/docs"
echo "Press Ctrl+C to stop"
echo ""

# Start with gunicorn for production
exec gunicorn \
    --bind 127.0.0.1:3003 \
    --workers 2 \
    --timeout 120 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info \
    api.app:app
