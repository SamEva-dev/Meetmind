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
from services.calendar import get_today_events
from utils.logger_config import logger
from datetime import datetime
from utils.datetime_utils import ensure_utc_aware
import pytz
import os

router = APIRouter()

@router.post("/start_record")
def start_record(title: str):
    meeting = create_meeting(title)
    filepath = start_recording(meeting.meetingId)
    return {"meetingId": meeting.meetingId, "file": filepath}

@router.post("/stop_record")
def stop_record(meetingId: str):
    stop_recording()
    update_meeting_status(meetingId, MeetingStatus.COMPLETED, datetime.now(pytz.utc))

    settings = load_settings()
    auto_transcribe = settings.get("autoTranscribe", True)
    auto_summarize = settings.get("autoSummarize", True)
    result = {"message": "Recording stopped."}

    if auto_transcribe:
        audio_path = get_audio_filepath(meetingId)
        transcript_path = transcribe_audio(meetingId, audio_path)
        file = MeetingFile(
            file_name=os.path.basename(transcript_path),
            file_path=str(transcript_path),
            type="transcript",
            date=datetime.now
        )
        add_meeting_file(meetingId, file)
        result["transcript_path"] = transcript_path

        if auto_summarize:
            summary_path = summarize_transcript(meetingId, transcript_path)
            file = MeetingFile(
                file_name=os.path.basename(summary_path),
                file_path=str(summary_path),
                type="summary",
                date=datetime.now
            )
            add_meeting_file(meetingId, file)
            result["summary_path"] = summary_path

    return result

@router.post("/meetings/stop_all")
def stop_all_meetings():
    print("Stopping all meetings...")
    meetings = load_meetings()
    stopped = []
    for m in meetings:
        if m.status == MeetingStatus.IN_PROGRESS:
            stop_recording()
            update_meeting_status(m.meetingId, MeetingStatus.COMPLETED, datetime.now(pytz.utc))
            stopped.append(m.meetingId)
    return {"message": "Reunions en cours arrete", "meetings": stopped}

@router.post("/transcribe")
def transcribe(meetingId: str):
    print(f"Transcribing meeting {meetingId}...")
    audio_path = get_audio_filepath(meetingId)
    transcript_path = transcribe_audio(meetingId, audio_path)
    file = MeetingFile(
        file_name=os.path.basename(transcript_path),
        file_path=str(transcript_path),
        type="transcript",
        date=datetime.now
    )
    add_meeting_file(meetingId, file)
    return {"transcript_path": transcript_path}

@router.post("/summarize")
def summarize(meetingId: str):
    transcript_path = get_transcript_filepath(meetingId)
    summary_path = summarize_transcript(meetingId, transcript_path)
    file = MeetingFile(
        file_name=os.path.basename(summary_path),
        file_path=str(summary_path),
        type="summary",
        date=datetime.now
    )
    add_meeting_file(meetingId, file)
    return {"summary_path": summary_path}

@router.get("/meetings")
def get_all_meetings():
    return list_meetings()

@router.get("/meetings/{meetingId}")
def get_one_meeting(meetingId: str):
    return get_meeting(meetingId)

@router.get("/meeting/today")
def get_today_meetings():
    meetings = load_meetings()
    today = datetime.now(pytz.utc).date()
    print(f"today: {today}")
    
    # Filtrer les réunions dont le début est aujourd'hui
    result = []
    for m in meetings:
        if m.startTimestamp and ensure_utc_aware(m.startTimestamp).date() == today:
            result.append(m)
    return result

@router.delete("/meetings/{meetingId}")
def delete_one_meeting(meetingId: str):
    delete_meeting(meetingId)
    return {"message": "Meeting deleted."}

@router.post("/meetings/{calendar_event_id}/force_start")
def force_start_meeting(calendar_event_id: str):
    meetings = load_meetings()
    existing = next((m for m in meetings if m.calendar_event_id == calendar_event_id), None)
    if not existing:
        raise HTTPException(status_code=404, detail="Aucune reunion associee a cet event Google")

    existing.status = MeetingStatus.IN_PROGRESS
    filepath = start_recording(existing.meetingId)
    return {
        "message": "Reunion demarree manuellement",
        "meetingId": existing.meetingId,
        "file": filepath
    }
