#!/usr/bin/env python3
"""
Predictor - Predict procrastination before it happens
Uses pattern analysis to generate early warnings and interventions
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple
from accountability.pattern_analyzer import PatternAnalyzer

class ProcrastinationPredictor:
    def __init__(self, workspace_root: str = "/Users/clawdbot/clawd"):
        self.workspace = Path(workspace_root)
        self.analyzer = PatternAnalyzer(workspace_root)
        
    def predict_procrastination(
        self, 
        current_context: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Predict likelihood of procrastination in the next hour
        
        Returns:
            {
                "risk_level": "low" | "medium" | "high",
                "confidence": 0.0-1.0,
                "reasons": ["list", "of", "reasons"],
                "historical_pattern": "description"
            }
        """
        now = datetime.now()
        current_hour = now.hour
        current_day = now.strftime("%A").lower()
        current_time = self._categorize_time(current_hour)
        
        # Get patterns
        procrastination_patterns = self.analyzer.analyze_procrastination_patterns(days=14)
        
        risk_factors = []
        risk_score = 0.0
        
        # Check day of week pattern
        day_events = procrastination_patterns["by_day_of_week"].get(current_day, 0)
        if day_events >= 3:
            risk_score += 0.3
            risk_factors.append(f"{current_day.title()} historically has {day_events} procrastination events")
        
        # Check time of day pattern
        time_events = procrastination_patterns["by_time_of_day"].get(current_time, 0)
        if time_events >= 2:
            risk_score += 0.3
            risk_factors.append(f"{current_time.title()} is a high-risk time ({time_events} events)")
        
        # Check if this exact hour has been problematic
        activities = self.analyzer.load_activities(days=14)
        hour_history = [
            act for act in activities 
            if act["hour"] == current_hour and act["type"] == "procrastinating"
        ]
        if len(hour_history) >= 2:
            risk_score += 0.4
            risk_factors.append(f"This hour ({current_hour}:00) has {len(hour_history)} procrastination events in last 2 weeks")
        
        # Check recent streak
        recent_activities = self.analyzer.load_activities(days=1)
        recent_procrastination = [
            act for act in recent_activities 
            if act["type"] == "procrastinating" and (now.timestamp() - act["timestamp"]) < 3600
        ]
        if recent_procrastination:
            risk_score += 0.3
            risk_factors.append("Already procrastinated in the last hour")
        
        # Determine risk level
        if risk_score >= 0.7:
            risk_level = "high"
        elif risk_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        confidence = min(risk_score, 1.0)
        
        return {
            "risk_level": risk_level,
            "confidence": confidence,
            "risk_score": risk_score,
            "reasons": risk_factors,
            "current_hour": current_hour,
            "current_day": current_day,
            "current_time": current_time,
            "prediction_timestamp": now.isoformat()
        }
    
    def generate_intervention(
        self,
        prediction: Dict,
        scheduled_task: Optional[str] = None
    ) -> str:
        """
        Generate an intervention message based on prediction
        
        Args:
            prediction: Output from predict_procrastination()
            scheduled_task: Current task Ross should be working on
        
        Returns:
            Intervention message string
        """
        risk_level = prediction["risk_level"]
        now = datetime.now()
        
        if risk_level == "low":
            return None  # No intervention needed
        
        time_str = now.strftime("%I:%M %p")
        day_str = now.strftime("%A")
        
        # Build intervention message
        if risk_level == "high":
            urgency = "🚨 HIGH RISK ALERT"
        else:
            urgency = "⚠️ HEADS UP"
        
        msg = f"{urgency}\n\n"
        msg += f"It's {time_str} on {day_str}. "
        
        # Add pattern context
        if prediction["reasons"]:
            msg += "Historical pattern detected:\n"
            for reason in prediction["reasons"]:
                msg += f"• {reason}\n"
            msg += "\n"
        
        # Add task context if available
        if scheduled_task:
            msg += f"**Today's priority**: {scheduled_task}\n\n"
            msg += "**DO IT NOW** before the pattern kicks in.\n"
        else:
            msg += "**Action**: Start your next revenue task NOW.\n"
        
        msg += f"\nProcrastination typically hits in the next 5-15 minutes.\n"
        msg += "Break the pattern. Move."
        
        return msg
    
    def should_intervene(
        self,
        prediction: Dict,
        last_intervention_time: Optional[datetime] = None
    ) -> bool:
        """
        Decide if we should send an intervention now
        
        Args:
            prediction: Current prediction
            last_intervention_time: When we last intervened
        
        Returns:
            True if intervention should be sent
        """
        # Don't intervene on low risk
        if prediction["risk_level"] == "low":
            return False
        
        # Don't spam interventions (wait at least 2 hours)
        if last_intervention_time:
            hours_since = (datetime.now() - last_intervention_time).seconds / 3600
            if hours_since < 2:
                return False
        
        # High risk = always intervene
        if prediction["risk_level"] == "high":
            return True
        
        # Medium risk = intervene if confidence > 0.5
        return prediction["confidence"] > 0.5
    
    def _categorize_time(self, hour: int) -> str:
        """Categorize hour into time of day"""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"


# CLI interface
if __name__ == "__main__":
    predictor = ProcrastinationPredictor()
    
    prediction = predictor.predict_procrastination()
    
    print(f"🔮 Procrastination Risk: {prediction['risk_level'].upper()}")
    print(f"   Confidence: {prediction['confidence']*100:.0f}%")
    print(f"   Time: {prediction['current_time']} ({prediction['current_hour']}:00)")
    print(f"   Day: {prediction['current_day'].title()}")
    
    if prediction['reasons']:
        print("\n📊 Risk Factors:")
        for reason in prediction['reasons']:
            print(f"   • {reason}")
    
    intervention = predictor.generate_intervention(
        prediction,
        scheduled_task="Example: Deploy FitTrack by 12pm"
    )
    
    if intervention:
        print("\n" + "="*60)
        print(intervention)
        print("="*60)
