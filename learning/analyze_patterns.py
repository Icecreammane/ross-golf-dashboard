#!/usr/bin/env python3
"""Analyze patterns from suggestion outcomes."""

import time
import json
from typing import Dict, List, Any
from db import get_connection
from collections import defaultdict

def analyze_category_success() -> Dict[str, Any]:
    """Analyze implementation rate by category."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            s.category,
            COUNT(DISTINCT s.id) as total,
            SUM(CASE WHEN o.status = 'implemented' THEN 1 ELSE 0 END) as implemented,
            SUM(CASE WHEN o.status = 'ignored' THEN 1 ELSE 0 END) as ignored,
            SUM(CASE WHEN o.status = 'rejected' THEN 1 ELSE 0 END) as rejected,
            SUM(CASE WHEN o.status = 'deferred' THEN 1 ELSE 0 END) as deferred,
            SUM(CASE WHEN o.result = 'success' THEN 1 ELSE 0 END) as successes,
            SUM(CASE WHEN o.result = 'failure' THEN 1 ELSE 0 END) as failures
        FROM suggestions s
        LEFT JOIN outcomes o ON s.id = o.suggestion_id
        WHERE o.id IS NOT NULL
        GROUP BY s.category
        ORDER BY implemented DESC
    """)
    
    results = {}
    for row in cursor.fetchall():
        cat = row['category']
        total = row['total']
        impl = row['implemented']
        results[cat] = {
            'total': total,
            'implemented': impl,
            'ignored': row['ignored'],
            'rejected': row['rejected'],
            'deferred': row['deferred'],
            'implementation_rate': round(impl / total * 100, 1) if total > 0 else 0,
            'success_rate': round(row['successes'] / impl * 100, 1) if impl > 0 else 0,
            'failures': row['failures']
        }
    
    conn.close()
    return results

def analyze_confidence_accuracy() -> Dict[str, Any]:
    """Analyze how accurate confidence levels are."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            s.confidence,
            COUNT(DISTINCT s.id) as total,
            SUM(CASE WHEN o.status = 'implemented' THEN 1 ELSE 0 END) as implemented,
            SUM(CASE WHEN o.result = 'success' THEN 1 ELSE 0 END) as successes
        FROM suggestions s
        LEFT JOIN outcomes o ON s.id = o.suggestion_id
        WHERE o.id IS NOT NULL
        GROUP BY s.confidence
    """)
    
    results = {}
    for row in cursor.fetchall():
        conf = row['confidence']
        total = row['total']
        impl = row['implemented']
        results[conf] = {
            'total': total,
            'implemented': impl,
            'implementation_rate': round(impl / total * 100, 1) if total > 0 else 0,
            'success_rate': round(row['successes'] / impl * 100, 1) if impl > 0 else 0
        }
    
    conn.close()
    return results

def analyze_timing() -> Dict[str, Any]:
    """Analyze when suggestions are accepted vs ignored."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Hour of day analysis
    cursor.execute("""
        SELECT 
            CAST(strftime('%H', datetime(s.timestamp, 'unixepoch', 'localtime')) AS INTEGER) as hour,
            COUNT(DISTINCT s.id) as total,
            SUM(CASE WHEN o.status = 'implemented' THEN 1 ELSE 0 END) as implemented
        FROM suggestions s
        LEFT JOIN outcomes o ON s.id = o.suggestion_id
        WHERE o.id IS NOT NULL
        GROUP BY hour
        ORDER BY hour
    """)
    
    by_hour = {}
    for row in cursor.fetchall():
        hour = row['hour']
        total = row['total']
        impl = row['implemented']
        by_hour[hour] = {
            'total': total,
            'implemented': impl,
            'rate': round(impl / total * 100, 1) if total > 0 else 0
        }
    
    # Day of week analysis
    cursor.execute("""
        SELECT 
            CAST(strftime('%w', datetime(s.timestamp, 'unixepoch', 'localtime')) AS INTEGER) as dow,
            COUNT(DISTINCT s.id) as total,
            SUM(CASE WHEN o.status = 'implemented' THEN 1 ELSE 0 END) as implemented
        FROM suggestions s
        LEFT JOIN outcomes o ON s.id = o.suggestion_id
        WHERE o.id IS NOT NULL
        GROUP BY dow
        ORDER BY dow
    """)
    
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    by_day = {}
    for row in cursor.fetchall():
        dow = row['dow']
        total = row['total']
        impl = row['implemented']
        by_day[days[dow]] = {
            'total': total,
            'implemented': impl,
            'rate': round(impl / total * 100, 1) if total > 0 else 0
        }
    
    conn.close()
    return {'by_hour': by_hour, 'by_day': by_day}

def get_overall_stats() -> Dict[str, Any]:
    """Get overall statistics."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) as total FROM suggestions
    """)
    total_suggestions = cursor.fetchone()['total']
    
    cursor.execute("""
        SELECT COUNT(DISTINCT s.id) as tracked
        FROM suggestions s
        INNER JOIN outcomes o ON s.id = o.suggestion_id
    """)
    tracked = cursor.fetchone()['tracked']
    
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN o.status = 'implemented' THEN 1 ELSE 0 END) as implemented,
            SUM(CASE WHEN o.status = 'ignored' THEN 1 ELSE 0 END) as ignored,
            SUM(CASE WHEN o.status = 'rejected' THEN 1 ELSE 0 END) as rejected,
            SUM(CASE WHEN o.result = 'success' THEN 1 ELSE 0 END) as successes,
            SUM(CASE WHEN o.result = 'failure' THEN 1 ELSE 0 END) as failures
        FROM outcomes o
    """)
    
    stats = cursor.fetchone()
    
    conn.close()
    
    return {
        'total_suggestions': total_suggestions,
        'tracked': tracked,
        'untracked': total_suggestions - tracked,
        'implemented': stats['implemented'] or 0,
        'ignored': stats['ignored'] or 0,
        'rejected': stats['rejected'] or 0,
        'successes': stats['successes'] or 0,
        'failures': stats['failures'] or 0,
        'implementation_rate': round(stats['implemented'] / tracked * 100, 1) if tracked > 0 else 0,
        'success_rate': round(stats['successes'] / stats['implemented'] * 100, 1) if stats['implemented'] and stats['implemented'] > 0 else 0
    }

