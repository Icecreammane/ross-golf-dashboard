#!/usr/bin/env python3
"""
Central API Client - Example usage for daemons
"""
import os
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional


class CentralAPIClient:
    """
    Client for interacting with Central API
    Use this in your daemons to push data to the central hub
    """
    
    def __init__(self, base_url: str = 'http://localhost:3003', token: Optional[str] = None):
        """
        Initialize API client
        
        Args:
            base_url: Base URL of Central API (default: http://localhost:3003)
            token: API token (default: read from API_TOKEN env var)
        """
        self.base_url = base_url.rstrip('/')
        self.token = token or os.getenv('API_TOKEN')
        
        if not self.token:
            raise ValueError("API token not provided. Set API_TOKEN environment variable.")
        
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f'{self.base_url}{endpoint}'
        
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            raise
    
    # === HEALTH CHECK ===
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health (no auth required)"""
        response = requests.get(f'{self.base_url}/system/health')
        return response.json()
    
    # === TASKS ===
    
    def get_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks"""
        response = self._request('GET', '/tasks')
        return response.json()
    
    def add_task(self, task_id: str, title: str, status: str = 'pending', 
                 priority: str = 'medium') -> Dict[str, Any]:
        """Add a new task"""
        task = {
            'id': task_id,
            'title': title,
            'status': status,
            'priority': priority
        }
        response = self._request('POST', '/tasks', json=task)
        return response.json()
    
    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """Delete a task"""
        response = self._request('DELETE', f'/tasks/{task_id}')
        return response.json()
    
    # === OPPORTUNITIES ===
    
    def get_opportunities(self) -> List[Dict[str, Any]]:
        """Get all opportunities"""
        response = self._request('GET', '/opportunities')
        return response.json()
    
    def add_opportunity(self, opp_id: str, title: str, source: str,
                       value: float = 0.0, confidence: float = 0.5) -> Dict[str, Any]:
        """Add a new opportunity"""
        opportunity = {
            'id': opp_id,
            'title': title,
            'source': source,
            'value': value,
            'confidence': confidence
        }
        response = self._request('POST', '/opportunities', json=opportunity)
        return response.json()
    
    # === EMAIL ===
    
    def get_email_summary(self) -> Dict[str, Any]:
        """Get email summary"""
        response = self._request('GET', '/email/summary')
        return response.json()
    
    def update_email_summary(self, unread_count: int, urgent_count: int) -> Dict[str, Any]:
        """Update email summary"""
        data = {
            'unread_count': unread_count,
            'urgent_count': urgent_count
        }
        response = self._request('POST', '/email/summary', json=data)
        return response.json()
    
    # === TWITTER ===
    
    def get_twitter_opportunities(self) -> List[Dict[str, Any]]:
        """Get Twitter opportunities"""
        response = self._request('GET', '/twitter/opportunities')
        return response.json()
    
    def add_twitter_opportunity(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Add Twitter opportunity"""
        response = self._request('POST', '/twitter/opportunities', json=opportunity)
        return response.json()
    
    # === REVENUE ===
    
    def get_revenue_metrics(self) -> Dict[str, Any]:
        """Get revenue metrics"""
        response = self._request('GET', '/revenue/metrics')
        return response.json()
    
    def update_revenue_metrics(self, daily: float, weekly: float, 
                              monthly: float, sources: Dict[str, float]) -> Dict[str, Any]:
        """Update revenue metrics"""
        data = {
            'daily': daily,
            'weekly': weekly,
            'monthly': monthly,
            'sources': sources
        }
        response = self._request('POST', '/revenue/metrics', json=data)
        return response.json()
    
    # === FITNESS ===
    
    def get_fitness_summary(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Get fitness summary for a date"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        response = self._request('GET', f'/fitness/summary?date={date}')
        return response.json()
    
    def update_fitness_data(self, steps: int, calories: int, 
                           active_minutes: int, date: Optional[str] = None) -> Dict[str, Any]:
        """Update fitness data"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        data = {
            'steps': steps,
            'calories': calories,
            'active_minutes': active_minutes,
            'date': date
        }
        response = self._request('POST', '/fitness/summary', json=data)
        return response.json()
    
    # === GOLF ===
    
    def get_golf_stats(self) -> Dict[str, Any]:
        """Get golf statistics"""
        response = self._request('GET', '/golf/stats')
        return response.json()
    
    def update_golf_stats(self, rounds: int, average_score: float,
                         handicap: float, last_round: Optional[Dict] = None) -> Dict[str, Any]:
        """Update golf statistics"""
        data = {
            'rounds': rounds,
            'average_score': average_score,
            'handicap': handicap,
            'last_round': last_round
        }
        response = self._request('POST', '/golf/stats', json=data)
        return response.json()
    
    # === WEATHER ===
    
    def get_weather(self, location: str = 'default') -> Dict[str, Any]:
        """Get current weather"""
        response = self._request('GET', f'/weather/current?location={location}')
        return response.json()
    
    def update_weather(self, temperature: float, conditions: str,
                      humidity: float, wind_speed: float, 
                      location: str = 'default') -> Dict[str, Any]:
        """Update weather data"""
        data = {
            'temperature': temperature,
            'conditions': conditions,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'location': location
        }
        response = self._request('POST', '/weather/current', json=data)
        return response.json()
    
    # === CACHE MANAGEMENT ===
    
    def clear_cache(self) -> Dict[str, Any]:
        """Clear all cached data"""
        response = self._request('POST', '/system/cache/clear')
        return response.json()


# === EXAMPLE USAGE ===

def example_daemon():
    """Example of how to use the client in a daemon"""
    
    # Initialize client (reads API_TOKEN from environment)
    client = CentralAPIClient()
    
    # Check if API is healthy
    health = client.health_check()
    print(f"API Status: {health['status']}")
    
    # Add a task
    task = client.add_task(
        task_id='task-001',
        title='Review pull request #42',
        status='pending',
        priority='high'
    )
    print(f"Task created: {task}")
    
    # Update email summary
    email_summary = client.update_email_summary(
        unread_count=15,
        urgent_count=3
    )
    print(f"Email summary updated: {email_summary}")
    
    # Update revenue metrics
    revenue = client.update_revenue_metrics(
        daily=250.00,
        weekly=1750.00,
        monthly=7500.00,
        sources={
            'stripe': 5000.00,
            'paypal': 2500.00
        }
    )
    print(f"Revenue updated: {revenue}")
    
    # Update fitness data
    fitness = client.update_fitness_data(
        steps=12500,
        calories=650,
        active_minutes=45
    )
    print(f"Fitness data updated: {fitness}")
    
    # Get all tasks
    tasks = client.get_tasks()
    print(f"Total tasks: {len(tasks)}")


if __name__ == '__main__':
    # Run example
    try:
        example_daemon()
    except Exception as e:
        print(f"Error: {e}")
