#!/usr/bin/env python3
"""
Proactive Intelligence Agent - Night Shift Research
Runs autonomously during off-hours, generates morning intel briefs
Monitors markets, competition, opportunities
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/Users/clawdbot/clawd")
MEMORY_DIR = WORKSPACE / "memory"
REPORTS_DIR = WORKSPACE / "reports"
INTEL_CONFIG = MEMORY_DIR / "proactive_intel_config.json"
INTEL_STATE = MEMORY_DIR / "proactive_intel_state.json"

class ProactiveIntel:
    def __init__(self):
        self.config = self.load_config()
        self.state = self.load_state()
        REPORTS_DIR.mkdir(exist_ok=True)
    
    def load_config(self):
        """Load intelligence gathering configuration"""
        if INTEL_CONFIG.exists():
            with open(INTEL_CONFIG) as f:
                return json.load(f)
        
        return {
            "research_targets": {
                "golf_coaching": {
                    "keywords": ["golf coaching", "golf lessons", "golf training", "golf performance"],
                    "platforms": ["reddit", "twitter", "producthunt"],
                    "focus": "pricing, offers, marketing strategies"
                },
                "notion_templates": {
                    "keywords": ["notion templates", "notion dashboard", "productivity templates"],
                    "platforms": ["reddit", "twitter", "gumroad"],
                    "focus": "bestsellers, pricing, what's trending"
                },
                "fitness_apps": {
                    "keywords": ["fitness app", "workout tracker", "training app"],
                    "platforms": ["producthunt", "reddit"],
                    "focus": "new launches, features, user feedback"
                },
                "florida_real_estate": {
                    "keywords": ["florida real estate", "moving to florida", "florida housing market"],
                    "platforms": ["reddit", "news"],
                    "focus": "market trends, best locations, cost of living"
                }
            },
            "research_schedule": {
                "start_hour": 23,  # 11 PM
                "end_hour": 7,  # 7 AM
                "runs_per_night": 3,
                "enabled": True
            },
            "alert_thresholds": {
                "high_opportunity": 0.8,
                "medium_opportunity": 0.5,
                "telegram_alert": True
            }
        }
    
    def load_state(self):
        """Load state tracking"""
        if INTEL_STATE.exists():
            with open(INTEL_STATE) as f:
                return json.load(f)
        
        return {
            "last_run": None,
            "total_runs": 0,
            "opportunities_found": 0,
            "reports_generated": 0
        }
    
    def should_run(self):
        """Check if we should run now"""
        if not self.config["research_schedule"]["enabled"]:
            return False
        
        hour = datetime.now().hour
        start = self.config["research_schedule"]["start_hour"]
        end = self.config["research_schedule"]["end_hour"]
        
        # Handle overnight window
        if start > end:  # e.g., 23:00 - 7:00
            in_window = hour >= start or hour < end
        else:
            in_window = start <= hour < end
        
        return in_window
    
    def run_research_cycle(self):
        """Run a complete research cycle"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Starting proactive intelligence cycle...")
        
        findings = {
            "timestamp": datetime.now().isoformat(),
            "targets": {},
            "opportunities": [],
            "summary": ""
        }
        
        # Research each target
        for target_name, target_config in self.config["research_targets"].items():
            print(f"Researching: {target_name}...")
            target_findings = self._research_target(target_name, target_config)
            findings["targets"][target_name] = target_findings
            
            # Check for opportunities
            opportunities = self._identify_opportunities(target_name, target_findings)
            findings["opportunities"].extend(opportunities)
        
        # Generate summary
        findings["summary"] = self._generate_summary(findings)
        
        # Update state
        self.state["last_run"] = datetime.now().isoformat()
        self.state["total_runs"] += 1
        self.state["opportunities_found"] += len(findings["opportunities"])
        self.save_state()
        
        return findings
    
    def _research_target(self, target_name, config):
        """Research a specific target"""
        # This is a PLACEHOLDER - in real implementation, this would:
        # - Use web_search tool to search each platform
        # - Scrape Reddit, Twitter, Product Hunt
        # - Analyze pricing, trends, sentiment
        # - Extract actionable insights
        
        # For now, return simulated structure
        findings = {
            "keywords_searched": config["keywords"],
            "platforms_checked": config["platforms"],
            "insights": [],
            "trending_topics": [],
            "competitor_activity": [],
            "pricing_data": [],
            "user_sentiment": "positive"  # positive, neutral, negative
        }
        
        # Placeholder insights
        if target_name == "golf_coaching":
            findings["insights"] = [
                "High-ticket coaching programs ($2k-5k) are gaining traction",
                "Video analysis tools are becoming standard offering",
                "Monthly membership models more popular than one-time purchases"
            ]
            findings["pricing_data"] = [
                {"competitor": "GolfTec", "price": "$3,500", "model": "package"},
                {"competitor": "Me and My Golf", "price": "$49/mo", "model": "subscription"}
            ]
        
        return findings
    
    def _identify_opportunities(self, target_name, findings):
        """Identify opportunities from findings"""
        opportunities = []
        
        # Analyze insights for opportunities
        for insight in findings.get("insights", []):
            if any(word in insight.lower() for word in ["trending", "gaining", "popular", "demand"]):
                opportunities.append({
                    "target": target_name,
                    "type": "market_trend",
                    "description": insight,
                    "confidence": 0.7,
                    "action": "Consider adapting offer based on this trend"
                })
        
        # Check pricing gaps
        if findings.get("pricing_data"):
            avg_price = self._extract_avg_price(findings["pricing_data"])
            if avg_price:
                opportunities.append({
                    "target": target_name,
                    "type": "pricing_insight",
                    "description": f"Market average pricing: ${avg_price}",
                    "confidence": 0.8,
                    "action": "Review your pricing strategy"
                })
        
        return opportunities
    
    def _extract_avg_price(self, pricing_data):
        """Extract average price from pricing data"""
        # Simple extraction - would be more sophisticated in real implementation
        prices = []
        for item in pricing_data:
            price_str = item.get("price", "")
            # Extract number
            import re
            match = re.search(r'\$?(\d+)', price_str)
            if match:
                prices.append(int(match.group(1)))
        
        return sum(prices) // len(prices) if prices else None
    
    def _generate_summary(self, findings):
        """Generate executive summary"""
        num_opportunities = len(findings["opportunities"])
        high_confidence = [o for o in findings["opportunities"] if o["confidence"] > 0.7]
        
        summary = f"""
Night Shift Intelligence Summary
Generated: {datetime.now().strftime("%Y-%m-%d %I:%M %p")}

Targets Researched: {len(findings['targets'])}
Opportunities Found: {num_opportunities}
High Confidence: {len(high_confidence)}

Top Opportunities:
"""
        
        for i, opp in enumerate(high_confidence[:5], 1):
            summary += f"{i}. [{opp['target']}] {opp['description']} ({opp['confidence']:.0%} confidence)\n"
        
        return summary.strip()
    
    def generate_daily_report(self, findings):
        """Generate full daily intelligence report"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        report_path = REPORTS_DIR / f"daily_intel_{date_str}.md"
        
        report = f"""# Daily Intelligence Report
