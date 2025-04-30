# backend-meetmind/services/recorder.py

import sounddevice as sd
import soundfile as sf
import threading
import queue
from datetime import datetime
from utils.file_utils import get_audio_filepath
from utils.logger_config import logger

recording_thread = None
recording_queue = queue.Queue()
recording_event = threading.Event()


def _record_worker(filename: str):
    try:
        samplerate = 44100  # Standard CD-quality
        channels = 1
        subtype = 'PCM_16'

        with sf.SoundFile(filename, mode='w', samplerate=samplerate, channels=channels, subtype=subtype) as file:
            with sd.InputStream(samplerate=samplerate, channels=channels, callback=lambda indata, frames, time, status: recording_queue.put(indata.copy())):
                logger.info(f"Recording started: {filename}")
                while not recording_event.is_set():
                    file.write(recording_queue.get())
    except Exception as e:
        logger.error(f"Erreur pendant l'enregistrement: {e}")


def start_recording(meeting_id: str) -> str:
    global recording_thread, recording_event

    filename = get_audio_filepath(meeting_id)
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
