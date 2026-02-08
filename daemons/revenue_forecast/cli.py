#!/usr/bin/env python3
"""
CLI tool for revenue forecasting
"""
import sys
import json
from datetime import datetime
from pathlib import Path

# Add daemon directory to path
daemon_dir = Path(__file__).parent
sys.path.insert(0, str(daemon_dir))

from database import RevenueDatabase
from forecaster import RevenueForecast
from stripe_integration import StripeIntegration

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")

def cmd_status(args):
    """Show current revenue status"""
    forecast = RevenueForecast()
    metrics = forecast.db.get_latest_metrics()
    
    if not metrics:
        print("❌ No revenue data available")
        print("Run 'revenue-forecast sync' to fetch data")
        return
    
    print_header("💰 Revenue Forecast Status")
    
    current = metrics['current_mrr']
    target = forecast.config['target_mrr']
    pct = (current / target * 100)
    
    print(f"Current MRR:     ${current:.2f}")
    print(f"Target MRR:      ${target:.2f}")
    print(f"Progress:        {pct:.1f}% {'✅' if pct >= 100 else '🎯'}")
    print(f"Gap:             ${target - current:.2f}")
    
    if metrics.get('customer_count'):
        print(f"Customers:       {metrics['customer_count']}")
    
    print(f"\n📊 Growth Metrics:")
    daily_rate = metrics.get('daily_growth_rate')
    weekly_rate = metrics.get('weekly_growth_rate')
    monthly_proj = metrics.get('monthly_projection')
    
    if daily_rate is not None:
        print(f"Daily Rate:      {daily_rate:+.2f}%")
        print(f"Weekly Rate:     {weekly_rate:+.2f}%")
        print(f"30-day Proj:     ${monthly_proj:.2f}")
    else:
        print(f"Daily Rate:      (need more data)")
        print(f"Weekly Rate:     (need more data)")
        print(f"30-day Proj:     (need more data)")
    
    days = metrics.get('days_to_target')
    if days and days > 0:
        target_date = (datetime.now().timestamp() + days * 86400)
        target_str = datetime.fromtimestamp(target_date).strftime("%B %d, %Y")
        print(f"\n🎯 Target Date:    {target_str} ({days} days)")
    elif current >= target:
        print(f"\n🎉 Target achieved!")
    elif days == -1:
        print(f"\n⚠️  Need positive growth to reach target")
    else:
        print(f"\n📊 Collecting data to calculate projections...")
    
    customers = metrics.get('customers_needed')
    if customers and customers > 0:
        print(f"Customers Needed: {customers} more (at $29/mo avg)")
    
    print(f"\nLast Updated:    {metrics.get('timestamp', 'Unknown')}")

def cmd_sync(args):
    """Sync MRR data from Stripe/mock"""
    print("🔄 Syncing revenue data...")
    
    stripe = StripeIntegration()
    data = stripe.get_current_mrr()
    
    if 'error' in data:
        print(f"❌ Error: {data['error']}")
        return
    
    db = RevenueDatabase()
    db.add_mrr_snapshot(
        mrr_cents=data['mrr_cents'],
        customer_count=data.get('customer_count', 0),
        source=data['source'],
        notes=data.get('note')
    )
    
    print(f"✅ Synced: ${data['mrr_cents']/100:.2f} MRR")
    print(f"   Source: {data['source']}")
    if data.get('customer_count'):
        print(f"   Customers: {data['customer_count']}")
    
    # Update metrics
    forecast = RevenueForecast()
    metrics = forecast.update_metrics()
    
    if 'error' not in metrics:
        print(f"\n📊 Metrics updated")
        if metrics.get('days_to_target', -1) > 0:
            print(f"   Target in {metrics['days_to_target']} days")

def cmd_scenarios(args):
    """Show forecast scenarios"""
    forecast = RevenueForecast()
    scenarios = forecast.generate_all_scenarios()
    
    if not scenarios:
        print("❌ Unable to calculate scenarios (need more data)")
        return
    
    print_header("📈 Forecast Scenarios")
    
    for s in scenarios:
        print(f"{s['message']}")
        print(f"   New MRR: ${s['new_mrr']:.2f}")
        print()