**Date:** {date_str}
**Generated:** {datetime.now().strftime("%I:%M %p")}
**Run #:** {self.state['total_runs']}

---

## Executive Summary

{findings['summary']}

---

## Detailed Findings

"""
        
        for target_name, target_data in findings['targets'].items():
            report += f"\n### {target_name.replace('_', ' ').title()}\n\n"
            report += f"**Focus:** {self.config['research_targets'][target_name]['focus']}\n\n"
            
            if target_data.get("insights"):
                report += "**Key Insights:**\n"
                for insight in target_data["insights"]:
                    report += f"- {insight}\n"
                report += "\n"
            
            if target_data.get("pricing_data"):
                report += "**Pricing Intelligence:**\n"
                for item in target_data["pricing_data"]:
                    report += f"- {item['competitor']}: {item['price']} ({item['model']})\n"
                report += "\n"
        
        report += "\n---\n\n## Opportunities\n\n"
        
        for opp in findings["opportunities"]:
            report += f"### {opp['description']}\n"
            report += f"- **Type:** {opp['type']}\n"
            report += f"- **Confidence:** {opp['confidence']:.0%}\n"
            report += f"- **Recommended Action:** {opp['action']}\n\n"
        
        report += "\n---\n\n*This report was generated automatically by Jarvis's Proactive Intelligence Agent.*\n"
        
        # Write report
        with open(report_path, "w") as f:
            f.write(report)
        
        self.state["reports_generated"] += 1
        self.save_state()
        
        print(f"✅ Report saved: {report_path}")
        return report_path
    
    def send_morning_brief(self, findings):
        """Send morning brief via Telegram (placeholder)"""
        # In real implementation, would use message tool
        brief = f"""🌅 Morning Intel Brief

Found {len(findings['opportunities'])} opportunities overnight.

Top insight: {findings['opportunities'][0]['description'] if findings['opportunities'] else 'No significant changes'}

Full report: reports/daily_intel_{datetime.now().strftime('%Y-%m-%d')}.md
"""
        
        print("Morning brief (would send via Telegram):")
        print(brief)
        
        return brief
    
    def save_config(self):
        """Save configuration"""
        INTEL_CONFIG.parent.mkdir(exist_ok=True)
        with open(INTEL_CONFIG, "w") as f:
            json.dump(self.config, f, indent=2)
    
    def save_state(self):
        """Save state"""
        INTEL_STATE.parent.mkdir(exist_ok=True)
        with open(INTEL_STATE, "w") as f:
            json.dump(self.state, f, indent=2)


def run_night_shift():
    """Run night shift intelligence gathering"""
    intel = ProactiveIntel()
    
    if not intel.should_run():
        print("Not in night shift window. Exiting.")
        return
    
    print("🌙 Night Shift Intelligence Agent Active")
    
    # Run research cycle
    findings = intel.run_research_cycle()
    
    # Generate report
    report_path = intel.generate_daily_report(findings)
    
    # Check if morning (should send brief)
    hour = datetime.now().hour
    if 6 <= hour < 9:
        intel.send_morning_brief(findings)
    
    print("✅ Night shift complete!")


def test_intel():
    """Test intelligence agent"""
    intel = ProactiveIntel()
    
    print("Proactive Intelligence Agent Test\n")
    
    # Force run regardless of time
    findings = intel.run_research_cycle()
    
    print("\n" + findings["summary"])
    
    # Generate report
    report_path = intel.generate_daily_report(findings)
    print(f"\n✅ Test report generated: {report_path}")
    
    # Show brief
    intel.send_morning_brief(findings)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        run_night_shift()
    else:
        test_intel()
