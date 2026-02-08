#!/usr/bin/env python3
"""
Test Decision Log System

Populates the decision log with realistic sample data:
- Various opportunity types (coaching, partnerships, feedback)
- Different sources (Twitter, email, revenue dashboard)
- Outcomes with varying success rates
- Revenue generation tracking
- Time-to-conversion tracking

Tests all major features:
- Decision logging
- Outcome recording
- Conversion rate calculation
- ROI analysis
- Insight generation
- Prediction engine
- Daily summaries
"""

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib
from decision_log import DecisionLog
from opportunity_scorer import OpportunityScorer
from decision_summary import DecisionSummaryGenerator

# Sample data templates
SAMPLE_OPPORTUNITIES = {
    'golf_coaching': {
        'twitter': [
            "Hey @jarvis, I saw your swing analysis posts. Can you help me fix my slice?",
            "Looking for a golf coach to improve my handicap. Your content is great!",
            "Do you offer 1-on-1 coaching? Want to work on my putting game"
        ],
        'email': [
            "Golf Coaching Inquiry - I'm interested in improving my game",
            "Coaching Request - 15 handicap looking to break 80",
            "Personal Golf Lessons - Can you help with my short game?"
        ]
    },
    'partnership': {
        'twitter': [
            "Want to collaborate on a golf fitness program?",
            "Let's partner up - I run a golf equipment company",
            "Interested in doing a joint webinar on golf analytics?"
        ],
        'email': [
            "Partnership Opportunity - Golf Analytics Platform",
            "Collaboration Proposal - Fitness + Golf Content",
            "Business Partnership - Golf Course Management Software"
        ]
    },
    'product_feedback': {
        'twitter': [
            "Tried your swing analyzer - here's some feedback...",
            "Love the app but have a feature request",
            "Bug report: The distance calculator seems off"
        ],
        'email': [
            "Feedback on your Golf Tracker",
            "Feature Request - Export to CSV",
            "Suggestion: Add weather integration"
        ]
    },
    'coaching': {
        'twitter': [
            "Can you help me build a fitness routine?",
            "Looking for someone to help me optimize my workout schedule",
            "Need coaching on nutrition and training"
        ],
        'email': [
            "Fitness Coaching Request",
            "Personal Training Inquiry - Online Sessions",
            "Nutrition and Workout Plan Needed"
        ]
    }
}

# Realistic conversion rates by type and source
CONVERSION_RATES = {
    ('twitter', 'golf_coaching'): 0.65,     # Twitter golf coaching converts well
    ('email', 'golf_coaching'): 0.75,       # Email golf coaching even better
    ('twitter', 'partnership'): 0.35,        # Partnerships are hit or miss
    ('email', 'partnership'): 0.45,
    ('twitter', 'product_feedback'): 0.10,   # Feedback rarely converts
    ('email', 'product_feedback'): 0.15,
    ('twitter', 'coaching'): 0.50,           # General coaching moderate
    ('email', 'coaching'): 0.60
}

# Revenue ranges by type
REVENUE_RANGES = {
    'golf_coaching': (150, 800),
    'coaching': (100, 500),
    'partnership': (200, 1000),
    'product_feedback': (0, 50)
}

# Time to conversion (in hours) by type
TIME_TO_CONVERSION = {
    'golf_coaching': (12, 72),      # 0.5-3 days
    'coaching': (24, 96),            # 1-4 days
    'partnership': (120, 720),       # 5-30 days
    'product_feedback': (1, 24)      # Quick feedback loop
}


def generate_decision_id(content: str, timestamp: str) -> str:
    """Generate unique decision ID"""
    data = f"{content}{timestamp}".encode()
    return hashlib.md5(data).hexdigest()[:16]


