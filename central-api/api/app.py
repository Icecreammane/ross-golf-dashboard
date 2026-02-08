"""
Central API Server - Main Application
Unified data hub for all daemons and dashboards
"""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields, Namespace
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import yaml
from datetime import datetime

from .auth import AuthManager, generate_token
from .cache import Cache
from .storage import DataStore


# Initialize Flask app
app = Flask(__name__)

# Load configuration
config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Override with environment variables
API_TOKEN = os.getenv('API_TOKEN', config['auth']['api_token'])
REDIS_ENABLED = os.getenv('REDIS_ENABLED', str(config['redis']['enabled'])).lower() == 'true'
REDIS_HOST = os.getenv('REDIS_HOST', config['redis']['host'])
REDIS_PORT = int(os.getenv('REDIS_PORT', config['redis']['port']))

# Setup logging
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'central-api.log')

handler = RotatingFileHandler(
    log_file,
    maxBytes=config['logging']['max_bytes'],
    backupCount=config['logging']['backup_count']
)
handler.setFormatter(logging.Formatter(config['logging']['format']))

app.logger.addHandler(handler)
app.logger.setLevel(getattr(logging, config['logging']['level']))

# Also log to console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(config['logging']['format']))
app.logger.addHandler(console_handler)

# Initialize components
auth_manager = AuthManager(API_TOKEN)
cache = Cache(
    redis_enabled=REDIS_ENABLED,
    redis_host=REDIS_HOST,
    redis_port=REDIS_PORT,
    default_ttl=config['redis']['default_ttl']
)
storage = DataStore(data_dir=os.path.join(os.path.dirname(__file__), '..', 'data'))

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[config['rate_limiting']['default_limit']],
    enabled=config['rate_limiting']['enabled']
)

# API documentation
api = Api(
    app,
    version='1.0.0',
    title='Central API',
    description='Unified data hub for all daemons and dashboards',
    doc='/docs',
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'API token. Format: Bearer YOUR_TOKEN'
        }
    },
    security='Bearer'
)

# Namespaces
ns_system = api.namespace('system', description='System operations')
ns_tasks = api.namespace('tasks', description='Task management')
ns_opportunities = api.namespace('opportunities', description='Business opportunities')
ns_email = api.namespace('email', description='Email summaries')
ns_twitter = api.namespace('twitter', description='Twitter opportunities')
ns_revenue = api.namespace('revenue', description='Revenue metrics')
ns_fitness = api.namespace('fitness', description='Fitness data')
ns_golf = api.namespace('golf', description='Golf statistics')
ns_weather = api.namespace('weather', description='Weather data')

# Models for Swagger documentation
task_model = api.model('Task', {
    'id': fields.String(required=True, description='Task ID'),
    'title': fields.String(required=True, description='Task title'),
    'status': fields.String(description='Task status', enum=['pending', 'in_progress', 'completed']),
    'priority': fields.String(description='Priority', enum=['low', 'medium', 'high']),
    'created_at': fields.String(description='Creation timestamp'),
})

opportunity_model = api.model('Opportunity', {
    'id': fields.String(required=True, description='Opportunity ID'),
    'title': fields.String(required=True, description='Opportunity title'),
    'source': fields.String(description='Source (email, twitter, etc)'),
    'value': fields.Float(description='Estimated value'),
    'confidence': fields.Float(description='Confidence score 0-1'),
})

email_summary_model = api.model('EmailSummary', {
    'unread_count': fields.Integer(description='Number of unread emails'),
    'urgent_count': fields.Integer(description='Number of urgent emails'),
    'last_check': fields.String(description='Last check timestamp'),
})

revenue_model = api.model('Revenue', {
    'daily': fields.Float(description='Daily revenue'),
    'weekly': fields.Float(description='Weekly revenue'),
    'monthly': fields.Float(description='Monthly revenue'),
    'sources': fields.Raw(description='Revenue by source'),
})

fitness_model = api.model('Fitness', {
    'steps': fields.Integer(description='Step count'),
    'calories': fields.Integer(description='Calories burned'),
    'active_minutes': fields.Integer(description='Active minutes'),
    'date': fields.String(description='Date'),
})

golf_model = api.model('Golf', {
    'rounds': fields.Integer(description='Number of rounds'),
    'average_score': fields.Float(description='Average score'),
    'handicap': fields.Float(description='Handicap'),
    'last_round': fields.Raw(description='Last round data'),
})

weather_model = api.model('Weather', {
    'temperature': fields.Float(description='Temperature (F)'),
    'conditions': fields.String(description='Weather conditions'),
    'humidity': fields.Float(description='Humidity percentage'),
    'wind_speed': fields.Float(description='Wind speed (mph)'),
    'location': fields.String(description='Location'),
})


# === SYSTEM ENDPOINTS ===

@ns_system.route('/health')
class Health(Resource):
    def get(self):
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'cache': 'redis' if cache.is_redis() else 'in-memory',
            'version': '1.0.0'
        }


