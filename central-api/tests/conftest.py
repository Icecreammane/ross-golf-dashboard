"""
Pytest configuration and fixtures
"""
import pytest
import os
import tempfile
import shutil
from api.app import app as flask_app
from api.storage import DataStore
from api.cache import Cache


@pytest.fixture
def app():
    """Create Flask app for testing"""
    # Use test configuration
    flask_app.config['TESTING'] = True
    flask_app.config['DEBUG'] = False
    
    yield flask_app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def auth_headers():
    """Get authorization headers for testing"""
    token = os.getenv('API_TOKEN', 'test_token_12345')
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def temp_data_dir():
    """Create temporary directory for test data"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_storage(temp_data_dir):
    """Create test data store"""
    return DataStore(data_dir=temp_data_dir)


@pytest.fixture
def test_cache():
    """Create test cache (in-memory only)"""
    return Cache(redis_enabled=False)
