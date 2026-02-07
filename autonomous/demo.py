#!/usr/bin/env python3
"""
Autonomous Operations Demo

Demonstrates the system in action with sample tasks.
"""

import sys
import time
sys.path.append('/Users/clawdbot/clawd/autonomous')

from build_scheduler import BuildScheduler, BuildTask, Priority
from autonomous_queue import AutonomousQueue
from context_scheduler import ContextScheduler
from problem_predictor import ProblemPredictor
from pattern_learner import PatternLearner
from self_improver import SelfImprover

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def demo_build_queue():
    print_header("1. BUILD QUEUE DEMONSTRATION")
    
    queue = AutonomousQueue()
    
    print("Adding sample tasks...\n")
    
    # Add various tasks
    tasks = [
        ("Optimize database queries", "Profile and optimize slow queries in fitness tracker", 2.0, "Performance optimization", Priority.HIGH),
        ("Build workout analytics", "Create charts showing workout trends over time", 5.0, "New features", Priority.MEDIUM),
        ("Fix crash on empty workout", "Handle edge case when workout has no exercises", 0.5, "Bug fixes", Priority.CRITICAL),
        ("Document REST API", "Write comprehensive API documentation", 2.0, "Documentation", Priority.MEDIUM),
        ("Research revenue opportunities", "Analyze fitness SaaS market and pricing", 8.0, "Research/analysis", Priority.HIGH),
    ]
    
    for title, desc, hours, category, priority in tasks:
        task_id = queue.add_to_queue(title, desc, hours, category, priority, auto_approve=(category in ["Performance optimization", "Bug fixes", "Documentation"]))
        auto_str = "AUTO-APPROVE" if category in ["Performance optimization", "Bug fixes", "Documentation"] else "NEEDS APPROVAL"
        print(f"✅ Added: {title} ({hours}h, {auto_str})")
    
    print("\n📊 Queue Statistics:")
    stats = queue.scheduler.get_stats()
    print(f"   Total tasks: {stats['total']}")
    print(f"   Queued: {stats['queued']}")
    
    time.sleep(1)

def demo_context_scheduler():
    print_header("2. CONTEXT-AWARE SCHEDULING")
    
    scheduler = ContextScheduler()
    
    print("Detecting current context...\n")
    context = scheduler.detect_context()
    
    print(f"📍 Current Context: {context.value}")
    print(f"⚡ Work Intensity: {scheduler.get_work_intensity(context)}")
    print(f"🔨 Max Concurrent: {scheduler.get_max_concurrent_builds(context)}")
    print(f"🤖 Autonomous Work: {scheduler.should_work_autonomously(context)}\n")
    
    print("Appropriate work categories:")
    categories = scheduler.get_appropriate_work_categories(context)
    for cat in categories:
        print(f"   • {cat}")
    
    print("\n🔮 Upcoming contexts (next 12 hours):")
    upcoming = scheduler.get_upcoming_contexts(hours_ahead=12)
    
    current_ctx = None
    for pred in upcoming[:12]:
        from datetime import datetime
        hour = datetime.fromisoformat(pred['time']).hour
        if pred['context'] != current_ctx:
            print(f"   {hour:02d}:00 - {pred['context']}")
            current_ctx = pred['context']
    
    time.sleep(1)

def demo_problem_predictor():
    print_header("3. PROBLEM PREDICTION & AUTO-FIX")
    
    predictor = ProblemPredictor()
    
    print("Collecting system metrics...\n")
    metrics = predictor.collect_metrics()
    
    print("📊 System Health:")
    disk = metrics.get("disk", {})
    print(f"   Disk: {disk.get('percent_used', 0):.1f}% used ({disk.get('gb_free', 0):.1f}GB free)")
    
    logs = metrics.get("log_files", {})
    print(f"   Logs: {logs.get('total_size_mb', 0):.0f}MB total")
    
    db = metrics.get("database", {})
    print(f"   Databases: {db.get('count', 0)} files, {db.get('total_size_mb', 0):.0f}MB total\n")
    
    print("Scanning for potential problems...")
    problems = predictor.predict_problems()
    
    if problems:
        print(f"\n⚠️  Found {len(problems)} potential issues:")
        for p in problems:
            icon = {"critical": "🚨", "warning": "⚠️", "info": "ℹ️"}.get(p.severity, "•")
            print(f"   {icon} {p.category}: {p.description}")
            if p.auto_fixable:
                print(f"      ✅ Auto-fixable")
    else:
        print("\n✅ No problems detected")
    
    time.sleep(1)

