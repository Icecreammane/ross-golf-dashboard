#!/usr/bin/env python3
"""
Send Drafted Opportunities to Ross via Telegram

Creates notification with inline buttons for approval/rejection.
Called by daemon or manually to send batch of opportunities.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "clawd" / "scripts"))
from opportunity_scanner import OpportunityQueue

def format_opportunity_message(opp):
    """Format opportunity as Telegram message"""
    emoji_map = {
        "reddit": "🔴",
        "twitter": "🐦",
        "email": "📧"
    }
    
    emoji = emoji_map.get(opp.source, "💼")
    
    message = f"""{emoji} **NEW OPPORTUNITY**

**{opp.title}**
Source: {opp.source} | Score: {opp.score}/100

**Context:**
{opp.context[:300]}{"..." if len(opp.context) > 300 else ""}

**DRAFTED RESPONSE:**
{opp.draft}

---
Tap a button to respond:"""
    
    return message

def create_approval_buttons(opp_id):
    """Create inline buttons for opportunity approval"""
    # Button format for Clawdbot: [{text, callback_data}]
    buttons = [
        [
            {"text": "✅ Approve & Send", "callback_data": f"opp_approve_{opp_id}"},
            {"text": "❌ Reject", "callback_data": f"opp_reject_{opp_id}"}
        ],
        [
            {"text": "✏️ Edit Draft", "callback_data": f"opp_edit_{opp_id}"},
            {"text": "💤 Snooze", "callback_data": f"opp_snooze_{opp_id}"}
        ]
    ]
    return buttons

def main():
    """Send drafted opportunities to Ross"""
    queue = OpportunityQueue()
    drafted = [opp for opp in queue.opportunities if opp.status == "drafted"]
    
    if not drafted:
        print("No drafted opportunities to send")
        return
    
    print(f"Found {len(drafted)} drafted opportunities")
    
    # Output as JSON for message tool to consume
    for opp in drafted[:5]:  # Send max 5 at a time
        notification = {
            "message": format_opportunity_message(opp),
            "buttons": create_approval_buttons(opp.id)
        }
        
        print(json.dumps(notification))
        print("---SEPARATOR---")  # Delimiter between notifications

if __name__ == "__main__":
    main()
