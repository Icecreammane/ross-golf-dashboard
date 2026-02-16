#!/usr/bin/env python3
"""Quick dashboard update for gym demo"""
import json
from datetime import datetime
from pathlib import Path

workspace = Path.home() / "clawd"
data_file = workspace / "dashboard-data.json"

# Read current data or create new
try:
    with open(data_file) as f:
        data = json.load(f)
except:
    data = {}

# Update with today's progress
data.update({
    "last_updated": datetime.now().isoformat(),
    "builds_today": 4,
    "builds_active": 2,
    "builds_queued": 3,
    "local_models_enabled": True,
    "local_models": ["llama3.1:8b", "qwen2.5:14b"],
    "cost_today": 4.50,
    "cost_saved_local": 10.50,
    "gym_demo_active": True
})

with open(data_file, "w") as f:
    json.dump(data, f, indent=2)

print("✅ Dashboard data updated")
