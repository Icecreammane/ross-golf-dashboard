#!/usr/bin/env python3
"""
YouTube Integration for Jarvis
High-level functions for working with YouTube transcripts.
"""

import re
import sys
import importlib.util
from pathlib import Path

# Load youtube_reader module directly
reader_path = Path(__file__).parent / "youtube-reader.py"
spec = importlib.util.spec_from_file_location("youtube_reader", reader_path)
youtube_reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(youtube_reader)

get_youtube_transcript = youtube_reader.get_youtube_transcript


def detect_youtube_url(text):
    """
    Detect YouTube URLs in text.
    
    Returns:
        list: List of detected YouTube URLs
    """
    pattern = r'https?://(?:www\.)?(?:youtube\.com/(?:watch\?v=|live/|embed/)|youtu\.be/)[a-zA-Z0-9_-]{11}'
    return re.findall(pattern, text)


def summarize_youtube(url):
    """
    Get a YouTube transcript with key information for summarization.
    
    Args:
        url: YouTube URL
    
    Returns:
        dict: {
            "success": bool,
            "transcript": str,
            "summary_prompt": str,  # Ready-to-use prompt for AI summarization
            "video_id": str,
            "duration_minutes": int,
            "error": str  # only if success=False
        }
    """
    result = get_youtube_transcript(url, include_timestamps=True)
    
    if not result['success']:
        return {
            "success": False,
            "error": result['error'],
            "transcript": "",
            "summary_prompt": "",
            "video_id": "",
            "duration_minutes": 0
        }
    
    duration_minutes = result['duration'] // 60
    word_count = len(result['transcript'].split())
    
    summary_prompt = f"""Please summarize this YouTube video transcript.

Video ID: {result['video_id']}
Duration: {duration_minutes} minutes
Word count: {word_count}

Key points to extract:
- Main topic/theme
- Key concepts or ideas
- Important takeaways
- Any code examples or technical details

Transcript:
{result['transcript']}"""
    
    return {
        "success": True,
        "transcript": result['transcript'],
        "summary_prompt": summary_prompt,
        "video_id": result['video_id'],
        "duration_minutes": duration_minutes
    }


def implement_from_youtube(url, feature_name=""):
    """
    Extract implementation details from a YouTube video transcript.
    
    Args:
        url: YouTube URL
        feature_name: Optional - specific feature to focus on
    
    Returns:
        dict: {
            "success": bool,
            "transcript": str,
            "implementation_prompt": str,  # Ready-to-use prompt for AI
            "video_id": str,
            "error": str  # only if success=False
        }
    """
    result = get_youtube_transcript(url, include_timestamps=True)
    
    if not result['success']:
        return {
            "success": False,
            "error": result['error'],
            "transcript": "",
            "implementation_prompt": "",
            "video_id": ""
        }
    
    feature_context = f" focusing on: {feature_name}" if feature_name else ""
    
    implementation_prompt = f"""Please analyze this YouTube video transcript and extract implementation details{feature_context}.

Video ID: {result['video_id']}
Duration: {result['duration'] // 60} minutes

Extract:
1. Code examples or pseudocode
2. Architecture/design patterns mentioned
3. Technical concepts and how they're used
4. Step-by-step implementation instructions
5. Dependencies or tools mentioned
6. Best practices or gotchas

Transcript:
{result['transcript']}"""
    
    return {
        "success": True,
        "transcript": result['transcript'],
        "implementation_prompt": implementation_prompt,
        "video_id": result['video_id']
    }


def quick_fetch(url):
    """
    Quick fetch of transcript without timestamps (faster, cleaner).
    
    Returns:
        dict: Simple result with just success, transcript, and error
    """
    result = get_youtube_transcript(url, include_timestamps=False)
    return {
        "success": result['success'],
        "transcript": result.get('transcript', ''),
        "error": result.get('error', ''),
        "video_id": result.get('video_id', ''),
        "duration_minutes": result.get('duration', 0) // 60
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 youtube-integration.py summarize <URL>")
        print("  python3 youtube-integration.py implement <URL> [feature_name]")
        print("  python3 youtube-integration.py detect <text>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "detect":
        text = " ".join(sys.argv[2:])
        urls = detect_youtube_url(text)
        if urls:
            print(f"Found {len(urls)} YouTube URL(s):")
            for url in urls:
                print(f"  - {url}")
        else:
            print("No YouTube URLs found")
    
    elif command == "summarize":
        if len(sys.argv) < 3:
            print("Error: URL required")
            sys.exit(1)
        
        url = sys.argv[2]
        result = summarize_youtube(url)
        
        if result['success']:
            print(f"✓ Ready for summarization")
            print(f"Video: {result['video_id']}")
            print(f"Duration: {result['duration_minutes']} minutes")
            print(f"\nPrompt to use with AI:\n")
            print(result['summary_prompt'])
        else:
            print(f"✗ Error: {result['error']}")
            sys.exit(1)
    
    elif command == "implement":
        if len(sys.argv) < 3:
            print("Error: URL required")
            sys.exit(1)
        
        url = sys.argv[2]
        feature = sys.argv[3] if len(sys.argv) > 3 else ""
        result = implement_from_youtube(url, feature)
        
        if result['success']:
            print(f"✓ Ready for implementation extraction")
            print(f"Video: {result['video_id']}")
            print(f"\nPrompt to use with AI:\n")
            print(result['implementation_prompt'])
        else:
            print(f"✗ Error: {result['error']}")
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}")
        print("Valid commands: detect, summarize, implement")
        sys.exit(1)
