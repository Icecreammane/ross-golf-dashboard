#!/usr/bin/env python3
"""
Quick test script demonstrating YouTube transcript functionality for Jarvis.
"""

import sys
import importlib.util
from pathlib import Path

# Load integration module
integration_path = Path(__file__).parent / "youtube-integration.py"
spec = importlib.util.spec_from_file_location("youtube_integration", integration_path)
youtube_integration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(youtube_integration)

def test_workflow():
    """Demonstrate the complete workflow."""
    
    print("=" * 80)
    print("YOUTUBE TRANSCRIPT READER - DEMONSTRATION")
    print("=" * 80)
    
    # Test 1: Auto-detect URLs
    print("\n[TEST 1] Auto-detecting YouTube URLs in messages")
    print("-" * 80)
    message = "Check out https://www.youtube.com/watch?v=dQw4w9WgXcQ and https://youtu.be/jNQXAC9IVRw"
    urls = youtube_integration.detect_youtube_url(message)
    print(f"Message: {message}")
    print(f"Found {len(urls)} URL(s): {urls}")
    
    # Test 2: Quick fetch
    print("\n[TEST 2] Quick transcript fetch")
    print("-" * 80)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    print(f"Fetching: {test_url}")
    result = youtube_integration.quick_fetch(test_url)
    if result['success']:
        print(f"✓ Success!")
        print(f"  Video ID: {result['video_id']}")
        print(f"  Duration: {result['duration_minutes']} minutes")
        print(f"  Transcript length: {len(result['transcript'])} characters")
        print(f"  First 200 chars: {result['transcript'][:200]}...")
    else:
        print(f"✗ Failed: {result['error']}")
    
    # Test 3: Summarization workflow
    print("\n[TEST 3] Summarization workflow")
    print("-" * 80)
    result = youtube_integration.summarize_youtube(test_url)
    if result['success']:
        print(f"✓ Ready for AI summarization!")
        print(f"  Video: {result['video_id']} ({result['duration_minutes']} min)")
        print(f"  Prompt length: {len(result['summary_prompt'])} chars")
        print(f"  [This prompt can now be passed to Claude/GPT for summarization]")
    else:
        print(f"✗ Failed: {result['error']}")
    
    # Test 4: Error handling
    print("\n[TEST 4] Error handling (video without captions)")
    print("-" * 80)
    no_captions_url = "https://www.youtube.com/live/UpM2H83MJO8"
    print(f"Fetching: {no_captions_url}")
    result = youtube_integration.quick_fetch(no_captions_url)
    if result['success']:
        print(f"✓ Success (unexpected)")
    else:
        print(f"✓ Graceful failure (expected)")
        print(f"  Error: {result['error']}")
        print(f"  [System handled error properly without crashing]")
    
    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)
    print("\nJarvis can now:")
    print("  • Auto-detect YouTube URLs in messages")
    print("  • Fetch transcripts quickly (with 24h caching)")
    print("  • Prepare prompts for AI summarization")
    print("  • Extract implementation details from tutorials")
    print("  • Handle errors gracefully")
    print("\nUsage: Just say 'watch this video: [URL]' or 'summarize [URL]'")
    print("=" * 80)

if __name__ == "__main__":
    test_workflow()
