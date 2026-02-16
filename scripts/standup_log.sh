#!/bin/bash
# Daily standup log template generator
# Usage: bash scripts/standup_log.sh

DATE=$(date +%Y-%m-%d)
DAY=$(date +%A)
LOG_FILE="/Users/clawdbot/clawd/memory/$DATE.md"

cat > "$LOG_FILE" << 'EOF'
# [DATE] ([DAY])

## 🚀 Shipped
- 

## 🚧 Blocked / In Progress
- 

## 🎯 Next
- 

## 💡 Key Decisions / Learnings
- 

## 📊 Stats
- Sessions: 
- Builds: 
- Cost: 

---
**Target: ~60 lines max. Standup format, not documentation.**
EOF

# Replace placeholders
sed -i '' "s/\[DATE\]/$DATE/g" "$LOG_FILE"
sed -i '' "s/\[DAY\]/$DAY/g" "$LOG_FILE"

echo "✅ Standup log created: $LOG_FILE"
echo "Keep it concise (~60 lines). Log outcomes, not process."
