#!/usr/bin/env python3
"""
/ask command - Fast local decision analysis for opportunity prioritization

Usage: /ask Which of these 3 opportunities should I pursue?

Fast (<2s), all local LLM analysis using decision history, conversion rates,
revenue potential, and effort required.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
import subprocess
import re

WORKSPACE = Path.home() / "clawd"
DECISION_HISTORY_FILE = WORKSPACE / "memory" / "decision_history.json"
CONVERSION_DATA_FILE = WORKSPACE / "memory" / "conversion_data.json"


class AskCommand:
    def __init__(self):
        self.decision_history = self._load_decision_history()
        self.conversion_data = self._load_conversion_data()
    
    def _load_decision_history(self):
        """Load past decisions for learning"""
        if DECISION_HISTORY_FILE.exists():
            try:
                with open(DECISION_HISTORY_FILE) as f:
                    return json.load(f)
            except:
                return {"decisions": []}
        return {"decisions": []}
    
    def _load_conversion_data(self):
        """Load conversion rates and revenue data"""
        if CONVERSION_DATA_FILE.exists():
            try:
                with open(CONVERSION_DATA_FILE) as f:
                    return json.load(f)
            except:
                return self._default_conversion_data()
        return self._default_conversion_data()
    
    def _default_conversion_data(self):
        """Default conversion rates based on opportunity type"""
        return {
            "email_inquiry": {
                "conversion_rate": 0.67,
                "avg_revenue": 290,
                "avg_effort_hours": 2
            },
            "partnership": {
                "conversion_rate": 0.30,
                "avg_revenue": 500,
                "avg_effort_hours": 8
            },
            "feature_request": {
                "conversion_rate": 0.10,
                "avg_revenue": 0,
                "avg_effort_hours": 4
            },
            "cold_outreach": {
                "conversion_rate": 0.15,
                "avg_revenue": 350,
                "avg_effort_hours": 3
            },
            "consulting": {
                "conversion_rate": 0.50,
                "avg_revenue": 450,
                "avg_effort_hours": 6
            },
            "product_idea": {
                "conversion_rate": 0.20,
                "avg_revenue": 1000,
                "avg_effort_hours": 20
            }
        }
    
    def _extract_opportunities_from_context(self, question, recent_context=None):
        """
        Extract opportunities from the question or recent context.
        In production, this would parse recent messages/emails/opportunities.
        """
        # For now, return a simple structure that the user can fill
        # In real usage, this would pull from opportunity_scanner or email context
        opportunities = []
        
        # Check if there are recent opportunities in memory
        opps_file = WORKSPACE / "memory" / "current_opportunities.json"
        if opps_file.exists():
            try:
                with open(opps_file) as f:
                    data = json.load(f)
                    opportunities = data.get("opportunities", [])[:5]  # Max 5
            except:
                pass
        
        return opportunities
    
    def _classify_opportunity_type(self, opp_text):
        """Classify opportunity to match against conversion data"""
        text_lower = opp_text.lower()
        
        if any(word in text_lower for word in ["email", "inquiry", "question", "golf"]):
            return "email_inquiry"
        elif any(word in text_lower for word in ["partnership", "collaborate", "joint"]):
            return "partnership"
        elif any(word in text_lower for word in ["feature", "request", "suggestion", "improvement"]):
            return "feature_request"
        elif any(word in text_lower for word in ["consulting", "advice", "coaching"]):
            return "consulting"
        elif any(word in text_lower for word in ["product", "build", "idea", "startup"]):
            return "product_idea"
        else:
            return "cold_outreach"
    
    def _score_opportunity(self, opp, opp_type):
        """Score an opportunity based on conversion data"""
        data = self.conversion_data.get(opp_type, self.conversion_data["cold_outreach"])
        
        conversion_rate = data["conversion_rate"]
        avg_revenue = data["avg_revenue"]
        effort_hours = data["avg_effort_hours"]
        
        # Expected value = conversion_rate * revenue
        expected_value = conversion_rate * avg_revenue
        
        # ROI = expected_value / effort_hours
        roi = expected_value / max(effort_hours, 0.5)
        
        # Overall score (weighted)
        score = (
            (conversion_rate * 30) +  # 30% weight on conversion
            (min(avg_revenue / 100, 10) * 25) +  # 25% weight on revenue (capped at 10)
            (roi * 25) +  # 25% weight on ROI
            ((10 - min(effort_hours, 10)) * 20)  # 20% weight on low effort (inverted)
        )
        
        return {
            "score": round(score, 2),
            "conversion_rate": conversion_rate,
            "expected_revenue": round(expected_value, 2),
            "effort_hours": effort_hours,
            "roi": round(roi, 2)
        }
    
    def _query_local_llm(self, prompt, max_tokens=500):
        """Query local LLM via ollama"""
        try:
            # Try fast models first, fall back to larger models
            models_to_try = ["qwen2.5:3b", "llama3.1:8b", "qwen2.5:14b"]
            
            # Check which models are available
            try:
                list_result = subprocess.run(
                    ["ollama", "list"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                available_models = list_result.stdout
                
                # Use first available model
                model = None
                for m in models_to_try:
                    if m in available_models:
                        model = m
                        break
                
                if not model:
                    return None  # No suitable models
            except:
                return None
            
            cmd = ["ollama", "run", model, "--no-interactive"]
            
            result = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=3  # 3 second timeout
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return None
        except Exception as e:
            print(f"LLM error: {e}")
            return None
    
    def analyze(self, question, opportunities=None):
        """Main analysis function"""
        start_time = time.time()
        
        # If no opportunities provided, try to extract from context
        if not opportunities:
            opportunities = self._extract_opportunities_from_context(question)
        
        if not opportunities or len(opportunities) == 0:
            return {
                "error": "No opportunities found. Add to memory/current_opportunities.json or provide in question.",
                "response_time": round(time.time() - start_time, 2)
            }
        
        # Score each opportunity
        scored = []
        for idx, opp in enumerate(opportunities):
            opp_text = opp if isinstance(opp, str) else opp.get("description", str(opp))
            opp_type = self._classify_opportunity_type(opp_text)
            scores = self._score_opportunity(opp, opp_type)
            
            scored.append({
                "label": chr(65 + idx),  # A, B, C, etc.
                "description": opp_text[:100],  # Truncate for display
                "type": opp_type,
                **scores
            })
        
        # Sort by score (highest first)
        scored.sort(key=lambda x: x["score"], reverse=True)
        
        # Build LLM prompt for additional reasoning
        prompt = self._build_llm_prompt(question, scored)
        llm_reasoning = self._query_local_llm(prompt)
        
        response_time = round(time.time() - start_time, 2)
        
        # Format response
        result = {
            "question": question,
            "ranked_opportunities": scored,
            "llm_reasoning": llm_reasoning,
            "response_time": response_time,
            "recommendation": self._format_recommendation(scored, llm_reasoning)
        }
        
        # Log decision for learning
        self._log_decision(question, result)
        
        return result
    
    def _build_llm_prompt(self, question, scored_opps):
        """Build prompt for local LLM analysis"""
        prompt = f"""You are a decision advisor. Analyze these opportunities and provide BRIEF reasoning (2-3 sentences).

