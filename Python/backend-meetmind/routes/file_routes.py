# backend-meetmind/routes/file_routes.py

from fastapi import APIRouter, HTTPException
from managers.meeting_manager import load_meetings
from models.meeting import MeetingFile
from datetime import datetime, date

router = APIRouter()

@router.get("/files/audio")
def get_audio_files():
    """
    Retourne la liste des fichiers audio générés aujourd'hui.
    """
    return _get_files_by_type("audio")

@router.get("/files/transcript")
def get_transcript_files():
    """
    Retourne la liste des fichiers de transcription générés aujourd'hui.
    """
    return _get_files_by_type("transcript")

@router.get("/files/summary")
def get_summary_files():
    """
    Retourne la liste des fichiers de résumé générés aujourd'hui.
    """
    return _get_files_by_type("summary")


def _get_files_by_type(file_type: str):
    meetings = load_meetings()
    result = []
    today = date.today()
    for meeting in meetings:
        if file_type == "audio":
            if meeting.audio_file and meeting.end_timestamp.date() == today:
                result.append(meeting)
        else:
            for f in meeting.files:
                # Filtrer par type et date
                print(f"File: {f.file_name}, Type: {f.type}, Date: {f.date.date()}")
                
                if f.type == file_type and f.date.date() == today:
                    result.append(f)

    return result
