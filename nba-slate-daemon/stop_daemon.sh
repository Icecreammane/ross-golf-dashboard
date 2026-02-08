#!/bin/bash
echo "🛑 Stopping NBA Slate Rankings Daemon..."
lsof -ti:5051 | xargs kill -9 2>/dev/null
echo "✅ Daemon stopped (port 5051 cleared)"
