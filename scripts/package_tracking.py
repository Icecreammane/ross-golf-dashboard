#!/usr/bin/env python3
"""
Package Tracking Auto-Monitor
Scans email for tracking numbers and monitors USPS/UPS/FedEx automatically

Features:
- Auto-detects tracking numbers from emails
- Monitors multiple carriers (USPS, UPS, FedEx)
- Alerts on delivery updates
- Format: "Golf clubs arriving tomorrow 2-5pm"
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

# Config
DATA_DIR = Path("/Users/clawdbot/clawd/data")
TRACKING_FILE = DATA_DIR / "package_tracking.json"

# Tracking number patterns
TRACKING_PATTERNS = {
    "USPS": [
        r"\b(94|93|92|94|95)\d{20}\b",  # USPS tracking (22 digits starting with 94/93/92/95)
        r"\b(420\d{9}(9[0-5])?\d{20})\b"  # USPS with prefix
    ],
    "UPS": [
        r"\b1Z[A-Z0-9]{16}\b",  # UPS tracking (1Z + 16 chars)
        r"\b\d{18}\b"  # UPS numeric (18 digits)
    ],
    "FedEx": [
        r"\b\d{12}\b",  # FedEx Express (12 digits)
        r"\b\d{15}\b",  # FedEx Ground (15 digits)
        r"\b96\d{20}\b"  # FedEx SmartPost
    ]
}

class PackageTracker:
    def __init__(self):
        self.packages = self.load_packages()
    
    def load_packages(self) -> List[Dict]:
        """Load tracked packages"""
        if TRACKING_FILE.exists():
            with open(TRACKING_FILE, 'r') as f:
                return json.load(f).get("packages", [])
        return []
    
    def save_packages(self):
        """Save tracked packages"""
        TRACKING_FILE.parent.mkdir(exist_ok=True)
        with open(TRACKING_FILE, 'w') as f:
            json.dump({"packages": self.packages, "last_updated": datetime.now().isoformat()}, f, indent=2)
    
    def detect_tracking_numbers(self, text: str) -> List[Dict]:
        """Detect tracking numbers from text (e.g., email body)"""
        found = []
        
        for carrier, patterns in TRACKING_PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    tracking_number = match if isinstance(match, str) else match[0]
                    
                    # Check if already tracking
                    if not any(p["tracking_number"] == tracking_number for p in self.packages):
                        found.append({
                            "tracking_number": tracking_number,
                            "carrier": carrier,
                            "detected_at": datetime.now().isoformat(),
                            "status": "detected",
                            "last_update": None
                        })
        
        return found
    
    def add_package(self, tracking_number: str, carrier: str, description: str = ""):
        """Manually add package to tracking"""
        package = {
            "tracking_number": tracking_number,
            "carrier": carrier,
            "description": description,
            "added_at": datetime.now().isoformat(),
            "status": "tracking",
            "last_update": None,
            "updates": []
        }
        
        self.packages.append(package)
        self.save_packages()
        
        return package
    
    def check_package_status(self, tracking_number: str, carrier: str) -> Optional[Dict]:
        """Check package status with carrier API"""
        # Placeholder - integrate with carrier APIs
        # In production, would query:
        # - USPS API: https://www.usps.com/business/web-tools-apis/
        # - UPS API: https://www.ups.com/upsdeveloperkit
        # - FedEx API: https://www.fedex.com/en-us/developer.html
        
        # Mock response
        return {
            "tracking_number": tracking_number,
            "carrier": carrier,
            "status": "out_for_delivery",
            "estimated_delivery": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "delivery_window": "2:00 PM - 5:00 PM",
            "location": "Nashville, TN",
            "last_update": datetime.now().isoformat()
        }
    
    def get_delivery_alerts(self) -> List[str]:
        """Get delivery alerts for packages arriving soon"""
        alerts = []
        today = datetime.now().date()
        
        for package in self.packages:
            if package.get("status") in ["delivered", "cancelled"]:
                continue
            
            # Check status
            status = self.check_package_status(
                package["tracking_number"],
                package["carrier"]
            )
            
            if status:
                delivery_date = datetime.strptime(status["estimated_delivery"], "%Y-%m-%d").date()
                days_until = (delivery_date - today).days
                
                description = package.get("description", "Package")
                carrier = package["carrier"]
                
                if days_until == 0:
                    # Delivering today
                    window = status.get("delivery_window", "today")
                    alerts.append(
                        f"📦 **{description}** arriving TODAY ({window})\n"
                        f"   Carrier: {carrier} | Track: {package['tracking_number'][:10]}..."
                    )
                elif days_until == 1:
                    # Delivering tomorrow
                    window = status.get("delivery_window", "")
                    alerts.append(
                        f"📦 **{description}** arriving TOMORROW {window}\n"
                        f"   Carrier: {carrier}"
                    )
                elif days_until <= 3:
                    # Arriving within 3 days
                    alerts.append(
                        f"📦 **{description}** arriving in {days_until} days ({delivery_date.strftime('%b %d')})\n"
                        f"   Carrier: {carrier}"
                    )
        
        return alerts
    
    def scan_email_for_tracking(self, email_subject: str, email_body: str) -> List[Dict]:
        """Scan email for tracking numbers"""
        # Common shipping email indicators
        shipping_keywords = [
            "shipped", "tracking", "delivery", "order", "package",
            "ups", "usps", "fedex", "amazon", "on its way"
        ]
        
        # Check if email is about shipping
        email_text = f"{email_subject} {email_body}".lower()
        is_shipping = any(keyword in email_text for keyword in shipping_keywords)
        
        if not is_shipping:
            return []
        
        # Extract tracking numbers
        detected = self.detect_tracking_numbers(email_body)
        
        # Try to extract package description from email
        for package in detected:
            # Look for product names near tracking numbers
            # This is simplified - production would use more sophisticated NLP
            if "golf" in email_text:
                package["description"] = "Golf clubs"
            elif "shoes" in email_text:
                package["description"] = "Shoes"
            else:
                package["description"] = "Package"
        
        return detected
    
    def get_tracking_summary(self) -> str:
        """Get summary of all tracked packages"""
        if not self.packages:
            return "📦 No packages currently being tracked"
        
        active = [p for p in self.packages if p.get("status") not in ["delivered", "cancelled"]]
        delivered = [p for p in self.packages if p.get("status") == "delivered"]
        
        summary = f"📦 **Package Tracking Summary**\n\n"
        
        if active:
            summary += f"**Active Shipments ({len(active)}):**\n"
            for package in active:
                desc = package.get("description", "Package")
                carrier = package["carrier"]
                summary += f"• {desc} ({carrier})\n"
        
        if delivered:
            summary += f"\n**Recently Delivered ({len(delivered)}):**\n"
            for package in delivered[:3]:
                desc = package.get("description", "Package")
                summary += f"✅ {desc}\n"
        
        return summary


def main():
    """Check package tracking"""
    tracker = PackageTracker()
    
    # Get delivery alerts
    alerts = tracker.get_delivery_alerts()
    
    if alerts:
        print("🚚 **Delivery Alerts**\n")
        for alert in alerts:
            print(alert)
            print()
    else:
        print("✅ No packages arriving in the next 3 days")
    
    # Show tracking summary
    print("\n" + tracker.get_tracking_summary())


if __name__ == "__main__":
    main()
