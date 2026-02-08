"""
Data storage layer for Central API
Manages persistent data in JSON files
"""
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path
import threading

logger = logging.getLogger(__name__)


class DataStore:
    """Thread-safe JSON file storage"""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.locks = {}
        self.master_lock = threading.Lock()
        logger.info(f"Data store initialized: {self.data_dir}")
    
    def _get_lock(self, key: str) -> threading.Lock:
        """Get or create a lock for a specific key"""
        with self.master_lock:
            if key not in self.locks:
                self.locks[key] = threading.Lock()
            return self.locks[key]
    
    def _get_file_path(self, key: str) -> Path:
        """Get file path for a key"""
        return self.data_dir / f"{key}.json"
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data for a key"""
        file_path = self._get_file_path(key)
        lock = self._get_lock(key)
        
        with lock:
            if not file_path.exists():
                return None
            
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error reading {key}: {e}")
                return None
    
    def set(self, key: str, data: Dict[str, Any]) -> bool:
        """Set data for a key"""
        file_path = self._get_file_path(key)
        lock = self._get_lock(key)
        
        # Add metadata
        if not isinstance(data, dict):
            data = {'value': data}
        
        data['_updated_at'] = datetime.now().isoformat()
        
        with lock:
            try:
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                return True
            except Exception as e:
                logger.error(f"Error writing {key}: {e}")
                return False
    
    def update(self, key: str, updates: Dict[str, Any]) -> bool:
        """Update specific fields in existing data"""
        lock = self._get_lock(key)
        
        with lock:
            current = self.get(key) or {}
            current.update(updates)
            return self.set(key, current)
    
    def delete(self, key: str) -> bool:
        """Delete data for a key"""
        file_path = self._get_file_path(key)
        lock = self._get_lock(key)
        
        with lock:
            if file_path.exists():
                try:
                    file_path.unlink()
                    return True
                except Exception as e:
                    logger.error(f"Error deleting {key}: {e}")
                    return False
            return False
    
    def list_keys(self) -> List[str]:
        """List all keys in storage"""
        return [f.stem for f in self.data_dir.glob('*.json')]
    
    def append_to_list(self, key: str, item: Any) -> bool:
        """Append an item to a list stored under key"""
        lock = self._get_lock(key)
        
        with lock:
            current = self.get(key) or {'items': []}
            if 'items' not in current:
                current['items'] = []
            
            # Add timestamp if item is a dict
            if isinstance(item, dict):
                item['_timestamp'] = datetime.now().isoformat()
            
            current['items'].append(item)
            return self.set(key, current)
    
    def get_list(self, key: str, limit: Optional[int] = None) -> List[Any]:
        """Get list of items, optionally limited"""
        data = self.get(key)
        if not data or 'items' not in data:
            return []
        
        items = data['items']
        if limit:
            return items[-limit:]  # Return most recent N items
        return items
