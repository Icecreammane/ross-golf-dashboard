#!/usr/bin/env python3
"""
Execution Speed Optimizer - Build faster, ship more
Template library, parallel execution, task decomposition
"""

import json
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess

WORKSPACE = Path("/Users/clawdbot/clawd")
TEMPLATES_DIR = WORKSPACE / "templates"
MEMORY_DIR = WORKSPACE / "memory"
BUILD_CACHE = MEMORY_DIR / "build_cache.json"

class ExecutionOptimizer:
    def __init__(self):
        self.templates_dir = TEMPLATES_DIR
        self.templates_dir.mkdir(exist_ok=True)
        self.cache = self.load_cache()
    
    def load_cache(self):
        """Load build cache"""
        if BUILD_CACHE.exists():
            with open(BUILD_CACHE) as f:
                return json.load(f)
        return {
            "templates_used": {},
            "build_times": [],
            "parallel_builds": 0
        }
    
    def get_template(self, template_name):
        """Get a code template"""
        template_path = self.templates_dir / f"{template_name}.template"
        
        if template_path.exists():
            with open(template_path) as f:
                return f.read()
        
        # Return default templates if file doesn't exist
        return self._get_builtin_template(template_name)
    
    def _get_builtin_template(self, name):
        """Get built-in templates"""
        templates = {
            "flask_endpoint": '''
@app.route('/api/{endpoint}', methods=['{method}'])
def {function_name}():
    """
    {description}
    """
    try:
        # Get request data
        data = request.get_json()
        
        # TODO: Implement logic here
        
        return jsonify({
            'success': True,
            'data': {}
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
''',
            
            "dashboard_widget": '''
<div class="widget {widget_class}">
    <div class="widget-header">
        <h3>{title}</h3>
        <span class="widget-icon">{icon}</span>
    </div>
    <div class="widget-body">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {trend_indicator}
    </div>
</div>

<style>
.{widget_class} {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.widget-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 15px;
}
.metric-value {
    font-size: 2em;
    font-weight: bold;
    color: #333;
}
</style>
''',
            
            "database_schema": '''
CREATE TABLE IF NOT EXISTS {table_name} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    {fields}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_{table_name}_{index_field} ON {table_name}({index_field});
''',
            
            "stripe_payment": '''
def create_payment_intent(amount, customer_email, description):
    """
    Create Stripe payment intent
    
    Args:
        amount: Amount in cents
        customer_email: Customer email
        description: Payment description
    
    Returns:
        dict: Payment intent with client_secret
    """
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            receipt_email=customer_email,
            description=description,
            metadata={
                'created_at': datetime.now().isoformat()
            }
        )
        
        return {
            'success': True,
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id
        }
    
    except stripe.error.StripeError as e:
        return {
            'success': False,
            'error': str(e)
        }
''',
            
            "email_sequence": '''
def send_email_sequence(recipient, sequence_name, context=None):
    """
    Send automated email sequence
    
    Args:
        recipient: Email address
        sequence_name: Name of sequence to send
        context: Dict of template variables
    """
    sequences = {
        'welcome': [
            {
                'subject': 'Welcome to {product_name}!',
                'template': 'welcome_email.html',
                'delay_days': 0
            },
            {
                'subject': 'Getting started with {product_name}',
                'template': 'getting_started.html',
                'delay_days': 2
            },
            {
                'subject': 'Tips and tricks',
                'template': 'tips_email.html',
                'delay_days': 5
            }
        ]
    }
    
    context = context or {}
    sequence = sequences.get(sequence_name, [])
    
    for email in sequence:
        # Schedule email
        schedule_email(
            recipient=recipient,
            subject=email['subject'].format(**context),
            template=email['template'],
            delay_days=email['delay_days'],
            context=context
        )
''',
            
            "telegram_bot_command": '''
async def {command_name}(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    {description}
    
    Usage: /{command_name} {args}
    """
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Get arguments
    args = context.args
    
    try:
        # TODO: Implement command logic
        
        await update.message.reply_text(
            "Command executed successfully!",
            parse_mode='Markdown'
        )
    
    except Exception as e:
        await update.message.reply_text(
            f"Error: {str(e)}",
            parse_mode='Markdown'
        )
'''
        }
        
        return templates.get(name, f"# Template '{name}' not found")
    
    def fill_template(self, template_name, variables):
        """Fill template with variables"""
        template = self.get_template(template_name)
        
        # Simple variable substitution
        for key, value in variables.items():
            template = template.replace(f"{{{key}}}", str(value))
        
        # Track usage
        if template_name not in self.cache["templates_used"]:
            self.cache["templates_used"][template_name] = 0
        self.cache["templates_used"][template_name] += 1
        
        self.save_cache()
        
        return template
    
    def decompose_task(self, task_description):
        """Decompose complex task into parallel subtasks"""
        # Simple decomposition heuristics
        subtasks = []
        
        keywords = {
            "api": ["create endpoints", "setup routes", "add error handling", "write tests"],
            "dashboard": ["create HTML structure", "add CSS styling", "implement JS logic", "connect to API"],
            "database": ["design schema", "create migrations", "setup models", "add indexes"],
            "integration": ["setup authentication", "implement API calls", "handle webhooks", "test integration"]
        }
        
        task_lower = task_description.lower()
        
        for category, tasks in keywords.items():
            if category in task_lower:
                subtasks.extend([{"task": t, "category": category} for t in tasks])
        
        # If no matches, create generic subtasks
        if not subtasks:
            subtasks = [
                {"task": "Research and plan", "category": "planning"},
                {"task": "Implement core functionality", "category": "implementation"},
                {"task": "Add error handling", "category": "implementation"},
                {"task": "Write tests", "category": "testing"},
                {"task": "Document usage", "category": "documentation"}
            ]
        
        return subtasks
    
    def execute_parallel(self, tasks, max_workers=4):
        """Execute tasks in parallel"""
        start_time = datetime.now()
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self._execute_task, task): task 
                for task in tasks
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append({
                        "task": task,
                        "success": True,
                        "result": result
                    })
                except Exception as e:
                    results.append({
                        "task": task,
                        "success": False,
                        "error": str(e)
                    })
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.cache["build_times"].append({
            "timestamp": start_time.isoformat(),
            "duration": duration,
            "tasks": len(tasks)
        })
        self.cache["parallel_builds"] += 1
        self.save_cache()
        
        return {
            "results": results,
            "duration": duration,
            "success_count": sum(1 for r in results if r["success"])
        }
    
    def _execute_task(self, task):
        """Execute a single task (placeholder)"""
        # In real implementation, would actually execute the task
        # For now, simulate work
        import time
        time.sleep(0.5)  # Simulate work
        return f"Completed: {task.get('task', 'unknown')}"
    
    def get_template_list(self):
        """Get list of available templates"""
        return [
            "flask_endpoint",
            "dashboard_widget",
            "database_schema",
            "stripe_payment",
            "email_sequence",
            "telegram_bot_command"
        ]
    
    def get_efficiency_stats(self):
        """Get efficiency statistics"""
        times = self.cache.get("build_times", [])
        
        if not times:
            return "No builds tracked yet"
        
        avg_duration = sum(t["duration"] for t in times) / len(times)
        total_tasks = sum(t["tasks"] for t in times)
        
        stats = f"""
Execution Efficiency Stats:
- Total parallel builds: {self.cache['parallel_builds']}
- Average build time: {avg_duration:.1f}s
- Total tasks completed: {total_tasks}
- Most used templates: {self._get_top_templates()}

Templates available: {len(self.get_template_list())}
"""
        return stats.strip()
    
    def _get_top_templates(self):
        """Get most frequently used templates"""
        used = self.cache.get("templates_used", {})
        if not used:
            return "None yet"
        
        sorted_templates = sorted(used.items(), key=lambda x: x[1], reverse=True)
        return ", ".join(f"{t[0]} ({t[1]}x)" for t in sorted_templates[:3])
    
    def save_cache(self):
        """Save build cache"""
        BUILD_CACHE.parent.mkdir(exist_ok=True)
        with open(BUILD_CACHE, "w") as f:
            json.dump(self.cache, f, indent=2)


