import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logger_config import logger
import sounddevice as sd
import numpy as np
import wave

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
