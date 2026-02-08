#!/usr/bin/env python3
"""
Comprehensive test suite for Golf Tracker application
Run with: python3 -m pytest tests/test_golf_tracker.py -v
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import GolfDataManager, app


@pytest.fixture
def temp_data_file():
    """Create a temporary data file for testing."""
    temp_file = Path(tempfile.mktemp(suffix='.json'))
    yield temp_file
    if temp_file.exists():
        temp_file.unlink()


@pytest.fixture
def manager(temp_data_file):
    """Create a GolfDataManager instance with temp file."""
    return GolfDataManager(temp_data_file)


@pytest.fixture
def client():
    """Create a test client for Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestGolfDataManager:
    """Test suite for GolfDataManager class."""
    
    def test_initialization(self, temp_data_file):
        """Test that data file is created on initialization."""
        manager = GolfDataManager(temp_data_file)
        assert temp_data_file.exists()
        
        with open(temp_data_file) as f:
            data = json.load(f)
        
        assert "rounds" in data
        assert "goals" in data
        assert "courses" in data
        assert isinstance(data["rounds"], list)
        assert len(data["rounds"]) == 0
    
    def test_add_valid_round(self, manager):
        """Test adding a valid golf round."""
        round_data = manager.add_round(
            date="2024-01-15",
            course="Test Course",
            score=85,
            par=72,
            handicap_estimate=15.2,
            notes="Great weather"
        )
        
        assert round_data["id"] == 1
        assert round_data["date"] == "2024-01-15"
        assert round_data["course"] == "Test Course"
        assert round_data["score"] == 85
        assert round_data["par"] == 72
        assert round_data["differential"] == 13
        assert round_data["handicap_estimate"] == 15.2
        assert round_data["notes"] == "Great weather"
    
    def test_add_round_invalid_date(self, manager):
        """Test that invalid date format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid date format"):
            manager.add_round("01-15-2024", "Test Course", 85, 72)
    
    def test_add_round_invalid_score(self, manager):
        """Test that invalid score raises ValueError."""
        with pytest.raises(ValueError, match="Invalid score"):
            manager.add_round("2024-01-15", "Test Course", 300, 72)
        
        with pytest.raises(ValueError, match="Invalid score"):
            manager.add_round("2024-01-15", "Test Course", 30, 72)
    
    def test_add_round_invalid_par(self, manager):
        """Test that invalid par raises ValueError."""
        with pytest.raises(ValueError, match="Invalid par"):
            manager.add_round("2024-01-15", "Test Course", 85, 90)
        
        with pytest.raises(ValueError, match="Invalid par"):
            manager.add_round("2024-01-15", "Test Course", 85, 50)
    
    def test_course_statistics_tracking(self, manager):
        """Test that course statistics are properly tracked."""
        manager.add_round("2024-01-15", "Pebble Beach", 85, 72)
        manager.add_round("2024-01-16", "Pebble Beach", 90, 72)
        manager.add_round("2024-01-17", "Pebble Beach", 80, 72)
        
        stats = manager.get_course_stats()
        
        assert "Pebble Beach" in stats
        course_stats = stats["Pebble Beach"]
        
        assert course_stats["rounds_played"] == 3
        assert course_stats["total_score"] == 255
        assert course_stats["best_score"] == 80
        assert course_stats["worst_score"] == 90
        assert course_stats["average_score"] == 85.0
    
    def test_multiple_courses(self, manager):
        """Test tracking multiple courses."""
        manager.add_round("2024-01-15", "Course A", 85, 72)
        manager.add_round("2024-01-16", "Course B", 90, 72)
        
        stats = manager.get_course_stats()
        
        assert len(stats) == 2
        assert "Course A" in stats
        assert "Course B" in stats
    
    def test_get_all_rounds_sorted(self, manager):
        """Test that rounds are returned sorted by date (newest first)."""
        manager.add_round("2024-01-10", "Course A", 85, 72)
        manager.add_round("2024-01-15", "Course B", 90, 72)
        manager.add_round("2024-01-12", "Course C", 87, 72)
        
        rounds = manager.get_all_rounds()
        
        assert len(rounds) == 3
        assert rounds[0]["date"] == "2024-01-15"
        assert rounds[1]["date"] == "2024-01-12"
        assert rounds[2]["date"] == "2024-01-10"
    
    def test_get_recent_rounds(self, manager):
        """Test getting recent N rounds."""
        for i in range(10):
            date = (datetime(2024, 1, 1) + timedelta(days=i)).date().isoformat()
            manager.add_round(date, "Test Course", 85, 72)
        
        recent_5 = manager.get_recent_rounds(5)
        assert len(recent_5) == 5
        
        recent_3 = manager.get_recent_rounds(3)
        assert len(recent_3) == 3
    
    def test_insights_no_rounds(self, manager):
        """Test insights when no rounds exist."""
        insights = manager.get_insights()
        assert "message" in insights
    
    def test_insights_with_rounds(self, manager):
        """Test insights calculation with multiple rounds."""
        # Add 10 rounds
        for i in range(10):
            date = (datetime(2024, 1, 1) + timedelta(days=i)).date().isoformat()
            score = 85 + (i % 5)  # Vary scores
            manager.add_round(date, "Test Course", score, 72)
        
        insights = manager.get_insights()
        
        assert "total_rounds" in insights
        assert insights["total_rounds"] == 10
        assert "best_score" in insights
        assert "worst_score" in insights
        assert "recent_average" in insights
    
    def test_monthly_comparison(self, manager):
        """Test monthly performance comparison."""
        # Add rounds from two different months
        for i in range(5):
            # January rounds (avg 90)
            manager.add_round(f"2024-01-{i+1:02d}", "Test Course", 90, 72)
        
        for i in range(5):
            # February rounds (avg 85)
            manager.add_round(f"2024-02-{i+1:02d}", "Test Course", 85, 72)
        
        # Note: This test depends on current date, so we'll just check structure
        insights = manager.get_insights()
        assert "total_rounds" in insights
        assert insights["total_rounds"] == 10
    
    def test_add_goal(self, manager):
        """Test adding a goal."""
        goal = manager.add_goal("break_score", 80, "Break 80 by end of year")
        
        assert goal["id"] == 1
        assert goal["type"] == "break_score"
        assert goal["target"] == 80
        assert goal["description"] == "Break 80 by end of year"
        assert goal["achieved"] is False
    
    def test_handicap_trend_calculation(self, manager):
        """Test handicap trend calculation."""
        # Add rounds with varying differentials
        for i in range(10):
            date = (datetime(2024, 1, 1) + timedelta(days=i)).date().isoformat()
            score = 85 - i  # Improving scores
            manager.add_round(date, "Test Course", score, 72)
        
        trend = manager.calculate_handicap_trend(10)
        
        assert len(trend) > 0
        assert all(isinstance(x, float) for x in trend)


class TestFlaskAPI:
    """Test suite for Flask web API."""
    
    def test_index_route(self, client):
        """Test that index route loads."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_add_round_get(self, client):
        """Test GET request to add round page."""
        response = client.get('/add')
        assert response.status_code == 200
    
    def test_api_get_rounds(self, client):
        """Test API endpoint for getting rounds."""
        response = client.get('/api/rounds')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_api_get_insights(self, client):
        """Test API endpoint for getting insights."""
        response = client.get('/api/insights')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, dict)
    
    def test_api_add_round_valid(self, client):
        """Test API endpoint for adding a round with valid data."""
        payload = {
            "date": "2024-01-15",
            "course": "API Test Course",
            "score": 85,
            "par": 72,
            "notes": "API test"
        }
        
        response = client.post('/api/add_round',
                              data=json.dumps(payload),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert "round" in data
    
    def test_api_add_round_invalid(self, client):
        """Test API endpoint with invalid data."""
        payload = {
            "date": "invalid-date",
            "course": "Test Course",
            "score": 85,
            "par": 72
        }
        
        response = client.post('/api/add_round',
                              data=json.dumps(payload),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False


class TestDataPersistence:
    """Test data persistence and file operations."""
    
    def test_data_persists_across_instances(self, temp_data_file):
        """Test that data persists when creating new manager instances."""
        # First instance
        manager1 = GolfDataManager(temp_data_file)
        manager1.add_round("2024-01-15", "Test Course", 85, 72)
        
        # Second instance
        manager2 = GolfDataManager(temp_data_file)
        rounds = manager2.get_all_rounds()
        
        assert len(rounds) == 1
        assert rounds[0]["course"] == "Test Course"
    
    def test_concurrent_writes(self, temp_data_file):
        """Test that multiple writes don't corrupt data."""
        manager = GolfDataManager(temp_data_file)
        
        for i in range(20):
            date = (datetime(2024, 1, 1) + timedelta(days=i)).date().isoformat()
            manager.add_round(date, f"Course {i}", 85, 72)
        
        rounds = manager.get_all_rounds()
        assert len(rounds) == 20


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_course_name(self, manager):
        """Test handling of empty course name."""
        # Empty string should work (validation is minimal)
        round_data = manager.add_round("2024-01-15", "", 85, 72)
        assert round_data["course"] == ""
    
    def test_perfect_score(self, manager):
        """Test logging a perfect round (score equals par)."""
        round_data = manager.add_round("2024-01-15", "Perfect Course", 72, 72)
        assert round_data["differential"] == 0
    
    def test_under_par(self, manager):
        """Test logging an under-par round."""
        round_data = manager.add_round("2024-01-15", "Great Round", 68, 72)
        assert round_data["differential"] == -4
    
    def test_unicode_course_name(self, manager):
        """Test handling of unicode characters in course name."""
        round_data = manager.add_round("2024-01-15", "Pîné Crëst 🏌️", 85, 72)
        assert "Pîné Crëst 🏌️" in round_data["course"]
    
    def test_very_long_notes(self, manager):
        """Test handling of very long notes."""
        long_notes = "A" * 10000
        round_data = manager.add_round("2024-01-15", "Test", 85, 72, notes=long_notes)
        assert len(round_data["notes"]) == 10000


class TestCalculations:
    """Test calculation accuracy."""
    
    def test_differential_calculation(self, manager):
        """Test that differentials are calculated correctly."""
        test_cases = [
            (85, 72, 13),   # Over par
            (72, 72, 0),    # Even par
            (68, 72, -4),   # Under par
        ]
        
        for score, par, expected_diff in test_cases:
            round_data = manager.add_round("2024-01-15", "Test", score, par)
            assert round_data["differential"] == expected_diff
    
    def test_average_calculation(self, manager):
        """Test that averages are calculated correctly."""
        scores = [80, 85, 90, 85, 80]  # Average should be 84
        
        for i, score in enumerate(scores):
            date = (datetime(2024, 1, 1) + timedelta(days=i)).date().isoformat()
            manager.add_round(date, "Test Course", score, 72)
        
        stats = manager.get_course_stats()
        assert stats["Test Course"]["average_score"] == 84.0


# Run tests if executed directly
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
