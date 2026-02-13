#!/usr/bin/env python3
"""Quick test of updated task generator with routing"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "clawd" / "scripts"))

from jarvis_helpers import smart_route

# Test what model would be used
model = smart_route("Generate 4-5 daily tasks based on goals and recent progress")
print(f"✅ Task generation would use: {model}")
print(f"   (Original: gpt-4o)")
print(f"   Savings: {'FREE!' if 'local' in model else 'Significant'}")
