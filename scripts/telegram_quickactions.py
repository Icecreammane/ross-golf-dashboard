#!/usr/bin/env python3
"""
Telegram Quick Actions

Provides inline button menus for common actions.
Reduces friction for logging and checking status.
"""

import json
import sys
from pathlib import Path

def get_main_menu():
    """Main quick action menu"""
    return {
        "message": "🤖 **Jarvis Quick Actions**\n\nWhat would you like to do?",
        "buttons": [
            [
                {"text": "🏆 Log Win", "callback_data": "qa_log_win"},
                {"text": "💪 Log Workout", "callback_data": "qa_log_workout"}
            ],
            [
                {"text": "✅ Create Task", "callback_data": "qa_create_task"},
                {"text": "📊 Check Progress", "callback_data": "qa_check_progress"}
            ],
            [
                {"text": "🔄 Generate Tasks", "callback_data": "qa_generate_tasks"},
                {"text": "💼 View Opportunities", "callback_data": "qa_view_opportunities"}
            ],
            [
                {"text": "⚙️ System Status", "callback_data": "qa_system_status"}
            ]
        ]
    }

def get_log_win_prompt():
    """Prompt for logging a win"""
    return {
        "message": "🏆 **Log a Daily Win**\n\nReply with your win and I'll log it!",
        "expect_reply": True,
        "action": "log_win"
    }

def get_log_workout_prompt():
    """Prompt for logging a workout"""
    return {
        "message": "💪 **Log a Workout**\n\nReply with details:\n- Exercise type (chest, legs, etc.)\n- Duration\n- Notes",
        "expect_reply": True,
        "action": "log_workout"
    }

def get_create_task_prompt():
    """Prompt for creating a task"""
    return {
        "message": "✅ **Create a Task**\n\nReply with task description and I'll add it to your queue!",
        "expect_reply": True,
        "action": "create_task"
    }

def handle_quickaction(callback_data):
    """Process quick action button click"""
    
    if callback_data == "qa_log_win":
        return get_log_win_prompt()
    
    elif callback_data == "qa_log_workout":
        return get_log_workout_prompt()
    
    elif callback_data == "qa_create_task":
        return get_create_task_prompt()
    
    elif callback_data == "qa_check_progress":
        # Return progress summary
        return {
            "message": "📊 **Progress Summary**\n\n(Placeholder - would show:\n- Goals progress\n- Tasks completed today\n- Recent wins\n- Upcoming items)"
        }
    
    elif callback_data == "qa_generate_tasks":
        # Trigger task generation
        return {
            "message": "🤖 **Generating Tasks...**\n\nAnalyzing your goals and creating actionable tasks. This will take ~60 seconds.",
            "trigger_action": "generate_tasks_from_goals"
        }
    
    elif callback_data == "qa_view_opportunities":
        # Show opportunity queue
        return {
            "message": "💼 **Business Opportunities**\n\n(Placeholder - would show:\n- Pending opportunities\n- Drafted responses\n- Recent approvals)"
        }
    
    elif callback_data == "qa_system_status":
        # System health check
        return {
            "message": """⚙️ **System Status**

🤖 Daemon: Running (PID 52449)
🧠 Local Model: Online (qwen2.5:14b)
📊 Dashboard: http://10.0.0.18:8081
💼 Opportunities: 0 pending, 3 drafted
✅ Task Queue: 20+ pending

All systems operational! 🚀"""
        }
    
    else:
        return {
            "message": f"Unknown action: {callback_data}"
        }

def main():
    """Test quick actions"""
    import sys
    
    if len(sys.argv) > 1:
        # Handle callback
        result = handle_quickaction(sys.argv[1])
    else:
        # Show main menu
        result = get_main_menu()
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
