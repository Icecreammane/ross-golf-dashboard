#!/usr/bin/env python3
"""
Quick viewer for email summaries
"""

import json
from pathlib import Path
from datetime import datetime

DATA_FILE = Path("/Users/clawdbot/clawd/data/email-summary.json")

def main():
    if not DATA_FILE.exists():
        print("📭 No email summaries yet")
        print(f"File will be created at: {DATA_FILE}")
        return
    
    try:
        with open(DATA_FILE) as f:
            summaries = json.load(f)
    except Exception as e:
        print(f"❌ Error reading summaries: {e}")
        return
    
    if not summaries:
        print("📭 No important emails found yet")
        return
    
    print(f"📧 {len(summaries)} Important Email(s)\n")
    print("=" * 80)
    
    # Show most recent first
    for i, email in enumerate(reversed(summaries[-20:]), 1):  # Last 20
        timestamp = email.get('timestamp', 'unknown')
        try:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime("%Y-%m-%d %H:%M")
        except:
            time_str = timestamp
        
        print(f"\n{i}. {email['subject']}")
        print(f"   From: {email['sender']} <{email.get('from_email', '')}>")
        print(f"   Time: {time_str}")
        print(f"   Reason: {email['importance_reason']}")
        
        if email.get('key_points'):
            print(f"   Key Points:")
            for point in email['key_points'][:3]:
                if point.strip():
                    print(f"     • {point[:100]}")
        
        preview = email.get('preview', '')
        if preview:
            print(f"   Preview: {preview[:150]}...")
    
    print("\n" + "=" * 80)
    print(f"\nTotal: {len(summaries)} important emails tracked")
    print(f"Showing: Most recent {min(20, len(summaries))}")

if __name__ == "__main__":
    main()
