"""
Twitter Engagement Monitor
Track mentions, competitors, and opportunities
"""

import os
from twitter_bot import TwitterBot
from typing import List, Dict
import json
from datetime import datetime

class EngagementMonitor:
    def __init__(self):
        self.bot = TwitterBot()
        self.opportunities_file = 'engagement_opportunities.json'
        
    def monitor_fittrack_mentions(self) -> List[Dict]:
        """Monitor mentions of FitTrack"""
        print("🔍 Monitoring FitTrack mentions...")
        
        queries = [
            "FitTrack",
            "@YourTwitterHandle",  # Replace with actual handle
            "fittrack app"
        ]
        
        all_mentions = []
        for query in queries:
            mentions = self.bot.search_mentions(query, max_results=20)
            all_mentions.extend(mentions)
        
        # Remove duplicates
        seen_ids = set()
        unique_mentions = []
        for mention in all_mentions:
            if mention['id'] not in seen_ids:
                unique_mentions.append(mention)
                seen_ids.add(mention['id'])
        
        print(f"📧 Found {len(unique_mentions)} mentions")
        return unique_mentions
    
    def monitor_competitor_discussions(self) -> List[Dict]:
        """Monitor competitor product discussions"""
        print("🔍 Monitoring competitor discussions...")
        
        competitors = [
            "MyFitnessPal",
            "Cronometer",
            "LoseIt",
            "Noom"
        ]
        
        # Search for complaints/questions about competitors
        queries = [
            f"{comp} expensive" for comp in competitors
        ] + [
            f"{comp} not working" for comp in competitors
        ] + [
            f"alternative to {comp}" for comp in competitors
        ]
        
        all_discussions = []
        for query in queries[:5]:  # Limit to avoid rate limits
            discussions = self.bot.search_mentions(query, max_results=5)
            all_discussions.extend(discussions)
        
        print(f"💬 Found {len(all_discussions)} competitor discussions")
        return all_discussions
    
    def monitor_macro_tracking_questions(self) -> List[Dict]:
        """Monitor questions about macro tracking"""
        print("🔍 Monitoring macro tracking questions...")
        
        queries = [
            "how to track macros",
            "macro tracking app recommendation",
            "best macro tracker",
            "calorie counting app",
            "track my protein"
        ]
        
        all_questions = []
        for query in queries[:3]:  # Limit queries
            questions = self.bot.search_mentions(query, max_results=5)
            all_questions.extend(questions)
        
        print(f"❓ Found {len(all_questions)} questions")
        return all_questions
    
    def identify_opportunities(self) -> List[Dict]:
        """Identify engagement opportunities"""
        opportunities = []
        
        # Get mentions
        mentions = self.monitor_fittrack_mentions()
        for mention in mentions:
            # Skip if already engaged
            if self.bot.has_engaged(mention['id']):
                continue
            
            opportunities.append({
                'type': 'mention',
                'tweet_id': mention['id'],
                'text': mention['text'],
                'priority': 'high',
                'suggested_action': 'reply_thanks'
            })
        
        # Get competitor discussions
        competitor_discussions = self.monitor_competitor_discussions()
        for discussion in competitor_discussions[:3]:  # Top 3 only
            if self.bot.has_engaged(discussion['id']):
                continue
            
            opportunities.append({
                'type': 'competitor_discussion',
                'tweet_id': discussion['id'],
                'text': discussion['text'],
                'priority': 'medium',
                'suggested_action': 'reply_helpful'
            })
        
        # Get questions
        questions = self.monitor_macro_tracking_questions()
        for question in questions[:3]:  # Top 3 only
            if self.bot.has_engaged(question['id']):
                continue
            
            opportunities.append({
                'type': 'question',
                'tweet_id': question['id'],
                'text': question['text'],
                'priority': 'medium',
                'suggested_action': 'reply_answer'
            })
        
        return opportunities
    
    def save_opportunities(self, opportunities: List[Dict]):
        """Save opportunities to file"""
        with open(self.opportunities_file, 'w') as f:
            json.dump({
                'updated_at': datetime.now().isoformat(),
                'opportunities': opportunities
            }, f, indent=2)
    
    def get_reply_template(self, opportunity: Dict) -> str:
        """Get suggested reply for opportunity"""
        action = opportunity['suggested_action']
        
        templates = {
            'reply_thanks': "Thanks for the mention! 🙏 Hope FitTrack is helping you hit your goals!",
            
            'reply_helpful': "Have you tried FitTrack? Clean interface, no BS, just simple macro tracking that actually works. Might be what you're looking for! 💪",
            
            'reply_answer': "I built FitTrack for exactly this! Simple macro tracking without the bloat. Check it out if you're looking for something straightforward. 🎯"
        }
        
        return templates.get(action, "Thanks for the mention!")
    
    def run_monitoring(self):
        """Run full monitoring cycle"""
        print("="*50)
        print("🤖 Twitter Engagement Monitor")
        print("="*50)
        
        # Authenticate
        if not self.bot.authenticate():
            return
        
        # Identify opportunities
        opportunities = self.identify_opportunities()
        
        if not opportunities:
            print("\n✅ No new engagement opportunities")
            return
        
        # Save opportunities
        self.save_opportunities(opportunities)
        
        print(f"\n📊 Found {len(opportunities)} engagement opportunities:")
        print("-"*50)
        
        for opp in opportunities[:5]:  # Show top 5
            print(f"\n{opp['priority'].upper()}: {opp['type']}")
            print(f"Tweet: {opp['text'][:80]}...")
            print(f"Suggested reply: {self.get_reply_template(opp)}")
        
        print("\n" + "="*50)
        print(f"💾 Full list saved to {self.opportunities_file}")


if __name__ == "__main__":
    monitor = EngagementMonitor()
    monitor.run_monitoring()
