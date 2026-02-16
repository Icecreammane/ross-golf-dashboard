#!/usr/bin/env python3
"""
Financial Sync Daemon - Daily sync of financial data
Runs at 6am daily via cron
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from financial_dashboard import sync_accounts, sync_transactions, check_budget_status, load_financial_data

def main():
    """Run daily financial sync"""
    print(f"[{datetime.now()}] Starting financial sync...")
    
    # Check if access token exists
    data = load_financial_data()
    if not data.get('access_token'):
        print("⚠️  No access token found. Please connect a bank account first.")
        return
    
    # Sync accounts
    print("📊 Syncing accounts...")
    accounts_result = sync_accounts()
    if 'error' in accounts_result:
        print(f"❌ Account sync failed: {accounts_result['error']}")
        return
    
    print(f"✅ Synced {len(accounts_result.get('accounts', []))} accounts")
    
    # Sync transactions
    print("💳 Syncing transactions...")
    transactions_result = sync_transactions(days=90)  # 90 days of history
    if 'error' in transactions_result:
        print(f"❌ Transaction sync failed: {transactions_result['error']}")
        return
    
    print(f"✅ Synced {len(transactions_result.get('transactions', []))} transactions")
    
    # Check budget status
    print("💰 Checking budget status...")
    budget_status = check_budget_status()
    
    # Check for budget alerts
    alerts = []
    for category, status in budget_status.items():
        if status['status'] == 'over_budget':
            alerts.append(f"🔴 {category}: ${status['spent']:.2f} / ${status['budget']:.2f} (OVER BUDGET)")
        elif status['status'] == 'warning':
            alerts.append(f"🟡 {category}: ${status['spent']:.2f} / ${status['budget']:.2f} (80% spent)")
    
    if alerts:
        print("\n⚠️  BUDGET ALERTS:")
        for alert in alerts:
            print(f"  {alert}")
    else:
        print("✅ All budgets on track!")
    
    print(f"\n✅ Financial sync completed at {datetime.now()}")

if __name__ == '__main__':
    main()