def generate_sample_data(decision_log: DecisionLog, days: int = 30):
    """
    Generate sample decision data for the past N days
    
    Args:
        decision_log: DecisionLog instance
        days: Number of days of historical data to generate
    """
    print(f"\n🎲 Generating {days} days of sample decision data...\n")
    
    total_decisions = 0
    total_outcomes = 0
    total_revenue = 0
    
    for day_offset in range(days, 0, -1):
        # Generate 1-5 decisions per day
        decisions_today = random.randint(1, 5)
        
        for _ in range(decisions_today):
            # Choose random opportunity type and source
            opp_type = random.choice(list(SAMPLE_OPPORTUNITIES.keys()))
            source = random.choice(['twitter', 'email'])
            
            # Get sample content
            content = random.choice(SAMPLE_OPPORTUNITIES[opp_type][source])
            
            # Generate timestamp for this decision (random time during the day)
            decision_date = datetime.now(timezone.utc) - timedelta(days=day_offset)
            random_hour = random.randint(8, 20)
            random_minute = random.randint(0, 59)
            decision_date = decision_date.replace(hour=random_hour, minute=random_minute)
            
            # Create decision
            decision_id = generate_decision_id(content, decision_date.isoformat())
            
            # Determine action based on type
            if opp_type in ['golf_coaching', 'coaching']:
                action = "Replied with coaching offer and availability"
            elif opp_type == 'partnership':
                action = "Scheduled call to discuss partnership"
            else:
                action = "Sent thank you and acknowledged feedback"
            
            # Log decision
            success = decision_log.log_decision(
                decision_id=decision_id,
                opportunity_type=opp_type,
                opportunity_source=source,
                action_taken=action,
                opportunity_content=content,
                opportunity_score=random.randint(60, 95),
                sender=f"user_{random.randint(1000, 9999)}",
                decision_maker="jarvis",
                context={'test_data': True}
            )
            
            if success:
                total_decisions += 1
                
                # Determine if this converts based on realistic conversion rates
                key = (source, opp_type)
                conversion_rate = CONVERSION_RATES.get(key, 0.3)
                converts = random.random() < conversion_rate
                
                if converts:
                    # Generate outcome
                    revenue_range = REVENUE_RANGES.get(opp_type, (0, 100))
                    revenue = random.uniform(*revenue_range)
                    
                    # Time to conversion
                    time_range = TIME_TO_CONVERSION.get(opp_type, (24, 168))
                    time_to_outcome = random.uniform(*time_range)
                    
                    # Record outcome (backdated)
                    # Outcome happens some time after decision
                    outcome_success = decision_log.record_outcome(
                        decision_id=decision_id,
                        outcome_type='conversion',
                        outcome_status='success',
                        revenue_generated=revenue,
                        customer_acquired=True,
                        deal_closed=True,
                        response_received=True,
                        notes=f"Test data: {opp_type} from {source}"
                    )
                    
                    if outcome_success:
                        total_outcomes += 1
                        total_revenue += revenue
                        print(f"  ✅ {decision_date.strftime('%Y-%m-%d')}: {opp_type} from {source} → ${revenue:.2f} ({time_to_outcome/24:.1f} days)")
                else:
                    # No conversion - still record response if applicable
                    if random.random() < 0.7:  # 70% get a response even if no conversion
                        decision_log.record_outcome(
                            decision_id=decision_id,
                            outcome_type='response',
                            outcome_status='no_conversion',
                            revenue_generated=0,
                            customer_acquired=False,
                            deal_closed=False,
                            response_received=True,
                            notes="Responded but did not convert"
                        )
                        total_outcomes += 1
                        print(f"  ↔️  {decision_date.strftime('%Y-%m-%d')}: {opp_type} from {source} → No conversion")
    
    print(f"\n📊 Sample Data Summary:")
    print(f"   Total decisions: {total_decisions}")
    print(f"   Total outcomes: {total_outcomes}")
    print(f"   Total revenue: ${total_revenue:.2f}")
    print(f"   Avg revenue per decision: ${total_revenue/total_decisions:.2f}")


def test_conversion_rates(decision_log: DecisionLog):
    """Test conversion rate calculations"""
    print("\n📈 CONVERSION RATES TEST\n")
    
    rates = decision_log.get_conversion_rates()
    
    if not rates:
        print("❌ No conversion data found")
        return
    
    print("Source → Type | Rate | Decisions | Revenue")
    print("-" * 60)
    for rate in rates:
        print(f"{rate['source_type']:8} → {rate['opportunity_type']:20} | "
              f"{rate['conversion_rate']:5.1f}% | {rate['total_decisions']:9} | "
              f"${rate['total_revenue']:8.2f}")


def test_roi_analysis(decision_log: DecisionLog):
    """Test ROI calculations"""
    print("\n💰 ROI ANALYSIS TEST\n")
    
    roi_data = decision_log.calculate_roi_by_type()
    
    if not roi_data:
        print("❌ No ROI data found")
        return
    
    print("Type | Source | Total Revenue | Avg/Decision | Decisions | Closed")
    print("-" * 80)
    for roi in roi_data:
        print(f"{roi['opportunity_type']:20} | {roi['opportunity_source']:8} | "
              f"${roi['total_revenue']:12.2f} | ${roi['avg_revenue_per_decision']:11.2f} | "
              f"{roi['decisions_made']:9} | {roi['closed_deals']:6}")


