import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logger_config import logger
import sounddevice as sd
import numpy as np
import wave


def record_audio(duration=5, filename="output.wav", samplerate=16000):
    """Enregistre l'audio du micro pendant X secondes."""
    try:
        logger.info(f"Démarrage de l'enregistrement pour {duration} secondes...")
        print(f"🎙️ Enregistrement pendant {duration} secondes...")

        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()

        if not os.path.exists("storage"):
            os.makedirs("storage")
            logger.info("Dossier 'storage' créé.")

        filepath = os.path.join("storage", filename)
        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16 bits = 2 octets
            wf.setframerate(samplerate)
            wf.writeframes(recording.tobytes())

        logger.info(f"Enregistrement terminé et sauvegardé sous {filepath}")
        print(f" Fichier audio sauvegardé sous : {filepath}")

    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement audio : {e}", exc_info=True)
        print(f" Erreur : {e}")
