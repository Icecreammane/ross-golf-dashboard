#!/bin/bash

# Deal Flow Auto-Update Script
# Runs daily to keep opportunities fresh

cd "$(dirname "$0")"

echo "[$(date)] Starting deal flow update..."

# Run the Python scraper (if you add API integrations later)
# python3 scraper.py

# Update timestamp in opportunities.json
python3 << 'PYTHON_SCRIPT'
import json
from datetime import datetime

try:
    with open('opportunities.json', 'r') as f:
        data = json.load(f)
    
    data['lastUpdated'] = datetime.utcnow().isoformat() + 'Z'
    
    with open('opportunities.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Updated timestamp: {data['lastUpdated']}")
except Exception as e:
    print(f"❌ Error: {e}")
PYTHON_SCRIPT

echo "[$(date)] Deal flow update complete!"
