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
    meetingId: str

class TranscriptResponse(BaseModel):
    meetingId: str
    transcript: str

class SummaryResponse(BaseModel):
    meetingId: str
  
class MeetingInfo(BaseModel):
    meetingId: str
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
    meetingId = str(uuid.uuid4())
    filename = f"{meetingId}.wav"

    logger.info(f"Initiating new streaming recording with ID: {meetingId}")

    try:
        start_streaming_recording(filename=filename)
        # Create meeting entry
        meeting_manager.create(meetingId)
    except Exception as e:
        logger.error(f"Failed to start recording for ID {meetingId}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error during start recording.")

    return {"meetingId": meetingId}

# --- stop recording ---
@app.post("/stop_record", response_model=MeetingResponse)
async def stop_record(meeting: MeetingResponse):
    logger.info(f"Stop recording request received for ID: {meeting.meetingId}")

    try:
        stop_streaming_recording()
        # Update meeting status to Completed
        meeting_manager.update_status(meeting.meetingId, "Completed")
    except Exception as e:
        logger.error(f"Failed to stop recording for ID {meeting.meetingId}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error during stop recording.")

    return {"meetingId": meeting.meetingId}

# --- transcription endpoint ---
@app.post("/transcribe", response_model=TranscriptResponse)
async def transcribe_endpoint(meeting: MeetingResponse):
    logger.info(f"Transcription request received for ID: {meeting.meetingId}")
    try:
        transcript = transcribe_audio(meeting.meetingId)
        # Update meeting status and transcript path
        transcript_path = f"storage/{meeting.meetingId}.txt"
        meeting_manager.update_status(meeting.meetingId, "Transcribed", transcript_path=transcript_path)
        logger.info(f"Transcription successful for ID: {meeting.meetingId}")
        return {"meetingId": meeting.meetingId, "transcript": transcript}
    except FileNotFoundError as fnf:
        logger.warning(str(fnf))
        raise HTTPException(status_code=404, detail=str(fnf))
    except Exception as e:
        logger.error(f"Internal error on /transcribe for ID {meeting.meetingId}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error during transcription.")

# --- summarization endpoint ---
@app.post("/summarize", response_model=SummaryResponse)
async def summarize_endpoint(meeting: MeetingResponse):
    logger.info(f"Summarization request received for ID: {meeting.meetingId}")
    try:
        summary = summarize_text(meeting.meetingId)
        # Update meeting status and summary path
        summary_path = f"storage/{meeting.meetingId}_summary.txt"
        meeting_manager.update_status(meeting.meetingId, "Summarized", summary_path=summary_path)
        logger.info(f"Summarization successful for ID: {meeting.meetingId}")
        return {"meetingId": meeting.meetingId, "summary": summary}
    except FileNotFoundError as fnf:
        logger.warning(str(fnf))
        raise HTTPException(status_code=404, detail=str(fnf))
    except Exception as e:
        logger.error(f"Internal error on /summarize for ID {meeting.meetingId}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error during summarization.")

# --- meetings endpoints ---
@app.get("/meetings", response_model=List[MeetingInfo])
async def list_meetings():
    logger.info("Listing all meetings")
    return meeting_manager.list_all()

@app.get("/meetings/{meetingId}", response_model=MeetingDetail)
async def get_meeting(meetingId: str):
    logger.info(f"Retrieving details for meeting ID: {meetingId}")
    meeting = meeting_manager.get(meetingId)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")
    return meeting

@app.delete("/meetings/{meetingId}")
async def delete_meeting(meetingId: str):
    logger.info(f"Delete request for meeting ID: {meetingId}")
    success = meeting_manager.delete(meetingId)
    if not success:
        raise HTTPException(status_code=404, detail="Meeting not found.")
    return {"detail": "Meeting deleted."}