def demo_pattern_learner():
    print_header("4. PATTERN LEARNING")
    
    learner = PatternLearner()
    
    print("Simulating usage patterns...\n")
    
    # Simulate some requests
    import json
    learner.log_request("nba_rankings", {"source": "manual"})
    learner.log_request("workout_log", {"type": "morning"})
    learner.log_request("nutrition_check", {"time": "evening"})
    
    print("✅ Logged requests (would learn patterns over time)")
    
    stats = learner.get_stats()
    print(f"\n📈 Pattern Stats:")
    print(f"   Total patterns: {stats['total_patterns']}")
    print(f"   High confidence: {stats['high_confidence']}")
    print(f"   Auto-execute enabled: {stats['auto_execute_enabled']}")
    
    if learner.patterns:
        print(f"\n📊 Learned Patterns:")
        for pattern in learner.patterns[:3]:
            print(f"   • {pattern.description} (confidence: {pattern.confidence:.0%})")
    else:
        print("\n💡 No patterns learned yet (need 3+ occurrences)")
    
    time.sleep(1)

def demo_self_improver():
    print_header("5. SELF-IMPROVEMENT")
    
    improver = SelfImprover()
    
    print("Monitoring performance...\n")
    
    # Simulate some metrics
    improver.log_response_time("database_query", 1500)
    improver.log_response_time("api_call", 800)
    
    print("✅ Logged response times")
    
    stats = improver.get_stats()
    print(f"\n📊 Performance Stats:")
    print(f"   Weaknesses detected: {stats['total_weaknesses']}")
    print(f"   Fixed: {stats['fixed']}")
    print(f"   Total improvements: {stats['total_improvements']}")
    
    suggestions = improver.suggest_improvements()
    if suggestions:
        print(f"\n💡 Improvement Suggestions:")
        for sugg in suggestions[:3]:
            print(f"   • {sugg['title']} ({sugg['estimated_hours']}h)")
    else:
        print("\n✅ No weaknesses detected (system performing well)")
    
    time.sleep(1)

def demo_overnight_runner():
    print_header("6. OVERNIGHT EXECUTION PREVIEW")
    
    from overnight_runner import OvernightRunner
    runner = OvernightRunner()
    
    is_overnight = runner.is_overnight_hours()
    
    if is_overnight:
        print("🌙 Currently overnight hours (11pm-7am)")
        print("   Autonomous work is ACTIVE\n")
    else:
        from datetime import datetime
        print(f"🌅 Currently daytime ({datetime.now().strftime('%I:%M %p')})")
        print("   Overnight runner will start at 11:00pm\n")
    
    print("📋 Overnight Schedule:")
    print("   11:00pm - Scan for problems")
    print("   11:05pm - Auto-fix problems")
    print("   11:10pm - Spawn builds (max 3 concurrent)")
    print("   Throughout night - Monitor progress")
    print("   6:30am - Generate completion report")
    print("   7:00am - Morning brief ready\n")
    
    print("🎯 Tonight's Plan:")
    scheduler = BuildScheduler()
    next_tasks = scheduler.get_next_scheduled_tasks(3)
    
    if next_tasks:
        for task in next_tasks:
            auto_str = "✅ AUTO" if task.auto_approve else "🔒 APPROVAL"
            print(f"   • {task.title} ({task.estimated_hours}h) {auto_str}")
    else:
        print("   No tasks queued for tonight (add some!)")
    
    time.sleep(1)

def demo_weekend_planner():
    print_header("7. WEEKEND BUILD PLANNING")
    
    from weekend_planner import WeekendPlanner
    planner = WeekendPlanner()
    
    is_weekend = planner.is_weekend()
    is_friday = planner.is_friday_evening()
    
    if is_weekend:
        print("📅 It's the weekend! Time for ambitious builds.\n")
    elif is_friday:
        print("🎉 Friday evening! Let's plan the weekend.\n")
    else:
        print("📅 Weekday - weekend planner activates Friday 6pm\n")
    
    print("🎯 Weekend Project Workflow:")
    print("   Friday 6pm - Present 5 project options")
    print("   Ross picks a project")
    print("   Saturday - Build in phases")
    print("   Sunday evening - Ship complete system\n")
    
    options = planner.generate_weekend_options()
    if options:
        print(f"💡 Available Weekend Projects ({len(options)}):")
        for i, opt in enumerate(options[:3], 1):
            print(f"   {i}. {opt['title']} ({opt['estimated_hours']}h)")
    else:
        print("💡 No weekend projects queued yet")
        print("   Add 8-12 hour builds to the queue!")

def main():
    print("\n" + "🚀" * 30)
    print(" " * 20 + "AUTONOMOUS OPERATIONS DEMO")
    print("🚀" * 30)
    
    try:
        demo_build_queue()
        demo_context_scheduler()
        demo_problem_predictor()
        demo_pattern_learner()
        demo_self_improver()
        demo_overnight_runner()
        demo_weekend_planner()
        
        print_header("DEMO COMPLETE")
        
        print("✅ All systems operational!")
        print("\n📚 Next Steps:")
        print("   1. Review docs in docs/AUTONOMOUS_OPERATIONS.md")
        print("   2. Add real tasks to the queue")
        print("   3. Set up cron jobs for overnight execution")
        print("   4. Let the system run tonight")
        print("   5. Check morning brief tomorrow\n")
        
        print("🎉 Ready to ship 24/7 productivity!")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
