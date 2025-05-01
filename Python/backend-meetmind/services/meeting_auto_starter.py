# backend-meetmind/services/meeting_auto_starter.py

import asyncio
from datetime import datetime, timedelta
from services.calendar import get_today_events
from managers.meeting_manager import load_meetings, update_meeting_status
from services.recorder import start_recording, stop_recording
from models.meeting import MeetingStatus
from utils.logger_config import logger
from utils.notification_utils import add_notification
from services.settings_service import load_settings
import pytz
import os

FALLBACK_AUTO_START = os.getenv("AUTO_START_ENABLED", "true").lower() == "true"
FALLBACK_AUTO_STOP = os.getenv("AUTO_STOP_ENABLED", "true").lower() == "true"

# Cache mémoire pour éviter les notifications répétées
last_notified_minutes = {}

async def auto_start_loop():
    logger.info("⏳ Surveillance automatique des reunions activee")
    while True:
        try:
            settings = load_settings()
            auto_start_enabled = settings.get("auto_start_enabled", FALLBACK_AUTO_START)
            auto_stop_enabled = settings.get("auto_stop_enabled", FALLBACK_AUTO_STOP)
            pre_notify = int(settings.get("pre_notify_delay", 10))
            repeat_notify = int(settings.get("repeat_notify_delay", 1))

            now = datetime.now(pytz.utc)
            meetings = load_meetings()
            google_events = get_today_events()

            for event in google_events:
                event_id = event.get("id")
                title = event.get("summary", "(Sans titre)")
                start = event["start"].get("dateTime") or event["start"].get("date")
                start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                delta_min = (start_dt - now).total_seconds() / 60

                match = next((m for m in meetings if m.calendar_event_id == event_id), None)
                if not match:
                    continue

                # 🔔 Pré-notification
                if match.status == MeetingStatus.UPCOMING and 0 < delta_min <= pre_notify:
                    already = last_notified_minutes.get(event_id)
                    if already is None or abs(delta_min - already) >= repeat_notify:
                        logger.info(f"🔔 Notification avant reunion : {title} ({int(delta_min)} min)")
                        add_notification(f"Reunion '{title}' commence dans {int(delta_min)} min", type="pre_notify")
                        last_notified_minutes[event_id] = int(delta_min)

                # 🟢 Auto start
                if auto_start_enabled and 0 <= delta_min <= 5:
                    if match.status == MeetingStatus.UPCOMING:
                        logger.info(f"🎯 Démarrage auto : {title} ({int(delta_min)} min)")
                        start_recording(match.meeting_id)
                        update_meeting_status(match.meeting_id, MeetingStatus.IN_PROGRESS)
                        logger.info(f"🎬 Reunion demarree automatiquement : {title}")
                        add_notification(f"Reunion demarree automatiquement : {title}", type="auto_start")

                # ⛔ Auto stop
                if auto_stop_enabled:
                    if match.status == MeetingStatus.IN_PROGRESS and match.end_timestamp:
                        if now >= match.end_timestamp:
                            logger.info(f"⏹️ Fin de reunion detectee : {match.title}")
                            stop_recording()
                            update_meeting_status(match.meeting_id, MeetingStatus.COMPLETED, now)
                            add_notification(f"Reunion terminee automatiquement : {match.title}", type="auto_stop")

        except Exception as e:
            logger.error(f"Erreur dans la surveillance automatique: {e}")

        await asyncio.sleep(60)  # vérifier chaque minute
