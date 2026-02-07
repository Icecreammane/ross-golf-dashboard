# Headless Notion Configuration

**Status:** Design phase (ready to build by Feb 3)

## DATABASE SCHEMA: "Jarvis Brain"

### Properties:
```
Title (Text) - What to remember
Content (Rich Text) - Full note content
Category (Select)
  - Goal
  - Insight
  - Idea
  - Task
  - Contact
  - Learning
  - Opportunity
  - Reference
Priority (Select)
  - Low
  - Medium
  - High
Date Created (Date) - Auto-set
Date Referenced (Date) - Updates when linked
Tags (Multi-select) - Auto-generated from content
Status (Select)
  - Active
  - Archive
  - Done
URL (URL) - Optional link reference
Related (Relation) - Links to other notes
```

## CAPTURE TRIGGERS (Telegram)

Listen for these patterns:

1. `"Remember: [anything]"` → Title: [anything], Category: auto-detect
2. `"Hey Jarvis, remember [anything]"` → Same as above
3. `"Note: [anything]"` → Same
4. `"Store this: [anything]"` → Same
5. `"Add to brain: [anything]"` → Same

## AUTO-CATEGORIZATION LOGIC

Parse content for keywords:

```
IF contains (goal, target, want, achieve, build, create) → GOAL
IF contains (learned, found, insight, discovered, realize) → INSIGHT
IF contains (idea, concept, thought, maybe, potential) → IDEA
IF contains (do, task, complete, finish, action) → TASK
IF contains (person, contact, email, connect) → CONTACT
IF contains (study, learn, understand, explain) → LEARNING
IF contains (opportunity, chance, could, market) → OPPORTUNITY
ELSE → REFERENCE
```

## AUTO-TAGGING

Extract key terms:
- People names → #people
- Topics → #topic-name
- Tools/platforms → #tool
- Revenue/business → #revenue
- Fitness/health → #fitness
- Fantasy football → #fantasy
- Golf → #golf
- AI/learning → #ai

## NOTION API INTEGRATION

Required:
- Notion API token (from workspace settings)
- Database ID (from Jarvis Brain database URL)
- Webhook listener on Telegram messages

Flow:
1. Telegram detects trigger pattern
2. Parse message content
3. Auto-categorize + auto-tag
4. Create page in Notion
5. Confirm back to user: "✅ Stored: [title]"

## EXAMPLE FLOW

**User sends:** "Remember: Golf swing tempo is key to consistency"

**System:**
- Title: "Golf swing tempo is key to consistency"
- Category: LEARNING (keyword: "key")
- Content: Full message text
- Tags: #golf, #technique, #learning
- Status: Active
- Date Created: [today]

**Response back to user:** "✅ Stored: Golf swing tempo is key to consistency #golf #learning"

## IMPLEMENTATION PRIORITY

1. Set up Notion API connection
2. Create Jarvis Brain database (manual setup)
3. Build categorization logic
4. Build tag generator
5. Add Telegram listener
6. Test with 5 sample notes

Ready to build this week.
