#!/usr/bin/env python3
"""
Response Tracker - Track outcomes for each message variation
Records sends, opens, replies, conversions for A/B testing
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class ResponseTracker:
    def __init__(self, workspace_root: str = "/Users/clawdbot/clawd"):
        self.workspace = Path(workspace_root)
        self.sales_dir = self.workspace / "sales"
        self.sales_dir.mkdir(exist_ok=True)
        
        self.responses_file = self.sales_dir / "responses.jsonl"
    
    def log_send(
        self,
        message_id: str,
        lead: str,
        variation: str,
        approach: str,
        message_content: str
    ) -> Dict:
        """
        Log a message send
        
        Args:
            message_id: Unique message identifier
            lead: Lead username/identifier
            variation: Variation ID
            approach: Approach type (direct, personal_story, etc.)
            message_content: Full message text
        
        Returns:
            Logged entry
        """
        entry = {
            "message_id": message_id,
            "lead": lead,
            "variation": variation,
            "approach": approach,
            "sent_at": int(datetime.now().timestamp()),
            "sent_datetime": datetime.now().isoformat(),
            "message": message_content,
            "opened": False,
            "replied": False,
            "signup": False,
            "conversion": False,
            "open_time": None,
            "reply_time": None,
            "conversion_time": None
        }
        
        self._append_entry(entry)
        return entry
    
    def log_open(self, message_id: str):
        """Log when a message is opened/read"""
        self._update_entry(message_id, {
            "opened": True,
            "open_time": int(datetime.now().timestamp())
        })
    
    def log_reply(self, message_id: str, reply_content: Optional[str] = None):
        """Log when lead replies"""
        update = {
            "replied": True,
            "reply_time": int(datetime.now().timestamp())
        }
        
        if reply_content:
            update["reply_content"] = reply_content
        
        self._update_entry(message_id, update)
    
    def log_signup(self, message_id: str):
        """Log when lead signs up"""
        self._update_entry(message_id, {
            "signup": True,
            "conversion": True,
            "conversion_time": int(datetime.now().timestamp())
        })
    
    def log_conversion(self, message_id: str, conversion_type: str = "signup"):
        """Log any conversion event"""
        self._update_entry(message_id, {
            "conversion": True,
            "conversion_type": conversion_type,
            "conversion_time": int(datetime.now().timestamp())
        })
    
    def get_metrics(self, variation: Optional[str] = None, approach: Optional[str] = None) -> Dict:
        """
        Get metrics for a variation or approach
        
        Args:
            variation: Specific variation ID (optional)
            approach: Approach type (optional)
        
        Returns:
            Aggregated metrics
        """
        entries = self._load_entries()
        
        # Filter entries
        if variation:
            entries = [e for e in entries if e["variation"] == variation]
        if approach:
            entries = [e for e in entries if e["approach"] == approach]
        
        if not entries:
            return {
                "send_count": 0,
                "open_rate": 0,
                "reply_rate": 0,
                "signup_rate": 0,
                "conversion_rate": 0
            }
        
        total = len(entries)
        opened = len([e for e in entries if e.get("opened", False)])
        replied = len([e for e in entries if e.get("replied", False)])
        signups = len([e for e in entries if e.get("signup", False)])
        conversions = len([e for e in entries if e.get("conversion", False)])
        
        # Calculate time to reply
        reply_times = [
            e.get("reply_time", 0) - e["sent_at"]
            for e in entries
            if e.get("replied", False) and e.get("reply_time")
        ]
        avg_reply_time = sum(reply_times) / len(reply_times) if reply_times else 0
        
        return {
            "send_count": total,
            "open_count": opened,
            "reply_count": replied,
            "signup_count": signups,
            "conversion_count": conversions,
            "open_rate": opened / total if total > 0 else 0,
            "reply_rate": replied / total if total > 0 else 0,
            "signup_rate": signups / total if total > 0 else 0,
            "conversion_rate": conversions / total if total > 0 else 0,
            "avg_reply_time_seconds": avg_reply_time,
            "avg_reply_time_hours": avg_reply_time / 3600 if avg_reply_time > 0 else 0
        }
    
    def get_all_approach_metrics(self) -> Dict[str, Dict]:
        """Get metrics for all approaches"""
        entries = self._load_entries()
        approaches = set(e["approach"] for e in entries)
        
        return {
            approach: self.get_metrics(approach=approach)
            for approach in approaches
        }
    
    def get_leaderboard(self, metric: str = "reply_rate", min_sends: int = 5) -> List[Dict]:
        """
        Get leaderboard of approaches sorted by metric
        
        Args:
            metric: Metric to sort by (reply_rate, open_rate, conversion_rate)
            min_sends: Minimum sends required to be included
        
        Returns:
            Sorted list of approaches with metrics
        """
        all_metrics = self.get_all_approach_metrics()
        
        # Filter by minimum sends
        filtered = {
            approach: metrics
            for approach, metrics in all_metrics.items()
            if metrics["send_count"] >= min_sends
        }
        
        # Sort by metric
        leaderboard = sorted(
            [
                {"approach": approach, **metrics}
                for approach, metrics in filtered.items()
            ],
            key=lambda x: x.get(metric, 0),
            reverse=True
        )
        
        return leaderboard
    
    def _append_entry(self, entry: Dict):
        """Append entry to JSONL file"""
        with open(self.responses_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def _load_entries(self) -> List[Dict]:
        """Load all entries"""
        if not self.responses_file.exists():
            return []
        
        entries = []
        with open(self.responses_file, "r") as f:
            for line in f:
                entries.append(json.loads(line.strip()))
        
        return entries
    
    def _update_entry(self, message_id: str, updates: Dict):
        """Update an existing entry (re-write file)"""
        entries = self._load_entries()
        
        # Find and update entry
        found = False
        for entry in entries:
            if entry["message_id"] == message_id:
                entry.update(updates)
                found = True
                break
        
        if not found:
            print(f"Warning: Message {message_id} not found")
            return
        
        # Rewrite file
        with open(self.responses_file, "w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")


# CLI interface
if __name__ == "__main__":
    import sys
    
    tracker = ResponseTracker()
    
    if len(sys.argv) < 2:
        # Show overall metrics
        print("📊 Outreach Metrics\n")
        
        all_metrics = tracker.get_all_approach_metrics()
        
        if not all_metrics:
            print("No data yet. Start sending messages!")
            sys.exit(0)
        
        print(f"{'Approach':<20} {'Sends':<8} {'Opens':<8} {'Replies':<8} {'Signups':<8}")
        print("="*60)
        
        for approach, metrics in all_metrics.items():
            print(f"{approach:<20} {metrics['send_count']:<8} "
                  f"{metrics['open_rate']*100:>6.1f}% {metrics['reply_rate']*100:>6.1f}% "
                  f"{metrics['signup_rate']*100:>6.1f}%")
        
        print("\n🏆 Leaderboard (by reply rate, min 5 sends):\n")
        
        leaderboard = tracker.get_leaderboard("reply_rate", min_sends=5)
        
        for i, entry in enumerate(leaderboard, 1):
            print(f"{i}. {entry['approach']}: {entry['reply_rate']*100:.1f}% reply rate "
                  f"({entry['reply_count']}/{entry['send_count']})")
    
    else:
        command = sys.argv[1]
        
        if command == "send":
            # Log a send
            msg_id = sys.argv[2]
            lead = sys.argv[3]
            approach = sys.argv[4]
            tracker.log_send(msg_id, lead, f"{approach}_v1", approach, "Example message")
            print(f"✅ Logged send to {lead}")
        
        elif command == "reply":
            msg_id = sys.argv[2]
            tracker.log_reply(msg_id)
            print(f"✅ Logged reply for {msg_id}")
        
        elif command == "signup":
            msg_id = sys.argv[2]
            tracker.log_signup(msg_id)
            print(f"✅ Logged signup for {msg_id}")
