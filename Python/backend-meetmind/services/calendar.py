# backend-meetmind/services/calendar.py

from __future__ import print_function
import datetime
import os.path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config import GOOGLE_CREDENTIALS_FILE, GOOGLE_SCOPES
from utils.logger_config import logger

# Token local (cache de session Google)
TOKEN_FILE = "token.json"


def get_calendar_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, GOOGLE_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GOOGLE_CREDENTIALS_FILE, GOOGLE_SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)


def get_today_events():
    try:
        service = get_calendar_service()
        now = datetime.datetime.utcnow()
        end_of_day = now.replace(hour=23, minute=59, second=59)

        print(f"Recherche des reunions entre {now} et {end_of_day}")

        events_result = service.events().list(
            calendarId='primary',
            timeMin=now.isoformat() + 'Z',
            timeMax=end_of_day.isoformat() + 'Z',
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        logger.info(f"{len(events)} reunions recuperees depuis Google Calendar")
        return events
    except Exception as e:
        logger.error(f"Erreur lors de la recuperation des reunions Google Calendar: {e}")
        return []
