#!/usr/bin/env python3
"""
Compress conversation context to reduce token usage.
Extracts key decisions, facts, and action items. Discards verbose back-and-forth.
"""

import json
import sys
from datetime import datetime

def compress_context(messages, threshold_tokens=50000):
    """
    Compress message history when it exceeds threshold.
    
    Args:
        messages: List of message dicts with 'role', 'content', 'timestamp'
        threshold_tokens: When to trigger compression (default 50k)
    
    Returns:
        {
            "compressed": True/False,
            "original_count": int,
            "compressed_count": int,
            "summary": str,
            "preserved_messages": [...],
            "tokens_saved": int (estimate)
        }
    """
    
    # Rough estimate: 1 token ≈ 4 characters
    total_chars = sum(len(str(m.get('content', ''))) for m in messages)
    estimated_tokens = total_chars // 4
    
    if estimated_tokens < threshold_tokens:
        return {
            "compressed": False,
            "original_count": len(messages),
            "estimated_tokens": estimated_tokens,
            "reason": f"Below threshold ({estimated_tokens} < {threshold_tokens})"
        }
    
    # Extract key information types
    decisions = []
    action_items = []
    builds_completed = []
    preferences_stated = []
    important_facts = []
    
    for msg in messages:
        content = str(msg.get('content', '')).lower()
        
        # Decision indicators
        if any(word in content for word in ['decided', 'agreed', 'let\'s do', 'go with', 'approved']):
            decisions.append(msg)
        
        # Action items
        if any(word in content for word in ['build', 'implement', 'fix', 'create', 'add']):
            action_items.append(msg)
        
        # Completions
        if any(word in content for word in ['complete', 'finished', 'done', 'ready', 'shipped']):
            builds_completed.append(msg)
        
        # Preferences
        if any(word in content for word in ['prefer', 'want', 'like', 'hate', 'always', 'never']):
            preferences_stated.append(msg)
        
        # Important facts (numbers, dates, specific details)
        if any(word in content for word in ['goal', 'target', 'deadline', 'cost', '$', 'calorie']):
            important_facts.append(msg)
    
    # Build compression summary
    summary_parts = []
    
    if decisions:
        summary_parts.append(f"**Decisions Made ({len(decisions)}):**")
        for d in decisions[-5:]:  # Last 5 decisions
            summary_parts.append(f"  - {d.get('content', '')[:200]}")
    
    if builds_completed:
        summary_parts.append(f"\n**Builds Completed ({len(builds_completed)}):**")
        for b in builds_completed[-5:]:
            summary_parts.append(f"  - {b.get('content', '')[:200]}")
    
    if preferences_stated:
        summary_parts.append(f"\n**Preferences Noted ({len(preferences_stated)}):**")
        for p in preferences_stated[-5:]:
            summary_parts.append(f"  - {p.get('content', '')[:200]}")
    
    if important_facts:
        summary_parts.append(f"\n**Key Facts ({len(important_facts)}):**")
        for f in important_facts[-5:]:
            summary_parts.append(f"  - {f.get('content', '')[:200]}")
    
    summary = "\n".join(summary_parts)
    
    # Preserve last N messages (most recent context)
    preserve_count = 20
    preserved = messages[-preserve_count:]
    
    # Calculate savings
    preserved_chars = sum(len(str(m.get('content', ''))) for m in preserved) + len(summary)
    saved_chars = total_chars - preserved_chars
    tokens_saved = saved_chars // 4
    
    return {
        "compressed": True,
        "original_count": len(messages),
        "compressed_count": preserve_count,
        "summary": summary,
        "preserved_messages": preserved,
        "tokens_saved": tokens_saved,
        "compression_ratio": f"{(tokens_saved / estimated_tokens * 100):.1f}%",
        "timestamp": datetime.now().isoformat()
    }

def main():
    """CLI interface for testing."""
    if len(sys.argv) < 2:
        print("Usage: python3 compress-context.py <session-file.jsonl>")
        sys.exit(1)
    
    session_file = sys.argv[1]
    
    # Load messages
    messages = []
    with open(session_file, 'r') as f:
        for line in f:
            try:
                msg = json.loads(line)
                messages.append(msg)
            except:
                continue
    
    result = compress_context(messages)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
