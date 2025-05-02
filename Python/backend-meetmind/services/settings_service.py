# backend-meetmind/services/settings_service.py

import json
from config import STORAGE_DIR
from pathlib import Path

SETTINGS_FILE = STORAGE_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "autoTranscribe": True,
    "autoSummarize": True,
    "autoStartEnabled": True,
    "autoStopEnabled": True,
    "preNotifyDelay": 10,  # minutes
    "repeatNotifyDelay": 1  # minutes
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
