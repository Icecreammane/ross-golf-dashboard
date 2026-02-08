#!/usr/bin/env python3
"""
Telegram Escalation Middleware - Intercepts and routes Telegram messages

Hooks into Telegram message flow to intelligently route queries:
- Low complexity: Answered instantly by local Llama
- High complexity: Forwarded to Sonnet (normal flow)

This middleware is transparent to the user - they just get faster responses
for simple queries and don't notice the routing.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from smart_escalation_engine import get_engine

WORKSPACE = Path.home() / "clawd"


class TelegramEscalationMiddleware:
    """Middleware for Telegram message routing"""
    
    def __init__(self):
        self.engine = get_engine()
        self.enabled = True  # Can be toggled via config
        self.config_file = WORKSPACE / "config" / "escalation_config.json"
        self._load_config()
    
    def _load_config(self):
        """Load escalation configuration"""
        try:
            if self.config_file.exists():
                config = json.loads(self.config_file.read_text())
                self.enabled = config.get("enabled", True)
                
                # Allow per-user overrides
                self.user_overrides = config.get("user_overrides", {})
        except Exception as e:
            print(f"Warning: Could not load escalation config: {e}", file=sys.stderr)
            self.user_overrides = {}
    
    def _should_process(self, message: Dict) -> bool:
        """Determine if message should go through escalation"""
        
        # Check if globally disabled
        if not self.enabled:
            return False
        
        # Skip if message is from a bot
        if message.get("from_bot", False):
            return False
        
        # Skip if message contains media/files (let main agent handle)
        if message.get("has_media", False) or message.get("has_file", False):
            return False
        
        # Skip commands (those go directly to main agent)
        text = message.get("text", "")
        if text.startswith("/"):
            return False
        
        # Check user overrides
        user_id = message.get("user_id")
        if user_id in self.user_overrides:
            return self.user_overrides[user_id].get("enabled", True)
        
        return True
    
    def _build_context(self, message: Dict) -> Dict:
        """Build context for escalation engine"""
        return {
            "platform": "telegram",
            "user_id": message.get("user_id"),
            "chat_type": message.get("chat_type", "private"),
            "timestamp": message.get("timestamp"),
            "has_reply": message.get("reply_to") is not None,
            "message_id": message.get("message_id")
        }
    
    def process_message(self, message: Dict) -> Dict:
        """
        Process incoming Telegram message
        
        Args:
            message: Dict with keys: text, user_id, chat_type, timestamp, etc.
        
        Returns:
            Dict with:
                - action: "respond_local" | "forward_cloud" | "error"
                - response: Local response text (if action=respond_local)
                - decision: Routing decision details
                - metadata: Additional info
        """
        
        # Check if we should process this message
        if not self._should_process(message):
            return {
                "action": "forward_cloud",
                "reason": "escalation_disabled_for_message",
                "decision": None
            }
        
        query = message.get("text", "").strip()
        
        if not query:
            return {
                "action": "forward_cloud",
                "reason": "empty_message",
                "decision": None
            }
        
        # Build context
        context = self._build_context(message)
        
        # Route the query
        try:
            decision = self.engine.route_query(query, context)
            
            if decision.route == "local" and decision.local_response:
                # Local response ready!
                return {
                    "action": "respond_local",
                    "response": decision.local_response,
                    "decision": decision,
                    "metadata": {
                        "response_time_ms": decision.response_time_ms,
                        "complexity": decision.complexity.overall,
                        "tokens_saved": decision.tokens_saved,
                        "cost_saved": decision.cost_saved
                    }
                }
            else:
                # Escalate to cloud
                return {
                    "action": "forward_cloud",
                    "reason": decision.reason,
                    "decision": decision,
                    "metadata": {
                        "complexity": decision.complexity.overall,
                        "escalation_reason": decision.reason
                    }
                }
        
        except Exception as e:
            # On error, escalate to be safe
            print(f"Error in escalation middleware: {e}", file=sys.stderr)
            return {
                "action": "forward_cloud",
                "reason": f"middleware_error: {str(e)}",
                "decision": None
            }
    
    def format_response(self, response: str, metadata: Dict = None) -> str:
        """
        Format local response for Telegram
        
        Optionally adds metadata footer for transparency
        """
        
        # For now, just return the response as-is
        # Could add: "⚡ Local response" footer if desired
        
        return response
    
    def get_stats(self) -> Dict:
        """Get middleware statistics"""
        return self.engine.get_cost_savings()


# Global middleware instance
_middleware = None

def get_middleware() -> TelegramEscalationMiddleware:
    """Get singleton middleware instance"""
    global _middleware
    if _middleware is None:
        _middleware = TelegramEscalationMiddleware()
    return _middleware


def intercept_telegram_message(message: Dict) -> Dict:
    """
    Main entry point for Telegram message interception
    
    This function should be called by the Telegram handler before
    forwarding messages to the main agent.
    
    Usage in telegram handler:
        from telegram_escalation_middleware import intercept_telegram_message
        
        # Before sending to main agent:
        result = intercept_telegram_message(message)
        
        if result["action"] == "respond_local":
            # Send local response immediately
            send_telegram_message(result["response"])
            return  # Don't forward to cloud
        else:
            # Forward to cloud as normal
            forward_to_main_agent(message)
    """
    middleware = get_middleware()
    return middleware.process_message(message)


# CLI for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Telegram escalation middleware")
    parser.add_argument("text", help="Message text to test")
    parser.add_argument("--user-id", default="12345", help="User ID")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    
    args = parser.parse_args()
    
    if args.stats:
        middleware = get_middleware()
        stats = middleware.get_stats()
        print(json.dumps(stats, indent=2))
    else:
        # Test message
        test_message = {
            "text": args.text,
            "user_id": args.user_id,
            "chat_type": "private",
            "timestamp": datetime.now().isoformat(),
            "message_id": 123,
            "has_media": False,
            "has_file": False,
            "from_bot": False
        }
        
        result = intercept_telegram_message(test_message)
        
        print(json.dumps({
            "action": result["action"],
            "reason": result.get("reason"),
            "response": result.get("response"),
            "metadata": result.get("metadata")
        }, indent=2))
