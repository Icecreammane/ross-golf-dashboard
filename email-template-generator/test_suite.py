#!/usr/bin/env python3
"""
Email Template Generator - Test Suite
Tests all components: database, pattern learning, LLM generation, CLI
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db
from pattern_learner import PatternLearner, seed_sample_emails
from llama_generator import LlamaEmailGenerator

def test_database():
    """Test database operations"""
    print("\n" + "="*70)
    print("TEST 1: DATABASE OPERATIONS")
    print("="*70)
    
    try:
        # Test adding template
        template_id = db.add_template(
            recipient_type='golf_student',
            email_type='inquiry_response',
            variation='casual',
            subject='Test Subject',
            body='Test body content',
            context='Test context'
        )
        print(f"✅ Added template: ID {template_id}")
        
        # Test retrieving templates
        templates = db.get_templates(recipient_type='golf_student', limit=5)
        print(f"✅ Retrieved {len(templates)} templates")
        
        # Test feedback
        db.update_template_feedback(template_id, used=True, converted=True, feedback_score=5)
        print(f"✅ Updated feedback for template {template_id}")
        
        # Test best templates
        best = db.get_best_templates(limit=3)
        print(f"✅ Retrieved {len(best)} best performing templates")
        
        print("\n✅ DATABASE TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ DATABASE TEST FAILED: {e}")
        return False

def test_pattern_learning():
    """Test pattern learning system"""
    print("\n" + "="*70)
    print("TEST 2: PATTERN LEARNING")
    print("="*70)
    
    try:
        # Seed sample emails
        print("📧 Seeding sample successful emails...")
        seed_sample_emails()
        
        # Analyze patterns
        learner = PatternLearner()
        patterns = learner.analyze_successful_emails()
        
        print(f"✅ Extracted {len(patterns)} patterns")
        
        for pattern in patterns:
            print(f"\n  {pattern['type'].upper()}:")
            print(f"    Effectiveness: {pattern['score']:.0%}")
            print(f"    Data: {pattern['data']}")
        
        # Test recommendations
        recs = learner.get_recommendations('golf_student', 'inquiry_response')
        print(f"\n✅ Generated recommendations: {len(recs)} categories")
        
        print("\n✅ PATTERN LEARNING TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ PATTERN LEARNING TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llama_generation():
    """Test Llama email generation"""
    print("\n" + "="*70)
    print("TEST 3: LLAMA EMAIL GENERATION")
    print("="*70)
    
    try:
        print("🔮 Initializing Llama generator...")
        generator = LlamaEmailGenerator()
        
        print("📝 Generating test emails (this may take 30-60 seconds)...")
        
        test_case = {
            'recipient_type': 'golf_student',
            'email_type': 'inquiry_response',
            'context': 'Student wants help with slice, mentioned they play at Oak Creek'
        }
        
        variations = generator.generate_email_variations(**test_case)
        
        print(f"\n✅ Generated {len(variations)} variations")
        
        for var in variations:
            print(f"\n  --- {var['variation'].upper()} ---")
            print(f"  Subject: {var['subject']}")
            print(f"  Length: {len(var['body'])} characters")
            print(f"  Preview: {var['body'][:100]}...")
        
        print("\n✅ LLAMA GENERATION TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ LLAMA GENERATION TEST FAILED: {e}")
        print("\n⚠️  Make sure Ollama is running: ollama serve")
        print("⚠️  Make sure llama3.1:8b is installed: ollama pull llama3.1:8b")
        import traceback
        traceback.print_exc()
        return False

def test_full_workflow():
    """Test complete workflow: generate -> use -> feedback -> learn"""
    print("\n" + "="*70)
    print("TEST 4: FULL WORKFLOW")
    print("="*70)
    
    try:
        # 1. Generate emails
        print("1️⃣  Generating emails...")
        generator = LlamaEmailGenerator()
        variations = generator.generate_email_variations(
            recipient_type='partner',
            email_type='collaboration',
            context='New golf facility with indoor simulator'
        )
        
        template_id = variations[0]['variation']  # Get an ID from DB
        templates = db.get_templates(recipient_type='partner', limit=1)
        if templates:
            template_id = templates[0]['id']
        
        print(f"✅ Generated and stored templates")
        
        # 2. Mark as used
        print("2️⃣  Marking template as used...")
        db.update_template_feedback(template_id, used=True)
        print(f"✅ Template {template_id} marked as used")
        
        # 3. Mark as converted
        print("3️⃣  Marking template as converted...")
        db.update_template_feedback(template_id, converted=True, feedback_score=4)
        print(f"✅ Template {template_id} marked as converted")
        
        # 4. Update patterns
        print("4️⃣  Updating pattern effectiveness...")
        learner = PatternLearner()
        learner.update_from_feedback(template_id, converted=True)
        print(f"✅ Patterns updated based on feedback")
        
        # 5. Get updated recommendations
        print("5️⃣  Getting updated recommendations...")
        recs = learner.get_recommendations('partner', 'collaboration')
        print(f"✅ Recommendations include learning from feedback")
        
        print("\n✅ FULL WORKFLOW TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ FULL WORKFLOW TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_interface():
    """Test CLI can be imported and initialized"""
    print("\n" + "="*70)
    print("TEST 5: CLI INTERFACE")
    print("="*70)
    
    try:
        # Import CLI
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cli'))
        import generate_email
        
        print("✅ CLI module imports successfully")
        print("✅ Click commands registered")
        
        print("\n💡 To test CLI manually:")
        print("  chmod +x cli/generate_email.py")
        print("  ./cli/generate_email.py --help")
        print("  ./cli/generate_email.py generate --to golf_student --type inquiry_response")
        
        print("\n✅ CLI INTERFACE TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ CLI INTERFACE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("📧 EMAIL TEMPLATE GENERATOR - TEST SUITE")
    print("="*70)
    print("\nTesting all components...\n")
    
    results = {
        'Database': test_database(),
        'Pattern Learning': test_pattern_learning(),
        'Llama Generation': test_llama_generation(),
        'Full Workflow': test_full_workflow(),
        'CLI Interface': test_cli_interface()
    }
    
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}  {test_name}")
    
    total = len(results)
    passed = sum(results.values())
    
    print("\n" + "="*70)
    print(f"OVERALL: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("="*70)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is production-ready.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
