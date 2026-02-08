#!/usr/bin/env python3
"""
Product Scoring System
Evaluates product ideas against criteria to make better decisions
"""

import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path.home() / "clawd"
SCORES_FILE = WORKSPACE / "memory" / "product_scores.json"

def score_product(name, market_validation, ross_fit, speed_to_revenue, effort):
    """
    Score a product idea on 4 dimensions (0-10 each)
    
    Returns total score (0-10) and recommendation
    """
    total = (market_validation + ross_fit + speed_to_revenue + effort) / 4
    
    if total >= 8:
        recommendation = "BUILD IT - Strong candidate"
    elif total >= 6:
        recommendation = "RECOMMEND - Good option with tradeoffs"
    elif total >= 4:
        recommendation = "MAYBE - Explain concerns"
    else:
        recommendation = "SKIP - Too many weaknesses"
    
    return {
        "name": name,
        "scores": {
            "market_validation": market_validation,
            "ross_fit": ross_fit,
            "speed_to_revenue": speed_to_revenue,
            "effort": effort
        },
        "total": round(total, 1),
        "recommendation": recommendation,
        "timestamp": datetime.now().isoformat()
    }

def log_score(score):
    """Log product score to history"""
    SCORES_FILE.parent.mkdir(exist_ok=True)
    
    history = []
    if SCORES_FILE.exists():
        with open(SCORES_FILE) as f:
            history = json.load(f)
    
    history.append(score)
    
    with open(SCORES_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def compare_products(products):
    """
    Compare multiple products and rank them
    
    products = [
        {name, market_validation, ross_fit, speed_to_revenue, effort},
        ...
    ]
    """
    scored = []
    for p in products:
        score = score_product(
            p['name'],
            p['market_validation'],
            p['ross_fit'],
            p['speed_to_revenue'],
            p['effort']
        )
        scored.append(score)
        log_score(score)
    
    # Sort by total score descending
    scored.sort(key=lambda x: x['total'], reverse=True)
    
    return scored

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Product Scorer - Usage:")
        print()
        print("Score single product:")
        print('  python3 product_scorer.py "Product Name" 8 9 7 6')
        print("  Args: market_validation ross_fit speed_to_revenue effort (0-10 each)")
        print()
        print("Example comparisons:")
        print('  python3 product_scorer.py compare')
        sys.exit(1)
    
    if sys.argv[1] == "compare":
        # Example comparison from tonight
        products = [
            {
                "name": "Volleyball Template",
                "market_validation": 6,
                "ross_fit": 5,
                "speed_to_revenue": 4,
                "effort": 6
            },
            {
                "name": "Fitness Tracker + Stripe",
                "market_validation": 8,
                "ross_fit": 10,
                "speed_to_revenue": 9,
                "effort": 7
            },
            {
                "name": "Action Plan + Revenue Dashboard",
                "market_validation": 7,
                "ross_fit": 10,
                "speed_to_revenue": 3,
                "effort": 8
            }
        ]
        
        results = compare_products(products)
        
        print("🎯 Product Comparison:\n")
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['name']}: {r['total']}/10")
            print(f"   {r['recommendation']}")
            print(f"   Market: {r['scores']['market_validation']}/10 | "
                  f"Fit: {r['scores']['ross_fit']}/10 | "
                  f"Speed: {r['scores']['speed_to_revenue']}/10 | "
                  f"Effort: {r['scores']['effort']}/10")
            print()
        
        print(f"✅ Winner: {results[0]['name']}")
        
    else:
        # Score single product
        name = sys.argv[1]
        market = int(sys.argv[2])
        fit = int(sys.argv[3])
        speed = int(sys.argv[4])
        effort = int(sys.argv[5])
        
        score = score_product(name, market, fit, speed, effort)
        log_score(score)
        
        print(f"\n🎯 Product Score: {name}")
        print(f"   Total: {score['total']}/10")
        print(f"   {score['recommendation']}")
        print(f"\n   Breakdown:")
        print(f"   - Market Validation: {market}/10")
        print(f"   - Ross Fit: {fit}/10")
        print(f"   - Speed to Revenue: {speed}/10")
        print(f"   - Effort: {effort}/10")
