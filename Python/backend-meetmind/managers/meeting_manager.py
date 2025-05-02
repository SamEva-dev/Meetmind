# backend-meetmind/managers/meeting_manager.py

import json
import uuid
from datetime import datetime
from typing import List, Optional
from models.meeting import Meeting, MeetingStatus, MeetingFile
from config import MEETINGS_FILE
from utils.logger_config import logger


def load_meetings() -> List[Meeting]:
    try:
        with open(MEETINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not data:
                return []
            return [Meeting(**item) for item in data]
    except FileNotFoundError:
        return []
    except Exception as e:
        logger.error(f"Erreur de chargement des reunions: {e}")
        return []


def save_meetings(meetings: List[Meeting]):
    try:
        if not isinstance(meetings, list):
            raise ValueError("save_meetings() attend une liste de Meeting")
        with open(MEETINGS_FILE, "w", encoding="utf-8") as f:
            f.write("[\n" + ",\n".join(m.model_dump_json(indent=2) for m in meetings) + "\n]")
        logger.info(f"Reunions sauvegardees dans {MEETINGS_FILE}")  
    except Exception as e:
        logger.error(f"Erreur de sauvegarde des reunions: {e}")



def create_meeting(title: str, calendar_event_id: Optional[str] = None) -> Meeting:
    meetings = load_meetings()
    meeting = Meeting(
        meeting_id=str(uuid.uuid4()),
        title=title,
        calendar_event_id=calendar_event_id,
        start_timestamp=datetime.now(),
        status=MeetingStatus.IN_PROGRESS,
        files=[]
    )
    logger.info(f"Nouvelle reunion meeting: {meeting} ")
    meetings.append(meeting)
    save_meetings(meetings)
    logger.info(f"Nouvelle reunion creee: {meeting.title} ({meeting.meeting_id})")
    return meeting


def update_meeting_status(meeting_id: str, status: MeetingStatus, end_timestamp: Optional[datetime] = None):
    meetings = load_meetings()
    for m in meetings:
        if m.meeting_id == meeting_id:
            m.status = status
            if end_timestamp:
                m.end_timestamp = end_timestamp
            save_meetings(meetings)
            logger.info(f"Statut mis a jour pour {meeting_id}: {status}")
            return
    logger.warning(f"Reunion non trouvee: {meeting_id}")


def add_meeting_file(meeting_id: str, file: MeetingFile):
    meetings = load_meetings()
    for m in meetings:
        if m.meeting_id == meeting_id:
            m.files.append(file)
            save_meetings(meetings)
            logger.info(f"Fichier ajoute a la reunion {meeting_id}: {file.file_name}")
            return
    logger.warning(f"Impossible d'ajouter le fichier, reunion non trouvee: {meeting_id}")


def get_meeting(meeting_id: str) -> Optional[Meeting]:
    for m in load_meetings():
        if m.meeting_id == meeting_id:
            return m
    return None


def delete_meeting(meeting_id: str):
    meetings = load_meetings()
    new_list = [m for m in meetings if m.meeting_id != meeting_id]
    save_meetings(new_list)
    logger.info(f"Reunion supprimee: {meeting_id}")


def list_meetings() -> List[Meeting]:
    return load_meetings()
