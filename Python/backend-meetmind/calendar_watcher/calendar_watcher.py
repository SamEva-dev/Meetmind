import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import datetime
import pickle
import pytz
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from logger_config import logger

# Scope to read calendar events
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_service():
    """
    Authenticate with Google Calendar and return a service client.
    """
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), 'token.pickle')

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.path.join(os.path.dirname(__file__), 'credentials.json'), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service

def get_next_events(max_results=5):
    """
    Fetch the next upcoming events from the user's primary calendar.
    """
    try:
        service = get_calendar_service()
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=max_results, singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            logger.info('No upcoming events found.')
            return []

        upcoming = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No Title')
            upcoming.append((start, summary))
            logger.info(f"Upcoming event: {start} - {summary}")

        return upcoming

    except Exception as e:
        logger.error(f"Error while fetching calendar events: {e}", exc_info=True)
        return []
