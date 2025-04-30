# backend_meetmind/calendar_service.py
# Integration Google Calendar and mapping for meetings

import os
import json
from datetime import datetime
from typing import List, Dict

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from fastapi import APIRouter, Depends

from meeting_manager import MeetingManager  # existing backend logic

# Scopes for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

router = APIRouter(prefix="/calendar", tags=["calendar"])

class CalendarService:
    def __init__(self, credentials_file: str = 'credentials.json', token_file: str = 'token.json'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.creds = None
        self._load_credentials()

    def _load_credentials(self):
        # Load saved token if exists
        if os.path.exists(self.token_file):
            data = json.load(open(self.token_file))
            self.creds = Credentials.from_authorized_user_info(data, SCOPES)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
            self.creds = flow.run_local_server(port=0)
            with open(self.token_file, 'w') as token:
                token.write(self.creds.to_json())

    def getTodaysEvents(self) -> List[Dict]:
        service = build('calendar', 'v3', credentials=self.creds)
        now = datetime.now(datetime.timezone.utc).isoformat()
        end_of_day = (datetime.now(datetime.timezone.utc).replace(hour=23, minute=59, second=59)).isoformat()

        events_result = service.events().list(
            calendarId='primary',
            timeMin=now.split('T')[0] + 'T00:00:00Z',
            timeMax=end_of_day,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        return events

# Dependency for injection
calendarService = CalendarService()

@router.get('/meetings/today')
async def get_meetings_today(meetingManager: MeetingManager = Depends()):
    events = calendarService.getTodaysEvents()
    todayMeetings = []

    for event in events:
        calendarEventId = event['id']
        title = event.get('summary', 'Untitled')
        startDate = event['start'].get('dateTime', event['start'].get('date'))
        # Check existing mapping or create new meeting
        meetingId = meetingManager.getOrCreateMeeting(calendarEventId, title, startDate)
        meeting = meetingManager.getMeetingById(meetingId)
        # Assign status: upcoming, inProgress, completed
        now = datetime.now(datetime.timezone.utc).isoformat()
        if meeting.status == 'In Progress':
            status = 'inProgress'
        elif meeting.endTimestamp and meeting.endTimestamp < now:
            status = 'completed'
        else:
            status = 'upcoming'
        todayMeetings.append({
            'meetingId': meetingId,
            'title': title,
            'startDate': startDate,
            'status': status
        })

    return todayMeetings
