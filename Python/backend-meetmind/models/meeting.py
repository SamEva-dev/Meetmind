from enum import Enum
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class MeetingStatus(str, Enum):
    UPCOMING = "UPCOMING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class MeetingFile(BaseModel):
    file_name: str
    file_path: str
    type: str  # "audio", "transcript", "summary"
    date: datetime

class Meeting(BaseModel):
    meetingId: str
    title: str
    calendar_event_id: Optional[str] = None
    created: datetime = datetime.now()
    startTimestamp: datetime
    endTimestamp: Optional[datetime] = None
    lastTimestamp: Optional[datetime] = None
    status: MeetingStatus = MeetingStatus.UPCOMING
    files: List[MeetingFile] = []
    audio_file: Optional[str] = None
    transcript_file: Optional[str] = None
    summary_file: Optional[str] = None
