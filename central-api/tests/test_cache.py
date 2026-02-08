"""
Cache layer tests
"""
import pytest
import time
from api.cache import InMemoryCache


def test_inmemory_cache_set_get(test_cache):
    """Test basic cache operations"""
    test_cache.set('test_key', {'value': 'test'})
    result = test_cache.get('test_key')
    
    assert result is not None
    assert result['value'] == 'test'


def test_inmemory_cache_expiration(test_cache):
    """Test that cache entries expire"""
    test_cache.set('test_key', {'value': 'test'}, ttl=1)
    
    # Should exist immediately
    assert test_cache.get('test_key') is not None
    
    # Wait for expiration
    time.sleep(2)
    
    # Should be gone
    assert test_cache.get('test_key') is None


def test_inmemory_cache_delete(test_cache):
    """Test deleting cache entries"""
    test_cache.set('test_key', {'value': 'test'})
    assert test_cache.get('test_key') is not None
    
    test_cache.delete('test_key')
    assert test_cache.get('test_key') is None


def test_inmemory_cache_clear(test_cache):
    """Test clearing all cache"""
    test_cache.set('key1', {'value': 1})
    test_cache.set('key2', {'value': 2})
    
    test_cache.clear()
    
    assert test_cache.get('key1') is None
    assert test_cache.get('key2') is None
