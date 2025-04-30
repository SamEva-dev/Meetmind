from enum import Enum
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class MeetingStatus(str, Enum):
    UPCOMING = "A venir"
    IN_PROGRESS = "En cours"
    COMPLETED = "Termine"

class MeetingFile(BaseModel):
    file_name: str
    file_path: str
    type: str  # "audio", "transcript", "summary"
    date: datetime

class Meeting(BaseModel):
    meeting_id: str
    title: str
    calendar_event_id: Optional[str] = None  # pour mapping futur
    start_timestamp: datetime
    end_timestamp: Optional[datetime] = None
    status: MeetingStatus = MeetingStatus.UPCOMING
    files: List[MeetingFile] = []
