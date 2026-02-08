#!/usr/bin/env python3
"""
Escalation Dashboard - Real-time view of routing decisions and cost savings

Shows live statistics, recent decisions, and trends.
"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from smart_escalation_engine import get_engine

WORKSPACE = Path.home() / "clawd"
LOG_FILE = WORKSPACE / "memory" / "escalation.log"


class EscalationDashboard:
    def __init__(self):
        self.engine = get_engine()
        self.log_file = LOG_FILE
    
    def _load_recent_logs(self, hours: int = 24) -> list:
        """Load logs from last N hours"""
        if not self.log_file.exists():
            return []
        
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = []
        
        try:
            with open(self.log_file) as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        entry_time = datetime.fromisoformat(entry["timestamp"])
                        
                        if entry_time >= cutoff:
                            recent.append(entry)
                    except:
                        continue
        except:
            return []
        
        return recent
    
    def _analyze_logs(self, logs: list) -> dict:
        """Analyze logs for trends"""
        analysis = {
            "total": len(logs),
            "local": 0,
            "cloud": 0,
            "avg_complexity": 0,
            "avg_response_time": 0,
            "total_tokens_saved": 0,
            "total_cost_saved": 0.0,
            "hourly_distribution": defaultdict(int),
            "complexity_distribution": {
                "low": 0,  # 0-33
                "medium": 0,  # 34-66
                "high": 0  # 67-100
            },
            "top_reasons": defaultdict(int)
        }
        
        if not logs:
            return analysis
        
        total_complexity = 0
        total_response_time = 0
        
        for log in logs:
            # Route counts
            if log["route"] == "local":
                analysis["local"] += 1
            else:
                analysis["cloud"] += 1
            
            # Complexity
            complexity = log.get("complexity", {}).get("overall", 50)
            total_complexity += complexity
            
            if complexity <= 33:
                analysis["complexity_distribution"]["low"] += 1
            elif complexity <= 66:
                analysis["complexity_distribution"]["medium"] += 1
            else:
                analysis["complexity_distribution"]["high"] += 1
            
            # Response time
            response_time = log.get("response_time_ms", 0)
            total_response_time += response_time
            
            # Savings
            analysis["total_tokens_saved"] += log.get("tokens_saved", 0)
            analysis["total_cost_saved"] += log.get("cost_saved", 0)
            
            # Hour distribution
            hour = datetime.fromisoformat(log["timestamp"]).hour
            analysis["hourly_distribution"][hour] += 1
            
            # Reasons
            reason = log.get("reason", "unknown")
            analysis["top_reasons"][reason] += 1
        
        # Averages
        analysis["avg_complexity"] = total_complexity / len(logs)
        analysis["avg_response_time"] = total_response_time / len(logs)
        analysis["local_percentage"] = (analysis["local"] / len(logs)) * 100 if logs else 0
        
        return analysis
    
    def print_dashboard(self, hours: int = 24):
        """Print formatted dashboard"""
        
        print("\n" + "="*70)
        print(f"{'Smart Escalation Dashboard':^70}")
        print("="*70 + "\n")
        
        # Overall stats
        savings = self.engine.get_cost_savings()
        
        print("📊 Overall Statistics (All Time)")
        print("-" * 70)
        print(f"  Total queries:         {savings.get('total_queries', 0):,}")
        print(f"  Local queries:         {savings.get('local_queries', 0):,} ({savings.get('local_percentage', 0):.1f}%)")
        print(f"  Cloud queries:         {savings.get('cloud_queries', 0):,}")
        print(f"  Tokens saved:          {savings.get('tokens_saved', 0):,}")
        print(f"  💰 Cost saved:         ${savings.get('cost_saved', 0):.4f}")
        
        if savings.get('started'):
            started = datetime.fromisoformat(savings['started'])
            days_running = (datetime.now() - started).days + 1
            print(f"  Running for:           {days_running} days")
            print(f"  Avg savings/day:       ${savings.get('cost_saved', 0) / days_running:.4f}")
        
        print()
        
        # Recent activity
        logs = self._load_recent_logs(hours)
        analysis = self._analyze_logs(logs)
        
        print(f"📈 Recent Activity (Last {hours} hours)")
        print("-" * 70)
        print(f"  Queries:               {analysis['total']:,}")
        print(f"  Local:                 {analysis['local']:,} ({analysis.get('local_percentage', 0):.1f}%)")
        print(f"  Cloud:                 {analysis['cloud']:,}")
        print(f"  Avg complexity:        {analysis['avg_complexity']:.1f}/100")
        print(f"  Avg response time:     {analysis['avg_response_time']:.0f}ms")
        print(f"  Tokens saved:          {analysis['total_tokens_saved']:,}")
        print(f"  💰 Cost saved:         ${analysis['total_cost_saved']:.4f}")
        print()
        
        # Complexity distribution
        print("🎯 Complexity Distribution")
        print("-" * 70)
        dist = analysis['complexity_distribution']
        total = analysis['total'] or 1
        
        low_pct = (dist['low'] / total) * 100
        med_pct = (dist['medium'] / total) * 100
        high_pct = (dist['high'] / total) * 100
        
        print(f"  Low (0-33):            {'█' * int(low_pct/2)} {dist['low']} ({low_pct:.1f}%)")
        print(f"  Medium (34-66):        {'█' * int(med_pct/2)} {dist['medium']} ({med_pct:.1f}%)")
        print(f"  High (67-100):         {'█' * int(high_pct/2)} {dist['high']} ({high_pct:.1f}%)")
        print()
        
        # Top escalation reasons
        if analysis['top_reasons']:
            print("🔍 Top Escalation Reasons")
            print("-" * 70)
            
            sorted_reasons = sorted(
                analysis['top_reasons'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            for reason, count in sorted_reasons:
                pct = (count / total) * 100
                print(f"  {reason:40s} {count:4d} ({pct:.1f}%)")
            
            print()
        
        # Recent queries (last 10)
        if logs:
            print("🕐 Recent Queries (Last 10)")
            print("-" * 70)
            
            for log in logs[-10:]:
                timestamp = datetime.fromisoformat(log["timestamp"]).strftime("%H:%M:%S")
                route = "LOCAL" if log["route"] == "local" else "CLOUD"
                query = log["query"][:50] + "..." if len(log["query"]) > 50 else log["query"]
                complexity = log.get("complexity", {}).get("overall", 0)
                
                route_symbol = "⚡" if route == "LOCAL" else "☁️"
                print(f"  {timestamp} {route_symbol} [{route:5s}] C:{complexity:3d} | {query}")
            
            print()
        
        print("="*70)
        print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
    
    def watch(self, hours: int = 24, refresh: int = 5):
        """Watch mode - refresh dashboard every N seconds"""
        import os
        
        try:
            while True:
                os.system('clear' if os.name != 'nt' else 'cls')
                self.print_dashboard(hours)
                print(f"Refreshing every {refresh} seconds... (Ctrl+C to exit)")
                time.sleep(refresh)
        except KeyboardInterrupt:
            print("\nExiting watch mode.")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Escalation routing dashboard")
    parser.add_argument("--hours", type=int, default=24,
                       help="Hours of recent activity to show (default: 24)")
    parser.add_argument("--watch", action="store_true",
                       help="Watch mode - auto-refresh")
    parser.add_argument("--refresh", type=int, default=5,
                       help="Refresh interval for watch mode (seconds)")
    
    args = parser.parse_args()
    
    dashboard = EscalationDashboard()
    
    if args.watch:
        dashboard.watch(args.hours, args.refresh)
    else:
        dashboard.print_dashboard(args.hours)


if __name__ == "__main__":
    main()
