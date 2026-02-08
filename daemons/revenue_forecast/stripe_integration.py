#!/usr/bin/env python3
"""
Stripe integration for automatic MRR tracking
Falls back to mock data when Stripe is not configured
"""
import os
import json
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

class StripeIntegration:
    def __init__(self, config_path: str = None):
        if not config_path:
            config_path = Path(__file__).parent / "config.json"
        
        with open(config_path) as f:
            self.config = json.load(f)
        
        self.mock_mode = self.config.get('mock_mode', True)
        self.stripe_enabled = self.config.get('stripe_enabled', False)
        
        # Try to load Stripe if enabled
        if self.stripe_enabled and not self.mock_mode:
            try:
                import stripe
                stripe.api_key = os.getenv('STRIPE_API_KEY')
                self.stripe = stripe
                self.mock_mode = False
            except ImportError:
                print("Warning: stripe package not installed, using mock mode")
                self.mock_mode = True
            except Exception as e:
                print(f"Warning: Stripe setup failed ({e}), using mock mode")
                self.mock_mode = True
    
    def get_current_mrr(self) -> Dict:
        """Get current MRR from Stripe or mock data"""
        if self.mock_mode:
            return self._get_mock_mrr()
        else:
            return self._get_stripe_mrr()
    
    def _get_stripe_mrr(self) -> Dict:
        """Fetch actual MRR from Stripe"""
        try:
            # Get all active subscriptions
            subscriptions = self.stripe.Subscription.list(
                status='active',
                limit=100
            )
            
            total_mrr_cents = 0
            customer_count = 0
            
            for sub in subscriptions.auto_paging_iter():
                # Sum up all subscription items
                for item in sub['items']['data']:
                    # Get the recurring amount
                    amount = item['price']['unit_amount']
                    quantity = item['quantity']
                    interval = item['price']['recurring']['interval']
                    
                    # Convert to monthly
                    if interval == 'month':
                        monthly_amount = amount * quantity
                    elif interval == 'year':
                        monthly_amount = (amount * quantity) / 12
                    elif interval == 'week':
                        monthly_amount = (amount * quantity) * 4.33
                    elif interval == 'day':
                        monthly_amount = (amount * quantity) * 30
                    else:
                        monthly_amount = 0
                    
                    total_mrr_cents += monthly_amount
                
                customer_count += 1
            
            return {
                'mrr_cents': int(total_mrr_cents),
                'customer_count': customer_count,
                'source': 'stripe',
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"Error fetching Stripe data: {e}")
            return {
                'error': str(e),
                'mrr_cents': 0,
                'customer_count': 0,
                'source': 'stripe_error'
            }
    
    def _get_mock_mrr(self) -> Dict:
        """Generate mock MRR data for testing"""
        # Load or create mock data file
        mock_file = Path(__file__).parent.parent.parent / "data" / "mock_revenue.json"
        mock_file.parent.mkdir(parents=True, exist_ok=True)
        
        if mock_file.exists():
            with open(mock_file) as f:
                mock_data = json.load(f)
        else:
            # Initialize with starting data
            mock_data = {
                'base_mrr_cents': 15000,  # $150 starting MRR
                'customer_count': 5,
                'daily_growth_cents': 50,  # $0.50/day growth
                'start_date': datetime.now().strftime("%Y-%m-%d")
            }
            with open(mock_file, 'w') as f:
                json.dump(mock_data, f, indent=2)
        
        # Calculate current mock MRR based on days since start
        start = datetime.fromisoformat(mock_data['start_date'])
        days_elapsed = (datetime.now() - start).days
        
        current_mrr = mock_data['base_mrr_cents'] + (days_elapsed * mock_data['daily_growth_cents'])
        
        # Add some randomness (±5%)
        import random
        variance = random.uniform(-0.05, 0.05)
        current_mrr = int(current_mrr * (1 + variance))
        
        return {
            'mrr_cents': current_mrr,
            'customer_count': mock_data['customer_count'] + (days_elapsed // 7),
            'source': 'mock',
            'timestamp': datetime.now().isoformat(),
            'note': 'Mock data for testing - configure Stripe for real data'
        }
    
    def update_mock_baseline(self, mrr_cents: int, customer_count: int):
        """Update mock data baseline (for testing)"""
        mock_file = Path(__file__).parent.parent.parent / "data" / "mock_revenue.json"
        mock_file.parent.mkdir(parents=True, exist_ok=True)
        
        mock_data = {
            'base_mrr_cents': mrr_cents,
            'customer_count': customer_count,
            'daily_growth_cents': 50,
            'start_date': datetime.now().strftime("%Y-%m-%d")
        }
        
        with open(mock_file, 'w') as f:
            json.dump(mock_data, f, indent=2)
        
        return mock_data
