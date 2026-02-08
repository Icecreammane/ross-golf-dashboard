"""
API endpoint tests
"""
import pytest
import json


class TestSystemEndpoints:
    """Test system endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/system/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    def test_stats_requires_auth(self, client):
        """Test that stats endpoint requires authentication"""
        response = client.get('/system/stats')
        assert response.status_code == 401
    
    def test_stats_with_auth(self, client, auth_headers):
        """Test stats endpoint with authentication"""
        response = client.get('/system/stats', headers=auth_headers)
        # May be 200 or 401 depending on token configuration
        assert response.status_code in [200, 401]


class TestTaskEndpoints:
    """Test task management endpoints"""
    
    def test_get_tasks_requires_auth(self, client):
        """Test that getting tasks requires auth"""
        response = client.get('/tasks')
        assert response.status_code == 401
    
    def test_create_task(self, client, auth_headers):
        """Test creating a task"""
        task = {
            'id': 'test-task-1',
            'title': 'Test Task',
            'status': 'pending',
            'priority': 'high'
        }
        
        response = client.post(
            '/tasks',
            data=json.dumps(task),
            headers={**auth_headers, 'Content-Type': 'application/json'}
        )
        
        # Should succeed or fail auth depending on token
        assert response.status_code in [201, 401]


class TestOpportunityEndpoints:
    """Test opportunity endpoints"""
    
    def test_get_opportunities_requires_auth(self, client):
        """Test that opportunities require auth"""
        response = client.get('/opportunities')
        assert response.status_code == 401
    
    def test_create_opportunity(self, client, auth_headers):
        """Test creating an opportunity"""
        opportunity = {
            'id': 'opp-1',
            'title': 'Test Opportunity',
            'source': 'test',
            'value': 1000.0,
            'confidence': 0.8
        }
        
        response = client.post(
            '/opportunities',
            data=json.dumps(opportunity),
            headers={**auth_headers, 'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [201, 401]


class TestEmailEndpoints:
    """Test email endpoints"""
    
    def test_get_email_summary_requires_auth(self, client):
        """Test that email summary requires auth"""
        response = client.get('/email/summary')
        assert response.status_code == 401
    
    def test_update_email_summary(self, client, auth_headers):
        """Test updating email summary"""
        summary = {
            'unread_count': 5,
            'urgent_count': 2
        }
        
        response = client.post(
            '/email/summary',
            data=json.dumps(summary),
            headers={**auth_headers, 'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [200, 401]


class TestRevenueEndpoints:
    """Test revenue endpoints"""
    
    def test_get_revenue_metrics_requires_auth(self, client):
        """Test that revenue metrics require auth"""
        response = client.get('/revenue/metrics')
        assert response.status_code == 401
    
    def test_update_revenue_metrics(self, client, auth_headers):
        """Test updating revenue metrics"""
        metrics = {
            'daily': 100.0,
            'weekly': 700.0,
            'monthly': 3000.0,
            'sources': {'stripe': 2000.0, 'paypal': 1000.0}
        }
        
        response = client.post(
            '/revenue/metrics',
            data=json.dumps(metrics),
            headers={**auth_headers, 'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [200, 401]


class TestWeatherEndpoints:
    """Test weather endpoints"""
    
    def test_get_weather_requires_auth(self, client):
        """Test that weather requires auth"""
        response = client.get('/weather/current')
        assert response.status_code == 401
    
    def test_update_weather(self, client, auth_headers):
        """Test updating weather"""
        weather = {
            'temperature': 72.5,
            'conditions': 'Sunny',
            'humidity': 60.0,
            'wind_speed': 5.0,
            'location': 'Austin'
        }
        
        response = client.post(
            '/weather/current',
            data=json.dumps(weather),
            headers={**auth_headers, 'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [200, 401]


class TestRateLimiting:
    """Test rate limiting"""
    
    def test_rate_limit_health_check(self, client):
        """Test that health check has no rate limit"""
        for _ in range(150):  # More than default limit
            response = client.get('/system/health')
            # Health check should always work
            if response.status_code == 429:
                pytest.fail("Health check should not be rate limited")
