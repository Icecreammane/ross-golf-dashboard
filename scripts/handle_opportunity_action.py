#!/usr/bin/env python3
"""
Opportunity Action Handler

Processes button clicks from Telegram:
- opp_approve_{id} → Send the response
- opp_reject_{id} → Mark as rejected, save for learning
- opp_edit_{id} → Prompt for edits
- opp_snooze_{id} → Re-queue for later

Also logs feedback for learning system.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path.home() / "clawd" / "scripts"))
from opportunity_scanner import OpportunityQueue
from opportunity_drafter import save_feedback

def handle_action(callback_data):
    """Process button callback"""
    parts = callback_data.split("_")
    if len(parts) < 3:
        return {"error": "Invalid callback data"}
    
    action = parts[1]  # approve, reject, edit, snooze
    opp_id = "_".join(parts[2:])  # Reconstruct ID
    
    queue = OpportunityQueue()
    
    # Find opportunity
    opp = None
    for o in queue.opportunities:
        if o.id == opp_id:
            opp = o
            break
    
    if not opp:
        return {"error": f"Opportunity {opp_id} not found"}
    
    if action == "approve":
        # Mark as approved
        queue.update_status(opp_id, "approved")
        
        # Save feedback for learning
        save_feedback(opp_id, "approved", opp.draft)
        
        # TODO: Actually send the response via appropriate channel
        # For now, just log it
        response = {
            "success": True,
            "action": "approved",
            "message": f"✅ Response approved! (Sending via {opp.source} would happen here)",
            "opp_title": opp.title
        }
        
    elif action == "reject":
        # Mark as rejected
        queue.update_status(opp_id, "rejected")
        
        # Save feedback for learning
        save_feedback(opp_id, "rejected", opp.draft)
        
        response = {
            "success": True,
            "action": "rejected",
            "message": f"❌ Opportunity rejected. Feedback saved for learning.",
            "opp_title": opp.title
        }
        
    elif action == "edit":
        # Prompt for edit (for now, just acknowledge)
        response = {
            "success": True,
            "action": "edit",
            "message": f"✏️ Reply with your edited version and I'll save it.",
            "current_draft": opp.draft,
            "opp_id": opp_id
        }
        
    elif action == "snooze":
        # Reset to pending
        queue.update_status(opp_id, "pending")
        
        response = {
            "success": True,
            "action": "snoozed",
            "message": f"💤 Opportunity snoozed. Will resurface later.",
            "opp_title": opp.title
        }
        
    else:
        response = {"error": f"Unknown action: {action}"}
    
    return response

def main():
    """Test handler"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 handle_opportunity_action.py <callback_data>")
        sys.exit(1)
    
    callback_data = sys.argv[1]
    result = handle_action(callback_data)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
