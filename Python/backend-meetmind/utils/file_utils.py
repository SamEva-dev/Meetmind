# backend-meetmind/utils/file_utils.py

from config import FILES_DIR
from datetime import datetime
from pathlib import Path


def get_audio_filepath(meeting_id: str) -> str:
    path = FILES_DIR / f"{meeting_id}.wav"
    return str(path)

def get_transcript_filepath(meeting_id: str) -> str:
    path = FILES_DIR / f"{meeting_id}_transcript.txt"
    return str(path)

def get_summary_filepath(meeting_id: str) -> str:
    path = FILES_DIR / f"{meeting_id}_summary.txt"
    return str(path)

def get_current_date_string() -> str:
    return datetime.now().strftime("%Y-%m-%d")
