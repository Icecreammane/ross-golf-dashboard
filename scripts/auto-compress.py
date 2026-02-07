#!/usr/bin/env python3
"""
Auto-compress context when token count exceeds threshold.
Called by main agent to manage memory efficiently.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Import the compressor we built earlier
sys.path.append(str(Path(__file__).parent))
from compress_context import compress_context

def should_compress(current_tokens, threshold=50000):
    """Check if we should compress based on token count."""
    return current_tokens >= threshold

def compress_and_save(session_file, output_dir="/Users/clawdbot/clawd/memory/compressed"):
    """
    Compress session and save summary.
    
    Returns:
        {
            "compressed": bool,
            "summary_file": str,
            "tokens_saved": int,
            "new_context": list (preserved messages)
        }
    """
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load session messages
    messages = []
    try:
        with open(session_file, 'r') as f:
            for line in f:
                try:
                    msg = json.loads(line)
                    messages.append(msg)
                except:
                    continue
    except Exception as e:
        return {
            "compressed": False,
            "error": str(e)
        }
    
    # Compress
    result = compress_context(messages)
    
    if not result.get('compressed'):
        return result
    
    # Save summary
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    summary_file = output_path / f"summary_{timestamp}.md"
    
    with open(summary_file, 'w') as f:
        f.write(f"# Context Compression Summary\n\n")
        f.write(f"**Compressed:** {result['timestamp']}\n\n")
        f.write(f"**Original messages:** {result['original_count']}\n")
        f.write(f"**Preserved messages:** {result['compressed_count']}\n")
        f.write(f"**Tokens saved:** ~{result['tokens_saved']}\n")
        f.write(f"**Compression ratio:** {result['compression_ratio']}\n\n")
        f.write("---\n\n")
        f.write(result['summary'])
    
    result['summary_file'] = str(summary_file)
    return result

def get_compression_hint(tokens_saved, compression_ratio):
    """Generate user-friendly hint about compression."""
    if tokens_saved < 10000:
        return "Minor compression applied."
    elif tokens_saved < 30000:
        return f"Compressed context by {compression_ratio} (~${tokens_saved * 0.000015:.2f} saved)."
    else:
        return f"Major compression! Saved {compression_ratio} of context (~${tokens_saved * 0.000015:.2f})."

# Integration function for main agent
def check_and_compress_if_needed(current_tokens, session_file):
    """
    Main integration point. Call this periodically from agent.
    
    Usage in main agent:
        if message_count % 50 == 0:  # Check every 50 messages
            result = check_and_compress_if_needed(current_tokens, session_file)
            if result.get('compressed'):
                # Inform user
                print(result['hint'])
    """
    
    if not should_compress(current_tokens):
        return {
            "compressed": False,
            "current_tokens": current_tokens,
            "threshold": 50000
        }
    
    result = compress_and_save(session_file)
    
    if result.get('compressed'):
        result['hint'] = get_compression_hint(
            result['tokens_saved'],
            result['compression_ratio']
        )
    
    return result

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: auto-compress.py <current_tokens> <session_file>")
        sys.exit(1)
    
    current_tokens = int(sys.argv[1])
    session_file = sys.argv[2]
    
    result = check_and_compress_if_needed(current_tokens, session_file)
    print(json.dumps(result, indent=2))
