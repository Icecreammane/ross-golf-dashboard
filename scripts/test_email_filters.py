#!/usr/bin/env python3
"""
Test email importance filters without connecting to Gmail
"""

import sys
sys.path.insert(0, '/Users/clawdbot/clawd/scripts')

from email_daemon import is_important, IMPORTANT_SENDERS, IMPORTANT_KEYWORDS, IMPORTANT_DOMAINS

def test_filters():
    """Test all filter scenarios"""
    
    print("=" * 60)
    print("Email Filter Test Suite")
    print("=" * 60)
    print()
    
    # Test cases: (sender, subject, from_email, expected_result)
    test_cases = [
        # Important senders
        ("Ross Johnson", "Meeting tomorrow", "ross@company.com", True, "sender: ross"),
        ("CEO Office", "Q4 Results", "ceo@company.com", True, "sender: ceo"),
        ("Investor Relations", "Follow up", "contact@vc-firm.com", True, "sender: investor"),
        ("Stripe Billing", "Invoice paid", "noreply@stripe.com", True, "domain: @stripe.com"),
        
        # Important keywords
        ("John Doe", "URGENT: Server down", "john@example.com", True, "keyword: urgent"),
        ("Jane Smith", "Deadline approaching for project", "jane@example.com", True, "keyword: deadline"),
        ("Support Team", "Action required: Verify your account", "support@service.com", True, "keyword: action required"),
        ("Billing Dept", "Invoice #12345 overdue", "billing@company.com", True, "keyword: invoice"),
        ("Security Team", "Payment verification needed", "security@bank.com", True, "keyword: payment"),
        
        # Important domains
        ("GitHub", "New pull request", "notifications@github.com", True, "domain: @github.com"),
        ("OpenAI", "API usage alert", "noreply@openai.com", True, "domain: @openai.com"),
        ("Anthropic", "Claude update", "updates@anthropic.com", True, "domain: @anthropic.com"),
        
        # Not important
        ("Newsletter", "Weekly digest", "newsletter@company.com", False, None),
        ("Marketing", "Check out our sale", "promo@store.com", False, None),
        ("Social Media", "You have new followers", "notify@social.com", False, None),
        ("Random Person", "Hey, how are you?", "random@example.com", False, None),
    ]
    
    passed = 0
    failed = 0
    
    for sender, subject, from_email, should_be_important, expected_reason in test_cases:
        result, reason = is_important(sender, subject, from_email)
        
        # Check if result matches expectation
        if result == should_be_important:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        
        # Print test result
        print(f"{status} | {sender}")
        print(f"     Subject: {subject}")
        print(f"     From: {from_email}")
        print(f"     Expected: {should_be_important} ({expected_reason})")
        print(f"     Got: {result} ({reason})")
        print()
    
    # Summary
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    print()
    
    # Print current filters
    print("Current Filters:")
    print("-" * 60)
    print(f"Important Senders ({len(IMPORTANT_SENDERS)}):")
    for s in IMPORTANT_SENDERS[:5]:
        print(f"  - {s}")
    if len(IMPORTANT_SENDERS) > 5:
        print(f"  ... and {len(IMPORTANT_SENDERS) - 5} more")
    print()
    
    print(f"Important Keywords ({len(IMPORTANT_KEYWORDS)}):")
    for k in IMPORTANT_KEYWORDS[:8]:
        print(f"  - {k}")
    if len(IMPORTANT_KEYWORDS) > 8:
        print(f"  ... and {len(IMPORTANT_KEYWORDS) - 8} more")
    print()
    
    print(f"Important Domains ({len(IMPORTANT_DOMAINS)}):")
    for d in IMPORTANT_DOMAINS:
        print(f"  - {d}")
    print()
    
    return failed == 0

if __name__ == "__main__":
    success = test_filters()
    sys.exit(0 if success else 1)
