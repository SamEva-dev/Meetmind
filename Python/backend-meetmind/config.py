import os
from pathlib import Path

# Dossiers de stockage
BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"
FILES_DIR = STORAGE_DIR / "files"
LOGS_DIR = BASE_DIR / "logs"

# Création auto des dossiers s'ils n'existent pas
for directory in [STORAGE_DIR, FILES_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Fichier de persistance des réunions
MEETINGS_FILE = STORAGE_DIR / "meetings.json"

# Configuration API Google (à ajuster lors de l'intégration OAuth)
GOOGLE_CREDENTIALS_FILE = BASE_DIR / "google_credentials.json"
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
