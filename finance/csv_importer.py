#!/usr/bin/env python3
"""
CSV Transaction Importer

Imports transactions from CSV exports from PNC, Chase, Venmo, Cash App.
Works immediately without API setup.

Usage:
1. Export CSVs from your banks
2. Put them in ~/clawd/finance/data/
3. Run this script
4. Dashboard updates with real data
"""

import csv
import json
from pathlib import Path
from datetime import datetime
import urllib.request

FINANCE_DIR = Path.home() / "clawd" / "finance"
DATA_DIR = FINANCE_DIR / "data"
TRANSACTIONS_FILE = FINANCE_DIR / "transactions.json"
OLLAMA_URL = "http://localhost:11434/api/generate"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)

def call_local_ai(prompt, temperature=0.3):
    """Use local AI for categorization"""
    try:
        data = json.dumps({
            "model": "qwen2.5:14b",
            "prompt": prompt,
            "temperature": temperature,
            "stream": False
        }).encode('utf-8')
        
        req = urllib.request.Request(
            OLLAMA_URL,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("response")
    except:
        return None

def categorize_transaction(description, amount):
    """
    Use local AI to categorize transaction
    
    Returns category like: Housing, Food, Transportation, Entertainment, etc.
    """
    
    prompt = f"""Categorize this financial transaction into ONE category.

Transaction: {description}
Amount: ${amount}

Categories:
- Housing (rent, mortgage, utilities)
- Food (groceries, restaurants, delivery)
- Transportation (gas, uber, car payment)
- Entertainment (movies, games, subscriptions)
- Shopping (clothes, amazon, etc)
- Health (gym, medical, insurance)
- Income (salary, freelance, refunds)
- Transfer (between accounts, venmo friends)
- Other

Respond with ONLY the category name, nothing else."""

    response = call_local_ai(prompt, temperature=0.2)
    
    if response:
        # Clean response
        category = response.strip().split('\n')[0].strip()
        # Validate it's one of our categories
        valid_categories = ['Housing', 'Food', 'Transportation', 'Entertainment', 
                           'Shopping', 'Health', 'Income', 'Transfer', 'Other']
        if category in valid_categories:
            return category
    
    # Fallback: simple keyword matching
    desc_lower = description.lower()
    
    if any(kw in desc_lower for kw in ['rent', 'mortgage', 'utility', 'electric', 'water', 'internet']):
        return 'Housing'
    elif any(kw in desc_lower for kw in ['restaurant', 'food', 'grocery', 'chipotle', 'doordash', 'uber eats']):
        return 'Food'
    elif any(kw in desc_lower for kw in ['gas', 'fuel', 'uber', 'lyft', 'car', 'auto']):
        return 'Transportation'
    elif any(kw in desc_lower for kw in ['netflix', 'spotify', 'movie', 'game', 'steam']):
        return 'Entertainment'
    elif any(kw in desc_lower for kw in ['amazon', 'target', 'walmart', 'store']):
        return 'Shopping'
    elif any(kw in desc_lower for kw in ['gym', 'fitness', 'doctor', 'pharmacy', 'insurance']):
        return 'Health'
    elif amount > 1000:  # Likely salary/large transfer
        return 'Income' if amount > 0 else 'Transfer'
    else:
        return 'Other'

def import_pnc(file_path):
    """Import PNC Bank CSV"""
    transactions = []
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Adapt to PNC's CSV format
                # Common format: Date, Description, Debit, Credit
                date_str = row.get('Date', row.get('date', ''))
                description = row.get('Description', row.get('description', ''))
                
                # Handle debit/credit columns
                debit = float(row.get('Debit', row.get('debit', 0)) or 0)
                credit = float(row.get('Credit', row.get('credit', 0)) or 0)
                
                amount = credit - debit  # Credit is positive, debit is negative
                
                if amount != 0:
                    transactions.append({
                        'date': date_str,
                        'description': description,
                        'amount': amount,
                        'account': 'PNC Bank',
                        'category': categorize_transaction(description, amount)
                    })
        
        print(f"  ✅ Imported {len(transactions)} transactions from PNC")
        return transactions
    
    except Exception as e:
        print(f"  ❌ Error importing PNC: {e}")
        return []

def import_chase(file_path):
    """Import Chase CSV"""
    transactions = []
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                date_str = row.get('Transaction Date', row.get('Date', ''))
                description = row.get('Description', row.get('Memo', ''))
                amount = float(row.get('Amount', 0) or 0)
                
                # Chase shows spending as negative
                amount = -abs(amount) if amount < 0 else amount
                
                if amount != 0:
                    transactions.append({
                        'date': date_str,
                        'description': description,
                        'amount': amount,
                        'account': 'Chase Card',
                        'category': categorize_transaction(description, amount)
                    })
        
        print(f"  ✅ Imported {len(transactions)} transactions from Chase")
        return transactions
    
    except Exception as e:
        print(f"  ❌ Error importing Chase: {e}")
        return []

def import_venmo(file_path):
    """Import Venmo CSV"""
    transactions = []
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                date_str = row.get('Datetime', row.get('Date', ''))
                description = row.get('Note', row.get('Description', ''))
                amount_str = row.get('Amount (total)', row.get('Amount', '0'))
                
                # Venmo format: "- $50.00" or "+ $50.00"
                amount = float(amount_str.replace('$', '').replace('+', '').replace(' ', '').strip())
                
                if row.get('Type', '') == 'Payment':
                    amount = -abs(amount)
                
                if amount != 0:
                    transactions.append({
                        'date': date_str,
                        'description': f"Venmo: {description}",
                        'amount': amount,
                        'account': 'Venmo',
                        'category': 'Transfer'  # Most Venmo is transfers
                    })
        
        print(f"  ✅ Imported {len(transactions)} transactions from Venmo")
        return transactions
    
    except Exception as e:
        print(f"  ❌ Error importing Venmo: {e}")
        return []

def import_cashapp(file_path):
    """Import Cash App CSV"""
    transactions = []
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                date_str = row.get('Date', row.get('Transaction Date', ''))
                description = row.get('Notes', row.get('Description', ''))
                amount = float(row.get('Amount', 0) or 0)
                trans_type = row.get('Transaction Type', '')
                
                # Cash App: negative = money out
                if 'sent' in trans_type.lower():
                    amount = -abs(amount)
                
                if amount != 0:
                    transactions.append({
                        'date': date_str,
                        'description': f"Cash App: {description}",
                        'amount': amount,
                        'account': 'Cash App',
                        'category': 'Transfer'  # Most Cash App is transfers
                    })
        
        print(f"  ✅ Imported {len(transactions)} transactions from Cash App")
        return transactions
    
    except Exception as e:
        print(f"  ❌ Error importing Cash App: {e}")
        return []

def import_all():
    """Import from all available CSV files"""
    print("\n💰 IMPORTING TRANSACTIONS FROM CSVs")
    print("=" * 60)
    print(f"📂 Looking in: {DATA_DIR}\n")
    
    all_transactions = []
    
    # Try to import from each source
    pnc_files = list(DATA_DIR.glob("pnc*.csv")) + list(DATA_DIR.glob("PNC*.csv"))
    if pnc_files:
        all_transactions.extend(import_pnc(pnc_files[0]))
    
    chase_files = list(DATA_DIR.glob("chase*.csv")) + list(DATA_DIR.glob("Chase*.csv"))
    if chase_files:
        all_transactions.extend(import_chase(chase_files[0]))
    
    venmo_files = list(DATA_DIR.glob("venmo*.csv")) + list(DATA_DIR.glob("Venmo*.csv"))
    if venmo_files:
        all_transactions.extend(import_venmo(venmo_files[0]))
    
    cashapp_files = list(DATA_DIR.glob("cashapp*.csv")) + list(DATA_DIR.glob("*cash*app*.csv"))
    if cashapp_files:
        all_transactions.extend(import_cashapp(cashapp_files[0]))
    
    if not all_transactions:
        print("\n❌ No CSV files found in ~/clawd/finance/data/")
        print("\n📋 To import transactions:")
        print("  1. Export CSVs from your banks")
        print("  2. Name them: pnc.csv, chase.csv, venmo.csv, cashapp.csv")
        print("  3. Put them in ~/clawd/finance/data/")
        print("  4. Run this script again")
        return
    
    # Save all transactions
    with open(TRANSACTIONS_FILE, 'w') as f:
        json.dump(all_transactions, f, indent=2)
    
    print(f"\n✅ IMPORT COMPLETE")
    print(f"   Total transactions: {len(all_transactions)}")
    print(f"   Saved to: {TRANSACTIONS_FILE}")
    
    # Generate quick stats
    income = sum(t['amount'] for t in all_transactions if t['amount'] > 0)
    expenses = abs(sum(t['amount'] for t in all_transactions if t['amount'] < 0))
    
    print(f"\n📊 QUICK STATS")
    print(f"   Income:   ${income:,.2f}")
    print(f"   Expenses: ${expenses:,.2f}")
    print(f"   Net:      ${income - expenses:,.2f}")

if __name__ == "__main__":
    import_all()
