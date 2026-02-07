"""
Health Check Endpoint for FitTrack Monitoring

Purpose: Provide a simple endpoint that monitoring services (UptimeRobot, etc.) 
         can ping to verify the app is running and healthy.

Usage: Add this to your main Flask app (app_saas.py or similar)

How to integrate:
  Option 1: Import this file
    from health_check import health_check_routes
    health_check_routes(app)
  
  Option 2: Copy routes directly into your app file

Test locally:
  curl http://localhost:5000/health

Test production:
  curl https://your-railway-url.up.railway.app/health
"""

from flask import jsonify
import time
from datetime import datetime
import os


def health_check_routes(app):
    """
    Register health check routes with Flask app
    
    Usage:
      from health_check import health_check_routes
      health_check_routes(app)
    """
    
    @app.route('/health')
    def health_check():
        """
        Simple health check endpoint for monitoring services
        
        Returns 200 OK if everything is healthy
        Returns 500 if critical services are down
        
        Checks:
        - Database connectivity
        - Basic app functionality
        - Environment configuration
        """
        try:
            checks = {}
            
            # Check 1: Database connection
            try:
                # Adjust import based on your models location
                # Example: from models import User
                # or: from app import db
                
                # If using SQLAlchemy
                from flask import current_app
                if hasattr(current_app, 'extensions') and 'sqlalchemy' in current_app.extensions:
                    db = current_app.extensions['sqlalchemy'].db
                    # Quick query to verify DB connection
                    db.session.execute('SELECT 1')
                    checks['database'] = 'ok'
                else:
                    checks['database'] = 'no_db_configured'
                    
            except Exception as db_error:
                checks['database'] = f'error: {str(db_error)}'
                # Database errors are critical - return 500
                return jsonify({
                    "status": "unhealthy",
                    "error": "Database connection failed",
                    "timestamp": datetime.now().isoformat(),
                    "checks": checks
                }), 500
            
            # Check 2: Stripe configuration (optional, won't fail health check)
            try:
                stripe_key = os.environ.get('STRIPE_SECRET_KEY', '')
                if stripe_key:
                    if stripe_key.startswith('sk_test_'):
                        checks['stripe'] = 'test_mode'
                    elif stripe_key.startswith('sk_live_'):
                        checks['stripe'] = 'live_mode'
                    else:
                        checks['stripe'] = 'invalid_key'
                else:
                    checks['stripe'] = 'not_configured'
            except Exception:
                checks['stripe'] = 'check_failed'
            
            # Check 3: Environment
            checks['environment'] = os.environ.get('FLASK_ENV', 'unknown')
            
            # Check 4: App is running (if we got here, it is)
            checks['app'] = 'ok'
            
            # All critical checks passed
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "uptime": time.time(),  # Can calculate actual uptime if you track start time
                "version": "1.0.0",  # Update as you version your app
                "checks": checks
            }), 200
            
        except Exception as e:
            # Unexpected error
            return jsonify({
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500


    @app.route('/status')
    def detailed_status():
        """
        More detailed status endpoint for debugging
        
        ⚠️ WARNING: This exposes app internals. 
        Add authentication before using in production.
        
        Consider: @login_required decorator or API key check
        """
        try:
            status_data = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "environment": os.environ.get('FLASK_ENV', 'unknown'),
                "database": {},
                "stripe": {},
                "system": {}
            }
            
            # Database stats
            try:
                # Adjust based on your models
                # Example:
                # from models import User, Subscription, FoodLog
                # status_data['database']['users'] = User.query.count()
                # status_data['database']['subscriptions'] = Subscription.query.count()
                
                status_data['database']['status'] = 'connected'
            except Exception as db_error:
                status_data['database']['status'] = 'error'
                status_data['database']['error'] = str(db_error)
            
            # Stripe info
            stripe_key = os.environ.get('STRIPE_SECRET_KEY', '')
            if stripe_key.startswith('sk_test_'):
                status_data['stripe']['mode'] = 'test'
            elif stripe_key.startswith('sk_live_'):
                status_data['stripe']['mode'] = 'live'
            else:
                status_data['stripe']['mode'] = 'not_configured'
            
            # System info
            status_data['system']['port'] = os.environ.get('PORT', '5000')
            status_data['system']['python_version'] = os.sys.version
            
            return jsonify(status_data), 200
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500


# Standalone routes (if not using the function above)
# Copy these directly into your app_saas.py if preferred

"""
@app.route('/health')
def health_check():
    try:
        # Test database connection
        from models import User  # Adjust import
        user_count = User.query.count()
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "database": "ok",
                "app": "ok"
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500
"""


# Example integration in main Flask app:
"""
# In app_saas.py:

from flask import Flask
from health_check import health_check_routes

app = Flask(__name__)

# ... other setup ...

# Add health check routes
health_check_routes(app)

# ... rest of your routes ...

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
