#!/usr/bin/env python3
"""
Notion Budget Template Generator - Build skeleton for Ross's first product
"""

import json
from datetime import datetime

def build_notion_template():
    """Build structure for Notion budget template product"""
    
    template = {
        "product_name": "Fitness Enthusiast Budget Tracker",
        "description": "Track spending on gym memberships, supplements, food, coaching - all in one place",
        "price_point": "$24.99",
        "target_market": "People spending $500+/month on fitness",
        "template_sections": [
            {
                "name": "Monthly Budget Overview",
                "type": "Dashboard",
                "includes": [
                    "Total monthly spending",
                    "By category breakdown (gym, food, supps, coaching)",
                    "% of income spent on fitness",
                    "ROI calculation (cost per lb muscle gained)"
                ]
            },
            {
                "name": "Expense Tracker",
                "type": "Database",
                "fields": [
                    "Date",
                    "Category (dropdown: Gym, Food, Supplements, Coaching, Equipment)",
                    "Description",
                    "Amount",
                    "Recurring (yes/no)",
                    "ROI Notes"
                ]
            },
            {
                "name": "Monthly Goals",
                "type": "Linked Database",
                "includes": [
                    "Budget by category",
                    "Actual spending vs budget",
                    "Savings targets"
                ]
            },
            {
                "name": "ROI Tracker",
                "type": "Calculation",
                "metrics": [
                    "Cost per pound of muscle gained",
                    "Cost per percentage body fat lost",
                    "Monthly spending trend",
                    "Best ROI categories"
                ]
            }
        ],
        "marketing_copy": """
SELL YOUR FITNESS BUDGET TRACKER ON GUMROAD:

Title: "Fitness Spending Tracker - Budget Like a Bodybuilder"

Description:
Stop wondering where your fitness money goes. 

This Notion template tracks every dollar you spend on your fitness journey - gym memberships, supplements, coaching, competition fees, recovery tools - and shows you the ROI.

Perfect for:
- Serious lifters tracking bulk/cut spending
- Athletes optimizing coaching ROI
- Fitness entrepreneurs managing their own health investment
- Anyone who spends $500+/month on fitness

Includes:
✓ Monthly budget dashboard
✓ Expense tracking by category
✓ ROI calculations (cost per lb muscle, cost per 1% body fat)
✓ Spending trend analysis
✓ Budget vs actual tracking

One-time purchase. Use forever. 

Price: $24.99
        """,
        "sales_channels": [
            "Gumroad (primary)",
            "Reddit fitness subreddits",
            "Twitter fitness community",
            "Email list (if you build one)"
        ],
        "build_timeline": "2-3 days",
        "launch_timeline": "1 day after build complete",
        "expected_first_month_sales": "15-25 units = $375-625"
    }
    
    return template

if __name__ == "__main__":
    template = build_notion_template()
    
    print("\n" + "="*70)
    print("📝 NOTION BUDGET TEMPLATE - PRODUCT SKELETON")
    print("="*70)
    
    print(f"\n📦 Product: {template['product_name']}")
    print(f"💰 Price: {template['price_point']}")
    print(f"👥 Target: {template['target_market']}")
    print(f"⏱️  Build Time: {template['build_timeline']}")
    
    print("\n" + "="*70)
    print("\n🏗️  TEMPLATE STRUCTURE:\n")
    
    for section in template['template_sections']:
        print(f"📌 {section['name']} ({section['type']})")
        if 'includes' in section:
            for item in section['includes']:
                print(f"   • {item}")
        elif 'fields' in section:
            for field in section['fields']:
                print(f"   • {field}")
        elif 'metrics' in section:
            for metric in section['metrics']:
                print(f"   • {metric}")
        print()
    
    print("="*70)
    print("\n💬 GUMROAD MARKETING COPY:\n")
    print(template['marketing_copy'])
    
    print("="*70)
    print("\n🚀 LAUNCH STRATEGY:\n")
    print(f"Sales Channels:")
    for channel in template['sales_channels']:
        print(f"  • {channel}")
    
    print(f"\n📈 Expected First Month: {template['expected_first_month_sales']}")
    
    # Save template
    with open("/Users/clawdbot/clawd/night_shift_output/notion_template_skeleton.json", "w") as f:
        json.dump(template, f, indent=2)
    
    print("\n✅ Template skeleton saved")

