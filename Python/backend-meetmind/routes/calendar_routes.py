# backend-meetmind/routes/calendar_routes.py

from fastapi import APIRouter
from services.calendar import get_today_events
from managers.meeting_manager import load_meetings, create_meeting
from models.meeting import Meeting, MeetingStatus
from datetime import datetime
from utils.logger_config import logger

router = APIRouter()

@router.get("/meetings/today", response_model=list[Meeting])
def get_today_meetings():
    events = get_today_events()
    meetings = load_meetings()
    meeting_map = {m.calendar_event_id: m for m in meetings if m.calendar_event_id}
    today_meetings = []

    for event in events:
        event_id = event.get("id")
        title = event.get("summary", "(Sans titre)")
        start = event["start"].get("dateTime") or event["start"].get("date")
        end = event["end"].get("dateTime") or event["end"].get("date")

        start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))

        now = datetime.utcnow().replace(tzinfo=start_dt.tzinfo)

        if event_id in meeting_map:
            meeting = meeting_map[event_id]
        else:
            meeting = create_meeting(title=title, calendar_event_id=event_id)
            meeting.status = MeetingStatus.UPCOMING

        # Mettre a jour le statut dynamiquement
        if start_dt <= now <= end_dt:
            meeting.status = MeetingStatus.IN_PROGRESS
        elif now > end_dt:
            meeting.status = MeetingStatus.COMPLETED
        else:
            meeting.status = MeetingStatus.UPCOMING

        meeting.start_timestamp = start_dt
        meeting.end_timestamp = end_dt
        today_meetings.append(meeting)

    return today_meetings
