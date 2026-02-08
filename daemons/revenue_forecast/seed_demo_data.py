#!/usr/bin/env python3
"""
Seed the database with realistic demo data for testing
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add daemon directory to path
daemon_dir = Path(__file__).parent
sys.path.insert(0, str(daemon_dir))

from database import RevenueDatabase

def seed_demo_data():
    """Create 30 days of realistic revenue growth data"""
    print("Seeding demo data...")
    
    db = RevenueDatabase()
    
    # Starting point: $150 MRR, 5 customers
    base_mrr = 15000  # cents
    base_customers = 5
    
    # Growth pattern: ~2% weekly growth, some variance
    for i in range(30):
        # Date for this snapshot (going backwards from today)
        date = datetime.now() - timedelta(days=29-i)
        
        # Calculate MRR with growth + some randomness
        import random
        daily_growth = 0.003  # ~0.3% per day = ~2.1% weekly
        growth_factor = (1 + daily_growth) ** i
        variance = random.uniform(-0.03, 0.03)  # ±3% daily variance
        
        mrr = int(base_mrr * growth_factor * (1 + variance))
        
        # Add customers every ~7 days
        customers = base_customers + (i // 7)
        
        # Insert with specific timestamp
        db.add_mrr_snapshot(
            mrr_cents=mrr,
            customer_count=customers,
            source="demo",
            notes=f"Demo data for day {i}",
            timestamp=date.isoformat()
        )
        
        print(f"  Day {i+1}: ${mrr/100:.2f} MRR, {customers} customers")
    
    print("\n✅ Seeded 30 days of demo data")
    print("Run: revenue-forecast status")

if __name__ == '__main__':
    seed_demo_data()
