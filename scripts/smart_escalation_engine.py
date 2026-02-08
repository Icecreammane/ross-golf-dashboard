#!/usr/bin/env python3
"""
Smart Escalation Engine - Intelligent LLM routing layer

Routes user queries to local Llama or cloud Sonnet based on complexity scoring.
Tracks cost savings and logs all routing decisions.
"""

import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass, asdict

WORKSPACE = Path.home() / "clawd"
ESCALATION_LOG = WORKSPACE / "memory" / "escalation.log"
COST_LOG = WORKSPACE / "memory" / "escalation_cost_savings.json"

# Pricing (per million tokens)
SONNET_INPUT_COST = 3.00  # $3 per 1M input tokens
SONNET_OUTPUT_COST = 15.00  # $15 per 1M output tokens
LOCAL_COST = 0.00  # Free!

# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"
SCORING_MODEL = "qwen2.5:14b"  # Strong reasoning for scoring
RESPONSE_MODEL = "llama3.1:8b"  # Fast for simple queries


@dataclass
class ComplexityScore:
    """Multi-dimensional complexity scoring"""
    overall: int  # 0-100
    factual_vs_reasoning: int  # 0 (pure fact) to 100 (deep reasoning)
    data_retrieval: int  # 0 (no data needed) to 100 (complex data queries)
    decision_making: int  # 0 (no decision) to 100 (critical decision)
    time_sensitivity: int  # 0 (not urgent) to 100 (immediate)
    reversibility: int  # 0 (easily reversible) to 100 (irreversible)
    confidence: int  # 0-100, local model's confidence in handling this
    
    def should_escalate(self) -> bool:
        """Determine if query should escalate to cloud"""
        # High complexity = always escalate
        if self.overall > 50:
            return True
        
        # Low confidence = escalate
        if self.confidence < 70:
            return True
        
        # Critical decisions = escalate
        if self.decision_making > 70 and self.reversibility > 70:
            return True
        
        # Otherwise, handle locally
        return False
    
    def get_reason(self) -> str:
        """Get human-readable escalation reason"""
        if self.overall > 50:
            return f"High complexity ({self.overall}/100)"
        if self.confidence < 70:
            return f"Low confidence ({self.confidence}%)"
        if self.decision_making > 70 and self.reversibility > 70:
            return "Critical irreversible decision"
        return "Local handling"


@dataclass
class RoutingDecision:
    """Complete routing decision with metadata"""
    query: str
    route: str  # "local" or "cloud"
    complexity: ComplexityScore
    reason: str
    timestamp: float
    response_time_ms: Optional[int] = None
    tokens_saved: Optional[int] = None
    cost_saved: Optional[float] = None
    local_response: Optional[str] = None


