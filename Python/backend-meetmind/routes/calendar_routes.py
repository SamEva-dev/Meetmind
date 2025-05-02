# backend-meetmind/routes/calendar_routes.py

from fastapi import APIRouter
from services.calendar import get_today_events
from managers.meeting_manager import load_meetings, create_meeting
from models.meeting import Meeting, MeetingStatus
from datetime import datetime
from utils.logger_config import logger

router = APIRouter()


