# backend-meetmind/utils/notification_utils.py

import json
from datetime import datetime
from config import STORAGE_DIR
from pathlib import Path

NOTIFICATION_FILE = STORAGE_DIR / "notifications.json"

def add_notification(message: str, type: str = "info"):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "type": type,
        "message": message
    }
    
    notifications = []
    if NOTIFICATION_FILE.exists():
        with open(NOTIFICATION_FILE, "r", encoding="utf-8") as f:
            try:
                notifications = json.load(f)
            except json.JSONDecodeError:
                notifications = []

    notifications.append(entry)
    with open(NOTIFICATION_FILE, "w", encoding="utf-8") as f:
        json.dump(notifications, f, indent=2, ensure_ascii=False)
