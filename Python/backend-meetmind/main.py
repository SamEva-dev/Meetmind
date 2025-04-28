from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

from logger_config import logger

from recorder.recorder import record_audio

app = FastAPI(
    title="MeetMind Backend",
    version="0.1.0",
    description="API locale pour enregistrement, transcription et résumé"
)

# --- modèles de requête/réponse ---
class MeetingResponse(BaseModel):
    meeting_id: str

class TranscriptResponse(BaseModel):
    meeting_id: str
    transcript: str

class SummaryResponse(BaseModel):
    meeting_id: str
    summary: str

# --- endpoints de base ---
@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/start_record", response_model=MeetingResponse)
async def start_record():
    meeting_id = str(uuid.uuid4())
    filename = f"{meeting_id}.wav"

    logger.info(f"Début d'un nouvel enregistrement avec ID : {meeting_id}")

    try:
        record_audio(duration=5, filename=filename)
        logger.info(f"Enregistrement terminé pour ID : {meeting_id}")
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement pour ID : {meeting_id} : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors de l'enregistrement.")

    return {"meeting_id": meeting_id}

@app.post("/stop_record", response_model=MeetingResponse)
async def stop_record(meeting: MeetingResponse):
    # TODO: arrêter l’enregistrement pour meeting.meeting_id
    return {"meeting_id": meeting.meeting_id}

@app.post("/transcribe", response_model=TranscriptResponse)
async def transcribe(meeting: MeetingResponse):
    # TODO: appeler transcription module sur le fichier audio
    transcript = ""  # placeholder
    return {"meeting_id": meeting.meeting_id, "transcript": transcript}

@app.post("/summarize", response_model=SummaryResponse)
async def summarize(meeting: MeetingResponse):
    # TODO: appeler summarizer module sur le transcript
    summary = ""  # placeholder
    return {"meeting_id": meeting.meeting_id, "summary": summary}

@app.get("/results/{meeting_id}")
async def get_results(meeting_id: str):
    # TODO: récupérer audio, transcript et résumé depuis le storage
    return {
        "meeting_id": meeting_id,
        "audio_path": f"storage/{meeting_id}.wav",
        "transcript": "...",
        "summary": "..."
    }