def test_insights(decision_log: DecisionLog):
    """Test insight generation"""
    print("\n💡 INSIGHTS TEST\n")
    
    insights = decision_log.generate_insights()
    
    if not insights:
        print("❌ No insights generated")
        return
    
    for i, insight in enumerate(insights, 1):
        print(f"{i}. {insight['title']}")
        print(f"   {insight['description']}")
        print(f"   Confidence: {insight['confidence']*100:.0f}% ({insight['data_points']} data points)")
        print()


def test_predictions(decision_log: DecisionLog):
    """Test prediction engine"""
    print("\n🔮 PREDICTION ENGINE TEST\n")
    
    # Test predictions for different opportunity types
    test_opportunities = [
        {'type': 'golf_coaching', 'source': 'twitter', 'content': 'Can you help with my golf swing?'},
        {'type': 'golf_coaching', 'source': 'email', 'content': 'Golf coaching inquiry'},
        {'type': 'partnership', 'source': 'twitter', 'content': 'Want to collaborate?'},
        {'type': 'product_feedback', 'source': 'email', 'content': 'Feature request'}
    ]
    
    for opp in test_opportunities:
        prediction = decision_log.predict_outcome(opp)
        
        print(f"Opportunity: {opp['type']} from {opp['source']}")
        print(f"  Conversion probability: {prediction['conversion_probability']:.1f}%")
        print(f"  Predicted revenue: ${prediction['predicted_revenue']:.2f}")
        print(f"  Avg time to close: {prediction.get('avg_time_to_close_days', 0):.1f} days")
        print(f"  Confidence: {prediction['confidence']*100:.0f}%")
        print(f"  Reasoning: {prediction['reasoning']}")
        print()


def test_opportunity_scoring(scorer: OpportunityScorer):
    """Test opportunity scorer with decision log integration"""
    print("\n🎯 OPPORTUNITY SCORING TEST\n")
    
    # Create test opportunities
    test_opportunities = [
        {
            'type': 'golf_coaching',
            'source': 'email',
            'score': 85,
            'content': 'Looking for golf coaching to improve my handicap',
            'sender': 'john_doe@example.com'
        },
        {
            'type': 'partnership',
            'source': 'twitter',
            'score': 70,
            'content': 'Want to collaborate on golf content?',
            'sender': '@golf_pro_tips'
        },
        {
            'type': 'product_feedback',
            'source': 'email',
            'score': 40,
            'content': 'Feature request for your app',
            'sender': 'user123@example.com'
        }
    ]
    
    for opp in test_opportunities:
        enhanced = scorer.score_opportunity(opp)
        
        print(f"Opportunity: {enhanced['type']} from {enhanced['source']}")
        print(f"  Original score: {enhanced['original_score']}")
        print(f"  Adjusted score: {enhanced['adjusted_score']}")
        print(f"  Predicted revenue: ${enhanced['predicted_revenue']:.2f}")
        print(f"  Conversion probability: {enhanced['conversion_probability']:.1f}%")
        print(f"  Recommendation: {enhanced['recommendation']}")
        print(f"  Reasoning: {enhanced['reasoning'][:150]}...")
        print()


def test_daily_summary(generator: DecisionSummaryGenerator):
    """Test daily summary generation"""
    print("\n📊 DAILY SUMMARY TEST\n")
    
    # Get summary for today
    summary = generator.generate_daily_summary()
    
    print(summary['performance_summary'])
    
    # Save summary
    json_file, md_file = generator.save_summary(summary)
    print(f"\n✅ Saved to {json_file} and {md_file}")


def main():
    """Run all tests"""
    print("=" * 80)
    print("🧪 DECISION LOG SYSTEM TEST SUITE")
    print("=" * 80)
    
    # Initialize components
    decision_log = DecisionLog()
    scorer = OpportunityScorer()
    generator = DecisionSummaryGenerator()
    
    # Generate sample data
    generate_sample_data(decision_log, days=30)
    
    # Run tests
    test_conversion_rates(decision_log)
    test_roi_analysis(decision_log)
    test_insights(decision_log)
    test_predictions(decision_log)
    test_opportunity_scoring(scorer)
    test_daily_summary(generator)
    
    # Cleanup
    decision_log.close()
    scorer.close()
    generator.close()
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)
    print("\nDatabase location:", decision_log.db_path)
    print("Reports location:", generator.REPORTS_DIR)
    print("\nNext steps:")
    print("1. Review generated reports in", generator.REPORTS_DIR)
    print("2. Run: python3 scripts/decision_summary.py")
    print("3. Check conversion rates: python3 scripts/decision_log.py conversions")
    print("4. Generate insights: python3 scripts/decision_log.py insights")


if __name__ == "__main__":
    main()
