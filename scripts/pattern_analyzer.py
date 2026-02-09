#!/usr/bin/env python3
"""
Pattern Analyzer - Learns from past interactions

Reviews decision history to identify:
- Which decision types have highest success rate
- What times of day you prefer certain tasks
- Your mood patterns
- What should I do more/less of
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import os
from typing import Dict, List, Any

class PatternAnalyzer:
    def __init__(self):
        self.workspace = Path(os.path.expanduser('~/clawd'))
        self.decision_log = self.workspace / 'memory' / 'decision-log.json'
        self.patterns_file = self.workspace / 'memory' / 'decision-patterns.json'
        self.daily_log_dir = self.workspace / 'memory'
    
    def analyze_all(self) -> Dict[str, Any]:
        """Run full pattern analysis"""
        
        decisions = self._load_decisions()
        
        patterns = {
            'analyzed_at': datetime.now().isoformat(),
            'total_decisions': len(decisions),
            'category_success': self._analyze_categories(decisions),
            'time_patterns': self._analyze_time_patterns(decisions),
            'mood_patterns': self._analyze_mood_patterns(decisions),
            'learnings': self._extract_learnings(decisions),
            'recommendations': self._generate_recommendations(decisions)
        }
        
        # Save patterns
        self.patterns_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.patterns_file, 'w') as f:
            json.dump(patterns, f, indent=2)
        
        return patterns
    
    def _load_decisions(self) -> List[Dict]:
        """Load all decision history"""
        if not self.decision_log.exists():
            return []
        
        with open(self.decision_log) as f:
            return json.load(f)
    
    def _analyze_categories(self, decisions: List[Dict]) -> Dict[str, Dict]:
        """Analyze success rate by decision category"""
        by_category = defaultdict(lambda: {'success': 0, 'total': 0, 'outcomes': defaultdict(int)})
        
        for d in decisions:
            category = d.get('decision_type', 'unknown')
            by_category[category]['total'] += 1
            
            outcome = d.get('outcome', 'unknown')
            by_category[category]['outcomes'][outcome] += 1
            
            if outcome in ['success', 'partial_success']:
                by_category[category]['success'] += 1
        
        # Convert to percentage success rate
        results = {}
        for category, stats in by_category.items():
            total = stats['total']
            success = stats['success']
            rate = (success / total * 100) if total > 0 else 0
            
            results[category] = {
                'success_rate': round(rate, 1),
                'total_decisions': total,
                'successful': success,
                'outcomes': dict(stats['outcomes'])
            }
        
        return results
    
    def _analyze_time_patterns(self, decisions: List[Dict]) -> Dict[str, Dict]:
        """Analyze patterns by time of day"""
        time_buckets = {
            'morning_6_9': [],
            'morning_9_12': [],
            'afternoon_12_5': [],
            'evening_5_10': [],
            'late_night_10_1': [],
            'night_1_6': []
        }
        
        for d in decisions:
            timestamp = d.get('timestamp', '')
            if not timestamp:
                continue
            
            try:
                hour = int(datetime.fromisoformat(timestamp).hour)
                outcome = d.get('outcome', 'unknown')
                
                if 6 <= hour < 9:
                    time_buckets['morning_6_9'].append(outcome)
                elif 9 <= hour < 12:
                    time_buckets['morning_9_12'].append(outcome)
                elif 12 <= hour < 17:
                    time_buckets['afternoon_12_5'].append(outcome)
                elif 17 <= hour < 22:
                    time_buckets['evening_5_10'].append(outcome)
                elif 22 <= hour or hour < 1:
                    time_buckets['late_night_10_1'].append(outcome)
                else:
                    time_buckets['night_1_6'].append(outcome)
            except:
                pass
        
        results = {}
        for time_bucket, outcomes in time_buckets.items():
            if not outcomes:
                results[time_bucket] = {'data': 'insufficient'}
                continue
            
            success_count = sum(1 for o in outcomes if o in ['success', 'partial_success'])
            total = len(outcomes)
            success_rate = success_count / total * 100 if total > 0 else 0
            
            results[time_bucket] = {
                'success_rate': round(success_rate, 1),
                'total_decisions': total,
                'best_for': self._determine_best_task_type(outcomes)
            }
        
        return results
    
    def _analyze_mood_patterns(self, decisions: List[Dict]) -> Dict[str, Dict]:
        """Analyze patterns by mood"""
        by_mood = defaultdict(lambda: {'success': 0, 'total': 0})
        
        for d in decisions:
            mood = d.get('recent_mood', 'unknown')
            by_mood[mood]['total'] += 1
            
            if d.get('outcome') in ['success', 'partial_success']:
                by_mood[mood]['success'] += 1
        
        results = {}
        for mood, stats in by_mood.items():
            total = stats['total']
            success = stats['success']
            rate = (success / total * 100) if total > 0 else 0
            
            results[mood] = {
                'success_rate': round(rate, 1),
                'total_decisions': total,
                'recommendation': self._mood_recommendation(mood, rate)
            }
        
        return results
    
    def _extract_learnings(self, decisions: List[Dict]) -> List[str]:
        """Extract key learnings"""
        learnings = []
        
        if not decisions:
            return ["No decisions logged yet"]
        
        # Learning 1: Most successful category
        by_category = defaultdict(lambda: {'success': 0, 'total': 0})
        for d in decisions:
            category = d.get('decision_type', 'unknown')
            by_category[category]['total'] += 1
            if d.get('outcome') in ['success', 'partial_success']:
                by_category[category]['success'] += 1
        
        if by_category:
            best_category = max(by_category.items(), key=lambda x: x[1]['success'] / max(x[1]['total'], 1))
            learnings.append(f"Highest success rate: {best_category[0]} ({best_category[1]['success']}/{best_category[1]['total']} successful)")
        
        # Learning 2: Failure patterns
        failures = [d for d in decisions if d.get('outcome') not in ['success', 'partial_success']]
        if failures:
            failure_categories = defaultdict(int)
            for f in failures:
                failure_categories[f.get('decision_type', 'unknown')] += 1
            
            worst = max(failure_categories.items(), key=lambda x: x[1])
            learnings.append(f"Most failures in: {worst[0]} ({worst[1]} failures)")
        
        # Learning 3: Time patterns
        morning_decisions = [d for d in decisions if '06' <= d.get('timestamp', '').split('T')[1][:2] < '12']
        if morning_decisions:
            morning_success = sum(1 for d in morning_decisions if d.get('outcome') in ['success', 'partial_success'])
            learnings.append(f"Morning decisions: {morning_success}/{len(morning_decisions)} successful")
        
        # Learning 4: Ambiguity patterns
        low_clarity = [d for d in decisions if d.get('clarity') == 'low']
        if low_clarity:
            low_success = sum(1 for d in low_clarity if d.get('outcome') in ['success', 'partial_success'])
            learnings.append(f"Low clarity requests: Only {low_success}/{len(low_clarity)} succeeded - Ask more clarification questions")
        
        return learnings
    
    def _generate_recommendations(self, decisions: List[Dict]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Rec 1: Ask more clarification on ambiguous requests
        low_clarity = [d for d in decisions if d.get('clarity') == 'low']
        if len(low_clarity) > len(decisions) * 0.3:  # >30% low clarity
            recommendations.append("ASK MORE CLARIFICATION: >30% of requests are ambiguous. Always ask about unclear requests.")
        
        # Rec 2: Reduce guessing
        guesses = [d for d in decisions if 'guess' in d.get('notes', '').lower()]
        if len(guesses) > len(decisions) * 0.2:
            recommendations.append("REDUCE GUESSING: >20% of failed decisions involved assumptions. Wait for data when unsure.")
        
        # Rec 3: Focus on winner categories
        if decisions:
            successes = [d for d in decisions if d.get('outcome') in ['success', 'partial_success']]
            if successes:
                successful_categories = defaultdict(int)
                for s in successes:
                    successful_categories[s.get('decision_type')] += 1
                
                top_cat = max(successful_categories.items(), key=lambda x: x[1])
                recommendations.append(f"DOUBLE DOWN: {top_cat[0]} has highest success. Build more autonomy here.")
        
        return recommendations
    
    def _determine_best_task_type(self, outcomes: List[str]) -> str:
        """Determine what task types work best for this time"""
        # Simplified - in production would look at decision types
        success_rate = sum(1 for o in outcomes if o in ['success', 'partial_success']) / len(outcomes)
        
        if success_rate > 0.8:
            return 'high_focus_tasks'
        elif success_rate > 0.6:
            return 'moderate_focus_tasks'
        else:
            return 'low_focus_tasks'
    
    def _mood_recommendation(self, mood: str, success_rate: float) -> str:
        """Recommendation for this mood"""
        if success_rate > 80:
            return "High autonomy when in this mood"
        elif success_rate > 60:
            return "Medium autonomy, check in after"
        else:
            return "Ask first when in this mood"


def main():
    """Run analysis"""
    analyzer = PatternAnalyzer()
    patterns = analyzer.analyze_all()
    
    print("=" * 60)
    print("PATTERN ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"\nTotal Decisions Analyzed: {patterns['total_decisions']}")
    
    print("\n--- Category Success Rates ---")
    for cat, stats in patterns['category_success'].items():
        print(f"{cat:15s}: {stats['success_rate']:5.1f}% ({stats['successful']}/{stats['total_decisions']})")
    
    print("\n--- Learnings ---")
    for i, learning in enumerate(patterns['learnings'], 1):
        print(f"{i}. {learning}")
    
    print("\n--- Recommendations ---")
    for i, rec in enumerate(patterns['recommendations'], 1):
        print(f"{i}. {rec}")
    
    print(f"\n✓ Patterns saved to: {analyzer.patterns_file}")


if __name__ == '__main__':
    main()