@ns_system.route('/stats')
class Stats(Resource):
    @api.doc(security='Bearer')
    @limiter.limit("10 per minute")
    def get(self):
        """Get system statistics"""
        auth_manager.require_auth(lambda: None)()  # Verify auth
        
        return {
            'storage_keys': len(storage.list_keys()),
            'cache_backend': 'redis' if cache.is_redis() else 'in-memory',
            'uptime': 'N/A',  # TODO: Track uptime
        }


@ns_system.route('/cache/clear')
class CacheClear(Resource):
    @api.doc(security='Bearer')
    def post(self):
        """Clear all cached data"""
        auth_manager.require_auth(lambda: None)()
        
        if cache.clear():
            app.logger.info("Cache cleared")
            return {'message': 'Cache cleared successfully'}
        return {'error': 'Failed to clear cache'}, 500


# === TASK ENDPOINTS ===

@ns_tasks.route('')
class TaskList(Resource):
    @api.doc(security='Bearer')
    @api.marshal_list_with(task_model)
    def get(self):
        """Get all tasks"""
        auth_manager.require_auth(lambda: None)()
        
        # Try cache first
        cached = cache.get('tasks:all')
        if cached:
            return cached
        
        # Get from storage
        tasks = storage.get_list('tasks')
        cache.set('tasks:all', tasks, ttl=60)
        return tasks
    
    @api.doc(security='Bearer')
    @api.expect(task_model)
    def post(self):
        """Create a new task"""
        auth_manager.require_auth(lambda: None)()
        
        task = api.payload
        task['created_at'] = datetime.now().isoformat()
        
        if storage.append_to_list('tasks', task):
            cache.delete('tasks:all')  # Invalidate cache
            app.logger.info(f"Task created: {task.get('id')}")
            return task, 201
        
        return {'error': 'Failed to create task'}, 500


@ns_tasks.route('/<string:task_id>')
class Task(Resource):
    @api.doc(security='Bearer')
    def get(self, task_id):
        """Get a specific task"""
        auth_manager.require_auth(lambda: None)()
        
        tasks = storage.get_list('tasks')
        task = next((t for t in tasks if t.get('id') == task_id), None)
        
        if task:
            return task
        return {'error': 'Task not found'}, 404
    
    @api.doc(security='Bearer')
    def delete(self, task_id):
        """Delete a task"""
        auth_manager.require_auth(lambda: None)()
        
        tasks = storage.get_list('tasks')
        filtered = [t for t in tasks if t.get('id') != task_id]
        
        if len(filtered) < len(tasks):
            storage.set('tasks', {'items': filtered})
            cache.delete('tasks:all')
            app.logger.info(f"Task deleted: {task_id}")
            return {'message': 'Task deleted'}
        
        return {'error': 'Task not found'}, 404


# === OPPORTUNITY ENDPOINTS ===

@ns_opportunities.route('')
class OpportunityList(Resource):
    @api.doc(security='Bearer')
    @api.marshal_list_with(opportunity_model)
    def get(self):
        """Get all opportunities"""
        auth_manager.require_auth(lambda: None)()
        
        cached = cache.get('opportunities:all')
        if cached:
            return cached
        
        opportunities = storage.get_list('opportunities')
        cache.set('opportunities:all', opportunities, ttl=300)
        return opportunities
    
    @api.doc(security='Bearer')
    @api.expect(opportunity_model)
    def post(self):
        """Add a new opportunity"""
        auth_manager.require_auth(lambda: None)()
        
        opportunity = api.payload
        if storage.append_to_list('opportunities', opportunity):
            cache.delete('opportunities:all')
            app.logger.info(f"Opportunity added: {opportunity.get('id')}")
            return opportunity, 201
        
        return {'error': 'Failed to create opportunity'}, 500


# === EMAIL ENDPOINTS ===

@ns_email.route('/summary')
class EmailSummary(Resource):
    @api.doc(security='Bearer')
    @api.marshal_with(email_summary_model)
    def get(self):
        """Get email summary"""
        auth_manager.require_auth(lambda: None)()
        
        cached = cache.get('email:summary')
        if cached:
            return cached
        
        summary = storage.get('email_summary') or {
            'unread_count': 0,
            'urgent_count': 0,
            'last_check': None
        }
        
        cache.set('email:summary', summary, ttl=300)
        return summary
    
    @api.doc(security='Bearer')
    def post(self):
        """Update email summary"""
        auth_manager.require_auth(lambda: None)()
        
        data = request.json
        data['last_check'] = datetime.now().isoformat()
        
        if storage.set('email_summary', data):
            cache.delete('email:summary')
            return data
        
        return {'error': 'Failed to update email summary'}, 500


# === TWITTER ENDPOINTS ===

