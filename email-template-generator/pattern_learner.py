"""
Email Template Generator - Pattern Learning System
Analyzes successful emails and extracts reusable patterns
"""

import re
from typing import List, Dict, Tuple
from collections import Counter
import database as db

class PatternLearner:
    """Learns from successful emails and extracts patterns"""
    
    def __init__(self):
        pass
    
    def analyze_successful_emails(self, recipient_type: str = None, email_type: str = None):
        """Analyze successful emails and extract patterns"""
        emails = db.get_successful_emails(recipient_type, email_type)
        
        if not emails:
            return []
        
        patterns = []
        
        # Extract structural patterns
        patterns.extend(self._extract_structure_patterns(emails))
        
        # Extract phrase patterns
        patterns.extend(self._extract_phrase_patterns(emails))
        
        # Extract opening patterns
        patterns.extend(self._extract_opening_patterns(emails))
        
        # Extract CTA patterns
        patterns.extend(self._extract_cta_patterns(emails))
        
        # Store patterns in database
        for pattern in patterns:
            db.add_pattern(
                pattern_type=pattern['type'],
                pattern_data=pattern['data'],
                effectiveness_score=pattern['score']
            )
        
        return patterns
    
    def _extract_structure_patterns(self, emails: List[Dict]) -> List[Dict]:
        """Extract structural patterns (length, paragraphs, etc.)"""
        patterns = []
        
        # Analyze average characteristics
        lengths = [len(email['body']) for email in emails]
        paragraphs = [len(email['body'].split('\n\n')) for email in emails]
        
        avg_length = sum(lengths) / len(lengths)
        avg_paragraphs = sum(paragraphs) / len(paragraphs)
        
        # Calculate percentiles manually
        sorted_lengths = sorted(lengths)
        p25_idx = len(sorted_lengths) // 4
        p75_idx = (len(sorted_lengths) * 3) // 4
        
        patterns.append({
            'type': 'structure',
            'data': {
                'avg_length': int(avg_length),
                'avg_paragraphs': int(avg_paragraphs),
                'length_range': [sorted_lengths[p25_idx], sorted_lengths[p75_idx]]
            },
            'score': 0.7
        })
        
        return patterns
    
    def _extract_phrase_patterns(self, emails: List[Dict]) -> List[Dict]:
        """Extract common high-performing phrases"""
        patterns = []
        
        # Combine all email bodies and find common meaningful phrases
        all_text = ' '.join([email['body'].lower() for email in emails])
        
        # Simple word frequency (exclude common words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'be', 'been',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
                     'could', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        
        words = re.findall(r'\b\w+\b', all_text)
        word_counts = Counter([w for w in words if w not in stop_words and len(w) > 3])
        
        top_phrases = [word for word, count in word_counts.most_common(10)]
        
        if top_phrases:
            patterns.append({
                'type': 'phrases',
                'data': {
                    'high_value_terms': top_phrases
                },
                'score': 0.6
            })
        
        return patterns
    
    def _extract_opening_patterns(self, emails: List[Dict]) -> List[Dict]:
        """Extract successful opening line patterns"""
        patterns = []
        
        openings = []
        for email in emails:
            # Get first sentence
            sentences = re.split(r'[.!?]', email['body'])
            if sentences:
                first_sentence = sentences[0].strip()
                if first_sentence:
                    openings.append(first_sentence)
        
        # Common opening strategies
        question_opens = [o for o in openings if '?' in o]
        personal_opens = [o for o in openings if any(word in o.lower() for word in ['i noticed', 'i saw', 'i came across'])]
        direct_opens = [o for o in openings if not '?' in o and len(o.split()) < 15]
        
        opening_types = {
            'question': len(question_opens) / len(openings) if openings else 0,
            'personal': len(personal_opens) / len(openings) if openings else 0,
            'direct': len(direct_opens) / len(openings) if openings else 0
        }
        
        # Store most common type
        if openings:
            best_type = max(opening_types, key=opening_types.get)
            patterns.append({
                'type': 'opening',
                'data': {
                    'strategy': best_type,
                    'examples': openings[:3],
                    'frequency': opening_types[best_type]
                },
                'score': opening_types[best_type]
            })
        
        return patterns
    
    def _extract_cta_patterns(self, emails: List[Dict]) -> List[Dict]:
        """Extract call-to-action patterns"""
        patterns = []
        
        cta_keywords = ['call', 'meet', 'discuss', 'chat', 'schedule', 'connect', 
                       'reply', 'let me know', 'interested', 'demo', 'talk']
        
        ctas = []
        for email in emails:
            # Get last 2 sentences
            sentences = re.split(r'[.!?]', email['body'])
            last_sentences = sentences[-3:]
            
            for sentence in last_sentences:
                if any(keyword in sentence.lower() for keyword in cta_keywords):
                    ctas.append(sentence.strip())
        
        if ctas:
            # Analyze CTA patterns
            question_ctas = [c for c in ctas if '?' in c]
            soft_ctas = [c for c in ctas if any(word in c.lower() for word in ['if', 'would', 'interested'])]
            direct_ctas = [c for c in ctas if any(word in c.lower() for word in ['schedule', 'book', 'call me'])]
            
            cta_types = {
                'question': len(question_ctas) / len(ctas),
                'soft': len(soft_ctas) / len(ctas),
                'direct': len(direct_ctas) / len(ctas)
            }
            
            best_cta_type = max(cta_types, key=cta_types.get)
            
            patterns.append({
                'type': 'cta',
                'data': {
                    'strategy': best_cta_type,
                    'examples': ctas[:3],
                    'frequency': cta_types[best_cta_type]
                },
                'score': cta_types[best_cta_type]
            })
        
        return patterns
    
    def get_recommendations(self, recipient_type: str, email_type: str) -> Dict:
        """Get pattern-based recommendations for generating new emails"""
        # Get relevant patterns
        structure = db.get_patterns('structure', min_effectiveness=0.5)
        phrases = db.get_patterns('phrases', min_effectiveness=0.5)
        opening = db.get_patterns('opening', min_effectiveness=0.5)
        cta = db.get_patterns('cta', min_effectiveness=0.5)
        
        # Get best templates
        best_templates = db.get_best_templates(recipient_type, email_type, limit=3)
        
        recommendations = {
            'structure': structure[0]['pattern_data'] if structure else None,
            'phrases': phrases[0]['pattern_data'] if phrases else None,
            'opening': opening[0]['pattern_data'] if opening else None,
            'cta': cta[0]['pattern_data'] if cta else None,
            'example_templates': best_templates
        }
        
        return recommendations
    
    def update_from_feedback(self, template_id: int, converted: bool):
        """Update pattern effectiveness based on template performance"""
        # Get template
        templates = db.get_templates()
        template = next((t for t in templates if t['id'] == template_id), None)
        
        if not template:
            return
        
        # Simple effectiveness update: +0.1 for conversion, -0.05 for non-conversion
        delta = 0.1 if converted else -0.05
        
        # Update all patterns (simplified - in production, would identify which patterns were used)
        patterns = db.get_patterns()
        for pattern in patterns:
            db.update_pattern_effectiveness(pattern['id'], delta)

