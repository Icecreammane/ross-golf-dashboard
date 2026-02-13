# FOOD LOGGING PROTOCOL

## Core Rule
**Ross logs food ONCE. I never ask him to repeat it.**

## When Food Comes In

### 1. Photo Received (via Telegram)
**Immediate action:**
1. Analyze photo with vision model
2. Extract description + macros
3. Log to `fitness_data.json` with timestamp
4. Confirm logged: "✅ Logged: [description] | [cal] cal | [protein]g P"

**Never:**
- Say "I'll log that later"
- Ask for details (estimate from photo)
- Wait for explicit "log this" command

### 2. Text Description Received
**Examples:**
- "Chicken wraps for lunch"
- "Had a banana"
- "Chipotle burrito"

**Immediate action:**
1. Extract food item
2. Estimate reasonable macros
3. Log with current timestamp
4. Confirm logged

### 3. Voice Message About Food
**Immediate action:**
1. Transcribe voice
2. Extract food items
3. Log each item
4. Confirm logged

## Photo Storage Structure
```
~/.clawdbot/media/inbound/[uuid].jpg
```

**Photos include timestamp in file metadata** - use `ls -lh` to get timestamp

## Daily Audit (During Heartbeat)
1. Check for new photos in media/inbound from today
2. Cross-reference with logged meals
3. If photo exists without corresponding log → analyze and log immediately
4. Alert if food mentioned in conversation but not logged

## Macro Estimation Guidelines
When exact info unavailable, use these standards:

### Proteins:
- Chicken breast (4oz): 180 cal, 35g P
- Ground beef (4oz): 240 cal, 22g P
- Fish (4oz): 140 cal, 28g P
- Eggs (2 large): 140 cal, 12g P

### Carbs:
- Rice (1 cup): 200 cal, 4g P, 45g C
- Pasta (1 cup): 220 cal, 8g P, 43g C
- Bread (2 slices): 160 cal, 6g P, 30g C
- Banana: 105 cal, 1g P, 27g C

### Common Meals:
- Chipotle burrito: 1000-1600 cal, 50-75g P
- Pizza (2 slices): 550-700 cal, 24-32g P
- Sub sandwich: 600-1200 cal, 30-50g P
- Wraps (chicken, 2): 500-600 cal, 40-50g P

## Error Recovery
If I miss a meal:
1. Search photos by date
2. Search conversation history for food mentions
3. Analyze and log immediately
4. Update this protocol if gap identified

## Never Ask Ross To:
- Re-send photos
- Re-describe meals
- Clarify what he ate (estimate from context)
- Confirm macros (estimate reasonable values)

## Automation
**Script: `scripts/auto_food_logger.py`**
- Monitors media/inbound every 5 minutes
- Auto-analyzes food photos
- Logs to tracker
- Runs during heartbeats

## Quality Standards
- Description must be specific (not "NO DESC")
- Calories must be non-zero
- Protein estimate required
- Time from photo metadata or current time

## This Protocol Prevents
- Missing days (Feb 3-12 issue)
- Empty descriptions (Feb 10 "NO DESC" issue)
- Asking Ross to repeat himself
- Logging friction

---

**Last updated:** 2026-02-12 22:20 CST
