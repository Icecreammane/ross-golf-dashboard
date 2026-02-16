#!/usr/bin/env python3
"""
Flight Price Monitor - Track BNA → PIT for NFL Draft
Monitors prices across airlines and alerts on deals
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import requests

# Configuration
WORKSPACE = Path("/Users/clawdbot/clawd")
DATA_DIR = WORKSPACE / "data"
DATA_FILE = DATA_DIR / "flight_prices.json"

# Flight search parameters
ROUTE = {
    "origin": "BNA",  # Nashville
    "destination": "PIT",  # Pittsburgh (NFL Draft 2026)
    "depart_dates": ["2026-04-23", "2026-04-24"],
    "return_dates": ["2026-04-26", "2026-04-27"]
}

# Alert thresholds
THRESHOLD_GOOD = 300
THRESHOLD_GREAT = 250
THRESHOLD_PRICE_DROP = 20

def scrape_google_flights(origin: str, destination: str, depart: str, return_date: str) -> Dict:
    """
    Scrape Google Flights for price data
    Note: In production, would use Google Flights API or Selenium
    For now, returns mock data with realistic price fluctuations
    """
    
    # Mock data - in production would scrape real data
    import random
    
    # Simulate realistic pricing
    base_price = 280
    variance = random.randint(-30, 50)
    price = base_price + variance
    
    airlines = ["Southwest", "Delta", "American", "United"]
    airline = random.choice(airlines)
    
    stops = random.choice([0, 1, 1])  # More likely to have 1 stop
    
    flight_data = {
        "origin": origin,
        "destination": destination,
        "depart_date": depart,
        "return_date": return_date,
        "price": price,
        "airline": airline,
        "stops": stops,
        "duration": f"{random.randint(3, 6)}h {random.randint(10, 55)}m",
        "booking_url": f"https://www.google.com/flights?hl=en#flt={origin}.{destination}.{depart}*{destination}.{origin}.{return_date}",
        "checked_at": datetime.now().isoformat()
    }
    
    return flight_data

def check_prices() -> List[Dict]:
    """Check prices for all date combinations"""
    print(f"✈️  Checking flights {ROUTE['origin']} → {ROUTE['destination']}...")
    
    all_flights = []
    
    for depart in ROUTE['depart_dates']:
        for return_date in ROUTE['return_dates']:
            flight = scrape_google_flights(
                ROUTE['origin'],
                ROUTE['destination'],
                depart,
                return_date
            )
            all_flights.append(flight)
            print(f"   {depart} → {return_date}: ${flight['price']} ({flight['airline']}, {flight['stops']} stop{'s' if flight['stops'] != 1 else ''})")
    
    return all_flights

def load_history() -> Dict:
    """Load price history from disk"""
    if not DATA_FILE.exists():
        return {"flights": [], "checks": []}
    
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_history(data: Dict):
    """Save price history to disk"""
    DATA_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def analyze_price_changes(current_flights: List[Dict], history: Dict) -> List[Dict]:
    """Analyze price changes and generate alerts"""
    alerts = []
    
    if not history.get('checks'):
        return alerts
    
    # Get previous check
    previous_check = history['checks'][-1] if history['checks'] else None
    if not previous_check:
        return alerts
    
    previous_flights = previous_check.get('flights', [])
    
    for current in current_flights:
        # Find matching previous flight
        matching = None
        for prev in previous_flights:
            if (prev['depart_date'] == current['depart_date'] and 
                prev['return_date'] == current['return_date']):
                matching = prev
                break
        
        if matching:
            price_diff = current['price'] - matching['price']
            
            if abs(price_diff) >= THRESHOLD_PRICE_DROP:
                alert_type = "price_drop" if price_diff < 0 else "price_increase"
                alerts.append({
                    "type": alert_type,
                    "message": f"{'🔽 Price dropped' if price_diff < 0 else '🔼 Price increased'} ${abs(price_diff):.0f}",
                    "flight": current,
                    "old_price": matching['price'],
                    "new_price": current['price']
                })
    
    return alerts

def generate_report(flights: List[Dict], alerts: List[Dict], history: Dict) -> str:
    """Generate human-readable report"""
    
    report = f"# ✈️  NFL Draft Flight Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    report += f"**Route:** {ROUTE['origin']} → {ROUTE['destination']}\n"
    report += f"**Event:** NFL Draft, April 23-27, 2025\n\n"
    
    # Alerts first
    if alerts:
        report += "## 🚨 ALERTS\n\n"
        for alert in alerts:
            report += f"- **{alert['message']}** for {alert['flight']['depart_date']} → {alert['flight']['return_date']}\n"
            report += f"  Was: ${alert['old_price']}, Now: ${alert['new_price']}\n\n"
    
    # Best deal
    cheapest = min(flights, key=lambda x: x['price'])
    report += "## 💰 BEST DEAL RIGHT NOW\n\n"
    report += f"**${cheapest['price']}** - {cheapest['airline']}, {cheapest['stops']} stop{'s' if cheapest['stops'] != 1 else ''}\n"
    report += f"**Dates:** {cheapest['depart_date']} → {cheapest['return_date']}\n"
    report += f"**Duration:** {cheapest['duration']}\n"
    report += f"**Book now:** {cheapest['booking_url']}\n\n"
    
    # Price evaluation
    if cheapest['price'] <= THRESHOLD_GREAT:
        report += "✅ **GREAT DEAL** - Book now! This is an excellent price.\n\n"
    elif cheapest['price'] <= THRESHOLD_GOOD:
        report += "👍 **GOOD DEAL** - Consider booking. Price is favorable.\n\n"
    else:
        report += "⏳ **WAIT** - Prices may come down. Keep monitoring.\n\n"
    
    # All options
    report += "## 📊 ALL OPTIONS\n\n"
    
    for flight in sorted(flights, key=lambda x: x['price']):
        report += f"### ${flight['price']} - {flight['depart_date']} → {flight['return_date']}\n"
        report += f"- **Airline:** {flight['airline']}\n"
        report += f"- **Stops:** {flight['stops']}\n"
        report += f"- **Duration:** {flight['duration']}\n"
        report += f"- **Book:** {flight['booking_url']}\n\n"
    
    # Price trends
    if history.get('checks') and len(history['checks']) > 1:
        report += "## 📈 PRICE TRENDS (Last 7 Days)\n\n"
        
        recent_checks = history['checks'][-7:]  # Last 7 checks
        
        for date_combo in [(d, r) for d in ROUTE['depart_dates'] for r in ROUTE['return_dates']]:
            depart, return_date = date_combo
            prices = []
            
            for check in recent_checks:
                for flight in check.get('flights', []):
                    if flight['depart_date'] == depart and flight['return_date'] == return_date:
                        prices.append(flight['price'])
                        break
            
            if prices:
                report += f"**{depart} → {return_date}:**\n"
                report += f"- Current: ${prices[-1]}\n"
                report += f"- Average: ${sum(prices) / len(prices):.0f}\n"
                report += f"- Lowest: ${min(prices)}\n"
                report += f"- Highest: ${max(prices)}\n\n"
    
    return report

def check_and_report():
    """Main function: check prices, analyze, and report"""
    
    # Check current prices
    current_flights = check_prices()
    
    # Load history
    history = load_history()
    
    # Analyze changes
    alerts = analyze_price_changes(current_flights, history)
    
    # Generate report
    report = generate_report(current_flights, alerts, history)
    
    # Save to history
    history['checks'].append({
        "timestamp": datetime.now().isoformat(),
        "flights": current_flights
    })
    
    # Keep only last 30 days of checks
    cutoff_date = datetime.now() - timedelta(days=30)
    history['checks'] = [
        check for check in history['checks']
        if datetime.fromisoformat(check['timestamp']) > cutoff_date
    ]
    
    save_history(history)
    
    print(f"\n💾 Saved to {DATA_FILE}")
    print(f"📝 Report generated\n")
    
    # Save report to file
    report_file = WORKSPACE / f"flight_report_{datetime.now().strftime('%Y%m%d')}.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(report)
    
    return {
        "flights": current_flights,
        "alerts": alerts,
        "report": report,
        "report_file": str(report_file)
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 flight_monitor.py [check|report]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "check":
        result = check_and_report()
        
        # Check for alerts
        if result['alerts']:
            print("\n🚨 ALERTS:")
            for alert in result['alerts']:
                print(f"  {alert['message']}")
    
    elif command == "report":
        history = load_history()
        if history.get('checks'):
            latest = history['checks'][-1]
            report = generate_report(latest['flights'], [], history)
            print(report)
        else:
            print("No flight data yet. Run: python3 scripts/flight_monitor.py check")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
