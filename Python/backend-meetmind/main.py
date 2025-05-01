# backend-meetmind/main.py

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.meeting_routes import router as meeting_router
from routes.calendar_routes import router as calendar_router
from routes.notification_routes import router as notification_router
from routes.settings_routes import router as settings_router
from services.meeting_auto_starter import auto_start_loop
from routes.health_routes import router as health_router
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
app.include_router(health_router)
app.include_router(meeting_router)
app.include_router(calendar_router)
app.include_router(notification_router)
app.include_router(settings_router)

@app.on_event("startup")
def startup_event():
    logger.info("🚀 MeetMind API demarree avec succes")
    asyncio.create_task(auto_start_loop())

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur MeetMind API"}
