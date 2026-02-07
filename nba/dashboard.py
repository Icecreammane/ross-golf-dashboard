#!/usr/bin/env python3
"""
NBA DFS Dashboard - Quick view of rankings and key info
"""

import json
from datetime import datetime

def load_rankings():
    """Load rankings from JSON"""
    try:
        with open('/Users/clawdbot/clawd/nba/rankings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ rankings.json not found. Run ./update_rankings.sh first.")
        return None

def load_injuries():
    """Load injury data"""
    try:
        with open('/Users/clawdbot/clawd/nba/injuries.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'injuries': []}

def show_dashboard():
    """Display interactive dashboard"""
    data = load_rankings()
    if not data:
        return
    
    injuries = load_injuries()
    rankings = data['rankings']
    
    print("=" * 70)
    print("🏀 NBA DFS DASHBOARD - Thursday 2/6/26".center(70))
    print("=" * 70)
    print()
    
    # Header info
    print(f"📊 Generated: {data.get('generated_at', 'Unknown')}")
    print(f"🎮 Games: {data.get('num_games', 0)}")
    print(f"👥 Players ranked: {data.get('num_players', 0)}")
    print()
    
    # Injury alerts
    if injuries['injuries']:
        print("🚨 INJURY ALERTS")
        print("-" * 70)
        for inj in injuries['injuries']:
            print(f"   {inj['status']:12} {inj['player']:25} ({inj['team']})")
            print(f"   {'':12} {inj['injury']}")
        print()
    
    # Trade deadline impacts summary
    trade_impacts = {'HIGH': 0, 'MED': 0, 'LOW': 0}
    for p in rankings:
        impact = p.get('trade_impact', 'None')
        if impact in trade_impacts:
            trade_impacts[impact] += 1
    
    if sum(trade_impacts.values()) > 0:
        print("🔄 TRADE DEADLINE IMPACTS")
        print("-" * 70)
        if trade_impacts['HIGH'] > 0:
            print(f"   🔥 HIGH impact players: {trade_impacts['HIGH']}")
        if trade_impacts['MED'] > 0:
            print(f"   ⚠️  MED impact players: {trade_impacts['MED']}")
        if trade_impacts['LOW'] > 0:
            print(f"   📊 LOW impact players: {trade_impacts['LOW']}")
        print()
    
    # Top 20 players
    print("⭐ TOP 20 PLAYERS")
    print("-" * 70)
    print(f"{'Rank':4} {'Player':25} {'Team':18} {'Pos':3} {'H/A':3} {'Proj FP':8} {'Trade':6}")
    print("-" * 70)
    
    for player in rankings[:20]:
        home = "H" if player['is_home'] else "A"
        trade_icon = ""
        if player.get('trade_impact') == 'HIGH':
            trade_icon = "🔥"
        elif player.get('trade_impact') == 'MED':
            trade_icon = "⚠️"
        elif player.get('trade_impact') == 'LOW':
            trade_icon = "📊"
        
        print(f"{player['rank']:4} {player['name']:25} {player['team'][:18]:18} "
              f"{player['position']:3} {home:3} {player['projected_fantasy_points']:8.1f} {trade_icon:6}")
    
    print()
    
    # Position leaders
    print("🎯 POSITION LEADERS")
    print("-" * 70)
    
    by_pos = {}
    for p in rankings:
        pos = p['position'] or 'UNK'
        if pos not in by_pos:
            by_pos[pos] = []
        by_pos[pos].append(p)
    
    for pos in ['G', 'F', 'C']:
        if pos in by_pos:
            top3 = by_pos[pos][:3]
            print(f"\n{pos} - Top 3:")
            for p in top3:
                print(f"   {p['rank']:2}. {p['name']:25} {p['projected_fantasy_points']:.1f} FP")
    
    print()
    print("=" * 70)
    print("💡 TIP: Run './update_rankings.sh' to refresh data")
    print("📖 Full report: ~/clawd/nba/rankings-report.md")
    print("=" * 70)

if __name__ == "__main__":
    show_dashboard()