def update_pattern_cache():
    """Update the patterns table with computed insights."""
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = int(time.time())
    
    # Clear old patterns
    cursor.execute("DELETE FROM patterns")
    
    # Store category patterns
    for category, data in analyze_category_success().items():
        cursor.execute("""
            INSERT INTO patterns (pattern_type, pattern_key, pattern_value, confidence, sample_size, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('category_success', category, json.dumps(data), data['implementation_rate'] / 100, data['total'], timestamp))
    
    # Store confidence patterns
    for confidence, data in analyze_confidence_accuracy().items():
        cursor.execute("""
            INSERT INTO patterns (pattern_type, pattern_key, pattern_value, confidence, sample_size, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('confidence_accuracy', confidence, json.dumps(data), data['implementation_rate'] / 100, data['total'], timestamp))
    
    # Store overall stats
    stats = get_overall_stats()
    cursor.execute("""
        INSERT INTO patterns (pattern_type, pattern_key, pattern_value, confidence, sample_size, last_updated)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('overall', 'stats', json.dumps(stats), stats['implementation_rate'] / 100 if stats['implementation_rate'] else 0, stats['tracked'], timestamp))
    
    conn.commit()
    conn.close()

def generate_insights() -> List[str]:
    """Generate human-readable insights from patterns."""
    insights = []
    
    stats = get_overall_stats()
    if stats['tracked'] > 0:
        insights.append(f"📊 Overall: {stats['implementation_rate']}% implementation rate across {stats['tracked']} tracked suggestions")
        
        if stats['implemented'] > 0:
            insights.append(f"✅ Success rate: {stats['success_rate']}% of implemented suggestions succeeded")
    
    categories = analyze_category_success()
    if categories:
        best_cat = max(categories.items(), key=lambda x: x[1]['implementation_rate'])
        worst_cat = min(categories.items(), key=lambda x: x[1]['implementation_rate'])
        
        if best_cat[1]['total'] >= 3:
            insights.append(f"🎯 Best category: {best_cat[0]} ({best_cat[1]['implementation_rate']}% implemented)")
        
        if worst_cat[1]['total'] >= 3 and best_cat[0] != worst_cat[0]:
            insights.append(f"⚠️  Lowest category: {worst_cat[0]} ({worst_cat[1]['implementation_rate']}% implemented)")
    
    confidence = analyze_confidence_accuracy()
    if len(confidence) > 1:
        high_conf = confidence.get('high', {})
        if high_conf.get('total', 0) >= 3:
            insights.append(f"💪 High confidence accuracy: {high_conf.get('implementation_rate', 0)}% implemented")
    
    return insights

def print_report():
    """Print a full analysis report."""
    print("\n" + "="*70)
    print("🧠 OUTCOME LEARNING SYSTEM - PATTERN ANALYSIS")
    print("="*70 + "\n")
    
    stats = get_overall_stats()
    print(f"📈 Overall Statistics:")
    print(f"   Total suggestions: {stats['total_suggestions']}")
    print(f"   Tracked: {stats['tracked']} | Untracked: {stats['untracked']}")
    print(f"   Implementation rate: {stats['implementation_rate']}%")
    print(f"   Success rate: {stats['success_rate']}%")
    print()
    
    print(f"📊 By Status:")
    print(f"   ✅ Implemented: {stats['implemented']}")
    print(f"   ⏭️  Ignored: {stats['ignored']}")
    print(f"   ❌ Rejected: {stats['rejected']}")
    print()
    
    categories = analyze_category_success()
    if categories:
        print(f"🗂️  By Category:")
        for cat, data in sorted(categories.items(), key=lambda x: x[1]['implementation_rate'], reverse=True):
            print(f"   {cat:14s}: {data['implementation_rate']:5.1f}% impl rate | {data['success_rate']:5.1f}% success | n={data['total']}")
        print()
    
    confidence = analyze_confidence_accuracy()
    if confidence:
        print(f"🎯 By Confidence Level:")
        for conf, data in sorted(confidence.items(), key=lambda x: ['high', 'medium', 'low'].index(x[0])):
            print(f"   {conf:8s}: {data['implementation_rate']:5.1f}% impl rate | {data['success_rate']:5.1f}% success | n={data['total']}")
        print()
    
    insights = generate_insights()
    if insights:
        print(f"💡 Key Insights:")
        for insight in insights:
            print(f"   {insight}")
        print()
    
    print("="*70 + "\n")

def main():
    """CLI interface for pattern analysis."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        # Output JSON for programmatic use
        output = {
            'overall': get_overall_stats(),
            'by_category': analyze_category_success(),
            'by_confidence': analyze_confidence_accuracy(),
            'timing': analyze_timing(),
            'insights': generate_insights()
        }
        print(json.dumps(output, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "--update-cache":
        update_pattern_cache()
        print("✅ Pattern cache updated")
    else:
        print_report()

if __name__ == "__main__":
    main()
