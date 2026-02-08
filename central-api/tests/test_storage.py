"""
Storage layer tests
"""
import pytest
from api.storage import DataStore


def test_storage_set_get(test_storage):
    """Test basic set and get operations"""
    test_storage.set('test_key', {'value': 'test_value'})
    result = test_storage.get('test_key')
    
    assert result is not None
    assert result['value'] == 'test_value'
    assert '_updated_at' in result


def test_storage_update(test_storage):
    """Test updating existing data"""
    test_storage.set('test_key', {'field1': 'value1'})
    test_storage.update('test_key', {'field2': 'value2'})
    
    result = test_storage.get('test_key')
    assert result['field1'] == 'value1'
    assert result['field2'] == 'value2'


def test_storage_delete(test_storage):
    """Test deleting data"""
    test_storage.set('test_key', {'value': 'test'})
    assert test_storage.get('test_key') is not None
    
    test_storage.delete('test_key')
    assert test_storage.get('test_key') is None


def test_storage_list_keys(test_storage):
    """Test listing all keys"""
    test_storage.set('key1', {'value': 1})
    test_storage.set('key2', {'value': 2})
    
    keys = test_storage.list_keys()
    assert 'key1' in keys
    assert 'key2' in keys


def test_storage_append_to_list(test_storage):
    """Test appending to list"""
    test_storage.append_to_list('items', {'id': 1})
    test_storage.append_to_list('items', {'id': 2})
    
    items = test_storage.get_list('items')
    assert len(items) == 2
    assert items[0]['id'] == 1
    assert items[1]['id'] == 2


def test_storage_get_list_with_limit(test_storage):
    """Test getting limited list"""
    for i in range(10):
        test_storage.append_to_list('items', {'id': i})
    
    recent = test_storage.get_list('items', limit=5)
    assert len(recent) == 5
    assert recent[-1]['id'] == 9  # Most recent
