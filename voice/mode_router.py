#!/usr/bin/env python3
"""
Mode Router - Route parsed commands to the right systems
Connects voice commands to Jarvis's capabilities
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

class ModeRouter:
    def __init__(self, workspace_root: str = "/Users/clawdbot/clawd"):
        self.workspace = Path(workspace_root)
    
    def route(self, parsed_command) -> Dict[str, Any]:
        """
        Route parsed command to appropriate handler
        
        Args:
            parsed_command: ParsedCommand object from VoiceCommandParser
        
        Returns:
            {
                "handler": "name_of_handler",
                "action": "specific_action",
                "params": {...},
                "requires_api": bool,
                "estimated_time": seconds
            }
        """
        intent = parsed_command.intent
        params = parsed_command.parameters
        
        routing_map = {
            # Status queries
            "get_mrr": {
                "handler": "stripe_api",
                "action": "get_mrr",
                "params": {},
                "requires_api": True,
                "estimated_time": 2
            },
            "get_revenue": {
                "handler": "stripe_api",
                "action": "get_total_revenue",
                "params": {},
                "requires_api": True,
                "estimated_time": 2
            },
            "get_progress": {
                "handler": "accountability",
                "action": "check_progress",
                "params": {},
                "requires_api": False,
                "estimated_time": 1
            },
            "check_launch": {
                "handler": "launch_tracker",
                "action": "get_status",
                "params": {},
                "requires_api": False,
                "estimated_time": 1
            },
            
            # Mode activation
            "activate_sales_mode": {
                "handler": "sales_mode",
                "action": "activate",
                "params": {"leads": params.get("leads", 5)},
                "requires_api": False,
                "estimated_time": 5
            },
            "activate_build_mode": {
                "handler": "build_mode",
                "action": "activate",
                "params": {},
                "requires_api": False,
                "estimated_time": 1
            },
            "activate_research_mode": {
                "handler": "research_mode",
                "action": "activate",
                "params": {},
                "requires_api": False,
                "estimated_time": 1
            },
            
            # Data logging
            "log_workout": {
                "handler": "fitness_tracker",
                "action": "log_workout",
                "params": {"description": params.get("description", "")},
                "requires_api": False,
                "estimated_time": 1
            },
            "log_food": {
                "handler": "nutrition_tracker",
                "action": "log_food",
                "params": {"description": params.get("description", "")},
                "requires_api": False,
                "estimated_time": 1
            },
            "log_win": {
                "handler": "win_tracker",
                "action": "log_win",
                "params": {"description": params.get("description", "")},
                "requires_api": False,
                "estimated_time": 1
            },
            
            # Guidance
            "get_next_task": {
                "handler": "task_manager",
                "action": "get_next_priority",
                "params": {},
                "requires_api": False,
                "estimated_time": 1
            },
            "get_advice": {
                "handler": "advisor",
                "action": "get_guidance",
                "params": {},
                "requires_api": False,
                "estimated_time": 2
            },
            "check_accountability": {
                "handler": "accountability",
                "action": "check_status",
                "params": {},
                "requires_api": False,
                "estimated_time": 1
            }
        }
        
        routing = routing_map.get(intent, {
            "handler": "unknown",
            "action": "fallback",
            "params": {},
            "requires_api": False,
            "estimated_time": 0
        })
        
        # Add metadata
        routing["intent"] = intent
        routing["parsed_at"] = datetime.now().isoformat()
        
        return routing
    
    def execute(self, routing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the routed command
        
        Args:
            routing: Output from route()
        
        Returns:
            {
                "success": bool,
                "result": Any,
                "error": Optional[str]
            }
        """
        handler = routing["handler"]
        action = routing["action"]
        params = routing["params"]
        
        try:
            # Route to appropriate handler
            if handler == "stripe_api":
                return self._handle_stripe(action, params)
            
            elif handler == "accountability":
                return self._handle_accountability(action, params)
            
            elif handler == "sales_mode":
                return self._handle_sales_mode(action, params)
            
            elif handler == "fitness_tracker":
                return self._handle_fitness(action, params)
            
            elif handler == "nutrition_tracker":
                return self._handle_nutrition(action, params)
            
            elif handler == "win_tracker":
                return self._handle_wins(action, params)
            
            elif handler == "task_manager":
                return self._handle_tasks(action, params)
            
            elif handler == "launch_tracker":
                return self._handle_launch(action, params)
            
            else:
                return {
                    "success": False,
                    "result": None,
                    "error": f"Unknown handler: {handler}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "error": str(e)
            }
    
    # Handler implementations
    
    def _handle_stripe(self, action: str, params: Dict) -> Dict:
        """Handle Stripe API calls"""
        # This would integrate with actual Stripe API
        # For now, return placeholder
        return {
            "success": True,
            "result": {
                "action": action,
                "message": "Stripe API integration pending"
            }
        }
    
    def _handle_accountability(self, action: str, params: Dict) -> Dict:
        """Handle accountability system"""
        if action == "check_progress":
            from accountability.intervention_engine import InterventionEngine
            engine = InterventionEngine(str(self.workspace))
            stats = engine.get_effectiveness_stats()
            
            return {
                "success": True,
                "result": stats
            }
        
        elif action == "check_status":
            from accountability.predictor import ProcrastinationPredictor
            predictor = ProcrastinationPredictor(str(self.workspace))
            prediction = predictor.predict_procrastination()
            
            return {
                "success": True,
                "result": prediction
            }
        
        return {"success": False, "error": "Unknown accountability action"}
    
    def _handle_sales_mode(self, action: str, params: Dict) -> Dict:
        """Handle sales mode activation"""
        leads = params.get("leads", 5)
        
        return {
            "success": True,
            "result": {
                "mode": "sales",
                "leads_to_find": leads,
                "message": f"Sales mode activated. Finding {leads} leads..."
            }
        }
    
    def _handle_fitness(self, action: str, params: Dict) -> Dict:
        """Handle fitness tracking"""
        description = params.get("description", "")
        
        # Log to fitness file
        fitness_file = self.workspace / "memory" / "fitness.jsonl"
        entry = {
            "timestamp": int(datetime.now().timestamp()),
            "datetime": datetime.now().isoformat(),
            "type": "workout",
            "description": description
        }
        
        with open(fitness_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        return {
            "success": True,
            "result": {"logged": description}
        }
    
    def _handle_nutrition(self, action: str, params: Dict) -> Dict:
        """Handle nutrition tracking"""
        description = params.get("description", "")
        
        # Log to nutrition file
        nutrition_file = self.workspace / "memory" / "nutrition.jsonl"
        entry = {
            "timestamp": int(datetime.now().timestamp()),
            "datetime": datetime.now().isoformat(),
            "type": "food",
            "description": description
        }
        
        with open(nutrition_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        return {
            "success": True,
            "result": {"logged": description}
        }
    
    def _handle_wins(self, action: str, params: Dict) -> Dict:
        """Handle win tracking"""
        description = params.get("description", "")
        
        # Log to wins file
        wins_file = self.workspace / "memory" / "wins.jsonl"
        entry = {
            "timestamp": int(datetime.now().timestamp()),
            "datetime": datetime.now().isoformat(),
            "win": description
        }
        
        with open(wins_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        return {
            "success": True,
            "result": {"logged": description}
        }
    
    def _handle_tasks(self, action: str, params: Dict) -> Dict:
        """Handle task management"""
        # Read from GOALS.md or task queue
        goals_file = self.workspace / "GOALS.md"
        
        if goals_file.exists():
            return {
                "success": True,
                "result": {
                    "message": "Check GOALS.md for next priority"
                }
            }
        
        return {
            "success": True,
            "result": {
                "message": "No tasks configured yet"
            }
        }
    
    def _handle_launch(self, action: str, params: Dict) -> Dict:
        """Handle launch tracking"""
        return {
            "success": True,
            "result": {
                "message": "Launch tracking integration pending"
            }
        }


# CLI interface
if __name__ == "__main__":
    import sys
    from voice.command_parser import VoiceCommandParser
    
    if len(sys.argv) < 2:
        print("Usage: python mode_router.py <command>")
        sys.exit(1)
    
    text = " ".join(sys.argv[1:])
    
    # Parse command
    parser = VoiceCommandParser()
    parsed = parser.parse(text)
    
    if not parsed:
        print("❌ Could not parse command")
        sys.exit(1)
    
    print(f"✅ Parsed: {parsed.intent}")
    
    # Route command
    router = ModeRouter()
    routing = router.route(parsed)
    
    print(f"📍 Routed to: {routing['handler']} → {routing['action']}")
    
    # Execute
    result = router.execute(routing)
    
    if result["success"]:
        print(f"✅ Success: {result['result']}")
    else:
        print(f"❌ Error: {result['error']}")
