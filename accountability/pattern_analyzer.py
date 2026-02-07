#!/usr/bin/env python3
"""
Pattern Analyzer - Extract insights from logged activity
Identifies productivity patterns, procrastination triggers, and optimal work times
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

class PatternAnalyzer:
    def __init__(self, workspace_root: str = "/Users/clawdbot/clawd"):
        self.workspace = Path(workspace_root)
        self.pattern_dir = self.workspace / "memory" / "patterns"
        self.activity_file = self.pattern_dir / "daily-activity.jsonl"
    
    def load_activities(self, days: int = 7) -> List[Dict]:
        """Load activities from last N days"""
        if not self.activity_file.exists():
            return []
        
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_ts = int(cutoff.timestamp())
        
        activities = []
        with open(self.activity_file, "r") as f:
            for line in f:
                entry = json.loads(line.strip())
                if entry["timestamp"] >= cutoff_ts:
                    activities.append(entry)
        
        return activities
    
    def analyze_productivity_windows(self, days: int = 7) -> Dict[str, Any]:
        """Find when Ross is most productive"""
        activities = self.load_activities(days)
        
        # Group by hour
        hourly_stats = defaultdict(lambda: {"total": 0, "completed": 0, "tasks": []})
        
        for act in activities:
            if act["type"] in ["revenue_task", "building", "selling"]:
                hour = act["hour"]
                hourly_stats[hour]["total"] += 1
                if act["completed"]:
                    hourly_stats[hour]["completed"] += 1
                hourly_stats[hour]["tasks"].append(act["action"])
        
        # Calculate completion rates
        productivity_by_hour = {}
        for hour, stats in hourly_stats.items():
            if stats["total"] > 0:
                completion_rate = stats["completed"] / stats["total"]
                productivity_by_hour[hour] = {
                    "completion_rate": completion_rate,
                    "total_tasks": stats["total"],
                    "completed_tasks": stats["completed"]
                }
        
        # Find best hours
        best_hours = sorted(
            productivity_by_hour.items(),
            key=lambda x: (x[1]["completion_rate"], x[1]["total_tasks"]),
            reverse=True
        )[:3]
        
        return {
            "hourly_breakdown": productivity_by_hour,
            "best_hours": [{"hour": h, **stats} for h, stats in best_hours],
            "analysis_period_days": days
        }
    
    def analyze_procrastination_patterns(self, days: int = 7) -> Dict[str, Any]:
        """Identify when and how procrastination happens"""
        activities = self.load_activities(days)
        
        # Find procrastination entries
        procrastination_events = [
            act for act in activities 
            if act["type"] == "procrastinating" or not act["completed"]
        ]
        
        # Group by day of week
        by_day = defaultdict(list)
        for event in procrastination_events:
            by_day[event["day_of_week"]].append(event)
        
        # Group by time of day
        by_time = defaultdict(list)
        for event in procrastination_events:
            by_time[event["time_of_day"]].append(event)
        
        # Find peak procrastination times
        peak_day = max(by_day.items(), key=lambda x: len(x[1])) if by_day else (None, [])
        peak_time = max(by_time.items(), key=lambda x: len(x[1])) if by_time else (None, [])
        
        return {
            "total_events": len(procrastination_events),
            "by_day_of_week": {day: len(events) for day, events in by_day.items()},
            "by_time_of_day": {time: len(events) for time, events in by_time.items()},
            "peak_procrastination_day": peak_day[0],
            "peak_procrastination_time": peak_time[0],
            "avg_duration_minutes": sum(e["duration"] for e in procrastination_events) / len(procrastination_events) / 60 if procrastination_events else 0
        }
    
    def analyze_task_avoidance(self, days: int = 7) -> Dict[str, Any]:
        """Identify which task types Ross avoids"""
        activities = self.load_activities(days)
        
        task_type_stats = defaultdict(lambda: {"attempted": 0, "completed": 0, "abandoned": 0})
        
        for act in activities:
            task_type = act["type"]
            task_type_stats[task_type]["attempted"] += 1
            if act["completed"]:
                task_type_stats[task_type]["completed"] += 1
            else:
                task_type_stats[task_type]["abandoned"] += 1
        
        # Calculate completion rates
        avoidance_analysis = {}
        for task_type, stats in task_type_stats.items():
            completion_rate = stats["completed"] / stats["attempted"] if stats["attempted"] > 0 else 0
            avoidance_analysis[task_type] = {
                "completion_rate": completion_rate,
                "attempted": stats["attempted"],
                "completed": stats["completed"],
                "abandoned": stats["abandoned"]
            }
        
        # Rank by avoidance (low completion rate + high abandonment)
        avoided_tasks = sorted(
            avoidance_analysis.items(),
            key=lambda x: (x[1]["completion_rate"], -x[1]["abandoned"])
        )
        
        return {
            "task_type_breakdown": avoidance_analysis,
            "most_avoided": avoided_tasks[0][0] if avoided_tasks else None,
            "most_completed": avoided_tasks[-1][0] if avoided_tasks else None
        }
    
    def generate_weekly_report(self, days: int = 7) -> str:
        """Generate human-readable weekly analysis"""
        productivity = self.analyze_productivity_windows(days)
        procrastination = self.analyze_procrastination_patterns(days)
        avoidance = self.analyze_task_avoidance(days)
        
        report = f"# Pattern Analysis - Last {days} Days\n\n"
        
        # Productivity windows
        report += "## 🎯 Peak Productivity Windows\n\n"
        if productivity["best_hours"]:
            for i, hour_data in enumerate(productivity["best_hours"], 1):
                hour = hour_data["hour"]
                rate = hour_data["completion_rate"] * 100
                tasks = hour_data["total_tasks"]
                time = datetime.strptime(f"{hour}:00", "%H:%M").strftime("%I:%M %p")
                report += f"{i}. **{time}**: {rate:.0f}% completion rate ({tasks} tasks)\n"
        else:
            report += "Not enough data yet. Keep logging!\n"
        
        report += "\n## 🚨 Procrastination Patterns\n\n"
        if procrastination["total_events"] > 0:
            report += f"- **Total procrastination events**: {procrastination['total_events']}\n"
            report += f"- **Peak day**: {procrastination['peak_procrastination_day'] or 'N/A'}\n"
            report += f"- **Peak time**: {procrastination['peak_procrastination_time'] or 'N/A'}\n"
            report += f"- **Avg duration**: {procrastination['avg_duration_minutes']:.0f} minutes\n"
        else:
            report += "No procrastination detected! 🎉\n"
        
        report += "\n## 🎭 Task Preferences\n\n"
        if avoidance["most_avoided"]:
            report += f"- **Most avoided**: {avoidance['most_avoided']}\n"
        if avoidance["most_completed"]:
            report += f"- **Most completed**: {avoidance['most_completed']}\n"
        
        report += "\n### Task Type Breakdown\n\n"
        for task_type, stats in avoidance["task_type_breakdown"].items():
            rate = stats["completion_rate"] * 100
            report += f"- **{task_type}**: {rate:.0f}% completion ({stats['completed']}/{stats['attempted']})\n"
        
        return report
    
    def get_insights_json(self, days: int = 7) -> Dict[str, Any]:
        """Get all insights as structured data"""
        return {
            "generated_at": datetime.now().isoformat(),
            "analysis_period_days": days,
            "productivity_windows": self.analyze_productivity_windows(days),
            "procrastination_patterns": self.analyze_procrastination_patterns(days),
            "task_avoidance": self.analyze_task_avoidance(days)
        }


# CLI interface
if __name__ == "__main__":
    import sys
    
    analyzer = PatternAnalyzer()
    
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    
    print(analyzer.generate_weekly_report(days))
