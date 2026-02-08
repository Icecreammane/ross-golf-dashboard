"""
Email Template Generator - Web Dashboard
Browse, edit, copy, and manage email templates
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database as db
from llama_generator import LlamaEmailGenerator
from pattern_learner import PatternLearner

app = Flask(__name__)
CORS(app)

generator = LlamaEmailGenerator()
learner = PatternLearner()

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/generate', methods=['POST'])
def api_generate():
    """Generate new email templates"""
    data = request.json
    
    recipient_type = data.get('recipient_type')
    email_type = data.get('email_type')
    context = data.get('context')
    
    if not recipient_type or not email_type:
        return jsonify({'error': 'recipient_type and email_type required'}), 400
    
    try:
        variations = generator.generate_email_variations(
            recipient_type=recipient_type,
            email_type=email_type,
            context=context
        )
        
        return jsonify({
            'success': True,
            'variations': variations
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/templates', methods=['GET'])
def api_templates():
    """Get templates with filters"""
    recipient_type = request.args.get('recipient_type')
    email_type = request.args.get('email_type')
    variation = request.args.get('variation')
    best = request.args.get('best') == 'true'
    limit = int(request.args.get('limit', 50))
    
    if best:
        templates = db.get_best_templates(recipient_type, email_type, limit)
    else:
        templates = db.get_templates(recipient_type, email_type, variation, limit)
    
    # Calculate conversion rates
    for t in templates:
        used = t.get('used', 0)
        converted = t.get('converted', 0)
        t['conversion_rate'] = (converted / used * 100) if used > 0 else 0
    
    return jsonify({
        'success': True,
        'templates': templates,
        'count': len(templates)
    })

@app.route('/api/templates/<int:template_id>', methods=['GET'])
def api_template(template_id):
    """Get single template"""
    templates = db.get_templates()
    template = next((t for t in templates if t['id'] == template_id), None)
    
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    # Calculate conversion rate
    used = template.get('used', 0)
    converted = template.get('converted', 0)
    template['conversion_rate'] = (converted / used * 100) if used > 0 else 0
    
    return jsonify({
        'success': True,
        'template': template
    })

@app.route('/api/templates/<int:template_id>', methods=['PUT'])
def api_update_template(template_id):
    """Update template (edit subject/body)"""
    # Note: This updates the template in memory for editing
    # For production, you'd want to add an update_template function to database.py
    data = request.json
    
    return jsonify({
        'success': True,
        'message': 'Template update feature coming soon'
    })

@app.route('/api/templates/<int:template_id>/feedback', methods=['POST'])
def api_feedback(template_id):
    """Add feedback for template"""
    data = request.json
    
    used = data.get('used')
    converted = data.get('converted')
    score = data.get('score')
    notes = data.get('notes')
    
    db.update_template_feedback(
        template_id=template_id,
        used=used,
        converted=converted,
        feedback_score=score,
        feedback_notes=notes
    )
    
    # Update patterns if converted
    if converted:
        learner.update_from_feedback(template_id, converted=True)
    
    return jsonify({
        'success': True,
        'message': 'Feedback recorded'
    })

@app.route('/api/successful-emails', methods=['GET'])
def api_successful_emails():
    """Get successful emails"""
    recipient_type = request.args.get('recipient_type')
    email_type = request.args.get('email_type')
    
    emails = db.get_successful_emails(recipient_type, email_type)
    
    return jsonify({
        'success': True,
        'emails': emails,
        'count': len(emails)
    })

@app.route('/api/successful-emails', methods=['POST'])
def api_add_successful_email():
    """Add successful email"""
    data = request.json
    
    db.add_successful_email(
        recipient_type=data.get('recipient_type'),
        email_type=data.get('email_type'),
        subject=data.get('subject'),
        body=data.get('body'),
        context=data.get('context'),
        outcome=data.get('outcome'),
        conversion_rate=data.get('conversion_rate')
    )
    
    return jsonify({
        'success': True,
        'message': 'Successful email added'
    })

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """Analyze patterns"""
    data = request.json
    recipient_type = data.get('recipient_type')
    email_type = data.get('email_type')
    
    patterns = learner.analyze_successful_emails(recipient_type, email_type)
    
    return jsonify({
        'success': True,
        'patterns': patterns,
        'count': len(patterns)
    })

@app.route('/api/patterns', methods=['GET'])
def api_patterns():
    """Get learned patterns"""
    pattern_type = request.args.get('pattern_type')
    min_effectiveness = float(request.args.get('min_effectiveness', 0.0))
    
    patterns = db.get_patterns(pattern_type, min_effectiveness)
    
    return jsonify({
        'success': True,
        'patterns': patterns,
        'count': len(patterns)
    })

@app.route('/api/recommendations', methods=['GET'])
def api_recommendations():
    """Get recommendations for generating emails"""
    recipient_type = request.args.get('recipient_type')
    email_type = request.args.get('email_type')
    
    if not recipient_type or not email_type:
        return jsonify({'error': 'recipient_type and email_type required'}), 400
    
    recommendations = learner.get_recommendations(recipient_type, email_type)
    
    return jsonify({
        'success': True,
        'recommendations': recommendations
    })

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Get usage statistics"""
    templates = db.get_templates(limit=1000)
    
    if not templates:
        return jsonify({
            'success': True,
            'stats': {
                'total_templates': 0,
                'templates_used': 0,
                'templates_converted': 0,
                'total_uses': 0,
                'total_conversions': 0,
                'overall_conversion_rate': 0
            }
        })
    
    total = len(templates)
    used = len([t for t in templates if t.get('used', 0) > 0])
    converted = len([t for t in templates if t.get('converted', 0) > 0])
    
    total_uses = sum(t.get('used', 0) for t in templates)
    total_conversions = sum(t.get('converted', 0) for t in templates)
    
    overall_conversion = (total_conversions / total_uses * 100) if total_uses > 0 else 0
    
    # Best templates
    best = db.get_best_templates(limit=5)
    
    # By recipient type
    by_recipient = {}
    for t in templates:
        rt = t['recipient_type']
        if rt not in by_recipient:
            by_recipient[rt] = {'count': 0, 'used': 0, 'converted': 0}
        by_recipient[rt]['count'] += 1
        by_recipient[rt]['used'] += t.get('used', 0)
        by_recipient[rt]['converted'] += t.get('converted', 0)
    
    return jsonify({
        'success': True,
        'stats': {
            'total_templates': total,
            'templates_used': used,
            'templates_converted': converted,
            'total_uses': total_uses,
            'total_conversions': total_conversions,
            'overall_conversion_rate': round(overall_conversion, 1),
            'best_templates': best,
            'by_recipient_type': by_recipient
        }
    })

@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'healthy', 'service': 'email-template-generator'})

if __name__ == '__main__':
    print("\n🚀 Email Template Generator Dashboard")
    print("=" * 60)
    print("Dashboard: http://localhost:3002")
    print("API Docs:  http://localhost:3002/api/stats")
    print("=" * 60)
    print("\n")
    
    app.run(host='0.0.0.0', port=3002, debug=True)