def seed_sample_emails():
    """Add sample successful emails for testing"""
    samples = [
        {
            'recipient_type': 'golf_student',
            'email_type': 'inquiry_response',
            'subject': 'Re: Golf Lessons Inquiry',
            'body': '''Hi [Name],

Thanks for reaching out about lessons! I'd love to help you improve your game.

I specialize in helping golfers break through plateaus with video analysis and personalized practice plans. Most students see improvement within 2-3 sessions.

Are you available for a quick 15-minute call this week to discuss your goals?

Best,
Ross''',
            'outcome': 'booked_lesson',
            'conversion_rate': 0.75
        },
        {
            'recipient_type': 'golf_student',
            'email_type': 'follow_up',
            'subject': 'Following up on your lesson inquiry',
            'body': '''Hey [Name],

I wanted to follow up on your interest in golf lessons. I have a couple spots opening up next week if you're still interested.

No pressure - just wanted to make sure my email didn't get lost in your inbox!

Let me know if you'd like to chat about your game.

Ross''',
            'outcome': 'booked_lesson',
            'conversion_rate': 0.50
        },
        {
            'recipient_type': 'partner',
            'email_type': 'collaboration',
            'subject': 'Partnership opportunity for golf instruction',
            'body': '''Hi [Name],

I noticed your facility has been growing quickly - congrats!

I'm a golf instructor working with players in the area, and I think we could create value for both our communities. I've helped 50+ students improve their handicaps this year.

Would you be open to a brief call to explore a potential partnership?

Thanks,
Ross''',
            'outcome': 'partnership',
            'conversion_rate': 0.30
        }
    ]
    
    for sample in samples:
        db.add_successful_email(**sample)
    
    print(f"✅ Added {len(samples)} sample successful emails")

if __name__ == '__main__':
    # Test the pattern learner
    print("🧠 Pattern Learning System Test\n")
    
    # Seed sample data
    seed_sample_emails()
    
    # Analyze patterns
    learner = PatternLearner()
    patterns = learner.analyze_successful_emails()
    
    print(f"\n📊 Extracted {len(patterns)} patterns:")
    for pattern in patterns:
        print(f"\n{pattern['type'].upper()}:")
        print(f"  Score: {pattern['score']:.2f}")
        print(f"  Data: {pattern['data']}")
    
    # Get recommendations
    print("\n\n💡 Recommendations for golf_student inquiry:")
    recs = learner.get_recommendations('golf_student', 'inquiry_response')
    for key, value in recs.items():
        if value:
            print(f"\n{key}:")
            print(f"  {value}")
