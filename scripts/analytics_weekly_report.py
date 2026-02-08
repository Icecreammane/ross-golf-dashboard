#!/usr/bin/env python3
"""
Analytics Weekly Report Generator
Generates comprehensive weekly analytics reports
Scheduled to run: Sunday @ 6pm
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
        logging.FileHandler(LOG_DIR / "analytics_reports.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("analytics_reports")

# File paths
WORKSPACE = Path.home() / "clawd"
DATA_DIR = WORKSPACE / "data"
REPORTS_DIR = WORKSPACE / "reports"
ANALYTICS_FILE = DATA_DIR / "analytics.json"
INSIGHTS_FILE = DATA_DIR / "analytics-insights.json"

# Create reports directory
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class WeeklyReportGenerator:
    """Generate weekly analytics reports"""
    
    def __init__(self):
        self.analytics = self._load_json(ANALYTICS_FILE)
        self.insights = self._load_json(INSIGHTS_FILE)
        self.report_date = datetime.utcnow()
        logger.info("Weekly Report Generator initialized")
    
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
    
    def _get_week_range(self) -> tuple:
        """Get start and end of current week"""
        end = datetime.utcnow()
        start = end - timedelta(days=7)
        return start, end
    
    def _filter_by_week(self, items: List[Dict], date_field: str) -> List[Dict]:
        """Filter items to current week"""
        start, end = self._get_week_range()
        
        filtered = []
        for item in items:
            try:
                date = datetime.fromisoformat(item.get(date_field, '').replace('Z', '+00:00'))
                if start <= date <= end:
                    filtered.append(item)
            except:
                pass
        
        return filtered
    
    def generate_text_report(self) -> str:
        """Generate text report for Telegram"""
        try:
            start, end = self._get_week_range()
            
            report = f"📊 **Weekly Analytics Report**\n"
            report += f"📅 {start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}\n\n"
            
            # Opportunities
            opportunities = self.analytics.get('opportunities', [])
            week_opps = self._filter_by_week(opportunities, 'tracked_at')
            
            report += "**🎯 Opportunities**\n"
            report += f"• New this week: {len(week_opps)}\n"
            
            if opportunities:
                converted = sum(1 for o in opportunities if o.get('converted'))
                total = len(opportunities)
                rate = (converted / total * 100) if total > 0 else 0
                report += f"• Conversion rate: {rate:.1f}% ({converted}/{total})\n"
            
            # Source breakdown
            source_perf = self.analytics.get('source_performance', {})
            report += f"\n**📈 Performance by Source**\n"
            for source, data in source_perf.items():
                if data['total'] > 0:
                    rate = (data['converted'] / data['total'] * 100)
                    report += f"• {source.capitalize()}: {rate:.0f}% ({data['converted']}/{data['total']}) - ${data['revenue']:.0f}\n"
            
            # Social posts
            social_posts = self.analytics.get('social_posts', [])
            week_posts = self._filter_by_week(social_posts, 'posted_at')
            
            report += f"\n**📱 Social Media**\n"
            report += f"• Posts this week: {len(week_posts)}\n"
            
            if week_posts:
                total_engagement = sum(
                    p.get('likes', 0) + p.get('retweets', 0) + p.get('replies', 0)
                    for p in week_posts
                )
                avg_engagement = total_engagement / len(week_posts)
                report += f"• Avg engagement: {avg_engagement:.1f} per post\n"
            
            # Best posting time
            engagement_by_hour = self.analytics.get('engagement_by_hour', {})
            best_hour = None
            best_avg = 0
            
            for hour, data in engagement_by_hour.items():
                if data['posts'] > 0:
                    avg = data['engagement'] / data['posts']
                    if avg > best_avg:
                        best_avg = avg
                        best_hour = int(hour)
            
            if best_hour is not None:
                time_str = f"{best_hour % 12 or 12}{'am' if best_hour < 12 else 'pm'}"
                report += f"• Best time to post: {time_str} ({best_avg:.0f} avg engagement)\n"
            
            # Key insights
            insights = self.insights.get('insights', [])
            high_priority = [i for i in insights if i['priority'] == 'high']
            
            if high_priority:
                report += f"\n**💡 Key Insights**\n"
                for insight in high_priority[:3]:  # Top 3
                    report += f"• {insight['insight']}\n"
            
            # Revenue
            conversions = self.analytics.get('conversions', [])
            week_conversions = self._filter_by_week(conversions, 'date')
            week_revenue = sum(c['revenue'] for c in week_conversions)
            total_revenue = sum(c['revenue'] for c in conversions)
            
            report += f"\n**💰 Revenue**\n"
            report += f"• This week: ${week_revenue:.0f}\n"
            report += f"• Total: ${total_revenue:.0f}\n"
            
            return report
        
        except Exception as e:
            logger.error(f"Error generating text report: {e}")
            return "Error generating report"
    
    def generate_html_report(self) -> str:
        """Generate HTML report for dashboard"""
        try:
            start, end = self._get_week_range()
            
            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weekly Analytics Report - {start.strftime('%b %d')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            padding: 24px;
            line-height: 1.6;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 32px;
            border-radius: 16px;
            margin-bottom: 24px;
            text-align: center;
        }}
        .header h1 {{ font-size: 32px; color: white; margin-bottom: 8px; }}
        .header .date {{ font-size: 14px; opacity: 0.9; color: white; }}
        .section {{
            background: #1a1a1a;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 16px;
            border-left: 4px solid #667eea;
        }}
        .section h2 {{ color: #667eea; margin-bottom: 16px; font-size: 20px; }}
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 16px;
        }}
        .stat-card {{
            background: #0f0f0f;
            padding: 16px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-card .number {{ font-size: 32px; font-weight: bold; color: #4ade80; margin-bottom: 4px; }}
        .stat-card .label {{ font-size: 12px; color: #888; text-transform: uppercase; }}
        .insight {{
            padding: 12px 16px;
            background: #0f0f0f;
            border-radius: 8px;
            margin-bottom: 8px;
            border-left: 3px solid #4ade80;
        }}
        .insight.high {{ border-left-color: #f87171; }}
        .insight.medium {{ border-left-color: #fbbf24; }}
        .table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
        .table th {{ text-align: left; padding: 8px; border-bottom: 2px solid #333; color: #888; }}
        .table td {{ padding: 8px; border-bottom: 1px solid #222; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 24px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Weekly Analytics Report</h1>
            <div class="date">{start.strftime('%B %d')} - {end.strftime('%B %d, %Y')}</div>
        </div>
"""
            
            # Opportunities section
            opportunities = self.analytics.get('opportunities', [])
            week_opps = self._filter_by_week(opportunities, 'tracked_at')
            converted = sum(1 for o in opportunities if o.get('converted'))
            total = len(opportunities)
            rate = (converted / total * 100) if total > 0 else 0
            
            html += f"""
        <div class="section">
            <h2>🎯 Opportunities Overview</h2>
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="number">{len(week_opps)}</div>
                    <div class="label">New This Week</div>
                </div>
                <div class="stat-card">
                    <div class="number">{total}</div>
                    <div class="label">Total Tracked</div>
                </div>
                <div class="stat-card">
                    <div class="number">{rate:.1f}%</div>
                    <div class="label">Conversion Rate</div>
                </div>
                <div class="stat-card">
                    <div class="number">{converted}</div>
                    <div class="label">Converted</div>
                </div>
            </div>
        </div>
"""
            
            # Source performance
            source_perf = self.analytics.get('source_performance', {})
            html += """
        <div class="section">
            <h2>📈 Performance by Source</h2>
            <table class="table">
                <tr>
                    <th>Source</th>
                    <th>Total</th>
                    <th>Converted</th>
                    <th>Rate</th>
                    <th>Revenue</th>
                </tr>
"""
            
            for source, data in source_perf.items():
                if data['total'] > 0:
                    rate = (data['converted'] / data['total'] * 100)
                    html += f"""
                <tr>
                    <td>{source.capitalize()}</td>
                    <td>{data['total']}</td>
                    <td>{data['converted']}</td>
                    <td>{rate:.0f}%</td>
                    <td>${data['revenue']:.0f}</td>
                </tr>
"""
            
            html += """
            </table>
        </div>
"""
            
            # Insights
            insights = self.insights.get('insights', [])
            if insights:
                html += """
        <div class="section">
            <h2>💡 Key Insights</h2>
"""
                for insight in insights:
                    priority_class = insight['priority']
                    html += f"""
            <div class="insight {priority_class}">
                <strong>[{insight['category'].upper()}]</strong> {insight['insight']}
            </div>
"""
                
                html += """
        </div>
"""
            
            # Footer
            html += f"""
        <div class="footer">
            Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} • Auto-updates weekly
        </div>
    </div>
</body>
</html>
"""
            
            return html
        
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            return "<html><body>Error generating report</body></html>"
    
    def save_reports(self) -> Dict[str, str]:
        """Generate and save both report formats"""
        try:
            # Generate reports
            text_report = self.generate_text_report()
            html_report = self.generate_html_report()
            
            # Save files
            date_str = self.report_date.strftime('%Y-%m-%d')
            text_file = REPORTS_DIR / f"analytics_report_{date_str}.txt"
            html_file = REPORTS_DIR / f"analytics_report_{date_str}.html"
            
            text_file.write_text(text_report)
            html_file.write_text(html_report)
            
            # Also save as "latest"
            (REPORTS_DIR / "analytics_report_latest.txt").write_text(text_report)
            (REPORTS_DIR / "analytics_report_latest.html").write_text(html_report)
            
            logger.info(f"Saved reports: {text_file} and {html_file}")
            
            return {
                "text_file": str(text_file),
                "html_file": str(html_file),
                "text_content": text_report
            }
        
        except Exception as e:
            logger.error(f"Error saving reports: {e}")
            return {}


def main():
    """Main execution"""
    logger.info("=== Weekly Analytics Report Generator Starting ===")
    
    generator = WeeklyReportGenerator()
    results = generator.save_reports()
    
    if results:
        print("\n" + "="*60)
        print("📊 WEEKLY ANALYTICS REPORT GENERATED")
        print("="*60 + "\n")
        print(results['text_content'])
        print("\n" + "="*60)
        print(f"💾 Saved to:")
        print(f"  • {results['text_file']}")
        print(f"  • {results['html_file']}")
        print("="*60)
    
    logger.info("=== Weekly Report Generator Complete ===")


if __name__ == "__main__":
    main()
