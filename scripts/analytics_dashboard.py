#!/usr/bin/env python3
"""
Analytics Dashboard Integration
Generates analytics dashboard data for display on revenue dashboard
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

# Configure logging
LOG_DIR = Path.home() / "clawd" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "analytics_dashboard.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("analytics_dashboard")

# File paths
WORKSPACE = Path.home() / "clawd"
DATA_DIR = WORKSPACE / "data"
ANALYTICS_FILE = DATA_DIR / "analytics.json"
INSIGHTS_FILE = DATA_DIR / "analytics-insights.json"
DASHBOARD_OUTPUT = DATA_DIR / "analytics-dashboard.json"


class AnalyticsDashboard:
    """Generate dashboard-ready analytics data"""
    
    def __init__(self):
        self.analytics = self._load_json(ANALYTICS_FILE)
        self.insights = self._load_json(INSIGHTS_FILE)
        logger.info("Analytics Dashboard initialized")
    
    def _load_json(self, filepath: Path) -> Dict:
        """Load JSON file"""
        if not filepath.exists():
            logger.warning(f"File not found: {filepath}")
            return {}
        
        try:
            with open(filepath) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
            return {}
    
    def get_overview_metrics(self) -> Dict:
        """Get high-level overview metrics"""
        try:
            opportunities = self.analytics.get('opportunities', [])
            conversions = self.analytics.get('conversions', [])
            social_posts = self.analytics.get('social_posts', [])
            
            total_opps = len(opportunities)
            converted = sum(1 for o in opportunities if o.get('converted'))
            conversion_rate = (converted / total_opps * 100) if total_opps > 0 else 0
            
            total_revenue = sum(c['revenue'] for c in conversions)
            
            # Last 7 days activity
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_opps = [o for o in opportunities if self._parse_date(o.get('tracked_at')) > week_ago]
            recent_conversions = [c for c in conversions if self._parse_date(c.get('date')) > week_ago]
            
            return {
                "total_opportunities": total_opps,
                "conversion_rate": round(conversion_rate, 1),
                "total_conversions": converted,
                "total_revenue": round(total_revenue, 2),
                "recent_opportunities": len(recent_opps),
                "recent_conversions": len(recent_conversions),
                "social_posts_tracked": len(social_posts)
            }
        except Exception as e:
            logger.error(f"Error getting overview metrics: {e}")
            return {}
    
    def get_source_performance(self) -> List[Dict]:
        """Get performance by source"""
        try:
            source_perf = self.analytics.get('source_performance', {})
            
            results = []
            for source, data in source_perf.items():
                if data['total'] > 0:
                    results.append({
                        "source": source.capitalize(),
                        "total": data['total'],
                        "converted": data['converted'],
                        "conversion_rate": round((data['converted'] / data['total']) * 100, 1),
                        "revenue": round(data['revenue'], 2)
                    })
            
            # Sort by conversion rate
            results.sort(key=lambda x: x['conversion_rate'], reverse=True)
            return results
        except Exception as e:
            logger.error(f"Error getting source performance: {e}")
            return []
    
    def get_engagement_timeline(self) -> Dict:
        """Get engagement by hour of day"""
        try:
            engagement_by_hour = self.analytics.get('engagement_by_hour', {})
            
            timeline = []
            for hour in range(24):
                data = engagement_by_hour.get(str(hour), {"posts": 0, "engagement": 0})
                avg_engagement = (data['engagement'] / data['posts']) if data['posts'] > 0 else 0
                
                # Convert hour to readable time
                time_str = f"{hour % 12 or 12}{'am' if hour < 12 else 'pm'}"
                
                timeline.append({
                    "hour": hour,
                    "time": time_str,
                    "posts": data['posts'],
                    "avg_engagement": round(avg_engagement, 1)
                })
            
            return {"timeline": timeline}
        except Exception as e:
            logger.error(f"Error getting engagement timeline: {e}")
            return {"timeline": []}
    
    def get_top_insights(self, limit: int = 5) -> List[Dict]:
        """Get top priority insights"""
        try:
            insights = self.insights.get('insights', [])
            
            # Sort by priority (high > medium > low)
            priority_order = {"high": 3, "medium": 2, "low": 1}
            sorted_insights = sorted(
                insights,
                key=lambda x: priority_order.get(x.get('priority', 'low'), 0),
                reverse=True
            )
            
            return sorted_insights[:limit]
        except Exception as e:
            logger.error(f"Error getting top insights: {e}")
            return []
    
    def get_weekly_trend(self) -> Dict:
        """Get week-over-week trends"""
        try:
            opportunities = self.analytics.get('opportunities', [])
            conversions = self.analytics.get('conversions', [])
            
            now = datetime.utcnow()
            week_ago = now - timedelta(days=7)
            two_weeks_ago = now - timedelta(days=14)
            
            # This week
            this_week_opps = [o for o in opportunities if self._parse_date(o.get('tracked_at')) > week_ago]
            this_week_conv = [c for c in conversions if self._parse_date(c.get('date')) > week_ago]
            
            # Last week
            last_week_opps = [o for o in opportunities if week_ago > self._parse_date(o.get('tracked_at')) > two_weeks_ago]
            last_week_conv = [c for c in conversions if week_ago > self._parse_date(c.get('date')) > two_weeks_ago]
            
            # Calculate changes
            opp_change = len(this_week_opps) - len(last_week_opps)
            conv_change = len(this_week_conv) - len(last_week_conv)
            
            return {
                "opportunities": {
                    "this_week": len(this_week_opps),
                    "last_week": len(last_week_opps),
                    "change": opp_change,
                    "trend": "up" if opp_change > 0 else "down" if opp_change < 0 else "flat"
                },
                "conversions": {
                    "this_week": len(this_week_conv),
                    "last_week": len(last_week_conv),
                    "change": conv_change,
                    "trend": "up" if conv_change > 0 else "down" if conv_change < 0 else "flat"
                }
            }
        except Exception as e:
            logger.error(f"Error getting weekly trend: {e}")
            return {}
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse ISO date string"""
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return datetime.min
    
    def generate_dashboard_data(self) -> Dict:
        """Generate complete dashboard data"""
        logger.info("Generating dashboard data...")
        
        try:
            dashboard_data = {
                "generated_at": datetime.utcnow().isoformat(),
                "overview": self.get_overview_metrics(),
                "source_performance": self.get_source_performance(),
                "engagement_timeline": self.get_engagement_timeline(),
                "insights": self.get_top_insights(),
                "weekly_trend": self.get_weekly_trend()
            }
            
            # Save to file
            with open(DASHBOARD_OUTPUT, 'w') as f:
                json.dump(dashboard_data, f, indent=2)
            
            logger.info(f"Dashboard data saved to {DASHBOARD_OUTPUT}")
            return dashboard_data
        
        except Exception as e:
            logger.error(f"Error generating dashboard data: {e}")
            return {}


