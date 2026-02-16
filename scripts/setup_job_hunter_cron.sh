#!/bin/bash
# Setup Job Hunter to run at 2am daily

echo "🔧 Setting up Job Hunter cron job..."

# Create cron job via Clawdbot gateway
curl -X POST http://localhost:8080/api/cron/add \
  -H "Content-Type: application/json" \
  -d '{
    "schedule": "0 2 * * *",
    "text": "Run job hunter: python3 ~/clawd/scripts/job_hunter.py",
    "note": "Overnight Job Hunter - Scans for new Florida R&D jobs",
    "enabled": true
  }'

echo ""
echo "✅ Job Hunter cron job created"
echo "⏰ Will run daily at 2:00 AM CST"
echo ""
echo "To test manually: python3 ~/clawd/scripts/job_hunter.py"
