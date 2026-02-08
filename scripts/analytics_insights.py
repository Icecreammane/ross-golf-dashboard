#!/usr/bin/env python3
"""
Analytics Insights Generator
Generates actionable insights from analytics data
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

# Configure logging
LOG_DIR = Path.home() / "clawd" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "analytics_insights.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("analytics_insights")

# File paths
WORKSPACE = Path.home() / "clawd"
DATA_DIR = WORKSPACE / "data"
ANALYTICS_FILE = DATA_DIR / "analytics.json"
INSIGHTS_FILE = DATA_DIR / "analytics-insights.json"


class InsightsGenerator:
    """Generate actionable insights from analytics"""
    
    def __init__(self):
        self.analytics = self._load_analytics()
        self.insights = []
        logger.info("Insights Generator initialized")
    
    def _load_analytics(self) -> Dict:
        """Load analytics data"""
        if not ANALYTICS_FILE.exists():
            logger.warning("Analytics file not found")
            return {}
        
        try:
            with open(ANALYTICS_FILE) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading analytics: {e}")
            return {}
    
    def _save_insights(self):
        """Save insights to file"""
        try:
            data = {
                "generated_at": datetime.utcnow().isoformat(),
                "insights": self.insights
            }
            with open(INSIGHTS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.insights)} insights")
        except Exception as e:
            logger.error(f"Error saving insights: {e}")
    
    def _add_insight(self, category: str, insight: str, priority: str = "medium", data: Dict = None):
        """Add an insight with metadata"""
        self.insights.append({
            "category": category,
            "insight": insight,
            "priority": priority,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data or {}
        })
        logger.info(f"[{priority.upper()}] {category}: {insight}")
    
    def analyze_conversion_rates(self):
        """Analyze conversion rates by source"""
        try:
            source_perf = self.analytics.get('source_performance', {})
            
            # Calculate conversion rates
            rates = {}
            for source, data in source_perf.items():
                if data['total'] > 0:
                    rate = (data['converted'] / data['total']) * 100
                    rates[source] = {
                        "rate": rate,
                        "total": data['total'],
                        "converted": data['converted'],
                        "revenue": data['revenue']
                    }
            
            if not rates:
                self._add_insight(
                    "conversion",
                    "No conversion data yet. Start tracking opportunities!",
                    "low"
                )
                return
            
            # Find best and worst performers
            sorted_rates = sorted(rates.items(), key=lambda x: x[1]['rate'], reverse=True)
            
            if len(sorted_rates) >= 2:
                best_source = sorted_rates[0]
                worst_source = sorted_rates[-1]
                
                # Generate insight
                if best_source[1]['rate'] > 0:
                    insight = f"{best_source[0].capitalize()} inquiries convert at {best_source[1]['rate']:.0f}%. "
                    insight += f"{worst_source[0].capitalize()} inquiries at {worst_source[1]['rate']:.0f}%. "
                    
                    if best_source[1]['rate'] > worst_source[1]['rate'] * 1.5:
                        insight += f"Focus on {best_source[0]} - it's {(best_source[1]['rate'] / max(worst_source[1]['rate'], 1)):.1f}x better!"
                        priority = "high"
                    else:
                        insight += f"Both channels performing similarly."
                        priority = "medium"
                    
                    self._add_insight(
                        "conversion",
                        insight,
                        priority,
                        {"rates": rates}
                    )
            
            # Revenue insights
            total_revenue = sum(r['revenue'] for r in rates.values())
            if total_revenue > 0:
                revenue_by_source = sorted(rates.items(), key=lambda x: x[1]['revenue'], reverse=True)
                top_revenue = revenue_by_source[0]
                
                self._add_insight(
                    "revenue",
                    f"{top_revenue[0].capitalize()} generated ${top_revenue[1]['revenue']:.0f} ({(top_revenue[1]['revenue']/total_revenue*100):.0f}% of total). Primary revenue driver.",
                    "high",
                    {"revenue_breakdown": {k: v['revenue'] for k, v in rates.items()}}
                )
        
        except Exception as e:
            logger.error(f"Error analyzing conversion rates: {e}")
    
    def analyze_posting_times(self):
        """Analyze best times to post"""
        try:
            engagement_by_hour = self.analytics.get('engagement_by_hour', {})
            
            # Calculate average engagement per post for each hour
            hourly_data = []
            for hour, data in engagement_by_hour.items():
                if data['posts'] > 0:
                    avg_engagement = data['engagement'] / data['posts']
                    hourly_data.append({
                        "hour": int(hour),
                        "avg_engagement": avg_engagement,
                        "posts": data['posts'],
                        "total_engagement": data['engagement']
                    })
            
            if not hourly_data:
                self._add_insight(
                    "posting_time",
                    "Not enough social post data yet. Track more posts to find best times.",
                    "low"
                )
                return
            
            # Find best performing hours
            sorted_hours = sorted(hourly_data, key=lambda x: x['avg_engagement'], reverse=True)
            
            if len(sorted_hours) >= 3:
                top3 = sorted_hours[:3]
                
                # Convert to readable time
                def hour_to_time(h):
                    return f"{h % 12 or 12}{'am' if h < 12 else 'pm'}"
                
                best_hour = top3[0]
                insight = f"Posts at {hour_to_time(best_hour['hour'])} get {best_hour['avg_engagement']:.0f} avg engagement. "
                
                # Check if there's a clear winner
                if best_hour['avg_engagement'] > top3[1]['avg_engagement'] * 1.5:
                    insight += f"That's 1.5x better than {hour_to_time(top3[1]['hour'])}. Schedule posts there!"
                    priority = "high"
                else:
                    top_times = [hour_to_time(t['hour']) for t in top3]
                    insight += f"Top times: {', '.join(top_times)}."
                    priority = "medium"
                
                self._add_insight(
                    "posting_time",
                    insight,
                    priority,
                    {"top_hours": [{"hour": t['hour'], "engagement": t['avg_engagement']} for t in top3]}
                )
        
        except Exception as e:
            logger.error(f"Error analyzing posting times: {e}")
    
    def analyze_opportunity_quality(self):
        """Analyze quality of opportunities by type"""
        try:
            opportunities = self.analytics.get('opportunities', [])
            
            if not opportunities:
                return
            
            # Group by type
            by_type = defaultdict(list)
            for opp in opportunities:
                by_type[opp.get('type', 'unknown')].append(opp)
            
            # Analyze each type
            type_performance = {}
            for opp_type, opps in by_type.items():
                converted = sum(1 for o in opps if o.get('converted'))
                total = len(opps)
                rate = (converted / total * 100) if total > 0 else 0
                
                type_performance[opp_type] = {
                    "total": total,
                    "converted": converted,
                    "rate": rate
                }
            
            # Find best performing type
            if type_performance:
                sorted_types = sorted(type_performance.items(), key=lambda x: x[1]['rate'], reverse=True)
                
                if len(sorted_types) >= 2:
                    best_type = sorted_types[0]
                    
                    if best_type[1]['rate'] > 0:
                        insight = f"{best_type[0].replace('_', ' ').title()} opportunities convert at {best_type[1]['rate']:.0f}%. "
                        insight += f"Focus on generating more of these high-quality leads."
                        
                        self._add_insight(
                            "opportunity_quality",
                            insight,
                            "medium",
                            {"type_performance": type_performance}
                        )
        
        except Exception as e:
            logger.error(f"Error analyzing opportunity quality: {e}")
    
    def analyze_trends(self):
        """Analyze trends over time"""
        try:
            opportunities = self.analytics.get('opportunities', [])
            conversions = self.analytics.get('conversions', [])
            
            if not opportunities:
                return
            
            # Last 7 days vs previous 7 days
            now = datetime.utcnow()
            last_7_days = now - timedelta(days=7)
            prev_7_days = now - timedelta(days=14)
            
            recent_opps = [o for o in opportunities if self._parse_date(o.get('timestamp')) > last_7_days]
            prev_opps = [o for o in opportunities if prev_7_days < self._parse_date(o.get('timestamp')) <= last_7_days]
            
            recent_conversions = [c for c in conversions if self._parse_date(c.get('date')) > last_7_days]
            prev_conversions = [c for c in conversions if prev_7_days < self._parse_date(c.get('date')) <= last_7_days]
            
            # Calculate growth
            opp_growth = len(recent_opps) - len(prev_opps)
            conv_growth = len(recent_conversions) - len(prev_conversions)
            
            if opp_growth > 0:
                self._add_insight(
                    "trend",
                    f"Opportunity volume up {opp_growth} this week! Momentum is building.",
                    "medium",
                    {"recent": len(recent_opps), "previous": len(prev_opps)}
                )
            
            if conv_growth > 0:
                self._add_insight(
                    "trend",
                    f"Conversions up {conv_growth} this week! Sales process is working.",
                    "high",
                    {"recent": len(recent_conversions), "previous": len(prev_conversions)}
                )
        
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse ISO date string"""
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return datetime.min
    
    def generate_action_items(self):
        """Generate specific action items"""
        try:
            # Priority actions based on insights
            high_priority = [i for i in self.insights if i['priority'] == 'high']
            
            actions = []
            
            # Conversion focus
            conversion_insights = [i for i in high_priority if i['category'] == 'conversion']
            if conversion_insights:
                actions.append("🎯 Double down on best performing channel")
            
            # Posting time
            time_insights = [i for i in high_priority if i['category'] == 'posting_time']
            if time_insights:
                actions.append("⏰ Schedule posts at optimal times")
            
            # Revenue
            revenue_insights = [i for i in high_priority if i['category'] == 'revenue']
            if revenue_insights:
                actions.append("💰 Prioritize highest revenue channel")
            
            if actions:
                self._add_insight(
                    "actions",
                    "Recommended actions: " + ", ".join(actions),
                    "high",
                    {"action_items": actions}
                )
        
        except Exception as e:
            logger.error(f"Error generating action items: {e}")
    
    def generate_all_insights(self) -> List[Dict]:
        """Generate all insights"""
        logger.info("Generating insights...")
        
        self.insights = []
        
        self.analyze_conversion_rates()
        self.analyze_posting_times()
        self.analyze_opportunity_quality()
        self.analyze_trends()
        self.generate_action_items()
        
        self._save_insights()
        
        return self.insights


def main():
    """Main execution"""
    logger.info("=== Insights Generator Starting ===")
    
    generator = InsightsGenerator()
    insights = generator.generate_all_insights()
    
    print("\n" + "="*60)
    print("🧠 ANALYTICS INSIGHTS")
    print("="*60 + "\n")
    
    for insight in insights:
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "⚪"}
        emoji = priority_emoji.get(insight['priority'], "⚪")
        print(f"{emoji} [{insight['category'].upper()}] {insight['insight']}\n")
    
    print("="*60)
    logger.info(f"Generated {len(insights)} insights")
    logger.info("=== Insights Generator Complete ===")


if __name__ == "__main__":
    main()
