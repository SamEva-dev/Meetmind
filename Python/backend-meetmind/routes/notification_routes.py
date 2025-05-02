# backend-meetmind/routes/notification_routes.py

from fastapi import APIRouter
from config import STORAGE_DIR
from pathlib import Path
import json

router = APIRouter()

@router.get("/notifications")
def get_notifications():
    notif_path = STORAGE_DIR / "notifications.json"
    if notif_path.exists():
        with open(notif_path, "r", encoding="utf-8") as f:
            try:
                print("Loading notifications from file...")
                data = json.load(f)
                print(data)
                if not isinstance(data, list):
                    raise ValueError("Invalid data format in notifications file.")
                return data
            except json.JSONDecodeError:
                return []
    return []

@router.delete("/notifications")
def clear_notifications():
    notif_path = STORAGE_DIR / "notifications.json"
    if notif_path.exists():
        notif_path.unlink()
    return {"message": "Notifications supprimees."}
