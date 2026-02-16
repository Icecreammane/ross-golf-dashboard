#!/bin/bash
# Daily job scanner - runs at 8am via cron
# Delivers Florida R&D job matches to Ross via Telegram

cd ~/clawd

# Run job search
echo "🔍 Scanning for Florida R&D jobs..."
python3 scripts/job_hunter.py scan --location florida --remote-ok

# Format results for Telegram
MATCHES=$(python3 << 'EOF'
import json
with open('data/job_matches.json', 'r') as f:
    data = json.load(f)

high = [j for j in data.get('jobs', []) if j.get('match_score', 0) >= 8]
medium = [j for j in data.get('jobs', []) if 6 <= j.get('match_score', 0) < 8]

msg = f"💼 **Daily Job Matches** ({len(data.get('jobs', []))} found)\n\n"

if high:
    msg += f"**🔥 Strong Matches ({len(high)}):**\n"
    for job in high[:3]:
        msg += f"• {job['title']} at {job['company']}\n"
        msg += f"  📍 {job['location']} | 💰 {job.get('salary', 'Not listed')}\n"
        msg += f"  🔗 {job['url']}\n\n"

if medium:
    msg += f"**💚 Good Matches ({len(medium)}):**\n"
    for job in medium[:2]:
        msg += f"• {job['title']} at {job['company']}\n"
        msg += f"  📍 {job['location']}\n\n"

print(msg)
EOF
)

# Send to Telegram (via message tool or direct API call)
echo "$MATCHES"

# TODO: Integrate with Telegram delivery
# For now, log to file
echo "$(date): Job scan complete" >> ~/clawd/logs/job-automation.log
echo "$MATCHES" >> ~/clawd/logs/daily-jobs-$(date +%Y-%m-%d).txt
