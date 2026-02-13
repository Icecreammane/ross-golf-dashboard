#!/usr/bin/env python3
"""
Cost-aware wrapper for spawning sub-agents with optimal model selection
Usage: python3 cost_aware_wrapper.py "<task_description>"
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path.home() / "clawd" / "scripts"))
from jarvis_helpers import smart_route

def main():
    if len(sys.argv) < 2:
        print("Usage: cost_aware_wrapper.py '<task_description>'")
        sys.exit(1)
    
    task = sys.argv[1]
    
    # Route to best model
    model = smart_route(task)
    
    # Output for integration
    result = {
        'task': task,
        'recommended_model': model,
        'spawn_command': f'sessions_spawn with model={model}'
    }
    
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
