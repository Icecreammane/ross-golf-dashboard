#!/usr/bin/env python3
"""
Opportunity Scorer with Decision Log Integration

Enhances opportunity scoring by learning from past decisions:
- Adjusts scores based on historical conversion rates
- Predicts revenue potential using actual outcomes
- Identifies patterns in successful opportunities
- Provides confidence scores for predictions

Integrates with:
- opportunity_aggregator.py (scores opportunities)
- decision_log.py (learns from outcomes)
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from decision_log import DecisionLog

# Paths
WORKSPACE = Path("/Users/clawdbot/clawd")
DATA_DIR = WORKSPACE / "data"
LOG_FILE = WORKSPACE / "logs" / "opportunity-scorer.log"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class OpportunityScorer:
    """Scores opportunities using historical decision data"""
    
    def __init__(self):
        self.decision_log = DecisionLog()
        self.conversion_rates = self._load_conversion_rates()
        self.roi_data = self._load_roi_data()
    
    def _load_conversion_rates(self) -> Dict:
        """Load conversion rates from decision log"""
        rates = self.decision_log.get_conversion_rates()
        
        # Index by source + type for quick lookup
        indexed = {}
        for rate in rates:
            key = f"{rate['source_type']}:{rate['opportunity_type']}"
            indexed[key] = rate
        
        return indexed
    
    def _load_roi_data(self) -> Dict:
        """Load ROI data from decision log"""
        roi = self.decision_log.calculate_roi_by_type()
        
        # Index by source + type
        indexed = {}
        for item in roi:
            key = f"{item['opportunity_source']}:{item['opportunity_type']}"
            indexed[key] = item
        
        return indexed
    
    def score_opportunity(self, opportunity: Dict) -> Dict:
        """
        Score an opportunity using historical data
        
        Args:
            opportunity: Opportunity dict with type, source, content, etc.
        
        Returns:
            Enhanced opportunity dict with:
            - adjusted_score: Score adjusted by historical performance
            - predicted_revenue: Expected revenue based on past outcomes
            - conversion_probability: Likelihood of conversion
            - confidence: Confidence in the prediction
            - reasoning: Why this score was assigned
        """
        opp_type = opportunity.get('type', 'general')
        source = opportunity.get('source', 'unknown')
        base_score = opportunity.get('score', 50)
        
        key = f"{source}:{opp_type}"
        
        # Get historical conversion rate
        conversion_data = self.conversion_rates.get(key)
        roi_data = self.roi_data.get(key)
        
        # Get prediction from decision log
        prediction = self.decision_log.predict_outcome(opportunity)
        
        # Calculate adjusted score
        adjusted_score = self._calculate_adjusted_score(
            base_score=base_score,
            conversion_data=conversion_data,
            roi_data=roi_data,
            prediction=prediction
        )
        
        # Build enhanced opportunity
        enhanced = opportunity.copy()
        enhanced.update({
            'original_score': base_score,
            'adjusted_score': adjusted_score,
            'predicted_revenue': prediction['predicted_revenue'],
            'conversion_probability': prediction['conversion_probability'],
            'prediction_confidence': prediction['confidence'],
            'historical_data': {
                'conversion_rate': conversion_data['conversion_rate'] if conversion_data else 0,
                'avg_revenue': roi_data['avg_revenue_per_decision'] if roi_data else 0,
                'sample_size': prediction['similar_count']
            },
            'reasoning': self._generate_reasoning(
                base_score, adjusted_score, conversion_data, roi_data, prediction
            ),
            'recommendation': self._get_recommendation(adjusted_score, prediction)
        })
        
        return enhanced
    
    def _calculate_adjusted_score(
        self,
        base_score: int,
        conversion_data: Optional[Dict],
        roi_data: Optional[Dict],
        prediction: Dict
    ) -> int:
        """
        Calculate adjusted score based on historical performance
        
        Scoring factors:
        - Base score from aggregator (40% weight)
        - Conversion rate (30% weight)
        - Average revenue (20% weight)
        - Prediction confidence (10% weight)
        """
        
        # Start with base score (40% weight)
        score = base_score * 0.4
        
        # Add conversion rate component (30% weight)
        if conversion_data and conversion_data['total_decisions'] >= 3:
            # Scale conversion rate (0-100%) to 0-30 points
            conversion_component = (conversion_data['conversion_rate'] / 100) * 30
            score += conversion_component
        else:
            # No data - use base score for this component
            score += base_score * 0.3
        
        # Add revenue component (20% weight)
        if roi_data and roi_data['decisions_made'] >= 3:
            # Scale revenue ($0-1000) to 0-20 points
            avg_revenue = roi_data['avg_revenue_per_decision']
            revenue_component = min(avg_revenue / 50, 20)  # $50 = 1 point, cap at 20
            score += revenue_component
        else:
            # No data - use base score
            score += base_score * 0.2
        
        # Add confidence component (10% weight)
        confidence_component = prediction['confidence'] * 10
        score += confidence_component
        
        # Ensure score is in 0-100 range
        return max(0, min(100, int(score)))
    
    def _generate_reasoning(
        self,
        base_score: int,
        adjusted_score: int,
        conversion_data: Optional[Dict],
        roi_data: Optional[Dict],
        prediction: Dict
    ) -> str:
        """Generate human-readable reasoning for the score"""
        
        reasons = []
        
        # Score change
        if adjusted_score > base_score + 5:
            reasons.append(f"Score increased from {base_score} to {adjusted_score} based on strong historical performance")
        elif adjusted_score < base_score - 5:
            reasons.append(f"Score decreased from {base_score} to {adjusted_score} based on weak historical performance")
        else:
            reasons.append(f"Score maintained at {adjusted_score} (similar to base score)")
        
        # Conversion data
        if conversion_data and conversion_data['total_decisions'] >= 3:
            rate = conversion_data['conversion_rate']
            if rate >= 60:
                reasons.append(f"High conversion rate: {rate:.1f}% ({conversion_data['total_decisions']} past opportunities)")
            elif rate >= 30:
                reasons.append(f"Moderate conversion rate: {rate:.1f}% ({conversion_data['total_decisions']} past opportunities)")
            else:
                reasons.append(f"Low conversion rate: {rate:.1f}% ({conversion_data['total_decisions']} past opportunities)")
        else:
            reasons.append("Limited historical data - score based on content analysis")
        
        # Revenue data
        if roi_data and roi_data['decisions_made'] >= 3:
            avg_rev = roi_data['avg_revenue_per_decision']
            if avg_rev >= 200:
                reasons.append(f"High revenue potential: avg ${avg_rev:.2f} per opportunity")
            elif avg_rev >= 50:
                reasons.append(f"Moderate revenue potential: avg ${avg_rev:.2f} per opportunity")
            else:
                reasons.append(f"Low revenue potential: avg ${avg_rev:.2f} per opportunity")
        
        # Prediction insight
        if prediction['similar_count'] >= 5:
            reasons.append(f"Prediction based on {prediction['similar_count']} similar opportunities")
            if prediction['conversion_probability'] >= 60:
                reasons.append(f"Strong likelihood of conversion ({prediction['conversion_probability']:.0f}%)")
        
        return " • ".join(reasons)
    
    def _get_recommendation(self, score: int, prediction: Dict) -> str:
        """Get action recommendation based on score and prediction"""
        
        if score >= 85 and prediction['conversion_probability'] >= 60:
            return "HIGH PRIORITY - Respond immediately, high conversion likelihood"
        elif score >= 70:
            return "MEDIUM-HIGH - Respond within 24 hours"
        elif score >= 50:
            return "MEDIUM - Review and respond within 2-3 days"
        elif score >= 30:
            return "LOW - Consider if time permits"
        else:
            return "VERY LOW - Likely not worth pursuing"
    
    def score_opportunities_batch(self, opportunities: List[Dict]) -> List[Dict]:
        """Score multiple opportunities and sort by adjusted score"""
        
        logger.info(f"Scoring {len(opportunities)} opportunities...")
        
        scored = []
        for opp in opportunities:
            enhanced = self.score_opportunity(opp)
            scored.append(enhanced)
        
        # Sort by adjusted score (descending)
        scored.sort(key=lambda x: x['adjusted_score'], reverse=True)
        
        logger.info(f"✅ Scored and ranked {len(scored)} opportunities")
        
        return scored
    
    def generate_scoring_report(self, opportunities: List[Dict]) -> Dict:
        """Generate a comprehensive scoring report"""
        
        scored = self.score_opportunities_batch(opportunities)
        
        # Categorize by priority
        high_priority = [o for o in scored if o['adjusted_score'] >= 80]
        medium_priority = [o for o in scored if 50 <= o['adjusted_score'] < 80]
        low_priority = [o for o in scored if o['adjusted_score'] < 50]
        
        # Calculate stats
        avg_score = sum(o['adjusted_score'] for o in scored) / len(scored) if scored else 0
        total_predicted_revenue = sum(o['predicted_revenue'] for o in scored)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_opportunities': len(scored),
            'average_score': round(avg_score, 1),
            'total_predicted_revenue': round(total_predicted_revenue, 2),
            'priority_breakdown': {
                'high': len(high_priority),
                'medium': len(medium_priority),
                'low': len(low_priority)
            },
            'top_opportunities': scored[:5],  # Top 5
            'scoring_model_version': '1.0',
            'data_sources': {
                'conversion_metrics': len(self.conversion_rates),
                'roi_data_points': len(self.roi_data)
            }
        }
        
        return report
    
    def close(self):
        """Close database connection"""
        self.decision_log.close()


def main():
    """CLI interface"""
    import sys
    
    scorer = OpportunityScorer()
    
    # Load opportunities from aggregator output
    opps_file = DATA_DIR / "opportunities.json"
    
    if not opps_file.exists():
        print(f"❌ Opportunities file not found: {opps_file}")
        print("Run opportunity_aggregator.py first")
        sys.exit(1)
    
    with open(opps_file, 'r') as f:
        data = json.load(f)
    
    opportunities = data.get('opportunities', [])
    
    if not opportunities:
        print("No opportunities to score")
        sys.exit(0)
    
    # Generate scoring report
    report = scorer.generate_scoring_report(opportunities)
    
    # Save enhanced opportunities
    enhanced_file = DATA_DIR / "opportunities_scored.json"
    with open(enhanced_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 OPPORTUNITY SCORING REPORT")
    print(f"   Total opportunities: {report['total_opportunities']}")
    print(f"   Average score: {report['average_score']}")
    print(f"   Predicted revenue: ${report['total_predicted_revenue']:.2f}")
    print(f"\n   Priority breakdown:")
    print(f"     High (80+): {report['priority_breakdown']['high']}")
    print(f"     Medium (50-79): {report['priority_breakdown']['medium']}")
    print(f"     Low (<50): {report['priority_breakdown']['low']}")
    print(f"\n   Top 5 opportunities:")
    
    for i, opp in enumerate(report['top_opportunities'], 1):
        print(f"\n   {i}. {opp['type']} from {opp['source']} (score: {opp['adjusted_score']})")
        print(f"      {opp['recommendation']}")
        print(f"      Predicted revenue: ${opp['predicted_revenue']:.2f}")
        print(f"      {opp['reasoning'][:100]}...")
    
    print(f"\n✅ Saved to {enhanced_file}")
    
    scorer.close()


if __name__ == "__main__":
    main()
