# backend-meetmind/utils/logger_config.py

import logging
from logging.handlers import TimedRotatingFileHandler
from config import LOGS_DIR
from pathlib import Path

log_file = LOGS_DIR / "meetmind.log"
logger = logging.getLogger("MeetMind")
logger.setLevel(logging.INFO)

handler = TimedRotatingFileHandler(
    filename=log_file,
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8"
)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Affiche aussi dans la console
console = logging.StreamHandler()
console.setFormatter(formatter)
logger.addHandler(console)
