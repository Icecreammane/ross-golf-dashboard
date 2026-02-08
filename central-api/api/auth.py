"""
Authentication middleware for Central API
"""
import os
import logging
from functools import wraps
from flask import request, jsonify

logger = logging.getLogger(__name__)


class AuthManager:
    """Manages API token authentication"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        if not api_token or api_token == "YOUR_SECURE_TOKEN_HERE":
            logger.warning("⚠️  API token not configured! Using insecure default.")
    
    def verify_token(self, token: str) -> bool:
        """Verify if provided token matches configured token"""
        return token == self.api_token
    
    def require_auth(self, f):
        """Decorator to require authentication for endpoints"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check Authorization header
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                logger.warning(f"Unauthorized request from {request.remote_addr}: No Authorization header")
                return jsonify({
                    'error': 'Unauthorized',
                    'message': 'Authorization header required'
                }), 401
            
            # Support "Bearer TOKEN" or just "TOKEN"
            token = auth_header.replace('Bearer ', '').strip()
            
            if not self.verify_token(token):
                logger.warning(f"Unauthorized request from {request.remote_addr}: Invalid token")
                return jsonify({
                    'error': 'Unauthorized',
                    'message': 'Invalid API token'
                }), 401
            
            return f(*args, **kwargs)
        
        return decorated_function


def generate_token() -> str:
    """Generate a secure API token"""
    import secrets
    return secrets.token_urlsafe(32)
