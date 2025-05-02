# backend-meetmind/services/recorder.py
import os
import sounddevice as sd
import soundfile as sf
import threading
import queue
from datetime import datetime
from utils.file_utils import get_audio_filepath
from utils.logger_config import logger
from models.meeting import MeetingStatus
from managers.meeting_manager import load_meetings, save_meetings
from services.calendar import get_today_events
from utils.datetime_utils import ensure_utc_aware

recording_thread = None
recording_queue = queue.Queue()
recording_event = threading.Event()


def _record_worker(filename: str):
    try:
        samplerate = 44100
        channels = 1
        subtype = 'PCM_16'

        with sf.SoundFile(filename, mode='w', samplerate=samplerate, channels=channels, subtype=subtype) as file:
            with sd.InputStream(samplerate=samplerate, channels=channels, callback=lambda indata, frames, time, status: recording_queue.put(indata.copy())):
                logger.info(f"Recording started: {filename}")
                while not recording_event.is_set():
                    file.write(recording_queue.get())
                logger.info("Recording stopped")
    except Exception as e:
        logger.error(f"Erreur pendant l'enregistrement: {e}")


def start_recording(meetingId: str) -> str:
    global recording_thread, recording_event
    meetings = load_meetings()
    meeting = next((m for m in meetings if m.meetingId == meetingId), None)

    if not meeting:
        logger.warning(f"Réunion non trouvée: {meetingId}")
        return ""

    filename = get_audio_filepath(meetingId)
    meeting.audio_file = os.path.basename(filename)
    #meeting.startTimestamp = datetime.now()
    meeting.status = MeetingStatus.IN_PROGRESS

    # Lier à Google Calendar si possible
    try:
        events = get_today_events()
        for event in events:
            if not meeting.calendar_event_id and event.get("id") == meeting.calendar_event_id:
                continue
            title = event.get("summary", "").strip()
            start = event["start"].get("dateTime") or event["start"].get("date")
            start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))

            if title.lower() in meeting.title.lower():
                #startTimestamp = datetime.fromisoformat(meeting.startTimestamp.replace("Z", "+00:00"))
                start_utc = ensure_utc_aware(start_dt)
                startTimestamp_utc = ensure_utc_aware(meeting.startTimestamp)
                diff = abs((start_utc - startTimestamp_utc).total_seconds())
                print(f"start_recording diff: {diff}")
                if diff <= 5 * 60:
                    meeting.calendar_event_id = event["id"]
                    logger.info(f"✅ Réunion liée à l’événement Google : {event['id']}")
                    break
    except Exception as e:
        logger.warning(f"Erreur de liaison avec Google Calendar : {e}")

    save_meetings(meetings)

    recording_event.clear()
    recording_thread = threading.Thread(target=_record_worker, args=(filename,), daemon=True)
    recording_thread.start()
    return filename


def stop_recording():
    global recording_thread, recording_event
    recording_event.set()
    if recording_thread:
        recording_thread.join()
        logger.info("Recording stopped")
