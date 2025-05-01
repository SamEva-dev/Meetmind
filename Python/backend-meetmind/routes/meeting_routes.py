# backend-meetmind/routes/meeting_routes.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from services.recorder import start_recording, stop_recording
from services.transcriber import transcribe_audio
from services.summarizer import summarize_transcript
from managers.meeting_manager import (
    create_meeting, update_meeting_status, add_meeting_file,
    list_meetings, get_meeting, delete_meeting, load_meetings
)
from services.settings_service import load_settings
from models.meeting import MeetingFile, MeetingStatus
from utils.file_utils import get_audio_filepath, get_transcript_filepath, get_summary_filepath
from utils.logger_config import logger
from datetime import datetime
import os

router = APIRouter()

@router.post("/start_record")
def start_record(title: str):
    meeting = create_meeting(title)
    filepath = start_recording(meeting.meeting_id)
    return {"meeting_id": meeting.meeting_id, "file": filepath}

@router.post("/stop_record")
def stop_record(meeting_id: str):
    stop_recording()
    update_meeting_status(meeting_id, MeetingStatus.COMPLETED, datetime.utcnow())

    settings = load_settings()
    auto_transcribe = settings.get("auto_transcribe", True)
    auto_summarize = settings.get("auto_summarize", True)

    result = {"message": "Recording stopped."}

    if auto_transcribe:
        audio_path = get_audio_filepath(meeting_id)
        transcript_path = transcribe_audio(meeting_id, audio_path)
        file = MeetingFile(
            file_name=os.path.basename(transcript_path),
            file_path=str(transcript_path),
            type="transcript",
            date=datetime.utcnow()
        )
        add_meeting_file(meeting_id, file)
        result["transcript_path"] = transcript_path

        if auto_summarize:
            summary_path = summarize_transcript(meeting_id, transcript_path)
            file = MeetingFile(
                file_name=os.path.basename(summary_path),
                file_path=str(summary_path),
                type="summary",
                date=datetime.utcnow()
            )
            add_meeting_file(meeting_id, file)
            result["summary_path"] = summary_path

    return result

@router.post("/meetings/stop_all")
def stop_all_meetings():
    meetings = load_meetings()
    stopped = []
    for m in meetings:
        if m.status == MeetingStatus.IN_PROGRESS:
            stop_recording()
            update_meeting_status(m.meeting_id, MeetingStatus.COMPLETED, datetime.utcnow())
            stopped.append(m.meeting_id)
    return {"message": "Reunions en cours arrete", "meetings": stopped}

@router.post("/transcribe")
def transcribe(meeting_id: str):
    audio_path = get_audio_filepath(meeting_id)
    transcript_path = transcribe_audio(meeting_id, audio_path)
    file = MeetingFile(
        file_name=os.path.basename(transcript_path),
        file_path=str(transcript_path),
        type="transcript",
        date=datetime.utcnow()
    )
    add_meeting_file(meeting_id, file)
    return {"transcript_path": transcript_path}

@router.post("/summarize")
def summarize(meeting_id: str):
    transcript_path = get_transcript_filepath(meeting_id)
    summary_path = summarize_transcript(meeting_id, transcript_path)
    file = MeetingFile(
        file_name=os.path.basename(summary_path),
        file_path=str(summary_path),
        type="summary",
        date=datetime.utcnow()
    )
    add_meeting_file(meeting_id, file)
    return {"summary_path": summary_path}

@router.get("/meetings")
def get_all_meetings():
    return list_meetings()

@router.get("/meetings/{meeting_id}")
def get_one_meeting(meeting_id: str):
    return get_meeting(meeting_id)

@router.delete("/meetings/{meeting_id}")
def delete_one_meeting(meeting_id: str):
    delete_meeting(meeting_id)
    return {"message": "Meeting deleted."}

@router.post("/meetings/{calendar_event_id}/force_start")
def force_start_meeting(calendar_event_id: str):
    meetings = load_meetings()
    existing = next((m for m in meetings if m.calendar_event_id == calendar_event_id), None)
    if not existing:
        raise HTTPException(status_code=404, detail="Aucune reunion associee a cet event Google")

    existing.status = MeetingStatus.IN_PROGRESS
    filepath = start_recording(existing.meeting_id)
    return {
        "message": "Reunion demarree manuellement",
        "meeting_id": existing.meeting_id,
        "file": filepath
    }
