# backend-meetmind/utils/file_utils.py

from config import FILES_DIR
from datetime import datetime
from pathlib import Path


def get_audio_filepath(meetingId: str) -> str:
    path = FILES_DIR / f"{meetingId}.wav"
    return str(path)

def get_transcript_filepath(meetingId: str) -> str:
    path = FILES_DIR / f"{meetingId}_transcript.txt"
    return str(path)

def get_summary_filepath(meetingId: str) -> str:
    path = FILES_DIR / f"{meetingId}_summary.txt"
    return str(path)

def get_current_date_string() -> str:
    return datetime.now().strftime("%Y-%m-%d")
