#!/usr/bin/env python3
"""
Confidence Tracker - Track wins, patterns, and confidence metrics
Answers: "When do you feel most confident?"
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

WORKSPACE = Path('/Users/clawdbot/clawd')
MEMORY_DIR = WORKSPACE / 'memory'
LOGS_DIR = WORKSPACE / 'logs'

CONFIDENCE_DATA_FILE = MEMORY_DIR / 'confidence_data.json'

class ConfidenceTracker:
    def __init__(self):
        self.data = self.load_data()
    
    def load_data(self):
        """Load existing confidence data"""
        if CONFIDENCE_DATA_FILE.exists():
            try:
                with open(CONFIDENCE_DATA_FILE) as f:
                    return json.load(f)
            except:
                pass
        
        # Default structure
        return {
            'score': 5,
            'stack': 0,
            'last_win': None,
            'trend': 'neutral',
            'wins': [],
            'patterns': {},
            'insights': []
        }
    
    def save_data(self):
        """Save confidence data"""
        MEMORY_DIR.mkdir(exist_ok=True)
        with open(CONFIDENCE_DATA_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def log_win(self, description, category='build', metadata=None):
        """
        Log a win (completed build, deployment, shipped feature)
        
        Args:
            description: What was accomplished
            category: 'build', 'deployment', 'pr', 'feature', etc.
            metadata: Additional data
        """
        win = {
            'timestamp': datetime.now().isoformat(),
            'description': description,
            'category': category,
            'metadata': metadata or {},
            'day_of_week': datetime.now().strftime('%A'),
            'hour': datetime.now().hour
        }
        
        self.data['wins'].append(win)
        self.data['stack'] += 1
        self.data['last_win'] = description
        
        # Update score based on stack
        self.update_score()
        
        # Detect patterns
        self.detect_patterns()
        
        self.save_data()
        
        return win
    
    def reset_stack(self):
        """Reset win stack (e.g., after a long break or setback)"""
        self.data['stack'] = 0
        self.save_data()
    
    def update_score(self):
        """Calculate confidence score (1-10) based on recent activity"""
        # Base score
        score = 5
        
        # Stack bonus (+1 per consecutive win, max +4)
        stack_bonus = min(self.data['stack'], 4)
        score += stack_bonus
        
        # Recent wins bonus (last 7 days)
        recent_wins = self.get_recent_wins(days=7)
        if len(recent_wins) > 0:
            score += min(len(recent_wins) // 2, 2)  # +1 per 2 wins, max +2
        
        # Cap at 10
        score = min(score, 10)
        
        # Trend calculation
        last_week_wins = len(self.get_recent_wins(days=7))
        prev_week_wins = len(self.get_wins_in_range(days_ago=14, days=7))
        
        if last_week_wins > prev_week_wins:
            self.data['trend'] = f'↑ Up {int((last_week_wins - prev_week_wins) / max(prev_week_wins, 1) * 100)}%'
        elif last_week_wins < prev_week_wins:
            self.data['trend'] = f'↓ Down {int((prev_week_wins - last_week_wins) / max(prev_week_wins, 1) * 100)}%'
        else:
            self.data['trend'] = 'neutral'
        
        self.data['score'] = score
    
    def get_recent_wins(self, days=7):
        """Get wins from the last N days"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = []
        
        for win in self.data['wins']:
            try:
                win_time = datetime.fromisoformat(win['timestamp'])
                if win_time >= cutoff:
                    recent.append(win)
            except:
                pass
        
        return recent
    
    def get_wins_in_range(self, days_ago=14, days=7):
        """Get wins from a specific date range"""
        end = datetime.now() - timedelta(days=days_ago)
        start = end - timedelta(days=days)
        wins = []
        
        for win in self.data['wins']:
            try:
                win_time = datetime.fromisoformat(win['timestamp'])
                if start <= win_time <= end:
                    wins.append(win)
            except:
                pass
        
        return wins
    
    def detect_patterns(self):
        """Detect patterns in wins (best times, days, etc.)"""
        if len(self.data['wins']) < 5:
            return  # Need more data
        
        # Analyze by day of week
        by_day = {}
        by_hour = {}
        
        for win in self.data['wins']:
            day = win.get('day_of_week', 'Unknown')
            hour = win.get('hour', -1)
            
            by_day[day] = by_day.get(day, 0) + 1
            
            if 0 <= hour < 24:
                by_hour[hour] = by_hour.get(hour, 0) + 1
        
        # Find peak day
        if by_day:
            peak_day = max(by_day.items(), key=lambda x: x[1])
            self.data['patterns']['peak_day'] = f"{peak_day[0]} ({peak_day[1]} wins)"
        
        # Find peak hour range
        if by_hour:
            peak_hour = max(by_hour.items(), key=lambda x: x[1])
            self.data['patterns']['peak_hour'] = f"{peak_hour[0]}:00 ({peak_hour[1]} wins)"
        
        # Generate insights
        self.generate_insights()
    
    def generate_insights(self):
        """Generate human-readable insights"""
        insights = []
        
        if 'peak_day' in self.data['patterns']:
            insights.append(f"You ship most on {self.data['patterns']['peak_day'].split()[0]}")
        
        if 'peak_hour' in self.data['patterns']:
            hour = int(self.data['patterns']['peak_hour'].split(':')[0])
            if hour < 12:
                time_of_day = 'morning'
            elif hour < 18:
                time_of_day = 'afternoon'
            else:
                time_of_day = 'evening'
            insights.append(f"Most productive in the {time_of_day}")
        
        # Stack insights
        if self.data['stack'] >= 3:
            insights.append(f"On a roll! {self.data['stack']} consecutive wins")
        
        # Recent activity
        recent_wins = self.get_recent_wins(days=7)
        if len(recent_wins) >= 5:
            insights.append(f"Hot week: {len(recent_wins)} wins in 7 days")
        
        self.data['insights'] = insights
    
    def scan_builds(self):
        """Scan BUILD_*.md files for completed builds"""
        existing_descriptions = {w['description'] for w in self.data['wins']}
        
        for build_file in WORKSPACE.glob('BUILD_*.md'):
            # Use file name as win description if not already logged
            description = f"Completed {build_file.stem}"
            
            if description not in existing_descriptions:
                # Check if file was modified recently (within last 7 days)
                mtime = datetime.fromtimestamp(build_file.stat().st_mtime)
                if datetime.now() - mtime < timedelta(days=7):
                    self.log_win(description, category='build', metadata={'file': build_file.name})
    
    def scan_git_commits(self, days=7):
        """Scan git commits for shipped code"""
        try:
            result = subprocess.run(
                ['git', 'log', f'--since={days} days ago', '--oneline'],
                cwd=WORKSPACE,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                commits = result.stdout.strip().split('\n')
                # Count significant commits (not just "update" or "fix")
                significant = [c for c in commits if len(c) > 20]
                
                if len(significant) > 0:
                    self.data['patterns']['git_commits_7d'] = len(significant)
        except:
            pass
    
    def scan_deployments(self):
        """Check for deployment URLs in SESSION_SUMMARY.md"""
        session_summary = WORKSPACE / 'SESSION_SUMMARY.md'
        if session_summary.exists():
            content = session_summary.read_text()
            
            # Count live URLs
            urls = []
            for line in content.split('\n'):
                if 'https://' in line and ('LIVE' in line or 'deployed' in line.lower()):
                    urls.append(line.strip())
            
            if urls:
                self.data['patterns']['live_deployments'] = len(urls)
    
    def get_summary(self):
        """Get current confidence summary"""
        return {
            'score': self.data['score'],
            'stack': self.data['stack'],
            'last_win': self.data['last_win'],
            'trend': self.data['trend'],
            'recent_wins': len(self.get_recent_wins(days=7)),
            'insights': self.data['insights'],
            'patterns': self.data['patterns']
        }
    
    def full_scan(self):
        """Run all scanners and update confidence data"""
        print("Scanning for wins and patterns...")
        
        self.scan_builds()
        self.scan_git_commits()
        self.scan_deployments()
        self.update_score()
        
        self.save_data()
        
        return self.get_summary()

def main():
    """Run confidence tracker"""
    tracker = ConfidenceTracker()
    summary = tracker.full_scan()
    
    print("\n🎯 CONFIDENCE TRACKER")
    print("=" * 50)
    print(f"Score: {summary['score']}/10")
    print(f"Stack: {summary['stack']} consecutive wins")
    print(f"Trend: {summary['trend']}")
    print(f"Recent wins (7d): {summary['recent_wins']}")
    
    if summary['last_win']:
        print(f"Last win: {summary['last_win']}")
    
    if summary['insights']:
        print(f"\n💡 Insights:")
        for insight in summary['insights']:
            print(f"  • {insight}")
    
    if summary['patterns']:
        print(f"\n📊 Patterns:")
        for key, value in summary['patterns'].items():
            print(f"  • {key}: {value}")
    
    print("=" * 50)

if __name__ == '__main__':
    main()
