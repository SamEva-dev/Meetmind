# backend-meetmind/services/meeting_auto_starter.py

import asyncio
from datetime import datetime, timedelta
from services.calendar import get_today_events
from managers.meeting_manager import load_meetings, save_meetings, update_meeting_status
from services.recorder import start_recording, stop_recording
from models.meeting import MeetingStatus
from routes.meeting_routes import stop_record
from utils.logger_config import logger
from utils.notification_utils import add_notification
from services.settings_service import load_settings
from models.meeting import Meeting
import pytz
import os
import uuid
import time

FALLBACK_AUTO_START = os.getenv("AUTO_START_ENABLED", "true").lower() == "true"
FALLBACK_AUTO_STOP = os.getenv("AUTO_STOP_ENABLED", "true").lower() == "true"

# Cache mémoire pour éviter les notifications répétées
last_notified_minutes = {}


def load_settings_with_fallback():
    settings = load_settings()
    return {
        "auto_start_enabled": settings.get("autoStartEnabled", FALLBACK_AUTO_START),
        "auto_stop_enabled": settings.get("autoStopEnabled", FALLBACK_AUTO_STOP),
        "pre_notify": int(settings.get("preNotifyDelay", 10)),
        "repeat_notify": int(settings.get("repeatNotifyDelay", 1)),
    }


def import_google_events_to_meetings(google_events, meetings):
    known_event_ids = {m.calendar_event_id for m in meetings if m.calendar_event_id}
    for event in google_events:
        event_id = event.get("id")
        if event_id in known_event_ids:
            continue

        title = event.get("summary", "(Sans titre)")

        tz_name = event["start"].get("timeZone")
        if tz_name:
            event_tz = pytz.timezone(tz_name)
        else:
            # fallback sur offset isoformat
            # datetime.fromisoformat(...).tzinfo contiendra un tzoffset
            dt0 = datetime.fromisoformat(event["start"]["dateTime"].replace("Z", "+00:00"))
            event_tz = dt0.tzinfo

        def parse_and_to_utc(field):
            raw = event[field].get("dateTime")
            dt_naive = datetime.fromisoformat(raw.replace("Z", "+00:00").split("+")[0])
            # on localise puis on convertit UTC
            localized = event_tz.localize(dt_naive) if not dt_naive.tzinfo else dt_naive
            return localized.astimezone(pytz.utc) 
           
        start_utc = parse_and_to_utc("start")
        end_utc   = parse_and_to_utc("end")

        #now = now.astimezone(start_dt.tzinfo)

        new_meeting = Meeting(
            meeting_id=str(uuid.uuid4()),
            title=title,
            calendar_event_id=event_id,
            start_timestamp=start_utc,
            end_timestamp=end_utc,
            status=MeetingStatus.UPCOMING,
        )
        meetings.append(new_meeting)
        logger.info(f"📅 Réunion importée automatiquement depuis Google : {title}")

    save_meetings(meetings)


def handle_pre_notification(event_id, title, delta_min, pre_notify, repeat_notify):
    already = last_notified_minutes.get(event_id)
    if already is None or abs(delta_min - already) >= repeat_notify:
        logger.info(f"🔔 Notification avant reunion : {title} ({int(delta_min)} min)")
        add_notification(f"Reunion '{title}' commence dans {int(delta_min)} min", type="pre_notify")
        last_notified_minutes[event_id] = int(delta_min)


def handle_auto_start(match, title, delta_min):
    logger.info(f"🎯 Démarrage auto : {title} ({int(delta_min)} min)")
    start_recording(match.meeting_id)
    update_meeting_status(match.meeting_id, MeetingStatus.IN_PROGRESS)
    logger.info(f"🎬 Reunion demarree automatiquement : {title}")
    add_notification(f"Reunion demarree automatiquement : {title}", type="auto_start")


def handle_auto_stop(match,  event_id, repeat_notify):
    end_utc   = ensure_utc_aware(match.end_timestamp)
    now_utc = datetime.now(pytz.utc)
    
    if end_utc - now_utc <= timedelta(minutes=1):
        already = last_notified_minutes.get(event_id)
        if already is None or abs((end_utc - now_utc).total_seconds() / 60 - already) >= repeat_notify:
            logger.info(f"⏰ Notification avant fin de reunion : {match.title}")
            add_notification(f"Reunion '{match.title}' se termine bientôt", type="pre_stop")
            last_notified_minutes[event_id] = int((end_utc - now_utc).total_seconds() / 60)
            time.sleep(60)
    print(f"Demarrage fin réunion")
    print(f"match.end_timestamp: {match.end_timestamp} now: {now_utc} end_utc: {end_utc}  delta: {end_utc - now_utc}")
    now_utc = datetime.now(pytz.utc)
    if now_utc >= end_utc:
        logger.info(f"⏹️ Fin de reunion detectee : {match.title}")
        stop_record(match.meeting_id)
        #update_meeting_status(match.meeting_id, MeetingStatus.COMPLETED, now_utc)
        add_notification(f"Reunion terminee automatiquement : {match.title}", type="auto_stop")
        logger.info(f"Reunion terminee automatiquement : {match.title}")


async def auto_start_loop():
    logger.info("⏳ Surveillance automatique des reunions activee")
    while True:
        try:
            print("auto_start_loop")
            settings = load_settings_with_fallback()
            
            meetings = load_meetings()
            google_events = get_today_events()

            import_google_events_to_meetings(google_events, meetings)
            for event in google_events:
                event_id = event.get("id")
                title = event.get("summary", "(Sans titre)")
                # start = event["start"].get("dateTime") or event["start"].get("date")
                # start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                # delta_min = (start_dt - now_utc).total_seconds() / 60

                match = next((m for m in meetings if m.calendar_event_id == event_id), None)
                if not match:
                    continue

                start_utc = ensure_utc_aware(match.start_timestamp)
                
                now_utc = datetime.now(pytz.utc)
                delta_min = (start_utc - now_utc).total_seconds() / 60

                if match.status == MeetingStatus.UPCOMING and 0 < delta_min <= settings["pre_notify"]:
                    handle_pre_notification(event_id, title, delta_min, settings["pre_notify"], settings["repeat_notify"])

                if settings["auto_start_enabled"] and 0 <= delta_min <= 1 and match.status == MeetingStatus.UPCOMING:
                    handle_auto_start(match, title, delta_min)

                if settings["auto_stop_enabled"] and match.status == MeetingStatus.IN_PROGRESS:
                    handle_auto_stop(match, event_id, settings["repeat_notify"])

        except Exception as e:
            logger.error(f"Erreur dans la surveillance automatique: {e}")

        await asyncio.sleep(60)  # vérifier chaque minute

def ensure_utc_aware(dt: datetime) -> datetime:
    """
    Si dt.n’a pas de tzinfo, on le localise en UTC.
    Sinon, on le convertit en UTC.
    """
    if dt.tzinfo is None:
        return pytz.utc.localize(dt)
    else:
        return dt.astimezone(pytz.utc)