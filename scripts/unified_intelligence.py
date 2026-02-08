#!/usr/bin/env python3
"""
Unified Intelligence System
Integrates all autonomous systems into one coordinated intelligence
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path.home() / "clawd"

class UnifiedIntelligence:
    """Master orchestrator for all autonomous systems"""
    
    def __init__(self):
        self.workspace = WORKSPACE
        self.state_file = self.workspace / "memory" / "unified-state.json"
        self.load_state()
    
    def load_state(self):
        """Load unified state"""
        if self.state_file.exists():
            with open(self.state_file) as f:
                self.state = json.load(f)
        else:
            self.state = {
                "last_sync": None,
                "systems": {
                    "operator_loop": {"status": "unknown", "last_check": None},
                    "god_mode": {"status": "unknown", "last_update": None},
                    "revenue_machine": {"status": "unknown", "last_action": None},
                    "multiverse": {"status": "unknown", "last_prediction": None}
                },
                "insights": [],
                "actions_pending": []
            }
    
    def save_state(self):
        """Save unified state"""
        self.state_file.parent.mkdir(exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def sync_all_systems(self):
        """Sync data across all systems"""
        print("🔄 Syncing all systems...")
        
        # Get God Mode predictions
        god_mode_data = self.get_god_mode_predictions()
        
        # Get Revenue Machine opportunities
        revenue_data = self.get_revenue_opportunities()
        
        # Get Operator Loop status
        operator_data = self.get_operator_status()
        
        # Get Multiverse predictions
        multiverse_data = self.get_multiverse_predictions()
        
        # Cross-pollinate insights
        insights = self.generate_unified_insights(
            god_mode_data,
            revenue_data,
            operator_data,
            multiverse_data
        )
        
        # Update state
        self.state["last_sync"] = datetime.now().isoformat()
        self.state["insights"] = insights
        
        self.save_state()
        
        return insights
    
    def get_god_mode_predictions(self):
        """Get behavioral predictions from God Mode"""
        try:
            behavior_file = self.workspace / "god_mode" / "behavioral_data.json"
            if behavior_file.exists():
                with open(behavior_file) as f:
                    data = json.load(f)
                    
                self.state["systems"]["god_mode"]["status"] = "operational"
                self.state["systems"]["god_mode"]["last_update"] = datetime.now().isoformat()
                
                return {
                    "tomorrow_energy": data.get("tomorrow_prediction", {}).get("energy", 0),
                    "peak_hours": data.get("peak_productivity_window", "Unknown"),
                    "predicted_wins": data.get("tomorrow_prediction", {}).get("wins", 0),
                    "bottleneck": data.get("bottleneck", "Unknown")
                }
        except Exception as e:
            print(f"⚠️ God Mode sync error: {e}")
            self.state["systems"]["god_mode"]["status"] = "error"
        
        return {}
    
    def get_revenue_opportunities(self):
        """Get revenue opportunities from Revenue Machine"""
        try:
            rev_file = self.workspace / "revenue" / "actions.json"
            opp_file = self.workspace / "revenue" / "opportunities.json"
            
            opportunities = []
            if opp_file.exists():
                with open(opp_file) as f:
                    data = json.load(f)
                    opportunities = data.get("opportunities", [])
            
            actions = []
            if rev_file.exists():
                with open(rev_file) as f:
                    actions = json.load(f)
            
            self.state["systems"]["revenue_machine"]["status"] = "operational"
            self.state["systems"]["revenue_machine"]["last_action"] = datetime.now().isoformat()
            
            # Calculate potential MRR
            total_potential = sum(
                (opp.get("monthly_low", 0) + opp.get("monthly_high", 0)) / 2
                for opp in opportunities
            )
            
            return {
                "opportunities_count": len(opportunities),
                "actions_logged": len(actions),
                "potential_mrr": total_potential,
                "top_opportunity": opportunities[0] if opportunities else None
            }
        except Exception as e:
            print(f"⚠️ Revenue Machine sync error: {e}")
            self.state["systems"]["revenue_machine"]["status"] = "error"
        
        return {}
    
    def get_operator_status(self):
        """Get status from Operator Loop"""
        try:
            queue_file = self.workspace / "opportunities" / "queue.json"
            drafted_file = self.workspace / "opportunities" / "drafted.json"
            
            queue = []
            drafted = []
            
            if queue_file.exists():
                with open(queue_file) as f:
                    queue = json.load(f)
            
            if drafted_file.exists():
                with open(drafted_file) as f:
                    drafted = json.load(f)
            
            self.state["systems"]["operator_loop"]["status"] = "operational"
            self.state["systems"]["operator_loop"]["last_check"] = datetime.now().isoformat()
            
            return {
                "pending_opportunities": len(queue),
                "drafted_responses": len(drafted),
                "ready_to_send": len([d for d in drafted if d.get("status") == "approved"])
            }
        except Exception as e:
            print(f"⚠️ Operator Loop sync error: {e}")
            self.state["systems"]["operator_loop"]["status"] = "error"
        
        return {}
    
    def get_multiverse_predictions(self):
        """Get predictions from Multiverse"""
        try:
            mv_file = self.workspace / "multiverse" / "timelines.json"
            
            if mv_file.exists():
                with open(mv_file) as f:
                    data = json.load(f)
                
                self.state["systems"]["multiverse"]["status"] = "operational"
                self.state["systems"]["multiverse"]["last_prediction"] = datetime.now().isoformat()
                
                # Extract timelines dict
                timelines_dict = data.get("timelines", {})
                
                # Find BEAST MODE timeline
                beast_mode = timelines_dict.get("beast_mode", {})
                
                # Get 1-year prediction
                one_year_prediction = None
                if beast_mode and "predictions" in beast_mode:
                    for pred in beast_mode["predictions"]:
                        if pred.get("timepoint") == "1_year":
                            one_year_prediction = pred
                            break
                
                return {
                    "timelines_count": len(timelines_dict),
                    "beast_mode_mrr": one_year_prediction.get("side_income", 0) if one_year_prediction else 0,
                    "best_timeline": beast_mode.get("name", "Unknown") if beast_mode else "Unknown"
                }
        except Exception as e:
            print(f"⚠️ Multiverse sync error: {e}")
            self.state["systems"]["multiverse"]["status"] = "error"
        
        return {}
    
    def generate_unified_insights(self, god_mode, revenue, operator, multiverse):
        """Generate insights by cross-referencing all systems"""
        insights = []
        now = datetime.now()
        
        # Energy-based task recommendations
        if god_mode.get("tomorrow_energy"):
            energy = god_mode["tomorrow_energy"]
            peak_hours = god_mode.get("peak_hours", "Unknown")
            
            if energy >= 80:
                insights.append({
                    "type": "recommendation",
                    "priority": "high",
                    "message": f"Tomorrow's energy: {energy}/100 (BEAST MODE) - Schedule hardest tasks during {peak_hours}",
                    "action": "time_block_deep_work",
                    "timestamp": now.isoformat()
                })
            elif energy < 60:
                insights.append({
                    "type": "warning",
                    "priority": "medium",
                    "message": f"Tomorrow's energy: {energy}/100 (lower than usual) - Plan lighter tasks, prioritize recovery",
                    "action": "adjust_expectations",
                    "timestamp": now.isoformat()
                })
        
        # Revenue opportunity prioritization
        if revenue.get("opportunities_count", 0) > 0:
            potential = revenue.get("potential_mrr", 0)
            top_opp = revenue.get("top_opportunity")
            
            if potential > 3000:
                insights.append({
                    "type": "revenue",
                    "priority": "high",
                    "message": f"${potential:.0f}/month potential identified - Top opportunity: {top_opp.get('name') if top_opp else 'Unknown'}",
                    "action": "prioritize_revenue_work",
                    "timestamp": now.isoformat()
                })
        
        # Operator Loop readiness
        if operator.get("drafted_responses", 0) > 0:
            drafted = operator["drafted_responses"]
            insights.append({
                "type": "action_required",
                "priority": "medium",
                "message": f"{drafted} responses drafted and ready for approval",
                "action": "review_drafted_responses",
                "timestamp": now.isoformat()
            })
        
        # Multiverse alignment
        if multiverse.get("beast_mode_mrr"):
            beast_mrr = multiverse["beast_mode_mrr"]
            current_potential = revenue.get("potential_mrr", 0)
            
            if current_potential > 0:
                progress = (current_potential / beast_mrr) * 100
                insights.append({
                    "type": "progress",
                    "priority": "low",
                    "message": f"On BEAST MODE timeline: {progress:.1f}% of 1-year projection (${current_potential:.0f}/${beast_mrr:.0f})",
                    "action": "track_progress",
                    "timestamp": now.isoformat()
                })
        
        # Cross-system recommendations
        if god_mode.get("bottleneck") and revenue.get("opportunities_count", 0) > 0:
            bottleneck = god_mode["bottleneck"]
            insights.append({
                "type": "optimization",
                "priority": "medium",
                "message": f"Bottleneck identified: {bottleneck} - Focus revenue efforts here first",
                "action": "address_bottleneck",
                "timestamp": now.isoformat()
            })
        
        return insights
    
    def get_system_health(self):
        """Check health of all systems"""
        health = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "operational",
            "systems": {}
        }
        
        for system_name, system_data in self.state["systems"].items():
            status = system_data.get("status", "unknown")
            health["systems"][system_name] = {
                "status": status,
                "healthy": status == "operational"
            }
            
            if status != "operational":
                health["overall_status"] = "degraded"
        
        return health
    
    def generate_unified_report(self):
        """Generate human-readable unified report"""
        self.sync_all_systems()
        
        report = []
        report.append("=" * 70)
        report.append("🧠 UNIFIED INTELLIGENCE REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p CST')}")
        report.append("")
        
        # System Health
        health = self.get_system_health()
        report.append("📊 SYSTEM HEALTH")
        report.append("-" * 70)
        status_emoji = "✅" if health["overall_status"] == "operational" else "⚠️"
        report.append(f"{status_emoji} Overall Status: {health['overall_status'].upper()}")
        
        for system_name, system_health in health["systems"].items():
            emoji = "✅" if system_health["healthy"] else "❌"
            report.append(f"  {emoji} {system_name.replace('_', ' ').title()}: {system_health['status']}")
        
        report.append("")
        
        # Insights
        if self.state.get("insights"):
            report.append("💡 UNIFIED INSIGHTS")
            report.append("-" * 70)
            
            # Group by priority
            high_priority = [i for i in self.state["insights"] if i.get("priority") == "high"]
            medium_priority = [i for i in self.state["insights"] if i.get("priority") == "medium"]
            low_priority = [i for i in self.state["insights"] if i.get("priority") == "low"]
            
            if high_priority:
                report.append("🔴 HIGH PRIORITY:")
                for insight in high_priority:
                    report.append(f"  • {insight['message']}")
                report.append("")
            
            if medium_priority:
                report.append("🟡 MEDIUM PRIORITY:")
                for insight in medium_priority:
                    report.append(f"  • {insight['message']}")
                report.append("")
            
            if low_priority:
                report.append("🟢 INFO:")
                for insight in low_priority:
                    report.append(f"  • {insight['message']}")
        else:
            report.append("💡 No insights generated yet")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


def main():
    """Run unified intelligence sync"""
    ui = UnifiedIntelligence()
    
    print(ui.generate_unified_report())
    
    # Save HTML version
    html_file = WORKSPACE / "unified-intelligence.html"
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unified Intelligence Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0a0a0a;
            color: #ffffff;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            padding: 40px 0;
            border-bottom: 2px solid #333;
            margin-bottom: 40px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 48px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .card {{
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 12px;
            padding: 24px;
        }}
        .card h2 {{
            margin: 0 0 20px 0;
            font-size: 20px;
            color: #667eea;
        }}
        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        .status-operational {{
            background: #10b981;
        }}
        .status-error {{
            background: #ef4444;
        }}
        .status-unknown {{
            background: #6b7280;
        }}
        .insight {{
            padding: 16px;
            margin-bottom: 12px;
            border-radius: 8px;
            border-left: 4px solid;
        }}
        .insight-high {{
            background: rgba(239, 68, 68, 0.1);
            border-color: #ef4444;
        }}
        .insight-medium {{
            background: rgba(251, 191, 36, 0.1);
            border-color: #fbbf24;
        }}
        .insight-low {{
            background: rgba(16, 185, 129, 0.1);
            border-color: #10b981;
        }}
        .metric {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin: 12px 0;
        }}
        .label {{
            font-size: 14px;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .timestamp {{
            text-align: center;
            color: #666;
            margin-top: 40px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Unified Intelligence</h1>
            <p>All systems synchronized and operational</p>
        </div>
        
        <div class="grid" id="systemsGrid"></div>
        
        <div class="card">
            <h2>💡 Unified Insights</h2>
            <div id="insightsContainer"></div>
        </div>
        
        <div class="timestamp" id="timestamp"></div>
    </div>
    
    <script>
        async function loadData() {{
            try {{
                const response = await fetch('/Users/clawdbot/clawd/memory/unified-state.json');
                const data = await response.json();
                
                renderSystems(data.systems);
                renderInsights(data.insights);
                updateTimestamp(data.last_sync);
            }} catch (error) {{
                console.error('Failed to load data:', error);
            }}
        }}
        
        function renderSystems(systems) {{
            const grid = document.getElementById('systemsGrid');
            grid.innerHTML = '';
            
            for (const [name, data] of Object.entries(systems)) {{
                const card = document.createElement('div');
                card.className = 'card';
                
                const statusClass = data.status === 'operational' ? 'operational' : 
                                   data.status === 'error' ? 'error' : 'unknown';
                
                card.innerHTML = `
                    <h2><span class="status-indicator status-${{statusClass}}"></span>${{name.replace(/_/g, ' ').toUpperCase()}}</h2>
                    <div class="label">Status</div>
                    <div class="metric">${{data.status}}</div>
                `;
                
                grid.appendChild(card);
            }}
        }}
        
        function renderInsights(insights) {{
            const container = document.getElementById('insightsContainer');
            container.innerHTML = '';
            
            if (!insights || insights.length === 0) {{
                container.innerHTML = '<p style="color: #666;">No insights available yet</p>';
                return;
            }}
            
            insights.forEach(insight => {{
                const div = document.createElement('div');
                div.className = `insight insight-${{insight.priority}}`;
                div.innerHTML = `
                    <strong>${{insight.type.replace(/_/g, ' ').toUpperCase()}}</strong>
                    <p>${{insight.message}}</p>
                `;
                container.appendChild(div);
            }});
        }}
        
        function updateTimestamp(timestamp) {{
            const elem = document.getElementById('timestamp');
            elem.textContent = `Last sync: ${{new Date(timestamp).toLocaleString()}}`;
        }}
        
        // Load data on page load
        loadData();
        
        // Refresh every 60 seconds
        setInterval(loadData, 60000);
    </script>
</body>
</html>"""
    
    with open(html_file, 'w') as f:
        f.write(html)
    
    print(f"\n💾 Dashboard saved to: {html_file}")
    print(f"🌐 View at: file://{html_file}")


if __name__ == "__main__":
    main()
