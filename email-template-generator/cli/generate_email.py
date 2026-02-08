#!/usr/bin/env python3
"""
Email Template Generator - CLI Tool
Usage: generate_email --to "prospect" --type "golf_inquiry"
"""

import click
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llama_generator import LlamaEmailGenerator
import database as db
from pattern_learner import PatternLearner

@click.group()
def cli():
    """Email Template Generator - Generate personalized golf outreach emails"""
    pass

@cli.command()
@click.option('--to', required=True, type=click.Choice(['golf_student', 'partner', 'platform', 'sponsor', 'media', 'prospect']), 
              help='Recipient type')
@click.option('--type', 'email_type', required=True, 
              type=click.Choice(['inquiry_response', 'follow_up', 'introduction', 'collaboration', 'update', 'thank_you', 'golf_inquiry']),
              help='Email type/purpose')
@click.option('--context', help='Additional context about the situation')
@click.option('--model', default='llama3.1:8b', help='Llama model to use')
@click.option('--save/--no-save', default=True, help='Save templates to database')
@click.option('--variation', type=click.Choice(['formal', 'casual', 'urgent', 'all']), default='all',
              help='Which variation to generate')
def generate(to, email_type, context, model, save, variation):
    """Generate email templates"""
    
    # Normalize recipient type aliases
    if to == 'prospect':
        to = 'golf_student'
    
    # Normalize email type aliases
    if email_type == 'golf_inquiry':
        email_type = 'inquiry_response'
    
    click.echo(f"\n🔮 Generating {variation} email(s) for {to} ({email_type})...")
    if context:
        click.echo(f"📝 Context: {context}")
    
    try:
        generator = LlamaEmailGenerator(model=model)
        
        if variation == 'all':
            # Generate all three variations
            variations = generator.generate_email_variations(
                recipient_type=to,
                email_type=email_type,
                context=context
            )
            
            click.echo(f"\n✨ Generated 3 variations:\n")
            
            for var in variations:
                click.echo(f"\n{'='*70}")
                click.echo(f"  {var['variation'].upper()} VARIATION")
                click.echo(f"{'='*70}")
                click.echo(f"\n📧 Subject: {var['subject']}\n")
                click.echo(var['body'])
                click.echo(f"\n{'='*70}\n")
        
        else:
            # Generate single variation
            variations = generator.generate_email_variations(
                recipient_type=to,
                email_type=email_type,
                context=context
            )
            
            # Find requested variation
            var = next((v for v in variations if v['variation'] == variation), None)
            
            if var:
                click.echo(f"\n{'='*70}")
                click.echo(f"📧 Subject: {var['subject']}\n")
                click.echo(var['body'])
                click.echo(f"\n{'='*70}\n")
        
        if save:
            click.echo("✅ Templates saved to database")
            click.echo("💡 Use 'generate_email list' to browse all templates")
            click.echo("💡 Use 'generate_email feedback <id>' to track performance")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--to', type=click.Choice(['golf_student', 'partner', 'platform', 'sponsor', 'media']),
              help='Filter by recipient type')
@click.option('--type', 'email_type',
              type=click.Choice(['inquiry_response', 'follow_up', 'introduction', 'collaboration', 'update', 'thank_you']),
              help='Filter by email type')
@click.option('--variation', type=click.Choice(['formal', 'casual', 'urgent']),
              help='Filter by variation')
@click.option('--limit', default=10, help='Number of templates to show')
@click.option('--best', is_flag=True, help='Show only best performing templates')
def list(to, email_type, variation, limit, best):
    """List generated templates"""
    
    if best:
        templates = db.get_best_templates(to, email_type, limit)
        click.echo(f"\n⭐ Top {len(templates)} performing templates:\n")
    else:
        templates = db.get_templates(to, email_type, variation, limit)
        click.echo(f"\n📋 Recent templates (showing {len(templates)}):\n")
    
    if not templates:
        click.echo("No templates found. Generate some with 'generate_email generate'")
        return
    
    for t in templates:
        used = t.get('used', 0)
        converted = t.get('converted', 0)
        conversion_rate = (converted / used * 100) if used > 0 else 0
        
        click.echo(f"{'='*70}")
        click.echo(f"ID: {t['id']} | {t['variation'].upper()} | {t['recipient_type']} → {t['email_type']}")
        click.echo(f"Subject: {t['subject']}")
        click.echo(f"Performance: {used} used, {converted} converted ({conversion_rate:.0f}%)")
        click.echo(f"Created: {t['generated_at']}")
        
        if t.get('context'):
            click.echo(f"Context: {t['context']}")
        
        click.echo(f"\n{t['body'][:200]}...")
        click.echo(f"{'='*70}\n")

@cli.command()
@click.argument('template_id', type=int)
@click.option('--used', is_flag=True, help='Mark as used')
@click.option('--converted', is_flag=True, help='Mark as converted (got response/result)')
@click.option('--score', type=click.IntRange(1, 5), help='Rate quality (1-5)')
@click.option('--notes', help='Feedback notes')
def feedback(template_id, used, converted, score, notes):
    """Add feedback for a template"""
    
    db.update_template_feedback(
        template_id=template_id,
        used=used,
        converted=converted,
        feedback_score=score,
        feedback_notes=notes
    )
    
    click.echo(f"✅ Feedback recorded for template {template_id}")
    
    if converted:
        click.echo("🎉 Nice! This template converted. Pattern learner will improve future emails.")
        
        # Update patterns
        learner = PatternLearner()
        learner.update_from_feedback(template_id, converted=True)

