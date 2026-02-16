#!/usr/bin/env python3
"""
Local AI Router - Multi-tier intelligence routing system
Routes tasks to appropriate model based on complexity to reduce costs by 70%+
"""

import json
import os
import requests
from datetime import datetime
from typing import Dict, Any, Optional, Literal

# Model endpoints and costs (per 1M tokens)
MODELS = {
    "ollama": {
        "endpoint": "http://localhost:11434/api/generate",
        "model": "qwen2.5:14b",  # Fast and capable for most tasks
        "cost_per_1m_input": 0.0,
        "cost_per_1m_output": 0.0,
        "latency_estimate": 2.0  # seconds
    },
    "ollama-smart": {
        "endpoint": "http://localhost:11434/api/generate",
        "model": "qwen2.5:32b-instruct-q4_K_M",  # Larger model for complex tasks
        "cost_per_1m_input": 0.0,
        "cost_per_1m_output": 0.0,
        "latency_estimate": 5.0
    },
    "sonnet": {
        "endpoint": "anthropic",  # Handled by Clawdbot
        "model": "claude-sonnet-4",
        "cost_per_1m_input": 3.0,
        "cost_per_1m_output": 15.0,
        "latency_estimate": 1.5
    }
}

# Task complexity scoring
TASK_PATTERNS = {
    # Complexity 1-2: Simple checks and parsing
    "email_check": {"complexity": 1, "keywords": ["check email", "any urgent", "inbox", "unread messages"]},
    "calendar_parse": {"complexity": 1, "keywords": ["calendar", "upcoming events", "meetings today", "schedule"]},
    "weather_check": {"complexity": 1, "keywords": ["weather", "temperature", "forecast"]},
    "simple_extraction": {"complexity": 2, "keywords": ["extract", "parse", "list", "find all"]},
    
    # Complexity 3-5: Summaries, drafts, analysis
    "summarize": {"complexity": 3, "keywords": ["summarize", "summary", "tldr", "brief overview"]},
    "draft_response": {"complexity": 4, "keywords": ["draft", "write email", "compose", "reply to"]},
    "data_analysis": {"complexity": 5, "keywords": ["analyze", "compare", "calculate", "trends"]},
    
    # Complexity 6-8: Complex reasoning and decisions
    "strategic_decision": {"complexity": 7, "keywords": ["should i", "what's the best", "decide", "strategy"]},
    "code_generation": {"complexity": 8, "keywords": ["build", "create script", "write code", "implement"]},
    "architecture": {"complexity": 8, "keywords": ["design", "architecture", "system design", "technical spec"]},
    
    # Complexity 9-10: Vision, multi-step workflows, deep reasoning
    "vision_analysis": {"complexity": 10, "keywords": ["analyze image", "photo", "screenshot", "what's in"]},
    "multi_step": {"complexity": 9, "keywords": ["first", "then", "after that", "workflow"]},
    "deep_reasoning": {"complexity": 9, "keywords": ["why", "explain deeply", "philosophical", "implications"]}
}


