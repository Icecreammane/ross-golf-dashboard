#!/usr/bin/env python3
"""
Google Calendar Integration for Jarvis
Read calendar events, show schedule, provide proactive alerts
"""

import os
import sys
import json
import datetime
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

WORKSPACE = Path.home() / "clawd"
CALENDAR_DIR = WORKSPACE / "calendar"
CREDENTIALS_FILE = CALENDAR_DIR / "credentials.json"
TOKEN_FILE = CALENDAR_DIR / "token.json"

# If modifying these scopes, delete token.json
SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_calendar_service():
    """Authenticate and return Google Calendar service"""
    creds = None
    
    # Load token if it exists
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    
    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    service = build('calendar', 'v3', credentials=creds)
    return service


def get_todays_events():
    """Get all events for today"""
    service = get_calendar_service()
    
    # Get start and end of today
    now = datetime.datetime.now()
    start_of_day = datetime.datetime.combine(now.date(), datetime.time.min)
    end_of_day = datetime.datetime.combine(now.date(), datetime.time.max)
    
    # Format as RFC3339 timestamp
    time_min = start_of_day.isoformat() + 'Z'
    time_max = end_of_day.isoformat() + 'Z'
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    return events


def get_upcoming_events(hours=24):
    """Get events in the next N hours"""
    service = get_calendar_service()
    
    now = datetime.datetime.utcnow()
    time_min = now.isoformat() + 'Z'
    time_max = (now + datetime.timedelta(hours=hours)).isoformat() + 'Z'
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    return events


def format_event(event):
    """Format event for display"""
    start = event['start'].get('dateTime', event['start'].get('date'))
    summary = event.get('summary', 'No title')
    
    # Parse datetime
    if 'T' in start:
        dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
        time_str = dt.strftime('%I:%M %p')
    else:
        time_str = 'All day'
    
    return f"{time_str} - {summary}"


def add_event(title, date_str, start_time, duration_hours=1):
    """
    Add an event to the calendar
    
    Args:
        title: Event title (e.g., "Volleyball")
        date_str: Date in YYYY-MM-DD format (e.g., "2026-02-13")
        start_time: Time in HH:MM format (e.g., "18:00")
        duration_hours: Event duration in hours (default 1)
    
    Returns:
        Created event object
    """
    service = get_calendar_service()
    
    # Build start and end times
    start_datetime = f"{date_str}T{start_time}:00"
    start_dt = datetime.datetime.fromisoformat(start_datetime)
    end_dt = start_dt + datetime.timedelta(hours=duration_hours)
    
    event = {
        'summary': title,
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': 'America/Chicago',
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': 'America/Chicago',
        },
    }
    
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return created_event


def main():
    """CLI for testing"""
    if len(sys.argv) > 1 and sys.argv[1] == "today":
        events = get_todays_events()
        if not events:
            print("No events today!")
        else:
            print(f"📅 Today's schedule ({len(events)} events):\n")
            for event in events:
                print(f"  • {format_event(event)}")
    
    elif len(sys.argv) > 1 and sys.argv[1] == "upcoming":
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        events = get_upcoming_events(hours)
        if not events:
            print(f"No events in the next {hours} hours")
        else:
            print(f"📅 Upcoming events ({len(events)} in next {hours}h):\n")
            for event in events:
                print(f"  • {format_event(event)}")
    
    else:
        print("Usage:")
        print("  python3 google_calendar.py today")
        print("  python3 google_calendar.py upcoming [hours]")


if __name__ == "__main__":
    main()
