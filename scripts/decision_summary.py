#!/usr/bin/env python3
"""
Daily Decision Summary Generator

Generates comprehensive daily summaries of:
- Decisions made
- Outcomes recorded
- Revenue generated
- Conversion rates
- Insights and patterns
- Predictions for pending opportunities

Can be run manually or scheduled via cron for daily reports.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from decision_log import DecisionLog
from opportunity_scorer import OpportunityScorer

# Paths
WORKSPACE = Path("/Users/clawdbot/clawd")
REPORTS_DIR = WORKSPACE / "reports" / "decision-summaries"
DATA_DIR = WORKSPACE / "data"

# Ensure directories
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class DecisionSummaryGenerator:
    """Generates daily decision summaries"""
    
    def __init__(self):
        self.decision_log = DecisionLog()
        self.scorer = OpportunityScorer()
    
    def generate_daily_summary(self, date: str = None) -> Dict:
        """
        Generate comprehensive daily summary
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
        
        Returns:
            Summary dict
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Generating decision summary for {date}")
        
        # Get basic daily summary from decision log
        base_summary = self.decision_log.get_daily_summary(date)
        
        # Get detailed decisions for the day
        detailed_decisions = self._get_detailed_decisions(date)
        
        # Get detailed outcomes for the day
        detailed_outcomes = self._get_detailed_outcomes(date)
        
        # Generate insights
        insights = self.decision_log.generate_insights()
        
        # Get ROI breakdown
        roi_breakdown = self.decision_log.calculate_roi_by_type()
        
        # Build comprehensive summary
        summary = {
            'date': date,
            'generated_at': datetime.now().isoformat(),
            'overview': {
                'decisions_made': base_summary['decisions']['count'],
                'outcomes_recorded': base_summary['outcomes']['total'],
                'revenue_generated': base_summary['outcomes']['revenue'],
                'customers_acquired': base_summary['outcomes']['customers'],
                'deals_closed': base_summary['outcomes']['deals_closed']
            },
            'decisions': detailed_decisions,
            'outcomes': detailed_outcomes,
            'insights': insights,
            'conversion_rates': base_summary['conversion_rates'],
            'roi_breakdown': roi_breakdown[:5],  # Top 5
            'performance_summary': self._generate_performance_summary(
                base_summary, detailed_decisions, detailed_outcomes
            )
        }
        
        return summary
    
    def _get_detailed_decisions(self, date: str) -> List[Dict]:
        """Get detailed list of decisions made on date"""
        cursor = self.decision_log.conn.cursor()
        
        cursor.execute("""
            SELECT 
                decision_id,
                timestamp,
                opportunity_type,
                opportunity_source,
                opportunity_content,
                opportunity_score,
                sender,
                action_taken,
                decision_maker
            FROM decisions
            WHERE DATE(timestamp) = ?
            ORDER BY timestamp DESC
        """, (date,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def _get_detailed_outcomes(self, date: str) -> List[Dict]:
        """Get detailed list of outcomes recorded on date"""
        cursor = self.decision_log.conn.cursor()
        
        cursor.execute("""
            SELECT 
                o.decision_id,
                o.outcome_type,
                o.outcome_status,
                o.revenue_generated,
                o.customer_acquired,
                o.deal_closed,
                o.time_to_outcome_hours,
                o.notes,
                d.opportunity_type,
                d.opportunity_source,
                d.sender
            FROM outcomes o
            JOIN decisions d ON o.decision_id = d.decision_id
            WHERE DATE(o.recorded_at) = ?
            ORDER BY o.recorded_at DESC
        """, (date,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def _generate_performance_summary(
        self,
        base_summary: Dict,
        decisions: List[Dict],
        outcomes: List[Dict]
    ) -> str:
        """Generate human-readable performance summary"""
        
        lines = []
        
        # Header
        lines.append(f"📊 DECISION PERFORMANCE SUMMARY")
        lines.append(f"Date: {base_summary['date']}")
        lines.append("")
        
        # Activity overview
        decision_count = base_summary['decisions']['count']
        outcome_count = base_summary['outcomes']['total']
        
        if decision_count == 0 and outcome_count == 0:
            lines.append("No decision activity today.")
            return "\n".join(lines)
        
        if decision_count > 0:
            lines.append(f"🎯 Decisions Made: {decision_count}")
            types = set(d['opportunity_type'] for d in decisions)
            sources = set(d['opportunity_source'] for d in decisions)
            lines.append(f"   Types: {', '.join(types)}")
            lines.append(f"   Sources: {', '.join(sources)}")
            lines.append("")
        
        # Outcomes
        if outcome_count > 0:
            revenue = base_summary['outcomes']['revenue']
            customers = base_summary['outcomes']['customers']
            deals = base_summary['outcomes']['deals_closed']
            
            lines.append(f"📈 Outcomes Recorded: {outcome_count}")
            lines.append(f"   Revenue: ${revenue:.2f}")
            lines.append(f"   New customers: {customers}")
            lines.append(f"   Deals closed: {deals}")
            lines.append("")
            
            # Highlight top outcome
            if outcomes:
                top_outcome = max(outcomes, key=lambda x: x['revenue_generated'] or 0)
                if top_outcome['revenue_generated'] > 0:
                    lines.append(f"🏆 Top Outcome:")
                    lines.append(f"   ${top_outcome['revenue_generated']:.2f} from {top_outcome['opportunity_type']} ({top_outcome['opportunity_source']})")
                    time_days = (top_outcome['time_to_outcome_hours'] or 0) / 24
                    lines.append(f"   Time to close: {time_days:.1f} days")
                    lines.append("")
        
        # Insights
        insights = base_summary.get('insights', [])
        if insights:
            lines.append(f"💡 Key Insights:")
            for insight in insights[:3]:  # Top 3
                lines.append(f"   • {insight['title']}")
            lines.append("")
        
        # Conversion rates
        conv_rates = base_summary.get('conversion_rates', [])
        if conv_rates:
            lines.append(f"🎯 Top Conversion Rates:")
            for rate in conv_rates:
                lines.append(f"   • {rate['source_type']} → {rate['opportunity_type']}: {rate['conversion_rate']:.1f}%")
            lines.append("")
        
        return "\n".join(lines)
    
    def save_summary(self, summary: Dict, date: str = None):
        """Save summary to file"""
        if not date:
            date = summary['date']
        
        # Save as JSON
        json_file = REPORTS_DIR / f"decision-summary-{date}.json"
        with open(json_file, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"✅ Saved JSON summary to {json_file}")
        
        # Save as human-readable markdown
        md_file = REPORTS_DIR / f"decision-summary-{date}.md"
        md_content = self._format_as_markdown(summary)
        with open(md_file, 'w') as f:
            f.write(md_content)
        logger.info(f"✅ Saved markdown summary to {md_file}")
        
        return json_file, md_file
    
    def _format_as_markdown(self, summary: Dict) -> str:
        """Format summary as markdown"""
        
        lines = [
            f"# Decision Summary - {summary['date']}",
            f"*Generated: {datetime.fromisoformat(summary['generated_at']).strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            "## 📊 Overview",
            "",
            f"- **Decisions Made:** {summary['overview']['decisions_made']}",
            f"- **Outcomes Recorded:** {summary['overview']['outcomes_recorded']}",
            f"- **Revenue Generated:** ${summary['overview']['revenue_generated']:.2f}",
            f"- **New Customers:** {summary['overview']['customers_acquired']}",
            f"- **Deals Closed:** {summary['overview']['deals_closed']}",
            ""
        ]
        
        # Decisions
        if summary['decisions']:
            lines.extend([
                "## 🎯 Decisions Made",
                ""
            ])
            for decision in summary['decisions']:
                time = datetime.fromisoformat(decision['timestamp']).strftime('%H:%M')
                lines.append(f"### {time} - {decision['opportunity_type'].replace('_', ' ').title()}")
                lines.append(f"- **Source:** {decision['opportunity_source']}")
                lines.append(f"- **From:** {decision['sender']}")
                lines.append(f"- **Score:** {decision['opportunity_score']}")
                lines.append(f"- **Action:** {decision['action_taken']}")
                if decision['opportunity_content']:
                    lines.append(f"- **Content:** {decision['opportunity_content'][:200]}...")
                lines.append("")
        
        # Outcomes
        if summary['outcomes']:
            lines.extend([
                "## 📈 Outcomes Recorded",
                ""
            ])
            for outcome in summary['outcomes']:
                lines.append(f"### {outcome['outcome_type'].replace('_', ' ').title()}")
                lines.append(f"- **Status:** {outcome['outcome_status']}")
                lines.append(f"- **Revenue:** ${outcome['revenue_generated']:.2f}")
                lines.append(f"- **Customer Acquired:** {'Yes' if outcome['customer_acquired'] else 'No'}")
                lines.append(f"- **Deal Closed:** {'Yes' if outcome['deal_closed'] else 'No'}")
                if outcome['time_to_outcome_hours']:
                    days = outcome['time_to_outcome_hours'] / 24
                    lines.append(f"- **Time to Outcome:** {outcome['time_to_outcome_hours']:.1f}h ({days:.1f} days)")
                lines.append(f"- **Type:** {outcome['opportunity_type']} from {outcome['opportunity_source']}")
                if outcome['notes']:
                    lines.append(f"- **Notes:** {outcome['notes']}")
                lines.append("")
        
        # Insights
        if summary['insights']:
            lines.extend([
                "## 💡 Insights",
                ""
            ])
            for insight in summary['insights']:
                lines.append(f"### {insight['title']}")
                lines.append(f"{insight['description']}")
                lines.append(f"*Confidence: {insight['confidence']*100:.0f}% based on {insight['data_points']} data points*")
                lines.append("")
        
        # Conversion rates
        if summary['conversion_rates']:
            lines.extend([
                "## 🎯 Conversion Rates",
                "",
                "| Source | Type | Rate | Decisions | Revenue |",
                "|--------|------|------|-----------|---------|"
            ])
            for rate in summary['conversion_rates']:
                lines.append(
                    f"| {rate['source_type']} | {rate['opportunity_type']} | "
                    f"{rate['conversion_rate']:.1f}% | {rate['total_decisions']} | "
                    f"${rate['total_revenue']:.2f} |"
                )
            lines.append("")
        
        # ROI breakdown
        if summary['roi_breakdown']:
            lines.extend([
                "## 💰 ROI Breakdown",
                "",
                "| Type | Source | Revenue | Avg/Decision | Decisions | Closed |",
                "|------|--------|---------|--------------|-----------|--------|"
            ])
            for roi in summary['roi_breakdown']:
                lines.append(
                    f"| {roi['opportunity_type']} | {roi['opportunity_source']} | "
                    f"${roi['total_revenue']:.2f} | ${roi['avg_revenue_per_decision']:.2f} | "
                    f"{roi['decisions_made']} | {roi['closed_deals']} |"
                )
            lines.append("")
        
        # Performance summary
        lines.extend([
            "## 📝 Performance Summary",
            "",
            "```",
            summary['performance_summary'],
            "```"
        ])
        
        return "\n".join(lines)
    
    def generate_weekly_summary(self) -> Dict:
        """Generate weekly summary (last 7 days)"""
        logger.info("Generating weekly summary...")
        
        summaries = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            daily = self.generate_daily_summary(date)
            summaries.append(daily)
        
        # Aggregate weekly stats
        total_decisions = sum(s['overview']['decisions_made'] for s in summaries)
        total_revenue = sum(s['overview']['revenue_generated'] for s in summaries)
        total_customers = sum(s['overview']['customers_acquired'] for s in summaries)
        total_deals = sum(s['overview']['deals_closed'] for s in summaries)
        
        # Get current insights
        insights = self.decision_log.generate_insights()
        
        weekly_summary = {
            'period': 'last_7_days',
            'start_date': summaries[-1]['date'],
            'end_date': summaries[0]['date'],
            'generated_at': datetime.now().isoformat(),
            'totals': {
                'decisions': total_decisions,
                'revenue': total_revenue,
                'customers': total_customers,
                'deals_closed': total_deals,
                'avg_decisions_per_day': total_decisions / 7,
                'avg_revenue_per_day': total_revenue / 7
            },
            'daily_summaries': summaries,
            'insights': insights,
            'conversion_rates': self.decision_log.get_conversion_rates(),
            'roi_breakdown': self.decision_log.calculate_roi_by_type()
        }
        
        return weekly_summary
    
    def close(self):
        """Close connections"""
        self.decision_log.close()
        self.scorer.close()


def main():
    """CLI interface"""
    import sys
    
    generator = DecisionSummaryGenerator()
    
    # Parse arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'weekly':
            summary = generator.generate_weekly_summary()
            
            # Save weekly summary
            weekly_file = REPORTS_DIR / f"weekly-summary-{datetime.now().strftime('%Y-W%U')}.json"
            with open(weekly_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            print(f"\n📊 WEEKLY SUMMARY ({summary['start_date']} to {summary['end_date']})")
            print(f"   Total decisions: {summary['totals']['decisions']}")
            print(f"   Total revenue: ${summary['totals']['revenue']:.2f}")
            print(f"   Total customers: {summary['totals']['customers']}")
            print(f"   Avg per day: {summary['totals']['avg_decisions_per_day']:.1f} decisions, ${summary['totals']['avg_revenue_per_day']:.2f}")
            print(f"\n✅ Saved to {weekly_file}")
        
        elif sys.argv[1] == 'date':
            if len(sys.argv) < 3:
                print("Usage: decision_summary.py date YYYY-MM-DD")
                sys.exit(1)
            
            date = sys.argv[2]
            summary = generator.generate_daily_summary(date)
            json_file, md_file = generator.save_summary(summary, date)
            
            print(summary['performance_summary'])
            print(f"\n✅ Saved to {json_file} and {md_file}")
        
        else:
            print("Usage: decision_summary.py [weekly|date YYYY-MM-DD]")
            sys.exit(1)
    
    else:
        # Default: today's summary
        summary = generator.generate_daily_summary()
        json_file, md_file = generator.save_summary(summary)
        
        print(summary['performance_summary'])
        print(f"\n✅ Saved to {json_file} and {md_file}")
    
    generator.close()


if __name__ == "__main__":
    main()
