#!/usr/bin/env python3
"""
Integration helpers for the main agent to easily use the outcome learning system.
"""

import re
import time
from typing import Optional, Dict, Any
from log_suggestion import log_suggestion
from track_outcome import track_outcome, get_latest_suggestions
from analyze_patterns import get_overall_stats, generate_insights, analyze_category_success

class OutcomeLearner:
    """Easy interface for the main agent to learn from suggestion outcomes."""
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id
        self.pending_suggestion_id: Optional[int] = None
    
    def suggest(self, 
                text: str, 
                category: str = "other",
                confidence: str = "medium",
                context: Optional[str] = None) -> int:
        """
        Log a suggestion and remember it for outcome tracking.
        
        Usage:
            learner = OutcomeLearner()
            learner.suggest("Let's build a dashboard", category="productivity", confidence="high")
        """
        suggestion_id = log_suggestion(text, category, confidence, context, self.session_id)
        self.pending_suggestion_id = suggestion_id
        return suggestion_id
    
    def detect_response(self, user_message: str) -> Optional[str]:
        """
        Auto-detect Ross's response to a suggestion.
        
        Returns one of: 'implemented', 'rejected', 'deferred', or None
        """
        msg_lower = user_message.lower().strip()
        
        # Positive responses
        positive_patterns = [
            r'\b(yes|yeah|yep|sure|ok|okay|sounds good|let\'s do it|go for it|do it|build it|make it)\b',
            r'\b(absolutely|definitely|perfect|great idea|love it)\b',
            r'\b(let\'s go|let\'s try|i\'m in|count me in)\b',
        ]
        
        # Deferred responses (check first - has priority over negative)
        deferred_patterns = [
            r'\b(maybe|eventually|someday)\b',
            r'\b(later|maybe later)\b',
            r'\b(let\'s wait|hold off|come back to|revisit)\b',
            r'\b(not yet|not ready|not priority)\b',
            r'\b(not now.*(maybe|eventually|later))\b',  # "not now, maybe later"
        ]
        
        # Negative responses
        negative_patterns = [
            r'\b(no|nah|nope|not really|don\'t think so)\b',
            r'\b(skip|pass|ignore|forget it|never mind)\b',
            r'\b(not interested|not worth it|waste of time)\b',
        ]
        
        for pattern in positive_patterns:
            if re.search(pattern, msg_lower):
                return 'implemented'
        
        for pattern in deferred_patterns:
            if re.search(pattern, msg_lower):
                return 'deferred'
        
        for pattern in negative_patterns:
            if re.search(pattern, msg_lower):
                return 'rejected'
        
        return None
    
    def track_pending(self, user_message: str) -> bool:
        """
        Try to track outcome for the pending suggestion based on user message.
        Returns True if tracked, False otherwise.
        """
        if not self.pending_suggestion_id:
            return False
        
        status = self.detect_response(user_message)
        if status:
            track_outcome(self.pending_suggestion_id, status, notes=f"Auto-detected from: {user_message[:100]}")
            self.pending_suggestion_id = None
            return True
        
        return False
    
    def mark(self, 
             suggestion_id: int,
             status: str,
             result: Optional[str] = None,
             notes: Optional[str] = None):
        """
        Manually mark a suggestion outcome.
        
        Usage:
            learner.mark(123, "implemented", result="success", notes="Ross loved it")
        """
        track_outcome(suggestion_id, status, result, notes)
    
    def get_insights(self) -> Dict[str, Any]:
        """Get current learning insights."""
        return {
            'stats': get_overall_stats(),
            'insights': generate_insights(),
            'by_category': analyze_category_success()
        }
    
    def should_suggest_category(self, category: str) -> Dict[str, Any]:
        """
        Check if suggestions in this category are typically well-received.
        Returns guidance on whether to suggest in this category.
        """
        categories = analyze_category_success()
        
        if category not in categories:
            return {
                'recommend': True,
                'confidence': 0.5,
                'reason': f"No data yet for '{category}' category",
                'sample_size': 0
            }
        
        data = categories[category]
        impl_rate = data['implementation_rate']
        success_rate = data['success_rate']
        sample_size = data['total']
        
        # Need at least 3 samples for meaningful data
        if sample_size < 3:
            return {
                'recommend': True,
                'confidence': 0.5,
                'reason': f"Limited data ({sample_size} samples) for '{category}'",
                'sample_size': sample_size,
                'data': data
            }
        
        # High implementation rate (>60%) = recommend
        if impl_rate >= 60:
            return {
                'recommend': True,
                'confidence': min(0.9, 0.5 + (sample_size / 20)),
                'reason': f"Ross implements {impl_rate}% of '{category}' suggestions (success rate: {success_rate}%)",
                'sample_size': sample_size,
                'data': data
            }
        
        # Medium implementation rate (30-60%) = cautiously recommend
        elif impl_rate >= 30:
            return {
                'recommend': True,
                'confidence': 0.6,
                'reason': f"Ross implements {impl_rate}% of '{category}' suggestions - moderate reception",
                'sample_size': sample_size,
                'data': data
            }
        
        # Low implementation rate (<30%) = avoid
        else:
            return {
                'recommend': False,
                'confidence': 0.3,
                'reason': f"Ross only implements {impl_rate}% of '{category}' suggestions - may not be valuable",
                'sample_size': sample_size,
                'data': data
            }
    
    def weekly_summary(self, days: int = 7) -> str:
        """Generate a weekly summary of suggestions and outcomes."""
        from db import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cutoff = int(time.time()) - (days * 86400)
        
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM suggestions
            WHERE timestamp >= ?
        """, (cutoff,))
        total = cursor.fetchone()['total']
        
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT s.id) as tracked,
                SUM(CASE WHEN o.status = 'implemented' THEN 1 ELSE 0 END) as implemented,
                SUM(CASE WHEN o.status = 'ignored' THEN 1 ELSE 0 END) as ignored,
                SUM(CASE WHEN o.status = 'rejected' THEN 1 ELSE 0 END) as rejected
            FROM suggestions s
            INNER JOIN outcomes o ON s.id = o.suggestion_id
            WHERE s.timestamp >= ?
        """, (cutoff,))
        
        row = cursor.fetchone()
        tracked = row['tracked'] or 0
        implemented = row['implemented'] or 0
        ignored = row['ignored'] or 0
        rejected = row['rejected'] or 0
        
        conn.close()
        
        summary = f"📊 Last {days} days: {total} suggestions, {tracked} tracked\n"
        if tracked > 0:
            summary += f"   ✅ {implemented} implemented | ⏭️  {ignored} ignored | ❌ {rejected} rejected\n"
            impl_rate = round(implemented / tracked * 100, 1)
            summary += f"   Implementation rate: {impl_rate}%"
        else:
            summary += "   (No outcomes tracked yet)"
        
        return summary


# Convenience functions for direct use
def suggest(text: str, category: str = "other", confidence: str = "medium", context: Optional[str] = None) -> int:
    """Quick function to log a suggestion. Returns suggestion ID."""
    learner = OutcomeLearner()
    return learner.suggest(text, category, confidence, context)

def check_category(category: str) -> Dict[str, Any]:
    """Quick function to check if a category is well-received."""
    learner = OutcomeLearner()
    return learner.should_suggest_category(category)

def get_summary(days: int = 7) -> str:
    """Quick function to get a weekly summary."""
    learner = OutcomeLearner()
    return learner.weekly_summary(days)


if __name__ == "__main__":
    # Demo usage
    print("🧠 Outcome Learning System - Agent Integration\n")
    
    learner = OutcomeLearner()
    
    print("Example: Check if 'productivity' suggestions are well-received:")
    result = learner.should_suggest_category('productivity')
    print(f"  Recommend: {result['recommend']} (confidence: {result['confidence']:.0%})")
    print(f"  Reason: {result['reason']}\n")
    
    print("Weekly summary:")
    print(learner.weekly_summary())
    print()
    
    insights = learner.get_insights()
    print("Current insights:")
    for insight in insights['insights']:
        print(f"  {insight}")
