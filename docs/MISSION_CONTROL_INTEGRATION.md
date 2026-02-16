# Mission Control Integration

**Integrate Core Assistant Features into Mission Control Dashboard**

---

## Overview

All 3 core features can display status widgets in Mission Control:

1. **Financial Status** - Current balance, today's spending, budget alerts
2. **Reservation Status** - Active searches, new availability
3. **Email Status** - Urgent count, action required, today's processed

---

## Widget Designs

### Financial Status Widget

```
┌─────────────────────────────────┐
│ 💰 FINANCIAL STATUS             │
├─────────────────────────────────┤
│ Total Balance: $12,345.67       │
│ Today's Spending: $45.23        │
│                                 │
│ Budget Alerts: 🔴 2             │
│   🔴 Food & Drink (over)        │
│   🟡 Transportation (warning)   │
│                                 │
│ Last Sync: 2 hours ago          │
│ [View Dashboard →]              │
└─────────────────────────────────┘
```

### Reservation Status Widget

```
┌─────────────────────────────────┐
│ 🍽️  RESERVATIONS                │
├─────────────────────────────────┤
│ Active Searches: 3              │
│                                 │
│ 🎉 New Availability:            │
│   • Husk Nashville              │
│     7:00 PM, 7:30 PM            │
│                                 │
│ [Search Now →]                  │
└─────────────────────────────────┘
```

### Email Status Widget

```
┌─────────────────────────────────┐
│ 📧 EMAIL TRIAGE                 │
├─────────────────────────────────┤
│ 🔴 Urgent: 2                    │
│ 🟡 Action Required: 5           │
│ 🔵 FYI: 12                      │
│                                 │
│ Today Processed: 47 emails      │
│ Auto-Archived: 8 spam           │
│                                 │
│ Last Check: 15 minutes ago      │
│ [Check Inbox →]                 │
└─────────────────────────────────┘
```

---

## Data API Endpoints

### Financial Status API

**Endpoint:** `GET /api/financial_status`

**Implementation:**

```python
# Add to financial_dashboard.py

@app.route('/api/financial_status')
def financial_status():
    """Get financial status for Mission Control"""
    data = load_financial_data()
    accounts = data.get('accounts', [])
    
    # Calculate total balance
    total_balance = sum(acc.get('balance', 0) for acc in accounts)
    
    # Calculate today's spending
    transactions = data.get('transactions', [])
    today = datetime.now().date()
    today_spending = sum(
        txn['amount'] for txn in transactions
        if datetime.fromisoformat(txn['date']).date() == today and txn['amount'] > 0
    )
    
    # Get budget alerts
    budget_status = check_budget_status()
    alerts = []
    for category, status in budget_status.items():
        if status['status'] in ['warning', 'over_budget']:
            alerts.append({
                'category': category,
                'status': status['status'],
                'spent': status['spent'],
                'budget': status['budget']
            })
    
    return jsonify({
        'total_balance': total_balance,
        'today_spending': today_spending,
        'budget_alerts': alerts,
        'last_sync': data.get('last_sync'),
        'dashboard_url': 'http://localhost:8082/finances'
    })
```

**Response:**

```json
{
  "total_balance": 12345.67,
  "today_spending": 45.23,
  "budget_alerts": [
    {
      "category": "Food and Drink",
      "status": "over_budget",
      "spent": 550.00,
      "budget": 500.00
    }
  ],
  "last_sync": "2024-02-15T10:30:00",
  "dashboard_url": "http://localhost:8082/finances"
}
```

---

### Reservation Status API

**Command:** `python3 scripts/get_reservation_status.py`

**Implementation:**

```python
#!/usr/bin/env python3
"""Get reservation status for Mission Control"""

import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / 'data'
SAVED_SEARCHES_PATH = DATA_DIR / 'saved_searches.json'

def get_reservation_status():
    """Get reservation status"""
    if not SAVED_SEARCHES_PATH.exists():
        return {
            'active_searches': 0,
            'new_availability': []
        }
    
    with open(SAVED_SEARCHES_PATH, 'r') as f:
        data = json.load(f)
    
    searches = [s for s in data.get('searches', []) if s.get('active', True)]
    
    # Check for new availability (would need to run search)
    # For now, just return count
    
    return {
        'active_searches': len(searches),
        'new_availability': [],  # Populated by daemon
        'last_check': datetime.now().isoformat()
    }

if __name__ == '__main__':
    status = get_reservation_status()
    print(json.dumps(status, indent=2))
```

