import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logger_config import logger
import sounddevice as sd
import numpy as np
import wave
import threading

# Global control variable
is_recording = False
recording_thread = None

def record_audio(duration=10, filename="output.wav", samplerate=16000):
    """
    Records microphone audio for the given duration (in seconds),
    and writes it to a WAV file in the storage folder.
    """
    try:
        logger.info(f"Starting audio recording for {duration} seconds...")
        print(f"🎙️ Recording for {duration} seconds...")

        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()

        if not os.path.exists("storage"):
            os.makedirs("storage")
            logger.info("Created 'storage' directory.")

        filepath = os.path.join("storage", filename)
        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16 bits = 2 bytes
            wf.setframerate(samplerate)
            wf.writeframes(recording.tobytes())

        logger.info(f"Recording finished and saved to {filepath}")
        print(f"✅ Audio file saved to: {filepath}")

    except Exception as e:
        logger.error(f"Error during audio recording: {e}", exc_info=True)
        print(f"❌ Error: {e}")

def _stream_audio(filename="output.wav", samplerate=16000):
    """
    Record audio continuously and save to a WAV file until stopped.
    """
    global is_recording

    try:
        if not os.path.exists("storage"):
            os.makedirs("storage")
            logger.info("Created 'storage' directory.")

        filepath = os.path.join("storage", filename)
        wf = wave.open(filepath, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16 bits
        wf.setframerate(samplerate)

        def callback(indata, frames, time, status):
            if status:
                logger.warning(f"Recording status: {status}")
            if is_recording:
                wf.writeframes(indata.copy())

        logger.info("Starting streaming audio recording...")
        with sd.InputStream(samplerate=samplerate, channels=1, dtype='int16', callback=callback):
            while is_recording:
                sd.sleep(100)  # sleep 100ms at each loop

        wf.close()
        logger.info(f"Streaming audio recording saved to {filepath}")

    except Exception as e:
        logger.error(f"Error during streaming audio recording: {e}", exc_info=True)

def start_streaming_recording(filename="output.wav"):
    """
    Start streaming audio recording in a background thread.
    """
    global is_recording, recording_thread
    if not is_recording:
        is_recording = True
        recording_thread = threading.Thread(target=_stream_audio, args=(filename,))
        recording_thread.start()
        logger.info("Streaming recording thread started.")
    else:
        logger.warning("Streaming recording already running.")

def stop_streaming_recording():
    """
    Stop the streaming audio recording.
    """
    global is_recording, recording_thread
    if is_recording:
        is_recording = False
        if recording_thread:
            recording_thread.join()
        logger.info("Streaming recording thread stopped.")
    else:
        logger.warning("No active streaming recording to stop.")
