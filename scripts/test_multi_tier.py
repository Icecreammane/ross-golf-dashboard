#!/usr/bin/env python3
"""
Quick test of multi-tier intelligence routing system
Shows routing decisions and cost savings without actually executing tasks
"""

from local_router import LocalRouter


def test_routing():
    """Test routing decisions for various tasks"""
    router = LocalRouter()
    
    print("\n" + "="*70)
    print("🧠 MULTI-TIER INTELLIGENCE ROUTING TEST")
    print("="*70 + "\n")
    
    test_cases = [
        ("Check my email for urgent messages", None, "Email check"),
        ("What's the weather today?", None, "Weather check"),
        ("Summarize this 5-page article", None, "Summarization"),
        ("Draft a professional email to decline a meeting", None, "Draft writing"),
        ("Should I accept this job offer at $150K with equity?", {"urgent": True}, "Strategic decision"),
        ("Build a React component for user authentication", None, "Code generation"),
        ("What's in this food photo?", {"has_image": True}, "Vision analysis"),
        ("Parse my calendar for conflicts next week", None, "Calendar parsing"),
    ]
    
    total_sonnet_cost = 0
    total_local_cost = 0
    total_tasks = len(test_cases)
    local_tasks = 0
    
    for task, context, label in test_cases:
        routing = router.route_task(task, context)
        
        # Estimate costs (assume 500 tokens input, 500 output)
        if routing["model"] == "sonnet":
            task_cost = (500 * 3.0 / 1_000_000) + (500 * 15.0 / 1_000_000)  # $0.009
            total_sonnet_cost += task_cost
        else:
            task_cost = 0.0  # Free!
            total_local_cost += 0.0
            local_tasks += 1
        
        model_emoji = {
            "ollama": "🟢",
            "ollama-smart": "🟡",
            "sonnet": "🔴"
        }
        
        print(f"{model_emoji[routing['model']]} {label}")
        print(f"   Task: {task[:60]}{'...' if len(task) > 60 else ''}")
        print(f"   → Model: {routing['model']} (complexity: {routing['complexity']}/10)")
        print(f"   → Cost: ${task_cost:.4f}")
        print(f"   → Reasoning: {routing['reasoning']}")
        print()
    
    # Summary
    print("="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"Total tasks: {total_tasks}")
    print(f"Local tasks: {local_tasks} ({local_tasks/total_tasks*100:.1f}%)")
    print(f"Sonnet tasks: {total_tasks - local_tasks} ({(total_tasks-local_tasks)/total_tasks*100:.1f}%)")
    print()
    
    # Cost comparison
    all_sonnet_cost = total_tasks * 0.009  # If all tasks used Sonnet
    actual_cost = total_sonnet_cost
    savings = all_sonnet_cost - actual_cost
    reduction = (savings / all_sonnet_cost * 100) if all_sonnet_cost > 0 else 0
    
    print(f"💰 COST ANALYSIS")
    print(f"   Without multi-tier: ${all_sonnet_cost:.4f}")
    print(f"   With multi-tier:    ${actual_cost:.4f}")
    print(f"   💚 Saved:           ${savings:.4f}")
    print(f"   📉 Reduction:       {reduction:.1f}%")
    print()
    
    # Projection
    daily_tasks = 50  # Estimate
    daily_savings = (savings / total_tasks) * daily_tasks
    monthly_savings = daily_savings * 30
    
    print(f"🔮 PROJECTIONS (assuming {daily_tasks} tasks/day)")
    print(f"   Daily savings:   ~${daily_savings:.2f}")
    print(f"   Monthly savings: ~${monthly_savings:.2f}")
    print()
    
    print("="*70)
    print("✅ Multi-tier routing reduces costs by routing simple tasks to FREE local AI!")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_routing()