def cmd_brief(args):
    """Generate daily brief update"""
    forecast = RevenueForecast()
    
    # Update metrics first
    metrics = forecast.update_metrics()
    if 'error' in metrics:
        print(f"❌ {metrics['error']}")
        return
    
    # Generate update
    update = forecast.generate_daily_update()
    
    # Save to database
    forecast.db.save_daily_update(update)
    
    print_header("📝 Daily Brief Update")
    print(update)
    print(f"\n✅ Saved to database for morning brief integration")

def cmd_history(args):
    """Show revenue history"""
    days = int(args[0]) if args else 30
    
    db = RevenueDatabase()
    history = db.get_historical_mrr(days)
    
    if not history:
        print(f"❌ No history data for last {days} days")
        return
    
    print_header(f"📊 Revenue History (Last {len(history)} days)")
    
    for h in history:
        mrr = h['avg_mrr_cents'] / 100
        print(f"{h['date']}: ${mrr:>8.2f}")
    
    # Show trend
    if len(history) >= 2:
        first = history[0]['avg_mrr_cents'] / 100
        last = history[-1]['avg_mrr_cents'] / 100
        change = last - first
        pct = (change / first * 100) if first > 0 else 0
        
        print(f"\n{'─' * 40}")
        print(f"Change: ${change:+.2f} ({pct:+.1f}%)")
        trend = "📈 Growing" if change > 0 else "📉 Declining" if change < 0 else "📊 Flat"
        print(f"Trend: {trend}")

def cmd_dashboard(args):
    """Output dashboard widget data"""
    forecast = RevenueForecast()
    data = forecast.get_dashboard_data()
    
    output_file = Path(__file__).parent.parent.parent / "data" / "revenue_forecast_widget.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Dashboard data written to: {output_file}")
    print(f"\n📊 Current Status:")
    if data['status'] == 'ok':
        print(f"   MRR: ${data['current_mrr']:.2f} / ${data['target_mrr']:.2f}")
        print(f"   Progress: {data['pct_complete']:.1f}%")

def cmd_set_mock(args):
    """Set mock data baseline for testing"""
    if len(args) < 2:
        print("Usage: revenue-forecast set-mock <mrr_dollars> <customer_count>")
        return
    
    mrr_dollars = float(args[0])
    customer_count = int(args[1])
    
    stripe = StripeIntegration()
    data = stripe.update_mock_baseline(int(mrr_dollars * 100), customer_count)
    
    print(f"✅ Mock baseline set:")
    print(f"   MRR: ${mrr_dollars:.2f}")
    print(f"   Customers: {customer_count}")
    print(f"   Growth: $0.50/day")

def cmd_help(args):
    """Show help"""
    print_header("Revenue Forecast CLI")
    
    commands = {
        'status': 'Show current revenue status and metrics',
        'sync': 'Sync MRR data from Stripe (or mock data)',
        'scenarios': 'Show forecast scenarios',
        'brief': 'Generate daily brief update',
        'history [days]': 'Show revenue history (default: 30 days)',
        'dashboard': 'Generate dashboard widget data',
        'set-mock <mrr> <customers>': 'Set mock data baseline for testing',
        'help': 'Show this help message'
    }
    
    for cmd, desc in commands.items():
        print(f"  {cmd:<30} {desc}")
    
    print("\nExamples:")
    print("  revenue-forecast status")
    print("  revenue-forecast sync")
    print("  revenue-forecast history 7")
    print("  revenue-forecast set-mock 150 5")

def main():
    commands = {
        'status': cmd_status,
        'sync': cmd_sync,
        'scenarios': cmd_scenarios,
        'brief': cmd_brief,
        'history': cmd_history,
        'dashboard': cmd_dashboard,
        'set-mock': cmd_set_mock,
        'help': cmd_help
    }
    
    if len(sys.argv) < 2:
        cmd_help([])
        return
    
    cmd = sys.argv[1]
    args = sys.argv[2:]
    
    if cmd not in commands:
        print(f"❌ Unknown command: {cmd}")
        print("Run 'revenue-forecast help' for usage")
        return
    
    try:
        commands[cmd](args)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