**Response:**

```json
{
  "active_searches": 3,
  "new_availability": [
    {
      "restaurant": "Husk Nashville",
      "times": ["7:00 PM", "7:30 PM"],
      "booking_url": "https://www.opentable.com/..."
    }
  ],
  "last_check": "2024-02-15T10:30:00"
}
```

---

### Email Status API

**Command:** `python3 scripts/get_email_status.py`

**Implementation:**

```python
#!/usr/bin/env python3
"""Get email status for Mission Control"""

import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / 'data'
EMAIL_DATA_PATH = DATA_DIR / 'email_classifications.json'

def get_email_status():
    """Get email status"""
    if not EMAIL_DATA_PATH.exists():
        return {
            'urgent': 0,
            'action_required': 0,
            'fyi': 0,
            'today_processed': 0,
            'auto_archived': 0
        }
    
    with open(EMAIL_DATA_PATH, 'r') as f:
        data = json.load(f)
    
    emails = data.get('emails', [])
    
    # Count by category
    urgent = sum(1 for e in emails if e['category'] == 'urgent')
    action_required = sum(1 for e in emails if e['category'] == 'action_required')
    fyi = sum(1 for e in emails if e['category'] == 'fyi')
    
    # Count today's emails
    today = datetime.now().date()
    today_emails = [
        e for e in emails
        if datetime.fromisoformat(e['classified_at']).date() == today
    ]
    
    auto_archived = sum(1 for e in today_emails if e['category'] == 'spam')
    
    return {
        'urgent': urgent,
        'action_required': action_required,
        'fyi': fyi,
        'today_processed': len(today_emails),
        'auto_archived': auto_archived,
        'last_check': data.get('last_check')
    }

if __name__ == '__main__':
    status = get_email_status()
    print(json.dumps(status, indent=2))
```

**Response:**

```json
{
  "urgent": 2,
  "action_required": 5,
  "fyi": 12,
  "today_processed": 47,
  "auto_archived": 8,
  "last_check": "2024-02-15T10:30:00"
}
```

---

## Mission Control Dashboard Code

**Add to Mission Control dashboard:**

```html
<!-- Financial Status Widget -->
<div class="widget" id="financial-widget">
  <h3>💰 Financial Status</h3>
  <div class="widget-content">
    <p><strong>Total Balance:</strong> <span id="total-balance">Loading...</span></p>
    <p><strong>Today's Spending:</strong> <span id="today-spending">Loading...</span></p>
    <div id="budget-alerts"></div>
    <p class="last-sync" id="financial-last-sync">Last sync: ...</p>
    <a href="http://localhost:8082/finances" target="_blank" class="view-link">View Dashboard →</a>
  </div>
</div>

<!-- Reservation Status Widget -->
<div class="widget" id="reservation-widget">
  <h3>🍽️ Reservations</h3>
  <div class="widget-content">
    <p><strong>Active Searches:</strong> <span id="active-searches">0</span></p>
    <div id="new-availability"></div>
    <button onclick="searchReservations()">Search Now →</button>
  </div>
</div>

<!-- Email Status Widget -->
<div class="widget" id="email-widget">
  <h3>📧 Email Triage</h3>
  <div class="widget-content">
    <p>🔴 Urgent: <span id="urgent-count">0</span></p>
    <p>🟡 Action Required: <span id="action-count">0</span></p>
    <p>🔵 FYI: <span id="fyi-count">0</span></p>
    <p><strong>Today Processed:</strong> <span id="today-processed">0</span></p>
    <p class="last-sync" id="email-last-sync">Last check: ...</p>
    <button onclick="checkEmail()">Check Inbox →</button>
  </div>
</div>
```

**JavaScript to load data:**

