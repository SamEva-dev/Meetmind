# backend-meetmind/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.meeting_routes import router as meeting_router
from utils.logger_config import logger

app = FastAPI(
    title="MeetMind API",
    description="Backend de transcription et gestion des reunions",
    version="1.0.0"
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # A restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes principales
app.include_router(meeting_router)

@app.on_event("startup")
def startup_event():
    logger.info("🚀 MeetMind API demarree avec succes")

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur MeetMind API"}