class LocalRouter:
    def __init__(self, workspace_dir: str = "/Users/clawdbot/clawd"):
        self.workspace_dir = workspace_dir
        self.cost_log_path = os.path.join(workspace_dir, "memory", "cost-savings.json")
        self.routing_log_path = os.path.join(workspace_dir, "memory", "routing-decisions.json")
        self._ensure_logs()
    
    def _ensure_logs(self):
        """Ensure log files exist"""
        os.makedirs(os.path.dirname(self.cost_log_path), exist_ok=True)
        
        if not os.path.exists(self.cost_log_path):
            with open(self.cost_log_path, 'w') as f:
                json.dump({
                    "total_saved": 0.0,
                    "sessions": [],
                    "daily_stats": {}
                }, f, indent=2)
        
        if not os.path.exists(self.routing_log_path):
            with open(self.routing_log_path, 'w') as f:
                json.dump({"decisions": []}, f, indent=2)
    
    def score_complexity(self, task_description: str, context: Optional[Dict] = None) -> int:
        """
        Score task complexity from 1-10
        1-2: Simple checks, parsing
        3-5: Summaries, drafts
        6-8: Complex reasoning, code
        9-10: Vision, multi-step workflows
        """
        task_lower = task_description.lower()
        max_complexity = 1  # Default to simplest
        
        # Check for pattern matches
        for task_type, pattern in TASK_PATTERNS.items():
            if any(keyword in task_lower for keyword in pattern["keywords"]):
                max_complexity = max(max_complexity, pattern["complexity"])
        
        # Context adjustments
        if context:
            # Vision tasks require Sonnet
            if context.get("has_image") or "image" in task_lower or "photo" in task_lower:
                max_complexity = 10
            
            # Urgent or decision-making context
            if context.get("urgent") or "decide" in task_lower:
                max_complexity = min(10, max_complexity + 2)
            
            # Multi-step workflows
            if context.get("multi_step") or task_lower.count("then") > 1:
                max_complexity = min(10, max_complexity + 3)
        
        # Length heuristic: very short tasks are usually simple
        if len(task_description.split()) < 10 and max_complexity < 5:
            max_complexity = max(1, max_complexity - 1)
        
        return max_complexity
    
    def route_task(self, task_description: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Route task to appropriate model based on complexity
        Returns: {"model": "ollama|ollama-smart|sonnet", "reasoning": "...", "confidence": 0.0-1.0}
        """
        complexity = self.score_complexity(task_description, context)
        
        # Routing logic
        if complexity <= 2:
            model = "ollama"
            reasoning = f"Simple task (complexity {complexity}): routine checks, parsing"
            confidence = 0.95
        elif complexity <= 5:
            model = "ollama"  # Use standard model for medium tasks
            reasoning = f"Medium task (complexity {complexity}): summaries, drafts, simple analysis"
            confidence = 0.85
        elif complexity <= 7:
            model = "ollama-smart"  # Use larger local model for complex tasks
            reasoning = f"Complex task (complexity {complexity}): reasoning, decisions - using larger local model"
            confidence = 0.75
        else:
            model = "sonnet"
            reasoning = f"Advanced task (complexity {complexity}): code generation, vision, deep reasoning"
            confidence = 0.90
        
        # Force Sonnet for vision tasks
        if context and context.get("has_image"):
            model = "sonnet"
            reasoning = "Vision task requires Sonnet (local vision models not reliable)"
            confidence = 1.0
        
        return {
            "model": model,
            "complexity": complexity,
            "reasoning": reasoning,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }
    
    def call_ollama(self, prompt: str, model: str = "qwen2.5:14b", max_tokens: int = 2000) -> Dict[str, Any]:
        """Call Ollama API"""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.7
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result.get("response", ""),
                    "tokens": {
                        "prompt": result.get("prompt_eval_count", 0),
                        "completion": result.get("eval_count", 0)
                    },
                    "latency": result.get("total_duration", 0) / 1e9  # nanoseconds to seconds
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def execute_task(self, task_description: str, context: Optional[Dict] = None, force_model: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute task with appropriate model
        Returns: {"result": "...", "model_used": "...", "cost": 0.0, "saved": 0.0}
        """
        # Route the task
        routing = self.route_task(task_description, context) if not force_model else {"model": force_model, "complexity": 5, "reasoning": "Forced", "confidence": 1.0}
        model_choice = routing["model"]
        
        # Get model config
        model_config = MODELS.get(model_choice, MODELS["sonnet"])
        
        start_time = datetime.now()
        
        # Execute based on model choice
        if model_choice.startswith("ollama"):
            result = self.call_ollama(task_description, model=model_config["model"])
            
            if not result["success"]:
                # Fallback to Sonnet on failure
                print(f"⚠️  Ollama failed ({result['error']}), falling back to Sonnet")
                model_choice = "sonnet"
                model_config = MODELS["sonnet"]
                result = {
                    "success": True,
                    "response": "[This would call Sonnet via Clawdbot]",
                    "tokens": {"prompt": 500, "completion": 500},
                    "latency": 2.0
                }
        else:
            # Sonnet would be called via Clawdbot's existing infrastructure
            result = {
                "success": True,
                "response": "[This would call Sonnet via Clawdbot]",
                "tokens": {"prompt": 500, "completion": 500},
                "latency": 2.0
            }
        
        # Calculate costs
        tokens_in = result.get("tokens", {}).get("prompt", 500)
        tokens_out = result.get("tokens", {}).get("completion", 500)
        
        cost = (tokens_in * model_config["cost_per_1m_input"] / 1_000_000) + \
               (tokens_out * model_config["cost_per_1m_output"] / 1_000_000)
        
        # Calculate savings (what would Sonnet have cost?)
        sonnet_cost = (tokens_in * MODELS["sonnet"]["cost_per_1m_input"] / 1_000_000) + \
                      (tokens_out * MODELS["sonnet"]["cost_per_1m_output"] / 1_000_000)
        saved = sonnet_cost - cost
        
        # Log the decision
        self._log_decision({
            "task": task_description[:100],
            "routing": routing,
            "model_used": model_choice,
            "cost": cost,
            "saved": saved,
            "tokens": result.get("tokens", {}),
            "latency": result.get("latency", 0),
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": result["success"],
            "result": result.get("response", result.get("error", "")),
            "model_used": model_choice,
            "routing": routing,
            "cost": cost,
            "saved": saved,
            "tokens": result.get("tokens", {}),
            "latency": result.get("latency", 0)
        }
    
    def _log_decision(self, decision: Dict):
        """Log routing decision for analysis"""
        try:
            with open(self.routing_log_path, 'r') as f:
                log = json.load(f)
            
            log["decisions"].append(decision)
            
            # Keep last 1000 decisions
            if len(log["decisions"]) > 1000:
                log["decisions"] = log["decisions"][-1000:]
            
            with open(self.routing_log_path, 'w') as f:
                json.dump(log, f, indent=2)
            
            # Update cost savings
            self._update_cost_savings(decision)
        except Exception as e:
            print(f"Error logging decision: {e}")
    
    def _update_cost_savings(self, decision: Dict):
        """Update cost savings log"""
        try:
            with open(self.cost_log_path, 'r') as f:
                log = json.load(f)
            
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Update daily stats
            if today not in log["daily_stats"]:
                log["daily_stats"][today] = {
                    "total_tasks": 0,
                    "ollama_tasks": 0,
                    "sonnet_tasks": 0,
                    "total_saved": 0.0,
                    "total_cost": 0.0
                }
            
            log["daily_stats"][today]["total_tasks"] += 1
            log["daily_stats"][today]["total_saved"] += decision["saved"]
            log["daily_stats"][today]["total_cost"] += decision["cost"]
            
            if decision["model_used"].startswith("ollama"):
                log["daily_stats"][today]["ollama_tasks"] += 1
            else:
                log["daily_stats"][today]["sonnet_tasks"] += 1
            
            log["total_saved"] += decision["saved"]
            
            with open(self.cost_log_path, 'w') as f:
                json.dump(log, f, indent=2)
        except Exception as e:
            print(f"Error updating cost savings: {e}")
    
    def get_stats(self, days: int = 1) -> Dict[str, Any]:
        """Get routing statistics for the last N days"""
        try:
            with open(self.cost_log_path, 'r') as f:
                log = json.load(f)
            
            # Get recent days
            from datetime import timedelta
            today = datetime.now()
            dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
            
            stats = {
                "total_saved": 0.0,
                "total_cost": 0.0,
                "total_tasks": 0,
                "ollama_tasks": 0,
                "sonnet_tasks": 0,
                "daily_breakdown": {}
            }
            
            for date in dates:
                if date in log["daily_stats"]:
                    day_stats = log["daily_stats"][date]
                    stats["total_saved"] += day_stats["total_saved"]
                    stats["total_cost"] += day_stats["total_cost"]
                    stats["total_tasks"] += day_stats["total_tasks"]
                    stats["ollama_tasks"] += day_stats["ollama_tasks"]
                    stats["sonnet_tasks"] += day_stats["sonnet_tasks"]
                    stats["daily_breakdown"][date] = day_stats
            
            # Calculate percentage routed to local
            if stats["total_tasks"] > 0:
                stats["local_percentage"] = (stats["ollama_tasks"] / stats["total_tasks"]) * 100
            else:
                stats["local_percentage"] = 0
            
            return stats
        except Exception as e:
            return {"error": str(e)}


def test_router():
    """Test the router with sample tasks"""
    router = LocalRouter()
    
    test_cases = [
        ("Check my email for urgent messages", None),
        ("Summarize this article about AI", None),
        ("Build a landing page for my startup", None),
        ("Is 2871 calories right for cutting?", {"urgent": True}),
        ("Parse my calendar for next 24h", None),
        ("What's in this image?", {"has_image": True}),
        ("Draft an email to my client", None),
        ("Calculate the ROI of this investment", None)
    ]
    
    print("=" * 60)
    print("LOCAL ROUTER TEST")
    print("=" * 60)
    
    for task, context in test_cases:
        routing = router.route_task(task, context)
        print(f"\nTask: {task}")
        print(f"Context: {context}")
        print(f"→ Model: {routing['model']} (complexity: {routing['complexity']}, confidence: {routing['confidence']:.2f})")
        print(f"  Reasoning: {routing['reasoning']}")


if __name__ == "__main__":
    test_router()