```javascript
// Load Financial Status
async function loadFinancialStatus() {
  try {
    const response = await fetch('http://localhost:8082/api/financial_status');
    const data = await response.json();
    
    document.getElementById('total-balance').textContent = `$${data.total_balance.toFixed(2)}`;
    document.getElementById('today-spending').textContent = `$${data.today_spending.toFixed(2)}`;
    
    const alertsHtml = data.budget_alerts.map(alert => {
      const icon = alert.status === 'over_budget' ? '🔴' : '🟡';
      return `<p>${icon} ${alert.category} ($${alert.spent.toFixed(2)} / $${alert.budget.toFixed(2)})</p>`;
    }).join('');
    
    document.getElementById('budget-alerts').innerHTML = alertsHtml || '<p>✅ All budgets on track</p>';
    document.getElementById('financial-last-sync').textContent = `Last sync: ${timeAgo(data.last_sync)}`;
  } catch (error) {
    console.error('Failed to load financial status:', error);
  }
}

// Load Reservation Status
async function loadReservationStatus() {
  try {
    const response = await fetch('http://localhost:3000/api/reservation_status');  // Add to your backend
    const data = await response.json();
    
    document.getElementById('active-searches').textContent = data.active_searches;
    
    if (data.new_availability.length > 0) {
      const availabilityHtml = data.new_availability.map(avail => 
        `<p>🎉 ${avail.restaurant}<br>${avail.times.join(', ')}</p>`
      ).join('');
      document.getElementById('new-availability').innerHTML = availabilityHtml;
    } else {
      document.getElementById('new-availability').innerHTML = '<p>No new availability</p>';
    }
  } catch (error) {
    console.error('Failed to load reservation status:', error);
  }
}

// Load Email Status
async function loadEmailStatus() {
  try {
    const response = await fetch('http://localhost:3000/api/email_status');  // Add to your backend
    const data = await response.json();
    
    document.getElementById('urgent-count').textContent = data.urgent;
    document.getElementById('action-count').textContent = data.action_required;
    document.getElementById('fyi-count').textContent = data.fyi;
    document.getElementById('today-processed').textContent = data.today_processed;
    document.getElementById('email-last-sync').textContent = `Last check: ${timeAgo(data.last_check)}`;
  } catch (error) {
    console.error('Failed to load email status:', error);
  }
}

// Helper: Time ago
function timeAgo(timestamp) {
  const now = new Date();
  const past = new Date(timestamp);
  const diffMs = now - past;
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 60) return `${diffMins} minutes ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours} hours ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays} days ago`;
}

// Load all on page load
document.addEventListener('DOMContentLoaded', () => {
  loadFinancialStatus();
  loadReservationStatus();
  loadEmailStatus();
  
  // Refresh every 5 minutes
  setInterval(() => {
    loadFinancialStatus();
    loadReservationStatus();
    loadEmailStatus();
  }, 300000);
});
```

---

## Backend API Routes

**Add to your main backend (Express/Flask):**

```python
# Flask example
from flask import Flask, jsonify
import subprocess
import json

@app.route('/api/reservation_status')
def reservation_status():
    result = subprocess.run(
        ['python3', 'scripts/get_reservation_status.py'],
        capture_output=True,
        text=True
    )
    return jsonify(json.loads(result.stdout))

@app.route('/api/email_status')
def email_status():
    result = subprocess.run(
        ['python3', 'scripts/get_email_status.py'],
        capture_output=True,
        text=True
    )
    return jsonify(json.loads(result.stdout))
```

---

## Styling

**CSS for widgets:**

```css
.widget {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.widget h3 {
  margin-bottom: 15px;
  color: #667eea;
}

.widget-content p {
  margin: 8px 0;
}

.last-sync {
  font-size: 0.9em;
  color: #666;
  margin-top: 10px;
}

.view-link {
  display: inline-block;
  margin-top: 10px;
  color: #667eea;
  text-decoration: none;
}

.view-link:hover {
  text-decoration: underline;
}
```

---

## Testing Integration

1. **Start Financial Dashboard:**
   ```bash
   python3 scripts/financial_dashboard.py
   ```

2. **Test API endpoints:**
   ```bash
   curl http://localhost:8082/api/financial_status
   ```

3. **Load Mission Control:**
   Open your Mission Control dashboard and verify widgets load data.

4. **Verify auto-refresh:**
   Wait 5 minutes and check that data updates automatically.

---

## Summary

All 3 features now integrate seamlessly into Mission Control:

✅ Financial status widget shows balance + alerts  
✅ Reservation widget shows active searches  
✅ Email widget shows triage status  
✅ Auto-refresh every 5 minutes  
✅ Direct links to dashboards  

**Mission Control is now your central command center!**
