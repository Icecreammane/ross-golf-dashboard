#!/usr/bin/env python3
"""
CSV Transaction Import
Manual import from bank/credit card CSV exports
Works immediately - no API setup needed
"""

import os
import csv
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path.home() / "clawd" / "data"
TRANSACTIONS_FILE = DATA_DIR / "transactions.json"

def detect_csv_format(filepath):
    """Auto-detect bank CSV format"""
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        
        # Common bank formats
        if 'Transaction Date' in headers:
            return 'chase'
        elif 'Date' in headers and 'Description' in headers:
            return 'generic'
        else:
            return 'unknown'

def parse_chase_csv(filepath):
    """Parse Chase bank CSV format"""
    transactions = []
    
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            trans = {
                'transaction_id': f"csv_{row['Transaction Date']}_{row['Amount']}",
                'date': row['Transaction Date'],
                'amount': -float(row['Amount']),  # Chase uses negative for spending
                'merchant': row['Description'],
                'category': [categorize_transaction(row['Description'])],
                'account': 'Chase',
                'pending': False,
                'source': 'csv_import'
            }
            transactions.append(trans)
    
    return transactions

def parse_generic_csv(filepath):
    """Parse generic CSV format (Date, Description, Amount)"""
    transactions = []
    
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Try different amount field names
            amount_field = next((f for f in ['Amount', 'amount', 'Debit', 'Credit'] if f in row), None)
            
            if not amount_field:
                continue
            
            amount = float(row[amount_field].replace('$', '').replace(',', ''))
            
            trans = {
                'transaction_id': f"csv_{row['Date']}_{amount}",
                'date': row['Date'],
                'amount': -abs(amount) if amount > 0 else abs(amount),
                'merchant': row.get('Description', 'Unknown'),
                'category': [categorize_transaction(row.get('Description', ''))],
                'account': 'Imported',
                'pending': False,
                'source': 'csv_import'
            }
            transactions.append(trans)
    
    return transactions

def categorize_transaction(description):
    """Simple categorization based on merchant name"""
    desc_lower = description.lower()
    
    if any(x in desc_lower for x in ['doordash', 'uber eats', 'grubhub', 'restaurant', 'pizza', 'mcdonald', 'taco bell', 'chipotle']):
        return 'Dining Out'
    elif any(x in desc_lower for x in ['publix', 'kroger', 'whole foods', 'trader joe', 'grocery']):
        return 'Groceries'
    elif any(x in desc_lower for x in ['shell', 'exxon', 'chevron', 'gas', 'fuel']):
        return 'Gas & Transportation'
    elif any(x in desc_lower for x in ['netflix', 'spotify', 'hulu', 'disney', 'subscription']):
        return 'Subscriptions'
    elif any(x in desc_lower for x in ['amazon', 'target', 'walmart', 'best buy']):
        return 'Shopping'
    elif any(x in desc_lower for x in ['venmo', 'paypal', 'zelle', 'cash app']):
        return 'Transfers'
    else:
        return 'Other'

def load_existing_transactions():
    """Load existing transactions"""
    if TRANSACTIONS_FILE.exists():
        with open(TRANSACTIONS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_transactions(transactions):
    """Save transactions to file"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(TRANSACTIONS_FILE, 'w') as f:
        json.dump(transactions, f, indent=2)
    
    print(f"✅ Saved {len(transactions)} transactions to {TRANSACTIONS_FILE}")

def import_csv(filepath):
    """Import CSV and merge with existing transactions"""
    print(f"📂 Importing: {filepath}")
    
    # Detect format
    csv_format = detect_csv_format(filepath)
    print(f"Format detected: {csv_format}")
    
    # Parse based on format
    if csv_format == 'chase':
        new_transactions = parse_chase_csv(filepath)
    else:
        new_transactions = parse_generic_csv(filepath)
    
    print(f"📊 Parsed {len(new_transactions)} transactions")
    
    # Load existing
    existing = load_existing_transactions()
    existing_ids = {t['transaction_id'] for t in existing}
    
    # Deduplicate
    unique_new = [t for t in new_transactions if t['transaction_id'] not in existing_ids]
    
    print(f"🔄 {len(unique_new)} new transactions (skipped {len(new_transactions) - len(unique_new)} duplicates)")
    
    # Merge
    all_transactions = existing + unique_new
    
    # Sort by date (newest first)
    all_transactions.sort(key=lambda x: x['date'], reverse=True)
    
    # Save
    save_transactions(all_transactions)
    
    # Summary
    print(f"\n📈 Summary:")
    print(f"   Total transactions: {len(all_transactions)}")
    print(f"   Date range: {all_transactions[-1]['date']} to {all_transactions[0]['date']}")
    
    # Category breakdown
    categories = {}
    for t in unique_new:
        cat = t['category'][0] if t['category'] else 'Unknown'
        categories[cat] = categories.get(cat, 0) + 1
    
    if categories:
        print(f"\n🏷️  New transactions by category:")
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            print(f"   {cat}: {count}")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 import_transactions_csv.py <csv_file>")
        print("\nExport CSV from your bank/credit card and run:")
        print("  python3 scripts/import_transactions_csv.py ~/Downloads/transactions.csv")
        return
    
    csv_file = sys.argv[1]
    
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return
    
    import_csv(csv_file)

if __name__ == "__main__":
    main()
