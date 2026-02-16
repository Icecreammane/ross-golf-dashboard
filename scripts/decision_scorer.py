#!/usr/bin/env python3
"""
Decision Confidence Scorer - Determines if I should execute autonomously or ask

Every decision gets a confidence score:
- >80: Execute without asking
- 60-80: Execute + notify
- 40-60: Ask with recommendation
- <40: Ask for clarification
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import os

class DecisionScorer:
    def __init__(self):
        self.workspace = Path(os.path.expanduser('~/clawd'))
        self.decision_log_file = self.workspace / 'memory' / 'decision-log.json'
        self.patterns_file = self.workspace / 'memory' / 'decision-patterns.json'
        
        # Load historical patterns
        self.patterns = self._load_patterns()
        self.history = self._load_history()
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load historical decision patterns"""
        if self.patterns_file.exists():
            with open(self.patterns_file) as f:
                return json.load(f)
        return {
            'category_approvals': {},
            'time_patterns': {},
            'mood_patterns': {},
            'confidence_adjustments': {}
        }
    
    def _load_history(self) -> list:
        """Load decision history"""
        if self.decision_log_file.exists():
            with open(self.decision_log_file) as f:
                return json.load(f)
        return []
    
    def score_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a decision for autonomy
        
        Args:
            decision: {
                'type': 'data_work|revenue|automation|external|creative|unknown',
                'request': 'full request text',
                'clarity': 'high|medium|low',
                'time_of_day': '23:19',
                'recent_mood': 'frustrated|focused|exploratory|casual',
                'similar_past_decisions': ['decision_id_1', 'decision_id_2']
            }
        
        Returns:
            {
                'confidence': 0-100,
                'recommendation': 'EXECUTE|EXECUTE_AND_NOTIFY|ASK_WITH_RECOMMENDATION|ASK_PERMISSION',
                'reasoning': 'explanation',
                'category_score': 0-100,
                'clarity_score': 0-100,
                'time_alignment': 0-100,
                'similar_past_success': 0-100
            }
        """
        
        base_confidence = 50
        category = decision.get('type', 'unknown')
        clarity = decision.get('clarity', 'medium')
        
        # Component 1: Category Approval History (0-30 points)
        category_score = self._score_category(category)
        
        # Component 2: Request Clarity (0-20 points)
        clarity_score = self._score_clarity(clarity)
        
        # Component 3: Time Alignment (0-15 points)
        time_score = self._score_time_alignment(decision.get('time_of_day'))
        
        # Component 4: Similar Past Success (0-25 points)
        past_success = self._score_similar_decisions(decision.get('similar_past_decisions', []))
        
        # Component 5: Mood Alignment (0-10 points)
        mood_score = self._score_mood_alignment(decision.get('recent_mood', 'neutral'))
        
        # Total confidence
        total_confidence = min(100, base_confidence + category_score + clarity_score + time_score + past_success + mood_score)
        
        # Determine recommendation
        if total_confidence >= 80:
            recommendation = 'EXECUTE'
        elif total_confidence >= 60:
            recommendation = 'EXECUTE_AND_NOTIFY'
        elif total_confidence >= 40:
            recommendation = 'ASK_WITH_RECOMMENDATION'
        else:
            recommendation = 'ASK_PERMISSION'
        
        return {
            'confidence': round(total_confidence, 1),
            'recommendation': recommendation,
            'reasoning': self._build_reasoning(category_score, clarity_score, time_score, past_success, mood_score),
            'scores': {
                'category': round(category_score, 1),
                'clarity': round(clarity_score, 1),
                'time_alignment': round(time_score, 1),
                'similar_past_success': round(past_success, 1),
                'mood': round(mood_score, 1)
            }
        }
    
    def _score_category(self, category: str) -> float:
        """Score based on category approval history (0-30)"""
        category_scores = self.patterns.get('category_approvals', {})
        
        # Default category scores based on typical patterns
        defaults = {
            'data_work': 25,        # High confidence in data/analysis
            'revenue': 20,          # Medium-high for revenue work
            'automation': 22,       # High for time-saving automation
            'external': 0,          # Always ask for external actions
            'creative': 5,          # Low confidence in creative decisions
            'unknown': 10           # Low for ambiguous requests
        }
        
        approval_rate = category_scores.get(category, defaults.get(category, 10))
        return approval_rate
    
    def _score_clarity(self, clarity: str) -> float:
        """Score based on request clarity (0-20)"""
        scores = {
            'high': 20,
            'medium': 10,
            'low': 0
        }
        return scores.get(clarity, 5)
    
    def _score_time_alignment(self, time_of_day: str = None) -> float:
        """Score based on time of day (0-15)"""
        if not time_of_day:
            return 7  # Neutral
        
        try:
            hour = int(time_of_day.split(':')[0])
            
            # Work hours: 9am-5pm = high confidence
            if 9 <= hour <= 17:
                return 12
            # Evening: 5pm-10pm = medium-high confidence
            elif 17 < hour <= 22:
                return 10
            # Late night: 10pm-1am = medium confidence (tired, might pivot)
            elif 22 < hour or hour < 1:
                return 8
            # Early morning: 1am-9am = low confidence (sleep time)
            else:
                return 3
        except:
            return 7
    
    def _score_similar_decisions(self, similar_ids: list) -> float:
        """Score based on similar past decisions (0-25)"""
        if not similar_ids:
            return 12  # Neutral, no history
        
        # Find outcomes of similar past decisions
        success_count = 0
        total_count = 0
        
        for past_id in similar_ids:
            for entry in self.history:
                if entry.get('id') == past_id:
                    total_count += 1
                    if entry.get('outcome') in ['success', 'partial_success']:
                        success_count += 1
        
        if total_count == 0:
            return 12
        
        success_rate = success_count / total_count
        return success_rate * 25
    
    def _score_mood_alignment(self, mood: str) -> float:
        """Score based on recent mood (0-10)"""
        scores = {
            'frustrated': 3,        # Wants quick action, less patience
            'focused': 8,           # Engaged, deliberate
            'exploratory': 6,       # Wants to think through options
            'casual': 5,            # Neutral mood
            'neutral': 5
        }
        return scores.get(mood, 5)
    
    def _build_reasoning(self, category: float, clarity: float, time: float, past: float, mood: float) -> str:
        """Build human-readable reasoning"""
        parts = []
        
        if category > 20:
            parts.append("Strong category confidence")
        elif category > 10:
            parts.append("Moderate category experience")
        else:
            parts.append("Low category confidence")
        
        if clarity > 15:
            parts.append("Request is very clear")
        elif clarity < 5:
            parts.append("Request is ambiguous")
        
        if time > 10:
            parts.append("Good time for this decision")
        elif time < 5:
            parts.append("Late/early hour may affect decisions")
        
        if past > 15:
            parts.append("Similar past decisions succeeded")
        
        if mood in ['frustrated']:
            parts.append("You're in action mode (frustrated)")
        
        return " | ".join(parts)
    
    def log_decision(self, decision_id: str, decision: Dict, outcome: str, notes: str = ""):
        """Log a decision and its outcome for learning"""
        scored = self.score_decision(decision)
        
        log_entry = {
            'id': decision_id,
            'timestamp': datetime.now().isoformat(),
            'decision_type': decision.get('type'),
            'request': decision.get('request', ''),
            'confidence_predicted': scored['confidence'],
            'recommendation': scored['recommendation'],
            'actually_executed': outcome in ['success', 'partial_success'],
            'outcome': outcome,
            'notes': notes
        }
        
        # Append to history
        self.history.append(log_entry)
        
        # Save
        self.decision_log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.decision_log_file, 'w') as f:
            json.dump(self.history, f, indent=2)
        
        return log_entry


def main():
    """Test the scorer"""
    scorer = DecisionScorer()
    
    # Example 1: Clear, high-confidence data work
    test1 = {
        'type': 'data_work',
        'request': 'Update NBA rankings with fresh slate data',
        'clarity': 'high',
        'time_of_day': '14:30',
        'recent_mood': 'focused',
        'similar_past_decisions': []
    }
    
    result1 = scorer.score_decision(test1)
    print("Test 1 (Data Work - Clear):")
    print(f"  Confidence: {result1['confidence']}")
    print(f"  Recommendation: {result1['recommendation']}")
    print(f"  Reasoning: {result1['reasoning']}\n")
    
    # Example 2: Ambiguous request
    test2 = {
        'type': 'unknown',
        'request': 'I need 50 players',
        'clarity': 'low',
        'time_of_day': '23:22',
        'recent_mood': 'frustrated',
        'similar_past_decisions': []
    }
    
    result2 = scorer.score_decision(test2)
    print("Test 2 (Ambiguous - Late Night):")
    print(f"  Confidence: {result2['confidence']}")
    print(f"  Recommendation: {result2['recommendation']}")
    print(f"  Reasoning: {result2['reasoning']}\n")
    
    # Example 3: Revenue work, high clarity
    test3 = {
        'type': 'revenue',
        'request': 'Build landing page for golf coaching',
        'clarity': 'high',
        'time_of_day': '10:00',
        'recent_mood': 'focused'
    }
    
    result3 = scorer.score_decision(test3)
    print("Test 3 (Revenue - Clear & Morning):")
    print(f"  Confidence: {result3['confidence']}")
    print(f"  Recommendation: {result3['recommendation']}")
    print(f"  Reasoning: {result3['reasoning']}\n")


if __name__ == '__main__':
    main()
