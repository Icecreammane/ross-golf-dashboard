#!/bin/bash

# 🚀 Golf Coaching Launch Script
# Run this when you're ready to post to Reddit

set -e

echo "🏌️  Golf Coaching Launch Script"
echo "================================"
echo ""

# Configuration
LANDING_PAGE_URL="${LANDING_PAGE_URL:-https://your-site.netlify.app}"
REDDIT_URL="https://old.reddit.com/r/golf/submit"
POST_FILE="$HOME/clawd/REDDIT-POST-FINAL.md"
MEMORY_FILE="$HOME/clawd/memory/$(date +%Y-%m-%d).md"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Verify landing page is accessible
echo "Step 1: Verifying landing page..."
if command -v curl &> /dev/null; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$LANDING_PAGE_URL" || echo "000")
    if [ "$HTTP_CODE" -eq 200 ]; then
        echo -e "${GREEN}✅ Landing page is live and accessible!${NC}"
    else
        echo -e "${RED}❌ Warning: Landing page returned HTTP $HTTP_CODE${NC}"
        echo "URL: $LANDING_PAGE_URL"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}⚠️  curl not found, skipping page verification${NC}"
fi
echo ""

# Step 2: Verify post is ready
echo "Step 2: Checking Reddit post file..."
if [ -f "$POST_FILE" ]; then
    echo -e "${GREEN}✅ Reddit post file found${NC}"
else
    echo -e "${RED}❌ Reddit post file not found: $POST_FILE${NC}"
    exit 1
fi
echo ""

# Step 3: Extract and display post body
echo "Step 3: Extracting post body..."
POST_BODY=$(sed -n '/^```markdown$/,/^```$/p' "$POST_FILE" | sed '1d;$d' | sed "s|\[YOUR_URL_HERE\]|$LANDING_PAGE_URL|g")

if [ -z "$POST_BODY" ]; then
    echo -e "${RED}❌ Could not extract post body from $POST_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Post body extracted and URL inserted${NC}"
echo ""

# Step 4: Copy post to clipboard
echo "Step 4: Copying post to clipboard..."
if command -v pbcopy &> /dev/null; then
    echo "$POST_BODY" | pbcopy
    echo -e "${GREEN}✅ Post copied to clipboard (Mac)${NC}"
elif command -v xclip &> /dev/null; then
    echo "$POST_BODY" | xclip -selection clipboard
    echo -e "${GREEN}✅ Post copied to clipboard (Linux)${NC}"
elif command -v clip.exe &> /dev/null; then
    echo "$POST_BODY" | clip.exe
    echo -e "${GREEN}✅ Post copied to clipboard (WSL)${NC}"
else
    echo -e "${YELLOW}⚠️  Clipboard tool not found. You'll need to copy manually.${NC}"
fi
echo ""

# Step 5: Display title options
echo "Step 5: Title options (choose one):"
echo ""
echo -e "${YELLOW}Option 1 (Recommended):${NC}"
grep -A 1 "Option 1: Value-First" "$POST_FILE" | tail -1 | sed 's/^```//'
echo ""
echo -e "${YELLOW}Option 2:${NC}"
grep -A 1 "Option 2: Question Hook" "$POST_FILE" | tail -1 | sed 's/^```//'
echo ""
echo -e "${YELLOW}Option 3:${NC}"
grep -A 1 "Option 3: Humble Approach" "$POST_FILE" | tail -1 | sed 's/^```//'
echo ""

# Step 6: Open Reddit in browser
echo "Step 6: Opening Reddit..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "$REDDIT_URL"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open "$REDDIT_URL" 2>/dev/null || sensible-browser "$REDDIT_URL" 2>/dev/null || echo "Please open: $REDDIT_URL"
else
    echo "Please open: $REDDIT_URL"
fi
echo -e "${GREEN}✅ Reddit opened${NC}"
echo ""

# Step 7: Set reminder (macOS only for now)
echo "Step 7: Setting 2-hour reminder..."
REMINDER_TIME=$(date -v+2H +"%I:%M %p" 2>/dev/null || date -d "+2 hours" +"%I:%M %p" 2>/dev/null || echo "2 hours from now")

if [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e "display notification \"Time to check your r/golf post comments!\" with title \"Golf Coaching Launch\" sound name \"default\"" 2>/dev/null &
    
    # Create a background job to remind in 2 hours
    (sleep 7200 && osascript -e 'display notification "Check your Reddit post now! First 2 hours are critical." with title "⏰ Golf Launch Reminder"' 2>/dev/null) &
    
    echo -e "${GREEN}✅ Reminder set for $REMINDER_TIME${NC}"
else
    echo -e "${YELLOW}⚠️  Auto-reminder only supported on macOS. Set a manual reminder for $REMINDER_TIME${NC}"
fi
echo ""

# Step 8: Log launch to memory
echo "Step 8: Logging launch..."
mkdir -p "$(dirname "$MEMORY_FILE")"

cat >> "$MEMORY_FILE" << EOF

## 🚀 Golf Coaching Launch - $(date +"%I:%M %p")

**Action:** Posted to r/golf
**Landing page:** $LANDING_PAGE_URL
**Post URL:** (paste here after posting)

**Metrics to track:**
- [ ] Upvotes after 1 hour: ___
- [ ] Comments after 1 hour: ___
- [ ] Form submissions after 1 hour: ___
- [ ] Upvotes after 24 hours: ___
- [ ] Total form submissions: ___
- [ ] Paying customers: ___

**Notes:**
- Check post every 5-10 minutes for first 2 hours
- Respond to EVERY comment
- Update landing page if common questions emerge

EOF

echo -e "${GREEN}✅ Launch logged to $MEMORY_FILE${NC}"
echo ""

# Step 9: Display response templates
echo "Step 9: Opening response templates..."
if command -v open &> /dev/null; then
    open "$HOME/clawd/REDDIT-POST-FINAL.md"
else
    echo "Response templates: $HOME/clawd/REDDIT-POST-FINAL.md"
fi
echo ""

# Final instructions
echo "================================"
echo -e "${GREEN}🎯 YOU'RE READY TO LAUNCH!${NC}"
echo "================================"
echo ""
echo "Next steps:"
echo "1. ✅ Post body is in your clipboard - paste it into Reddit"
echo "2. ✅ Choose one of the title options above"
echo "3. ✅ Use 'Discussion' flair (not Promotion)"
echo "4. ✅ Hit POST and start engaging!"
echo ""
echo "Remember:"
echo "- Respond to EVERY comment in first 2 hours"
echo "- Be humble, not salesy"
echo "- Check back at $REMINDER_TIME"
echo ""
echo "Good luck! 🏌️"
echo ""

# Optional: Wait for user to confirm post
read -p "Press ENTER after you've posted to continue..." 

# Ask for post URL
read -p "Paste your Reddit post URL here: " POST_URL

if [ -n "$POST_URL" ]; then
    sed -i.bak "s|Post URL:.*|Post URL: $POST_URL|" "$MEMORY_FILE"
    echo -e "${GREEN}✅ Post URL saved to memory${NC}"
    
    # Open the post in browser
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "$POST_URL"
    fi
fi

echo ""
echo "✨ Launch complete! Now go engage with comments!"
echo ""
