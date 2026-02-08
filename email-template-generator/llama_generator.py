"""
Email Template Generator - Llama LLM Integration
Uses local Ollama/Llama to generate personalized email templates
"""

import ollama
import json
from typing import List, Dict, Tuple
import database as db
from pattern_learner import PatternLearner

class LlamaEmailGenerator:
    """Generate emails using local Llama LLM"""
    
    def __init__(self, model: str = "llama3.1:8b"):
        self.model = model
        self.pattern_learner = PatternLearner()
        
        # Verify Ollama is running
        try:
            ollama.list()
        except Exception as e:
            raise RuntimeError(f"Ollama not available: {e}")
    
    def generate_email_variations(self, 
                                  recipient_type: str,
                                  email_type: str,
                                  context: str = None) -> List[Dict]:
        """
        Generate 3 variations: formal, casual, urgent
        
        Args:
            recipient_type: 'golf_student', 'partner', 'platform', etc.
            email_type: 'inquiry', 'follow_up', 'introduction', etc.
            context: Additional context about the specific situation
        
        Returns:
            List of 3 email dictionaries (formal, casual, urgent)
        """
        
        # Get pattern-based recommendations
        recommendations = self.pattern_learner.get_recommendations(recipient_type, email_type)
        
        # Get past successful emails for reference
        past_emails = db.get_successful_emails(recipient_type, email_type)
        
        # Generate each variation
        variations = []
        
        for tone in ['formal', 'casual', 'urgent']:
            email = self._generate_single_email(
                recipient_type=recipient_type,
                email_type=email_type,
                tone=tone,
                context=context,
                recommendations=recommendations,
                past_emails=past_emails[:2]  # Use top 2 examples
            )
            
            variations.append({
                'variation': tone,
                'subject': email['subject'],
                'body': email['body'],
                'recipient_type': recipient_type,
                'email_type': email_type,
                'context': context
            })
            
            # Store in database
            db.add_template(
                recipient_type=recipient_type,
                email_type=email_type,
                variation=tone,
                subject=email['subject'],
                body=email['body'],
                context=context
            )
        
        return variations
    
    def _generate_single_email(self,
                               recipient_type: str,
                               email_type: str,
                               tone: str,
                               context: str,
                               recommendations: Dict,
                               past_emails: List[Dict]) -> Dict:
        """Generate a single email with specific tone"""
        
        # Build prompt with patterns and examples
        prompt = self._build_prompt(
            recipient_type=recipient_type,
            email_type=email_type,
            tone=tone,
            context=context,
            recommendations=recommendations,
            past_emails=past_emails
        )
        
        # Call Llama
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': 0.7 if tone == 'casual' else 0.5,
                    'top_p': 0.9,
                    'num_predict': 500
                }
            )
            
            # Parse response
            email = self._parse_response(response['response'])
            
            return email
            
        except Exception as e:
            print(f"⚠️ Error generating email: {e}")
            # Fallback to template
            return self._fallback_template(recipient_type, email_type, tone)
    
    def _build_prompt(self,
                     recipient_type: str,
                     email_type: str,
                     tone: str,
                     context: str,
                     recommendations: Dict,
                     past_emails: List[Dict]) -> str:
        """Build comprehensive prompt for Llama"""
        
        # Recipient type descriptions
        recipient_descriptions = {
            'golf_student': 'potential or current golf student looking for lessons/coaching',
            'partner': 'potential business partner (golf facilities, clubs, instructors)',
            'platform': 'golf technology platform or app for potential integration',
            'sponsor': 'potential sponsor for golf events or content',
            'media': 'golf media outlet or publication'
        }
        
        # Email type descriptions
        email_type_descriptions = {
            'inquiry_response': 'responding to their inquiry about services',
            'follow_up': 'following up on previous conversation or inquiry',
            'introduction': 'cold introduction/outreach',
            'collaboration': 'proposing a partnership or collaboration',
            'update': 'sharing progress or new offerings',
            'thank_you': 'thanking for meeting/opportunity'
        }
        
        recipient_desc = recipient_descriptions.get(recipient_type, recipient_type)
        email_type_desc = email_type_descriptions.get(email_type, email_type)
        
        # Tone guidelines
        tone_guidelines = {
            'formal': 'Professional and polished. Use proper business email structure. Respectful and composed.',
            'casual': 'Friendly and conversational. Like texting a friend. Use contractions, be warm.',
            'urgent': 'Time-sensitive and action-oriented. Create urgency without being pushy. Clear CTA.'
        }
        
        tone_guide = tone_guidelines[tone]
        
        # Build prompt
        prompt = f"""You are Ross, a professional golf instructor writing an email. Generate a {tone} email.

RECIPIENT: {recipient_desc}
EMAIL TYPE: {email_type_desc}
TONE: {tone_guide}
"""
        
        if context:
            prompt += f"\nSPECIFIC CONTEXT: {context}"
        
        # Add pattern recommendations
        if recommendations.get('structure'):
            struct = recommendations['structure']
            prompt += f"\n\nSTRUCTURE GUIDANCE:"
            prompt += f"\n- Target length: {struct['avg_length']} characters ({struct['length_range'][0]}-{struct['length_range'][1]})"
            prompt += f"\n- Use {struct['avg_paragraphs']} paragraphs"
        
        if recommendations.get('opening'):
            opening = recommendations['opening']
            prompt += f"\n\nOPENING STRATEGY: Use a {opening['strategy']} opening"
            if opening.get('examples'):
                prompt += f"\n- Example: {opening['examples'][0]}"
        
        if recommendations.get('cta'):
            cta = recommendations['cta']
            prompt += f"\n\nCALL-TO-ACTION: Use a {cta['strategy']} CTA"
            if cta.get('examples'):
                prompt += f"\n- Example: {cta['examples'][0]}"
        
        # Add successful examples
        if past_emails:
            prompt += f"\n\nHIGH-PERFORMING EXAMPLES (for reference, don't copy):"
            for i, email in enumerate(past_emails[:2], 1):
                prompt += f"\n\nExample {i} (conversion rate: {email.get('conversion_rate', 0):.0%}):"
                prompt += f"\nSubject: {email['subject']}"
                prompt += f"\n{email['body'][:200]}..."
        
        prompt += f"""

REQUIREMENTS:
1. Write subject line and body
2. Keep email under 200 words
3. Match the {tone} tone throughout
4. Use "Ross" as signature
5. Include one clear call-to-action
6. Be genuine and helpful, not salesy
7. Reference golf/instruction naturally

OUTPUT FORMAT:
Subject: [subject line]

[email body]

Ross"""
        
        return prompt
    
    def _parse_response(self, response: str) -> Dict:
        """Parse Llama response into structured email"""
        
        # Extract subject
        subject_match = response.split('Subject:', 1)
        if len(subject_match) > 1:
            subject_line = subject_match[1].split('\n', 1)[0].strip()
            body_text = subject_match[1].split('\n', 1)[1].strip() if '\n' in subject_match[1] else ""
        else:
            # No subject found, use first line
            lines = response.strip().split('\n')
            subject_line = lines[0].strip()
            body_text = '\n'.join(lines[1:]).strip()
        
        # Clean up body
        body_text = body_text.strip()
        
        # Ensure signature
        if not body_text.endswith('Ross'):
            body_text += '\n\nRoss'
        
        return {
            'subject': subject_line,
            'body': body_text
        }
    
    def _fallback_template(self, recipient_type: str, email_type: str, tone: str) -> Dict:
        """Fallback template if LLM fails"""
        
        templates = {
            'formal': {
                'subject': f'Re: {email_type.replace("_", " ").title()}',
                'body': '''Dear [Name],

Thank you for your interest. I would be pleased to discuss this opportunity further.

I specialize in golf instruction and have helped numerous students improve their game through personalized coaching and analysis.

Would you be available for a brief conversation this week?

Best regards,
Ross'''
            },
            'casual': {
                'subject': f'Quick note about {email_type.replace("_", " ")}',
                'body': '''Hey [Name],

Thanks for reaching out! I'd love to chat about this.

I work with golfers at all levels and always looking for good people to connect with.

Let me know if you want to grab a coffee or jump on a quick call!

Ross'''
            },
            'urgent': {
                'subject': f'Time-sensitive: {email_type.replace("_", " ").title()}',
                'body': '''Hi [Name],

I wanted to reach out quickly because I have limited availability this week.

I think we could create something valuable together, but spots are filling up fast.

Can you let me know by tomorrow if you're interested in discussing further?

Ross'''
            }
        }
        
        return templates.get(tone, templates['casual'])

def test_generator():
    """Test the email generator"""
    print("🚀 Testing Llama Email Generator\n")
    
    generator = LlamaEmailGenerator()
    
    # Test case
    test_cases = [
        {
            'recipient_type': 'golf_student',
            'email_type': 'inquiry_response',
            'context': 'Student wants to work on driving distance, mentioned they slice'
        },
        {
            'recipient_type': 'partner',
            'email_type': 'collaboration',
            'context': 'Local golf facility with driving range, want to offer lessons there'
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST CASE {i}")
        print(f"Recipient: {test['recipient_type']}")
        print(f"Type: {test['email_type']}")
        print(f"Context: {test['context']}")
        print(f"{'='*60}\n")
        
        try:
            variations = generator.generate_email_variations(**test)
            
            for var in variations:
                print(f"\n--- {var['variation'].upper()} VARIATION ---")
                print(f"Subject: {var['subject']}")
                print(f"\n{var['body']}")
                print("\n")
        
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_generator()
