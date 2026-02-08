#!/usr/bin/env python3
"""
Revenue Tracker - Track every action → money

Logs all money-related activities:
- Opportunities found
- Applications sent
- Proposals made
- Interviews scheduled
- Clients closed
- Revenue earned

Builds the attribution model: What actions led to money?
"""

import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / "clawd"
REVENUE_LOG = WORKSPACE / "revenue" / "activity_log.jsonl"

REVENUE_LOG.parent.mkdir(exist_ok=True)

def log_revenue_event(event_type, data):
    """
    Log a revenue-related event
    
    event_type: opportunity_found, application_sent, proposal_sent, 
                interview_scheduled, client_closed, payment_received,
                time_invested, opportunity_passed
    """
    
    event = {
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        "data": data
    }
    
    with open(REVENUE_LOG, 'a') as f:
        f.write(json.dumps(event) + '\n')
    
    return event

def log_opportunity(source, title, value, url=None):
    """Log a new opportunity discovered"""
    return log_revenue_event("opportunity_found", {
        "source": source,  # upwork, reddit, twitter, email, referral
        "title": title,
        "value": value,  # potential $ amount
        "url": url
    })

def log_application(opportunity_id, time_spent_minutes):
    """Log application sent"""
    return log_revenue_event("application_sent", {
        "opportunity_id": opportunity_id,
        "time_spent": time_spent_minutes
    })

def log_proposal(opportunity_id, proposed_rate, time_spent_minutes):
    """Log proposal sent"""
    return log_revenue_event("proposal_sent", {
        "opportunity_id": opportunity_id,
        "proposed_rate": proposed_rate,
        "time_spent": time_spent_minutes
    })

def log_interview(opportunity_id, scheduled_date):
    """Log interview scheduled"""
    return log_revenue_event("interview_scheduled", {
        "opportunity_id": opportunity_id,
        "date": scheduled_date
    })

def log_client_closed(opportunity_id, actual_value, timeline):
    """Log client closed (WON!)"""
    return log_revenue_event("client_closed", {
        "opportunity_id": opportunity_id,
        "value": actual_value,
        "timeline": timeline
    })

def log_payment_received(client_id, amount, payment_method):
    """Log actual payment received"""
    return log_revenue_event("payment_received", {
        "client_id": client_id,
        "amount": amount,
        "payment_method": payment_method
    })

def log_time_invested(activity, hours, notes=None):
    """Log time spent on revenue activities"""
    return log_revenue_event("time_invested", {
        "activity": activity,  # prospecting, applying, building_portfolio, etc.
        "hours": hours,
        "notes": notes
    })

def log_opportunity_passed(opportunity_id, reason):
    """Log why you passed on an opportunity (learning data)"""
    return log_revenue_event("opportunity_passed", {
        "opportunity_id": opportunity_id,
        "reason": reason
    })

def get_revenue_summary():
    """Get summary of all revenue activity"""
    if not REVENUE_LOG.exists():
        return {
            "total_opportunities": 0,
            "applications_sent": 0,
            "interviews_scheduled": 0,
            "clients_closed": 0,
            "total_revenue": 0,
            "pipeline_value": 0
        }
    
    opportunities = 0
    applications = 0
    interviews = 0
    clients = 0
    revenue = 0
    pipeline = 0
    
    with open(REVENUE_LOG) as f:
        for line in f:
            try:
                event = json.loads(line.strip())
                event_type = event.get('type')
                
                if event_type == 'opportunity_found':
                    opportunities += 1
                    pipeline += event['data'].get('value', 0)
                elif event_type == 'application_sent':
                    applications += 1
                elif event_type == 'interview_scheduled':
                    interviews += 1
                elif event_type == 'client_closed':
                    clients += 1
                    revenue += event['data'].get('value', 0)
                elif event_type == 'payment_received':
                    pass  # Already counted in client_closed
            except:
                continue
    
    return {
        "total_opportunities": opportunities,
        "applications_sent": applications,
        "interviews_scheduled": interviews,
        "clients_closed": clients,
        "total_revenue": revenue,
        "pipeline_value": pipeline,
        "conversion_rate": (clients / opportunities * 100) if opportunities > 0 else 0
    }

def main():
    """CLI interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Revenue Tracker - Track path to money")
        print("\nUsage:")
        print("  revenue_tracker.py opportunity 'Upwork React job' 1500 'url'")
        print("  revenue_tracker.py application 'opp_123' 45")
        print("  revenue_tracker.py proposal 'opp_123' 1000 60")
        print("  revenue_tracker.py closed 'opp_123' 1200 '2-weeks'")
        print("  revenue_tracker.py payment 'client_123' 1200 'stripe'")
        print("  revenue_tracker.py time 'prospecting' 2.5 'Found 3 leads'")
        print("  revenue_tracker.py summary")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "summary":
        summary = get_revenue_summary()
        print(json.dumps(summary, indent=2))
    
    elif command == "opportunity":
        title = sys.argv[2] if len(sys.argv) > 2 else "Opportunity"
        value = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        url = sys.argv[4] if len(sys.argv) > 4 else None
        event = log_opportunity("manual", title, value, url)
        print(f"💰 Logged: {title} (${value})")
    
    elif command == "application":
        opp_id = sys.argv[2] if len(sys.argv) > 2 else "unknown"
        time = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        event = log_application(opp_id, time)
        print(f"📤 Application sent: {opp_id}")
    
    elif command == "proposal":
        opp_id = sys.argv[2] if len(sys.argv) > 2 else "unknown"
        rate = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        time = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        event = log_proposal(opp_id, rate, time)
        print(f"📝 Proposal sent: ${rate}")
    
    elif command == "closed":
        opp_id = sys.argv[2] if len(sys.argv) > 2 else "unknown"
        value = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        timeline = sys.argv[4] if len(sys.argv) > 4 else "TBD"
        event = log_client_closed(opp_id, value, timeline)
        print(f"🎉 CLIENT CLOSED: ${value}!")
    
    elif command == "payment":
        client_id = sys.argv[2] if len(sys.argv) > 2 else "unknown"
        amount = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        method = sys.argv[4] if len(sys.argv) > 4 else "unknown"
        event = log_payment_received(client_id, amount, method)
        print(f"💵 PAYMENT RECEIVED: ${amount}!")
    
    elif command == "time":
        activity = sys.argv[2] if len(sys.argv) > 2 else "revenue_work"
        hours = float(sys.argv[3]) if len(sys.argv) > 3 else 0
        notes = sys.argv[4] if len(sys.argv) > 4 else None
        event = log_time_invested(activity, hours, notes)
        print(f"⏱️  Time logged: {hours}h on {activity}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
