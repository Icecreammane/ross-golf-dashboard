#!/bin/bash
# YouTube Transcript Fetcher
# Quick CLI tool for fetching YouTube transcripts

if [ -z "$1" ]; then
    echo "Usage: ./youtube-transcript.sh <YouTube URL>"
    echo ""
    echo "Examples:"
    echo "  ./youtube-transcript.sh https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    echo "  ./youtube-transcript.sh https://youtu.be/dQw4w9WgXcQ"
    echo "  ./youtube-transcript.sh https://www.youtube.com/live/UpM2H83MJO8"
    exit 1
fi

# Run the Python module
python3 ~/clawd/systems/youtube-reader.py "$1"
