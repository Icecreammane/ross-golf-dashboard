#!/usr/bin/env python3
"""
Log income to Florida Fund
Usage: python3 log_income.py <amount> <source>
Example: python3 log_income.py 500 "Fantasy sports winnings"
"""

import json
import sys
from datetime import datetime
from pathlib import Path

DATA_FILE = Path.home() / "clawd" / "florida-fund-data.json"

def log_income(amount, source):
    """Add income to the Florida Fund"""
    # Load existing data
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
    
    # Add new income
    data['total_saved'] += amount
    data['monthly_income'] += amount  # Simplified - would track per month
    data['income_history'].insert(0, {
        'amount': amount,
        'source': source,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'timestamp': datetime.now().isoformat()
    })
    
    # Keep only last 10 entries in history
    data['income_history'] = data['income_history'][:10]
    
    # Save updated data
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Logged ${amount} from {source}")
    print(f"📊 Total saved: ${data['total_saved']:,} / ${data['goal']:,}")
    print(f"🎯 Progress: {(data['total_saved'] / data['goal'] * 100):.1f}%")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 log_income.py <amount> <source>")
        print('Example: python3 log_income.py 500 "Fantasy sports"')
        sys.exit(1)
    
    amount = float(sys.argv[1])
    source = " ".join(sys.argv[2:])
    log_income(amount, source)