@ns_twitter.route('/opportunities')
class TwitterOpportunities(Resource):
    @api.doc(security='Bearer')
    def get(self):
        """Get Twitter opportunities"""
        auth_manager.require_auth(lambda: None)()
        
        cached = cache.get('twitter:opportunities')
        if cached:
            return cached
        
        opportunities = storage.get_list('twitter_opportunities')
        cache.set('twitter:opportunities', opportunities, ttl=300)
        return opportunities
    
    @api.doc(security='Bearer')
    def post(self):
        """Add Twitter opportunity"""
        auth_manager.require_auth(lambda: None)()
        
        opportunity = request.json
        if storage.append_to_list('twitter_opportunities', opportunity):
            cache.delete('twitter:opportunities')
            return opportunity, 201
        
        return {'error': 'Failed to add Twitter opportunity'}, 500


# === REVENUE ENDPOINTS ===

@ns_revenue.route('/metrics')
class RevenueMetrics(Resource):
    @api.doc(security='Bearer')
    @api.marshal_with(revenue_model)
    def get(self):
        """Get revenue metrics"""
        auth_manager.require_auth(lambda: None)()
        
        cached = cache.get('revenue:metrics')
        if cached:
            return cached
        
        metrics = storage.get('revenue_metrics') or {
            'daily': 0,
            'weekly': 0,
            'monthly': 0,
            'sources': {}
        }
        
        cache.set('revenue:metrics', metrics, ttl=600)
        return metrics
    
    @api.doc(security='Bearer')
    def post(self):
        """Update revenue metrics"""
        auth_manager.require_auth(lambda: None)()
        
        data = request.json
        if storage.set('revenue_metrics', data):
            cache.delete('revenue:metrics')
            app.logger.info("Revenue metrics updated")
            return data
        
        return {'error': 'Failed to update revenue metrics'}, 500


# === FITNESS ENDPOINTS ===

@ns_fitness.route('/summary')
class FitnessSummary(Resource):
    @api.doc(security='Bearer')
    @api.marshal_with(fitness_model)
    def get(self):
        """Get fitness summary"""
        auth_manager.require_auth(lambda: None)()
        
        date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        cache_key = f'fitness:summary:{date}'
        
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        summary = storage.get(f'fitness_{date}') or {
            'steps': 0,
            'calories': 0,
            'active_minutes': 0,
            'date': date
        }
        
        cache.set(cache_key, summary, ttl=600)
        return summary
    
    @api.doc(security='Bearer')
    def post(self):
        """Update fitness data"""
        auth_manager.require_auth(lambda: None)()
        
        data = request.json
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        if storage.set(f'fitness_{date}', data):
            cache.delete(f'fitness:summary:{date}')
            return data
        
        return {'error': 'Failed to update fitness data'}, 500


# === GOLF ENDPOINTS ===

@ns_golf.route('/stats')
class GolfStats(Resource):
    @api.doc(security='Bearer')
    @api.marshal_with(golf_model)
    def get(self):
        """Get golf statistics"""
        auth_manager.require_auth(lambda: None)()
        
        cached = cache.get('golf:stats')
        if cached:
            return cached
        
        stats = storage.get('golf_stats') or {
            'rounds': 0,
            'average_score': 0,
            'handicap': 0,
            'last_round': None
        }
        
        cache.set('golf:stats', stats, ttl=3600)
        return stats
    
    @api.doc(security='Bearer')
    def post(self):
        """Update golf statistics"""
        auth_manager.require_auth(lambda: None)()
        
        data = request.json
        if storage.set('golf_stats', data):
            cache.delete('golf:stats')
            return data
        
        return {'error': 'Failed to update golf stats'}, 500


# === WEATHER ENDPOINTS ===

@ns_weather.route('/current')
class CurrentWeather(Resource):
    @api.doc(security='Bearer')
    @api.marshal_with(weather_model)
    def get(self):
        """Get current weather"""
        auth_manager.require_auth(lambda: None)()
        
        location = request.args.get('location', 'default')
        cache_key = f'weather:{location}'
        
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        weather = storage.get(f'weather_{location}') or {
            'temperature': 0,
            'conditions': 'Unknown',
            'humidity': 0,
            'wind_speed': 0,
            'location': location
        }
        
        cache.set(cache_key, weather, ttl=600)
        return weather
    
    @api.doc(security='Bearer')
    def post(self):
        """Update weather data"""
        auth_manager.require_auth(lambda: None)()
        
        data = request.json
        location = data.get('location', 'default')
        
        if storage.set(f'weather_{location}', data):
            cache.delete(f'weather:{location}')
            return data
        
        return {'error': 'Failed to update weather data'}, 500


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded', 'message': str(e)}), 429


if __name__ == '__main__':
    host = config['api']['host']
    port = config['api']['port']
    debug = config['api']['debug']
    
    app.logger.info(f"🚀 Central API starting on {host}:{port}")
    app.logger.info(f"📚 API docs: http://{host}:{port}/docs")
    app.logger.info(f"🔐 Auth: {'Configured' if API_TOKEN != 'YOUR_SECURE_TOKEN_HERE' else '⚠️  DEFAULT TOKEN'}")
    app.logger.info(f"💾 Cache: {'Redis' if cache.is_redis() else 'In-Memory'}")
    
    app.run(host=host, port=port, debug=debug)