class SmartEscalationEngine:
    def __init__(self):
        self.workspace = WORKSPACE
        self.log_file = ESCALATION_LOG
        self.cost_log = COST_LOG
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """Ensure log directories exist"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.cost_log.parent.mkdir(parents=True, exist_ok=True)
    
    def _call_ollama(self, model: str, prompt: str, system: str = None) -> Dict:
        """Call Ollama API"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            if system:
                payload["system"] = system
            
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # Fallback: if local LLM fails, escalate
            return {"error": str(e), "response": "", "eval_count": 0}
    
    def _extract_json_from_response(self, text: str) -> Dict:
        """Extract JSON from LLM response (handles markdown blocks)"""
        text = text.strip()
        
        # Remove markdown code blocks
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
            if text.startswith("json"):
                text = text[4:]
        
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            # Try to find JSON object in text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(text[start:end])
                except:
                    pass
            
            # Fallback: return default escalation scores
            return {
                "overall": 75,
                "factual_vs_reasoning": 50,
                "data_retrieval": 50,
                "decision_making": 50,
                "time_sensitivity": 50,
                "reversibility": 50,
                "confidence": 30
            }
    
    def score_complexity(self, query: str, context: Dict = None) -> ComplexityScore:
        """Score query complexity using local LLM"""
        
        system_prompt = """You are a query complexity analyzer. Score queries on multiple dimensions (0-100).
Return ONLY valid JSON with these exact fields:
{
  "overall": <0-100>,
  "factual_vs_reasoning": <0=pure fact, 100=deep reasoning>,
  "data_retrieval": <0=no data, 100=complex queries>,
  "decision_making": <0=no decision, 100=critical decision>,
  "time_sensitivity": <0=not urgent, 100=immediate>,
  "reversibility": <0=easily reversible, 100=irreversible>,
  "confidence": <0-100, your confidence in handling this locally>
}

Guidelines:
- Factual queries (weather, time, definitions): overall 0-20
- Light reasoning (explanations, comparisons): overall 21-50
- High complexity (strategic decisions, code architecture, multi-step reasoning): overall 51-100
- Low confidence if query needs external APIs, personal judgment, or creative work"""

        user_prompt = f"""Score this query:

Query: "{query}"

Context: {json.dumps(context or {}, indent=2)}

Return ONLY the JSON scoring object, no explanation."""

        start_time = time.time()
        result = self._call_ollama(SCORING_MODEL, user_prompt, system_prompt)
        score_time = int((time.time() - start_time) * 1000)
        
        if "error" in result:
            # If scoring fails, escalate to be safe
            return ComplexityScore(
                overall=75,
                factual_vs_reasoning=50,
                data_retrieval=50,
                decision_making=50,
                time_sensitivity=50,
                reversibility=50,
                confidence=30
            )
        
        scores = self._extract_json_from_response(result.get("response", "{}"))
        
        return ComplexityScore(
            overall=min(100, max(0, scores.get("overall", 50))),
            factual_vs_reasoning=min(100, max(0, scores.get("factual_vs_reasoning", 50))),
            data_retrieval=min(100, max(0, scores.get("data_retrieval", 50))),
            decision_making=min(100, max(0, scores.get("decision_making", 50))),
            time_sensitivity=min(100, max(0, scores.get("time_sensitivity", 50))),
            reversibility=min(100, max(0, scores.get("reversibility", 50))),
            confidence=min(100, max(0, scores.get("confidence", 50)))
        )
    
    def generate_local_response(self, query: str, context: Dict = None) -> Tuple[str, int]:
        """Generate response using local LLM with available data"""
        
        # Gather available local data
        available_data = self._gather_local_data(context)
        
        system_prompt = """You are Jarvis, Ross's AI assistant. Answer queries using available local data.
Be concise, accurate, and helpful. If you're unsure, say so clearly.
If the query requires external data or complex reasoning beyond your capability, say: "ESCALATE_NEEDED"."""

        user_prompt = f"""Query: {query}

Available data:
{json.dumps(available_data, indent=2)}

Respond directly to the query. Be brief and accurate."""

        start_time = time.time()
        result = self._call_ollama(RESPONSE_MODEL, user_prompt, system_prompt)
        response_time = int((time.time() - start_time) * 1000)
        
        if "error" in result:
            return "ESCALATE_NEEDED", response_time
        
        response = result.get("response", "").strip()
        
        # Check if local model wants to escalate
        if "ESCALATE_NEEDED" in response:
            return "ESCALATE_NEEDED", response_time
        
        return response, response_time
    
    def _gather_local_data(self, context: Dict = None) -> Dict:
        """Gather available local data for context"""
        data = {
            "workspace": str(self.workspace),
            "current_time": datetime.now().isoformat(),
            "context": context or {}
        }
        
        # Add quick reads of recent memory if available
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            memory_file = self.workspace / "memory" / f"{today}.md"
            if memory_file.exists():
                data["today_memory"] = memory_file.read_text()[:500]  # First 500 chars
        except:
            pass
        
        # Add dashboard data if available
        try:
            dashboard_file = self.workspace / "data" / "dashboard.json"
            if dashboard_file.exists():
                data["dashboard"] = json.loads(dashboard_file.read_text())
        except:
            pass
        
        return data
    
    def route_query(self, query: str, context: Dict = None) -> RoutingDecision:
        """Main routing logic - decide local or cloud"""
        
        start_time = time.time()
        
        # Step 1: Score complexity
        complexity = self.score_complexity(query, context)
        
        # Step 2: Decide route
        should_escalate = complexity.should_escalate()
        route = "cloud" if should_escalate else "local"
        reason = complexity.get_reason()
        
        # Step 3: If local, try to generate response
        local_response = None
        response_time_ms = None
        
        if route == "local":
            local_response, response_time_ms = self.generate_local_response(query, context)
            
            # If local model escalates itself, change route
            if local_response == "ESCALATE_NEEDED":
                route = "cloud"
                reason = "Local model requested escalation"
                local_response = None
        
        # Calculate cost savings
        tokens_saved = 0
        cost_saved = 0.0
        
        if route == "local":
            # Estimate tokens (rough: 1 token ≈ 4 chars)
            estimated_tokens = len(query) // 4 + len(local_response or "") // 4
            tokens_saved = estimated_tokens
            
            # Calculate cost saved
            input_cost = (len(query) // 4) / 1_000_000 * SONNET_INPUT_COST
            output_cost = (len(local_response or "") // 4) / 1_000_000 * SONNET_OUTPUT_COST
            cost_saved = input_cost + output_cost
        
        total_time = int((time.time() - start_time) * 1000)
        
        decision = RoutingDecision(
            query=query,
            route=route,
            complexity=complexity,
            reason=reason,
            timestamp=time.time(),
            response_time_ms=response_time_ms or total_time,
            tokens_saved=tokens_saved,
            cost_saved=cost_saved,
            local_response=local_response
        )
        
        # Log decision
        self._log_decision(decision)
        
        # Update cost savings
        if route == "local":
            self._update_cost_savings(tokens_saved, cost_saved)
        
        return decision
    
    def _log_decision(self, decision: RoutingDecision):
        """Log routing decision to escalation.log"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(decision.timestamp).isoformat(),
            "route": decision.route,
            "query": decision.query[:100] + "..." if len(decision.query) > 100 else decision.query,
            "reason": decision.reason,
            "complexity": asdict(decision.complexity),
            "response_time_ms": decision.response_time_ms,
            "tokens_saved": decision.tokens_saved,
            "cost_saved": round(decision.cost_saved, 6) if decision.cost_saved else 0
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def _update_cost_savings(self, tokens: int, cost: float):
        """Update cumulative cost savings"""
        try:
            if self.cost_log.exists():
                data = json.loads(self.cost_log.read_text())
            else:
                data = {
                    "total_queries": 0,
                    "local_queries": 0,
                    "cloud_queries": 0,
                    "tokens_saved": 0,
                    "cost_saved": 0.0,
                    "started": datetime.now().isoformat()
                }
            
            data["total_queries"] += 1
            data["local_queries"] += 1
            data["tokens_saved"] += tokens
            data["cost_saved"] += cost
            data["last_updated"] = datetime.now().isoformat()
            data["local_percentage"] = round(
                (data["local_queries"] / data["total_queries"]) * 100, 1
            )
            
            self.cost_log.write_text(json.dumps(data, indent=2))
        
        except Exception as e:
            print(f"Warning: Could not update cost savings: {e}")
    
    def get_cost_savings(self) -> Dict:
        """Get current cost savings stats"""
        if not self.cost_log.exists():
            return {
                "total_queries": 0,
                "local_queries": 0,
                "cloud_queries": 0,
                "tokens_saved": 0,
                "cost_saved": 0.0,
                "local_percentage": 0
            }
        
        try:
            return json.loads(self.cost_log.read_text())
        except:
            return {}


# Singleton instance
_engine = None

def get_engine() -> SmartEscalationEngine:
    """Get singleton engine instance"""
    global _engine
    if _engine is None:
        _engine = SmartEscalationEngine()
    return _engine


if __name__ == "__main__":
    # Quick test
    engine = get_engine()
    
    test_queries = [
        "What time is it?",
        "Should I invest in Bitcoin or Ethereum?",
        "Summarize today's memory",
        "Design a distributed system architecture for real-time video processing"
    ]
    
    print("Smart Escalation Engine - Test Run\n")
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        decision = engine.route_query(query)
        print(f"Route: {decision.route} ({decision.reason})")
        print(f"Complexity: {decision.complexity.overall}/100")
        print(f"Confidence: {decision.complexity.confidence}%")
        print(f"Response time: {decision.response_time_ms}ms")
        
        if decision.local_response:
            print(f"Local response: {decision.local_response[:200]}...")
    
    print("\n" + "="*60)
    savings = engine.get_cost_savings()
    print(f"\nCost Savings Summary:")
    print(f"  Total queries: {savings['total_queries']}")
    print(f"  Local: {savings['local_queries']} ({savings.get('local_percentage', 0)}%)")
    print(f"  Cloud: {savings['cloud_queries']}")
    print(f"  Tokens saved: {savings['tokens_saved']:,}")
    print(f"  Cost saved: ${savings['cost_saved']:.4f}")
