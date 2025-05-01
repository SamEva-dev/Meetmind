# backend-meetmind/routes/settings_routes.py

from fastapi import APIRouter, HTTPException
from services.settings_service import load_settings, save_settings

router = APIRouter()

@router.get("/settings")
def get_settings():
    return load_settings()

@router.put("/settings")
def update_settings(payload: dict):
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Invalid settings payload")
    save_settings(payload)
    return {"message": "Parametres mis a jour."}
