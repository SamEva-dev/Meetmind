import os
import json
import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List 
import uuid

import asyncio
from calendar_watcher.background_task import calendar_monitor

from meeting_manager import MeetingManager

from logger_config import logger
from recorder.recorder import start_streaming_recording, stop_streaming_recording
from transcription.transcribe import transcribe_audio
from summarizer.summarize import summarize_text


app = FastAPI(
    title="MeetMind Backend",
    version="0.1.0",
    description="Local API for meeting recording, transcription and summarization"
)

# Initialize Meeting Manager
meeting_manager = MeetingManager()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(calendar_monitor())
    logger.info("Background calendar monitor task started at API startup.")

# --- request/response schemas ---
class MeetingResponse(BaseModel):
    meeting_id: str

class TranscriptResponse(BaseModel):
    meeting_id: str
    transcript: str

class SummaryResponse(BaseModel):
    meeting_id: str
  
class MeetingInfo(BaseModel):
    meeting_id: str
    status: str

class MeetingDetail(MeetingInfo):
    start_timestamp: str
    end_timestamp: str = None
    transcript_path: str = None
    summary_path: str = None

# --- health check ---
@app.get("/health")
async def health_check():
    logger.info("Health check requested")
    return {"status": "ok"}

# --- start recording ---
@app.post("/start_record", response_model=MeetingResponse)
async def start_record():
    meeting_id = str(uuid.uuid4())
    filename = f"{meeting_id}.wav"

    logger.info(f"Initiating new streaming recording with ID: {meeting_id}")

    try:
        start_streaming_recording(filename=filename)
        # Create meeting entry
        meeting_manager.create(meeting_id)
    except Exception as e:
        logger.error(f"Failed to start recording for ID {meeting_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error during start recording.")

    return {"meeting_id": meeting_id}

# --- stop recording ---
@app.post("/stop_record", response_model=MeetingResponse)
async def stop_record(meeting: MeetingResponse):
    logger.info(f"Stop recording request received for ID: {meeting.meeting_id}")

    try:
        stop_streaming_recording()
        # Update meeting status to Completed
        meeting_manager.update_status(meeting.meeting_id, "Completed")
    except Exception as e:
        logger.error(f"Failed to stop recording for ID {meeting.meeting_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error during stop recording.")

    return {"meeting_id": meeting.meeting_id}

# --- transcription endpoint ---
@app.post("/transcribe", response_model=TranscriptResponse)
async def transcribe_endpoint(meeting: MeetingResponse):
    logger.info(f"Transcription request received for ID: {meeting.meeting_id}")
    try:
        transcript = transcribe_audio(meeting.meeting_id)
        # Update meeting status and transcript path
        transcript_path = f"storage/{meeting.meeting_id}.txt"
        meeting_manager.update_status(meeting.meeting_id, "Transcribed", transcript_path=transcript_path)
        logger.info(f"Transcription successful for ID: {meeting.meeting_id}")
        return {"meeting_id": meeting.meeting_id, "transcript": transcript}
    except FileNotFoundError as fnf:
        logger.warning(str(fnf))
        raise HTTPException(status_code=404, detail=str(fnf))
    except Exception as e:
        logger.error(f"Internal error on /transcribe for ID {meeting.meeting_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error during transcription.")

# --- summarization endpoint ---
@app.post("/summarize", response_model=SummaryResponse)
async def summarize_endpoint(meeting: MeetingResponse):
    logger.info(f"Summarization request received for ID: {meeting.meeting_id}")
    try:
        summary = summarize_text(meeting.meeting_id)
        # Update meeting status and summary path
        summary_path = f"storage/{meeting.meeting_id}_summary.txt"
        meeting_manager.update_status(meeting.meeting_id, "Summarized", summary_path=summary_path)
        logger.info(f"Summarization successful for ID: {meeting.meeting_id}")
        return {"meeting_id": meeting.meeting_id, "summary": summary}
    except FileNotFoundError as fnf:
        logger.warning(str(fnf))
        raise HTTPException(status_code=404, detail=str(fnf))
    except Exception as e:
        logger.error(f"Internal error on /summarize for ID {meeting.meeting_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error during summarization.")

# --- meetings endpoints ---
@app.get("/meetings", response_model=List[MeetingInfo])
async def list_meetings():
    logger.info("Listing all meetings")
    return meeting_manager.list_all()

@app.get("/meetings/{meeting_id}", response_model=MeetingDetail)
async def get_meeting(meeting_id: str):
    logger.info(f"Retrieving details for meeting ID: {meeting_id}")
    meeting = meeting_manager.get(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")
    return meeting

@app.delete("/meetings/{meeting_id}")
async def delete_meeting(meeting_id: str):
    logger.info(f"Delete request for meeting ID: {meeting_id}")
    success = meeting_manager.delete(meeting_id)
    if not success:
        raise HTTPException(status_code=404, detail="Meeting not found.")
    return {"detail": "Meeting deleted."}