def generate_html_widget() -> str:
    """Generate HTML widget for embedding in revenue dashboard"""
    try:
        dashboard = AnalyticsDashboard()
        data = dashboard.generate_dashboard_data()
        
        overview = data.get('overview', {})
        source_perf = data.get('source_performance', [])
        insights = data.get('insights', [])
        
        html = """
<div class="analytics-widget" style="background: #1a1a1a; border-radius: 12px; padding: 24px; margin-top: 16px; border-left: 4px solid #667eea;">
    <h2 style="color: #667eea; margin-bottom: 16px; font-size: 20px;">📊 Analytics Dashboard</h2>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 16px;">
"""
        
        # Overview metrics
        metrics = [
            ("Opportunities", overview.get('total_opportunities', 0)),
            ("Conversion Rate", f"{overview.get('conversion_rate', 0)}%"),
            ("Conversions", overview.get('total_conversions', 0)),
            ("Revenue", f"${overview.get('total_revenue', 0):.0f}")
        ]
        
        for label, value in metrics:
            html += f"""
        <div style="background: #0f0f0f; padding: 12px; border-radius: 8px; text-align: center;">
            <div style="font-size: 24px; font-weight: bold; color: #4ade80;">{value}</div>
            <div style="font-size: 11px; color: #888; text-transform: uppercase;">{label}</div>
        </div>
"""
        
        html += """
    </div>
"""
        
        # Source performance
        if source_perf:
            html += """
    <h3 style="color: #888; font-size: 14px; margin-bottom: 8px;">Performance by Source</h3>
    <div style="margin-bottom: 16px;">
"""
            for source in source_perf:
                width = min(source['conversion_rate'], 100)
                html += f"""
        <div style="margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 4px;">
                <span style="color: #e0e0e0;">{source['source']}</span>
                <span style="color: #4ade80;">{source['conversion_rate']}% ({source['converted']}/{source['total']})</span>
            </div>
            <div style="background: #0f0f0f; height: 6px; border-radius: 3px; overflow: hidden;">
                <div style="background: #4ade80; height: 100%; width: {width}%;"></div>
            </div>
        </div>
"""
            
            html += """
    </div>
"""
        
        # Top insights
        if insights:
            html += """
    <h3 style="color: #888; font-size: 14px; margin-bottom: 8px;">Key Insights</h3>
"""
            priority_colors = {"high": "#f87171", "medium": "#fbbf24", "low": "#888"}
            
            for insight in insights[:3]:
                color = priority_colors.get(insight.get('priority', 'low'), '#888')
                html += f"""
    <div style="padding: 10px 12px; background: #0f0f0f; border-radius: 6px; margin-bottom: 6px; border-left: 3px solid {color}; font-size: 13px;">
        <strong style="color: {color};">[{insight.get('category', '').upper()}]</strong> {insight.get('insight', '')}
    </div>
"""
        
        html += """
    <div style="text-align: center; margin-top: 16px;">
        <a href="/reports/analytics_report_latest.html" style="display: inline-block; padding: 8px 16px; background: #667eea; color: white; text-decoration: none; border-radius: 6px; font-size: 13px; font-weight: 600;">
            View Full Report →
        </a>
    </div>
</div>
"""
        
        return html
    
    except Exception as e:
        logger.error(f"Error generating HTML widget: {e}")
        return "<div>Error loading analytics</div>"


def main():
    """Main execution"""
    logger.info("=== Analytics Dashboard Generator Starting ===")
    
    dashboard = AnalyticsDashboard()
    data = dashboard.generate_dashboard_data()
    
    print("\n" + "="*60)
    print("📊 ANALYTICS DASHBOARD DATA")
    print("="*60)
    print(json.dumps(data, indent=2))
    print("="*60)
    
    # Generate HTML widget
    widget_html = generate_html_widget()
    widget_file = WORKSPACE / "analytics_widget.html"
    widget_file.write_text(widget_html)
    print(f"\n💾 HTML widget saved to: {widget_file}")
    
    logger.info("=== Analytics Dashboard Generator Complete ===")


if __name__ == "__main__":
    main()