Question: {question}

Opportunities (pre-scored):
"""
        for opp in scored_opps:
            prompt += f"\n{opp['label']}: {opp['description']}"
            prompt += f"\n  - Conversion: {int(opp['conversion_rate']*100)}%"
            prompt += f"\n  - Expected revenue: ${opp['expected_revenue']}"
            prompt += f"\n  - Effort: {opp['effort_hours']}h"
            prompt += f"\n  - Score: {opp['score']}/10"
        
        prompt += "\n\nProvide brief reasoning for why the top option is best. Be concise."
        
        return prompt
    
    def _format_recommendation(self, scored, llm_reasoning):
        """Format the final recommendation"""
        lines = []
        
        # Ranking
        for opp in scored:
            line = f"{opp['label']}: {opp['description'][:60]}"
            line += f" ({int(opp['conversion_rate']*100)}% conversion, "
            line += f"${opp['expected_revenue']} expected, "
            line += f"{opp['effort_hours']}h effort)"
            lines.append(line)
        
        ranking = " > ".join([o['label'] for o in scored])
        
        output = f"**Ranking:** {ranking}\n\n"
        output += "\n".join([f"{i+1}. {line}" for i, line in enumerate(lines)])
        
        if llm_reasoning:
            output += f"\n\n**Reasoning:** {llm_reasoning}"
        
        return output
    
    def _log_decision(self, question, result):
        """Log decision for future learning"""
        decision_entry = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "recommendation": result["ranked_opportunities"][0]["label"],
            "response_time": result["response_time"],
            "opportunities": result["ranked_opportunities"]
        }
        
        self.decision_history["decisions"].append(decision_entry)
        
        # Keep last 100 decisions
        if len(self.decision_history["decisions"]) > 100:
            self.decision_history["decisions"] = self.decision_history["decisions"][-100:]
        
        # Save
        DECISION_HISTORY_FILE.parent.mkdir(exist_ok=True)
        with open(DECISION_HISTORY_FILE, 'w') as f:
            json.dump(self.decision_history, f, indent=2)


def handle_ask_command(question_text, opportunities=None):
    """
    Main entry point for /ask command
    
    Args:
        question_text: The decision question from user
        opportunities: Optional list of opportunities to analyze
    
    Returns:
        Formatted string response
    """
    cmd = AskCommand()
    result = cmd.analyze(question_text, opportunities)
    
    if "error" in result:
        return f"❌ {result['error']}"
    
    output = result["recommendation"]
    output += f"\n\n⚡ Response time: {result['response_time']}s"
    
    return output


if __name__ == "__main__":
    # Test mode
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 ask_command.py 'Your decision question'")
        sys.exit(1)
    
    question = " ".join(sys.argv[1:])
    response = handle_ask_command(question)
    print(response)
