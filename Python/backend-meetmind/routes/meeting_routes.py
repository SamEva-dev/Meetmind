# backend-meetmind/routes/meeting_routes.py

from fastapi import APIRouter, UploadFile, File
from services.recorder import start_recording, stop_recording
from services.transcriber import transcribe_audio
from services.summarizer import summarize_transcript
from managers.meeting_manager import (
    create_meeting, update_meeting_status, add_meeting_file,
    list_meetings, get_meeting, delete_meeting
)
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
    return {"message": "Recording stopped."}

@router.post("/transcribe")
def transcribe(meeting_id: str):
    logger.info("Préparation à la transcription %s", meeting_id)
    audio_path = get_audio_filepath(meeting_id)
    logger.info("Audio trouvé %s", audio_path)
    transcript_path = transcribe_audio(meeting_id, audio_path)
    logger.info("Transcription terminée %s", transcript_path)
    file = MeetingFile(
        file_name=os.path.basename(transcript_path),
        file_path=str(transcript_path),
        type="transcript",
        date=datetime.utcnow()
    )
    logger.info("Ajout du fichier de transcription %s", file.file_name)
    logger.info("Ajout du fichier de transcription %s", file.file_path)
    add_meeting_file(meeting_id, file)
    logger.info("Fichier de transcription ajouté %s", meeting_id)
    logger.info("Fichier de transcription ajouté %s", transcript_path)
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
