#!/usr/bin/env python3
"""
Example integration for morning brief daemon

Drop this into your morning brief generation script:
"""

import sys
from pathlib import Path

# Add daemon directory to path
daemon_dir = Path(__file__).parent
sys.path.insert(0, str(daemon_dir))

from forecaster import RevenueForecast

def get_revenue_brief_update():
    """
    Get one-sentence revenue update for morning brief
    
    Returns:
        str: One-sentence update like:
             "📈 Revenue: $165/500 MRR (33%) - Hit $500 on Apr 15"
    
    Usage in morning brief:
        revenue_update = get_revenue_brief_update()
        brief_sections.append(revenue_update)
    """
    try:
        forecast = RevenueForecast()
        
        # Update metrics (if needed)
        forecast.update_metrics()
        
        # Generate and save update
        update = forecast.generate_daily_update()
        forecast.db.save_daily_update(update)
        
        return update
        
    except Exception as e:
        # Graceful fallback if forecasting fails
        return f"💰 Revenue: (tracking error: {str(e)})"

def get_revenue_detailed():
    """
    Get detailed revenue status for expanded morning brief
    
    Returns:
        dict: Full metrics including growth rates, scenarios, etc.
    """
    try:
        forecast = RevenueForecast()
        metrics = forecast.update_metrics()
        scenarios = forecast.generate_all_scenarios()
        
        return {
            'current_mrr': metrics['current_mrr'],
            'target_mrr': metrics['target_mrr'],
            'pct_complete': (metrics['current_mrr'] / metrics['target_mrr'] * 100),
            'daily_growth_rate': metrics.get('daily_growth_rate'),
            'weekly_growth_rate': metrics.get('weekly_growth_rate'),
            'days_to_target': metrics.get('days_to_target'),
            'customers_needed': metrics.get('customers_needed'),
            'scenarios': scenarios
        }
        
    except Exception as e:
        return {'error': str(e)}

# Example usage in morning brief:
if __name__ == '__main__':
    # Simple one-liner
    print(get_revenue_brief_update())
    
    # Or detailed version
    print("\nDetailed:")
    details = get_revenue_detailed()
    if 'error' not in details:
        print(f"Current: ${details['current_mrr']:.2f}")
        print(f"Progress: {details['pct_complete']:.1f}%")
        if details['days_to_target'] and details['days_to_target'] > 0:
            print(f"Target in: {details['days_to_target']} days")
        print(f"\nBest scenario: {details['scenarios'][0]['message']}")
