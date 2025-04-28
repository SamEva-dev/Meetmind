from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

from logger_config import logger
from recorder.recorder import record_audio
from transcription.transcribe import transcribe_audio
from summarizer.summarize import summarize_text


app = FastAPI(
    title="MeetMind Backend",
    version="0.1.0",
    description="Local API for meeting recording, transcription and summarization"
)

# --- request/response schemas ---
class MeetingResponse(BaseModel):
    meeting_id: str

class TranscriptResponse(BaseModel):
    meeting_id: str
    transcript: str

class SummaryResponse(BaseModel):
    meeting_id: str
    summary: str

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

    logger.info(f"Initiating new recording with ID: {meeting_id}")
    try:
        record_audio(duration=10, filename=filename)
        logger.info(f"Recording completed for ID: {meeting_id}")
    except Exception as e:
        logger.error(f"Recording failed for ID {meeting_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error occurred during recording.")

    return {"meeting_id": meeting_id}

# --- stop recording (placeholder) ---
@app.post("/stop_record", response_model=MeetingResponse)
async def stop_record(meeting: MeetingResponse):
    logger.info(f"Stop recording requested for ID: {meeting.meeting_id}")
    # TODO: implement stopping a long-running recording session
    return {"meeting_id": meeting.meeting_id}

# --- transcription endpoint ---
@app.post("/transcribe", response_model=TranscriptResponse)
async def transcribe_endpoint(meeting: MeetingResponse):
    logger.info(f"Transcription request received for ID: {meeting.meeting_id}")
    try:
        transcript = transcribe_audio(meeting.meeting_id)
        logger.info(f"Transcription successful for ID: {meeting.meeting_id}")
        return {"meeting_id": meeting.meeting_id, "transcript": transcript}
    except FileNotFoundError as fnf:
        logger.warning(str(fnf))
        raise HTTPException(status_code=404, detail=str(fnf))
    except Exception as e:
        logger.error(f"Internal error on /transcribe for ID {meeting.meeting_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error during transcription.")
    
@app.post("/summarize", response_model=SummaryResponse)
async def summarize_endpoint(meeting: MeetingResponse):
    logger.info(f"Summarization request received for ID: {meeting.meeting_id}")
    try:
        summary = summarize_text(meeting.meeting_id)
        logger.info(f"Summarization successful for ID: {meeting.meeting_id}")
        return {"meeting_id": meeting.meeting_id, "summary": summary}
    except FileNotFoundError as fnf:
        logger.warning(str(fnf))
        raise HTTPException(status_code=404, detail=str(fnf))
    except Exception as e:
        logger.error(f"Internal error on /summarize for ID {meeting.meeting_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error during summarization.")
    
# --- get full results ---
@app.get("/results/{meeting_id}")
async def get_results(meeting_id: str):
    logger.info(f"Results requested for ID: {meeting_id}")
    # TODO: implement actual retrieval of audio, transcript, and summary
    return {
        "meeting_id": meeting_id,
        "audio_path": f"storage/{meeting_id}.wav",
        "transcript": "...",
        "summary": "..."
    }