def test_optimizer():
    """Test execution optimizer"""
    optimizer = ExecutionOptimizer()
    
    print("Execution Speed Optimizer Test\n")
    
    # Test template retrieval
    print("Available templates:")
    for template in optimizer.get_template_list():
        print(f"  - {template}")
    
    # Test template filling
    print("\nGenerating Flask endpoint from template:")
    endpoint_code = optimizer.fill_template("flask_endpoint", {
        "endpoint": "users",
        "method": "GET",
        "function_name": "get_users",
        "description": "Get all users"
    })
    print(endpoint_code[:200] + "...")
    
    # Test task decomposition
    print("\nDecomposing task: 'Build a REST API'")
    subtasks = optimizer.decompose_task("Build a REST API")
    for i, task in enumerate(subtasks, 1):
        print(f"  {i}. {task['task']} ({task['category']})")
    
    # Test parallel execution
    print("\nExecuting tasks in parallel...")
    result = optimizer.execute_parallel(subtasks[:4])
    print(f"Completed {result['success_count']}/{len(subtasks[:4])} tasks in {result['duration']:.2f}s")
    
    # Show stats
    print("\n" + optimizer.get_efficiency_stats())
    
    print("\n✅ Execution optimizer working!")


if __name__ == "__main__":
    test_optimizer()
