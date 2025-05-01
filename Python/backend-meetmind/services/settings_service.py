# backend-meetmind/services/settings_service.py

import json
from config import STORAGE_DIR
from pathlib import Path

SETTINGS_FILE = STORAGE_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "auto_transcribe": True,
    "auto_summarize": True,
    "auto_start_enabled": True,
    "auto_stop_enabled": True,
    "pre_notify_delay": 10,  # minutes
    "repeat_notify_delay": 1  # minutes
}

def load_settings():
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return DEFAULT_SETTINGS.copy()
    else:
        return DEFAULT_SETTINGS.copy()

def save_settings(new_settings: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(new_settings, f, indent=2, ensure_ascii=False)