@cli.command()
@click.argument('template_id', type=int)
@click.option('--copy', is_flag=True, help='Copy to clipboard (macOS)')
def show(template_id, copy):
    """Show full template by ID"""
    
    templates = db.get_templates()
    template = next((t for t in templates if t['id'] == template_id), None)
    
    if not template:
        click.echo(f"❌ Template {template_id} not found", err=True)
        sys.exit(1)
    
    click.echo(f"\n{'='*70}")
    click.echo(f"Template #{template['id']}")
    click.echo(f"{template['variation'].upper()} | {template['recipient_type']} → {template['email_type']}")
    click.echo(f"{'='*70}\n")
    
    click.echo(f"Subject: {template['subject']}\n")
    click.echo(template['body'])
    click.echo(f"\n{'='*70}")
    
    used = template.get('used', 0)
    converted = template.get('converted', 0)
    conversion_rate = (converted / used * 100) if used > 0 else 0
    
    click.echo(f"\n📊 Performance: {used} used, {converted} converted ({conversion_rate:.0f}%)")
    
    if template.get('feedback_score'):
        click.echo(f"⭐ Rating: {template['feedback_score']}/5")
    
    if template.get('feedback_notes'):
        click.echo(f"💬 Notes: {template['feedback_notes']}")
    
    if copy:
        import subprocess
        full_email = f"Subject: {template['subject']}\n\n{template['body']}"
        subprocess.run('pbcopy', text=True, input=full_email)
        click.echo("\n✅ Copied to clipboard!")

@cli.command()
@click.option('--to', type=click.Choice(['golf_student', 'partner', 'platform', 'sponsor', 'media']),
              help='Analyze patterns for recipient type')
@click.option('--type', 'email_type',
              help='Analyze patterns for email type')
def analyze(to, email_type):
    """Analyze past emails and extract patterns"""
    
    click.echo(f"\n🧠 Analyzing successful emails...")
    if to:
        click.echo(f"📧 Filtering by recipient: {to}")
    if email_type:
        click.echo(f"📝 Filtering by type: {email_type}")
    
    learner = PatternLearner()
    patterns = learner.analyze_successful_emails(to, email_type)
    
    if not patterns:
        click.echo("\n⚠️  No successful emails found to analyze")
        click.echo("💡 Add past successful emails with 'generate_email add-success'")
        return
    
    click.echo(f"\n✨ Extracted {len(patterns)} patterns:\n")
    
    for pattern in patterns:
        click.echo(f"{'='*70}")
        click.echo(f"{pattern['type'].upper()}")
        click.echo(f"Effectiveness: {pattern['score']:.0%}")
        click.echo(f"{'='*70}")
        
        for key, value in pattern['data'].items():
            click.echo(f"  {key}: {value}")
        
        click.echo("")

@cli.command()
@click.option('--to', required=True, type=click.Choice(['golf_student', 'partner', 'platform', 'sponsor', 'media']))
@click.option('--type', 'email_type', required=True)
@click.option('--subject', required=True, prompt=True)
@click.option('--body', required=True, prompt=True)
@click.option('--outcome', help='What happened (e.g., "booked_lesson", "partnership")')
@click.option('--conversion-rate', type=float, help='Success rate (0.0-1.0)')
def add_success(to, email_type, subject, body, outcome, conversion_rate):
    """Add a past successful email for learning"""
    
    db.add_successful_email(
        recipient_type=to,
        email_type=email_type,
        subject=subject,
        body=body,
        outcome=outcome,
        conversion_rate=conversion_rate
    )
    
    click.echo(f"\n✅ Added successful email to learning database")
    click.echo(f"💡 Run 'generate_email analyze' to update patterns")

@cli.command()
def stats():
    """Show usage statistics"""
    
    templates = db.get_templates(limit=1000)
    
    if not templates:
        click.echo("📊 No templates generated yet")
        return
    
    total = len(templates)
    used = len([t for t in templates if t.get('used', 0) > 0])
    converted = len([t for t in templates if t.get('converted', 0) > 0])
    
    total_uses = sum(t.get('used', 0) for t in templates)
    total_conversions = sum(t.get('converted', 0) for t in templates)
    
    overall_conversion = (total_conversions / total_uses * 100) if total_uses > 0 else 0
    
    click.echo(f"\n📊 Email Template Generator Stats")
    click.echo(f"{'='*70}")
    click.echo(f"Total templates generated: {total}")
    click.echo(f"Templates used: {used} ({used/total*100:.0f}%)")
    click.echo(f"Templates converted: {converted}")
    click.echo(f"\nTotal uses: {total_uses}")
    click.echo(f"Total conversions: {total_conversions}")
    click.echo(f"Overall conversion rate: {overall_conversion:.1f}%")
    click.echo(f"{'='*70}\n")
    
    # Best performing
    best = db.get_best_templates(limit=3)
    if best:
        click.echo("⭐ Top 3 templates:\n")
        for i, t in enumerate(best, 1):
            conv_rate = (t.get('converted', 0) / t.get('used', 1) * 100)
            click.echo(f"{i}. Template #{t['id']} - {conv_rate:.0f}% conversion")
            click.echo(f"   {t['variation']} | {t['recipient_type']} → {t['email_type']}")
            click.echo(f"   Subject: {t['subject']}\n")

if __name__ == '__main__':
    cli()
