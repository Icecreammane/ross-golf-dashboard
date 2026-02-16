#!/usr/bin/env python3
"""
Smart Expense Categorizer + Tax Helper
Auto-categorizes transactions and flags tax deductions
"""

import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json
import os

class ExpenseCategorizer:
    """
    Auto-categorizes transactions and identifies tax deductions
    """
    
    # Categories
    CATEGORIES = {
        'work': ['office', 'equipment', 'software', 'subscription', 'tools', 'laptop', 'monitor'],
        'meals_work': ['chipotle', 'lunch', 'coffee', 'meeting', 'client'],
        'meals_personal': ['dinner', 'breakfast', 'restaurant', 'food', 'grocery'],
        'gas': ['gas', 'fuel', 'shell', 'exxon', 'chevron'],
        'entertainment': ['movie', 'netflix', 'spotify', 'game', 'concert'],
        'travel': ['hotel', 'flight', 'airbnb', 'uber', 'lyft', 'rental'],
        'education': ['course', 'training', 'book', 'udemy', 'coursera'],
        'utilities': ['electric', 'water', 'internet', 'phone', 'at&t', 'verizon'],
        'personal': ['amazon', 'target', 'walmart']
    }
    
    # Tax deduction rules (IRS 2026 guidelines)
    TAX_RULES = {
        'home_office_equipment': {
            'keywords': ['desk', 'chair', 'monitor', 'laptop', 'keyboard', 'mouse', 'office'],
            'deductible_pct': 100,
            'irs_code': 'Schedule C - Business Equipment'
        },
        'work_meals': {
            'keywords': ['client', 'meeting', 'business lunch', 'business dinner'],
            'deductible_pct': 50,
            'irs_code': 'Schedule C - Meals (50% limit)'
        },
        'professional_development': {
            'keywords': ['course', 'training', 'book', 'conference', 'workshop', 'certification'],
            'deductible_pct': 100,
            'irs_code': 'Schedule C - Education'
        },
        'mileage': {
            'keywords': ['gas', 'fuel', 'mileage'],
            'deductible_pct': 65.5,  # 2026 IRS mileage rate (cents/mile)
            'irs_code': 'Schedule C - Vehicle Expenses'
        },
        'software_subscriptions': {
            'keywords': ['software', 'subscription', 'saas', 'tool', 'github', 'aws', 'heroku'],
            'deductible_pct': 100,
            'irs_code': 'Schedule C - Software & Services'
        }
    }
    
    def __init__(self):
        self.rule_cache = {}
    
    def categorize(self, description: str, amount: float, merchant: str = "") -> str:
        """
        Auto-categorize transaction based on description and merchant
        
        Returns category name: work, meals_work, meals_personal, gas, entertainment, etc.
        """
        text = f"{description.lower()} {merchant.lower()}"
        
        # Check each category's keywords
        scores = {}
        for category, keywords in self.CATEGORIES.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[category] = score
        
        # Return category with highest match score
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        # Default to personal
        return 'personal'
    
    def identify_deductions(self, description: str, category: str, amount: float, 
                           location: str = "") -> Optional[Dict]:
        """
        Identify if transaction is potentially tax deductible
        
        Returns dict with deduction info or None if not deductible
        """
        text = f"{description.lower()} {location.lower()}"
        
        # Special rules
        # 1. Meals near office location = work lunch
        if 'chipotle' in text and 'near office' in location.lower():
            return {
                'type': 'work_meals',
                'amount': amount,
                'deductible_amount': amount * 0.50,
                'deductible_pct': 50,
                'irs_code': self.TAX_RULES['work_meals']['irs_code'],
                'notes': 'Work-related meal (50% deductible)'
            }
        
        # Check tax rules
        for rule_name, rule_data in self.TAX_RULES.items():
            if any(keyword in text for keyword in rule_data['keywords']):
                deductible_pct = rule_data['deductible_pct'] / 100.0
                return {
                    'type': rule_name,
                    'amount': amount,
                    'deductible_amount': amount * deductible_pct,
                    'deductible_pct': rule_data['deductible_pct'],
                    'irs_code': rule_data['irs_code'],
                    'notes': f'Potentially deductible ({rule_data["deductible_pct"]}%)'
                }
        
        return None
    
    def generate_monthly_report(self, transactions: List[Dict]) -> Dict:
        """
        Generate monthly tax report with deductions summary
        
        Args:
            transactions: List of transaction dicts with keys:
                         date, description, amount, category, merchant
        
        Returns dict with:
            - total_deductions
            - by_category breakdown
            - top_3_categories
            - ytd_total
            - export_ready (CSV data)
        """
        deductions_by_category = {}
        total_deductions = 0.0
        export_rows = []
        
        for txn in transactions:
            deduction = self.identify_deductions(
                txn.get('description', ''),
                txn.get('category', ''),
                txn['amount'],
                txn.get('location', '')
            )
            
            if deduction:
                category = deduction['type']
                if category not in deductions_by_category:
                    deductions_by_category[category] = {
                        'count': 0,
                        'total': 0.0,
                        'deductible': 0.0,
                        'items': []
                    }
                
                deductions_by_category[category]['count'] += 1
                deductions_by_category[category]['total'] += deduction['amount']
                deductions_by_category[category]['deductible'] += deduction['deductible_amount']
                deductions_by_category[category]['items'].append({
                    'date': txn.get('date'),
                    'description': txn.get('description'),
                    'amount': deduction['amount'],
                    'deductible': deduction['deductible_amount']
                })
                
                total_deductions += deduction['deductible_amount']
                
                # CSV export row
                export_rows.append({
                    'Date': txn.get('date'),
                    'Description': txn.get('description'),
                    'Category': category,
                    'Amount': f"${deduction['amount']:.2f}",
                    'Deductible Amount': f"${deduction['deductible_amount']:.2f}",
                    'Deductible %': f"{deduction['deductible_pct']}%",
                    'IRS Code': deduction['irs_code']
                })
        
        # Sort categories by deductible amount
        top_3 = sorted(
            deductions_by_category.items(),
            key=lambda x: x[1]['deductible'],
            reverse=True
        )[:3]
        
        return {
            'total_deductions': total_deductions,
            'by_category': deductions_by_category,
            'top_3_categories': [(cat, data['deductible']) for cat, data in top_3],
            'export_rows': export_rows,
            'summary': f"${total_deductions:,.2f} in potential deductions this month"
        }
    
    def export_to_csv(self, report: Dict, filename: str = "tax_deductions.csv"):
        """Export deductions to CSV for tax time"""
        import csv
        
        if not report.get('export_rows'):
            return None
        
        with open(filename, 'w', newline='') as f:
            fieldnames = report['export_rows'][0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(report['export_rows'])
        
        return filename


class TaxHelper:
    """
    Year-to-date tax deduction tracking and reporting
    """
    
    def __init__(self, data_file='tax_deductions.json'):
        self.data_file = data_file
        self.categorizer = ExpenseCategorizer()
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load existing deduction data"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {'ytd_deductions': {}, 'monthly_totals': {}}
    
    def _save_data(self):
        """Save deduction data"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def track_transaction(self, date: str, description: str, amount: float, 
                         category: str, merchant: str = "", location: str = ""):
        """Track a transaction and identify deductions"""
        deduction = self.categorizer.identify_deductions(
            description, category, amount, location
        )
        
        if not deduction:
            return None
        
        # Add to YTD tracking
        year = datetime.fromisoformat(date).year
        month = datetime.fromisoformat(date).strftime('%Y-%m')
        
        if year not in self.data['ytd_deductions']:
            self.data['ytd_deductions'][year] = {}
        
        if month not in self.data['monthly_totals']:
            self.data['monthly_totals'][month] = 0.0
        
        deduction_type = deduction['type']
        if deduction_type not in self.data['ytd_deductions'][year]:
            self.data['ytd_deductions'][year][deduction_type] = 0.0
        
        self.data['ytd_deductions'][year][deduction_type] += deduction['deductible_amount']
        self.data['monthly_totals'][month] += deduction['deductible_amount']
        
        self._save_data()
        
        return deduction
    
    def get_ytd_summary(self, year: int = None) -> Dict:
        """Get year-to-date deduction summary"""
        if year is None:
            year = datetime.now().year
        
        ytd = self.data['ytd_deductions'].get(year, {})
        total = sum(ytd.values())
        
        return {
            'year': year,
            'total_deductions': total,
            'by_category': ytd,
            'summary': f"${total:,.2f} in deductions for {year}"
        }
    
    def get_monthly_summary(self, month: str = None) -> float:
        """Get deductions for a specific month (YYYY-MM)"""
        if month is None:
            month = datetime.now().strftime('%Y-%m')
        
        return self.data['monthly_totals'].get(month, 0.0)


if __name__ == '__main__':
    # Test the categorizer
    categorizer = ExpenseCategorizer()
    
    # Test transactions
    test_txns = [
        {'date': '2026-02-01', 'description': 'Laptop for work', 'amount': 1200, 'category': 'work', 'merchant': 'Apple Store'},
        {'date': '2026-02-02', 'description': 'Chipotle lunch', 'amount': 12, 'category': 'meals_work', 'merchant': 'Chipotle', 'location': 'near office'},
        {'date': '2026-02-03', 'description': 'Udemy course', 'amount': 50, 'category': 'education', 'merchant': 'Udemy'},
        {'date': '2026-02-04', 'description': 'Gas', 'amount': 45, 'category': 'gas', 'merchant': 'Shell'},
        {'date': '2026-02-05', 'description': 'Office chair', 'amount': 300, 'category': 'work', 'merchant': 'IKEA'},
    ]
    
    # Test categorization
    print("=== Testing Expense Categorization ===")
    for txn in test_txns:
        category = categorizer.categorize(txn['description'], txn['amount'], txn['merchant'])
        print(f"{txn['description']} → {category}")
    
    print("\n=== Testing Tax Deduction Detection ===")
    report = categorizer.generate_monthly_report(test_txns)
    print(f"Total Deductions: ${report['total_deductions']:.2f}")
    print(f"\nTop 3 Categories:")
    for cat, amount in report['top_3_categories']:
        print(f"  {cat}: ${amount:.2f}")
    
    print(f"\n{report['summary']}")
