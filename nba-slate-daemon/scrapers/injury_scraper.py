"""
Injury news scraper for ESPN and RotoWire
Fetches latest injury updates for NBA players
"""
import requests
from datetime import datetime
import json
from typing import List, Dict

class InjuryScraper:
    def __init__(self):
        self.espn_url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/news"
        self.injury_keywords = ['injury', 'out', 'questionable', 'doubtful', 'probable', 'gtd', 'dnp']
        
    def fetch_espn_injuries(self) -> List[Dict]:
        """Fetch injury news from ESPN API"""
        try:
            response = requests.get(self.espn_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            injuries = []
            for article in data.get('articles', [])[:50]:  # Check recent 50 articles
                headline = article.get('headline', '').lower()
                description = article.get('description', '').lower()
                
                # Check if injury-related
                if any(keyword in headline or keyword in description for keyword in self.injury_keywords):
                    injuries.append({
                        'source': 'ESPN',
                        'headline': article.get('headline', ''),
                        'description': article.get('description', ''),
                        'timestamp': article.get('published', ''),
                        'url': article.get('links', {}).get('web', {}).get('href', '')
                    })
            
            return injuries
        except Exception as e:
            print(f"Error fetching ESPN injuries: {e}")
            return []
    
    def fetch_rotowire_injuries(self) -> List[Dict]:
        """Fetch injury news from RotoWire (scraping fallback if no API)"""
        # RotoWire doesn't have a free API, using ESPN as primary source
        # Could add web scraping here if needed
        return []
    
    def get_all_injuries(self) -> Dict:
        """Fetch all injury news from available sources"""
        espn_injuries = self.fetch_espn_injuries()
        rotowire_injuries = self.fetch_rotowire_injuries()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'injuries': espn_injuries + rotowire_injuries,
            'count': len(espn_injuries) + len(rotowire_injuries)
        }
    
    def get_player_injury_status(self, player_name: str) -> List[Dict]:
        """Get injury status for specific player"""
        all_injuries = self.get_all_injuries()
        player_injuries = []
        
        for injury in all_injuries['injuries']:
            if player_name.lower() in injury['headline'].lower() or \
               player_name.lower() in injury['description'].lower():
                player_injuries.append(injury)
        
        return player_injuries
