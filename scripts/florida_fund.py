#!/usr/bin/env python3
"""
Florida Fund Income Tracker
Manage income logs for the Florida Freedom Fund
"""

import json
import sys
from datetime import datetime
from pathlib import Path

DATA_FILE = Path.home() / "clawd" / "data" / "florida-fund.json"

def load_data():
    """Load Florida Fund data"""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        "total_saved": 0,
        "monthly_income": 0,
        "goal": 50000,
        "income_history": [],
        "last_updated": datetime.now().isoformat()
    }

def save_data(data):
    """Save Florida Fund data"""
    data['last_updated'] = datetime.now().isoformat()
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_income(source, amount, date=None):
    """Add income to the fund"""
    data = load_data()
    
    entry = {
        "source": source,
        "amount": float(amount),
        "date": date or datetime.now().isoformat()
    }
    
    data['income_history'].append(entry)
    data['total_saved'] += float(amount)
    
    # Recalculate monthly income (last 30 days)
    thirty_days_ago = datetime.now().timestamp() - (30 * 24 * 60 * 60)
    recent_income = [
        item for item in data['income_history']
        if datetime.fromisoformat(item['date']).timestamp() > thirty_days_ago
    ]
    data['monthly_income'] = sum(item['amount'] for item in recent_income)
    
    save_data(data)
    
    progress = (data['total_saved'] / data['goal']) * 100
    print(f"✅ Added ${amount:,.2f} from {source}")
    print(f"💰 Total saved: ${data['total_saved']:,.2f} ({progress:.1f}%)")
    print(f"🎯 Remaining: ${data['goal'] - data['total_saved']:,.2f}")
    
    return data

def get_status():
    """Get current status"""
    data = load_data()
    progress = (data['total_saved'] / data['goal']) * 100
    remaining = data['goal'] - data['total_saved']
    
    print("🌴 FLORIDA FREEDOM FUND")
    print("=" * 50)
    print(f"Total Saved:     ${data['total_saved']:>12,.2f}")
    print(f"Goal:            ${data['goal']:>12,.2f}")
    print(f"Remaining:       ${remaining:>12,.2f}")
    print(f"Progress:        {progress:>12.1f}%")
    print(f"Monthly Income:  ${data['monthly_income']:>12,.2f}")
    
    if data['monthly_income'] > 0:
        months_remaining = remaining / data['monthly_income']
        print(f"Est. Timeline:   {months_remaining:>12.1f} months")
    
    print(f"\nTotal entries: {len(data['income_history'])}")
    
    return data

def list_income(limit=10):
    """List recent income entries"""
    data = load_data()
    
    if not data['income_history']:
        print("No income logged yet")
        return
    
    print(f"\n📈 Recent Income (last {limit}):")
    print("-" * 60)
    
    sorted_history = sorted(
        data['income_history'],
        key=lambda x: x['date'],
        reverse=True
    )[:limit]
    
    for entry in sorted_history:
        date = datetime.fromisoformat(entry['date']).strftime('%Y-%m-%d')
        print(f"{date}  {entry['source']:<30}  +${entry['amount']:>10,.2f}")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 florida_fund.py status")
        print("  python3 florida_fund.py add <source> <amount> [date]")
        print("  python3 florida_fund.py list [limit]")
        print("\nExamples:")
        print("  python3 florida_fund.py add 'Freelance Project' 1500")
        print("  python3 florida_fund.py add 'App Revenue' 250.50")
        print("  python3 florida_fund.py list 20")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "status":
        get_status()
    elif command == "add":
        if len(sys.argv) < 4:
            print("Error: 'add' requires source and amount")
            sys.exit(1)
        source = sys.argv[2]
        amount = float(sys.argv[3])
        date = sys.argv[4] if len(sys.argv) > 4 else None
        add_income(source, amount, date)
    elif command == "list":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        list_income(limit)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
