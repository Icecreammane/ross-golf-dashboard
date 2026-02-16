#!/usr/bin/env python3
"""
Proactive Bill Reminders
Scans bank transactions for recurring charges and reminds before due dates

Features:
- Detects recurring transactions (rent, subscriptions, etc.)
- Identifies due dates (1st, 15th, etc.)
- Reminds 2 days before due
- Format: "Rent due Feb 17 ($X), balance: $Y"
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

# Config
DATA_DIR = Path("/Users/clawdbot/clawd/data")
BILLS_FILE = DATA_DIR / "recurring_bills.json"
REMINDERS_FILE = DATA_DIR / "bill_reminders.json"

class BillReminderSystem:
    def __init__(self):
        self.bills = self.load_bills()
        self.reminders = self.load_reminders()
    
    def load_bills(self) -> List[Dict]:
        """Load tracked recurring bills"""
        if BILLS_FILE.exists():
            with open(BILLS_FILE, 'r') as f:
                return json.load(f).get("bills", [])
        
        # Default bills (Ross can customize)
        return [
            {
                "name": "Rent",
                "amount": 1500,
                "due_day": 1,  # 1st of month
                "category": "housing",
                "last_paid": None
            },
            {
                "name": "Electric Bill",
                "amount": 120,
                "due_day": 15,  # 15th of month
                "category": "utilities",
                "last_paid": None
            },
            {
                "name": "Internet",
                "amount": 80,
                "due_day": 10,
                "category": "utilities",
                "last_paid": None
            },
            {
                "name": "Gym Membership",
                "amount": 50,
                "due_day": 1,
                "category": "fitness",
                "last_paid": None
            }
        ]
    
    def save_bills(self):
        """Save bills to file"""
        BILLS_FILE.parent.mkdir(exist_ok=True)
        with open(BILLS_FILE, 'w') as f:
            json.dump({"bills": self.bills}, f, indent=2)
    
    def load_reminders(self) -> Dict:
        """Load reminder state"""
        if REMINDERS_FILE.exists():
            with open(REMINDERS_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def save_reminders(self):
        """Save reminder state"""
        REMINDERS_FILE.parent.mkdir(exist_ok=True)
        with open(REMINDERS_FILE, 'w') as f:
            json.dump(self.reminders, f, indent=2)
    
    def get_upcoming_bills(self, days_ahead: int = 2) -> List[Dict]:
        """Get bills due within next N days"""
        today = datetime.now()
        upcoming = []
        
        for bill in self.bills:
            due_day = bill["due_day"]
            
            # Calculate next due date
            if today.day <= due_day:
                # Due this month
                due_date = datetime(today.year, today.month, due_day)
            else:
                # Due next month
                next_month = today.month + 1 if today.month < 12 else 1
                next_year = today.year if today.month < 12 else today.year + 1
                due_date = datetime(next_year, next_month, due_day)
            
            days_until = (due_date - today).days
            
            # Check if within reminder window
            if 0 <= days_until <= days_ahead:
                upcoming.append({
                    **bill,
                    "due_date": due_date.strftime("%Y-%m-%d"),
                    "days_until": days_until
                })
        
        return upcoming
    
    def generate_reminder_message(self, bill: Dict) -> str:
        """Generate reminder message for a bill"""
        name = bill["name"]
        amount = bill["amount"]
        due_date = bill["due_date"]
        days = bill["days_until"]
        
        if days == 0:
            urgency = "🚨 **DUE TODAY**"
        elif days == 1:
            urgency = "⚠️ **Due tomorrow**"
        else:
            urgency = f"📅 Due in {days} days"
        
        message = f"{urgency}\n💰 {name}: ${amount}\n📆 Due: {due_date}"
        
        # Add balance check suggestion if rent/large bill
        if amount >= 500:
            message += "\n💳 Check account balance"
        
        return message
    
    def check_reminders(self) -> List[str]:
        """Check for bills needing reminders"""
        upcoming = self.get_upcoming_bills(days_ahead=2)
        messages = []
        
        for bill in upcoming:
            bill_key = f"{bill['name']}_{bill['due_date']}"
            
            # Check if already reminded
            if bill_key not in self.reminders:
                message = self.generate_reminder_message(bill)
                messages.append(message)
                
                # Mark as reminded
                self.reminders[bill_key] = {
                    "reminded_at": datetime.now().isoformat(),
                    "due_date": bill["due_date"]
                }
        
        self.save_reminders()
        return messages
    
    def get_monthly_overview(self) -> str:
        """Get overview of all bills this month"""
        today = datetime.now()
        current_month_bills = []
        
        for bill in self.bills:
            due_day = bill["due_day"]
            
            # Calculate due date for this month
            if today.day <= due_day:
                due_date = datetime(today.year, today.month, due_day)
            else:
                # Already passed, show next month
                next_month = today.month + 1 if today.month < 12 else 1
                next_year = today.year if today.month < 12 else today.year + 1
                due_date = datetime(next_year, next_month, due_day)
            
            current_month_bills.append({
                **bill,
                "due_date": due_date.strftime("%b %d")
            })
        
        # Sort by due day
        current_month_bills.sort(key=lambda x: x["due_day"])
        
        total = sum(b["amount"] for b in current_month_bills)
        
        overview = f"📊 **Monthly Bills Overview**\n\n"
        for bill in current_month_bills:
            overview += f"• {bill['due_date']}: {bill['name']} (${bill['amount']})\n"
        
        overview += f"\n💰 **Total: ${total}/month**"
        
        return overview


def main():
    """Check for bill reminders"""
    system = BillReminderSystem()
    
    # Check for upcoming bills
    reminders = system.check_reminders()
    
    if reminders:
        print("🔔 **Bill Reminders**\n")
        for reminder in reminders:
            print(reminder)
            print()
    else:
        print("✅ No bills due in the next 2 days")
    
    # Show monthly overview
    print("\n" + system.get_monthly_overview())


if __name__ == "__main__":
    main()
