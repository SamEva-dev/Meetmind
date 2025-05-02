# backend-meetmind/services/transcriber.py

import os
from utils.logger_config import logger
from utils.file_utils import get_transcript_filepath
from faster_whisper import WhisperModel

# Chargement du modèle Whisper
model = WhisperModel("base", compute_type="int8", device="cpu")

def transcribe_audio(meetingId: str, audio_path: str) -> str:
    try:
        logger.info(f"Transcription de l'audio {audio_path} pour la reunion {meetingId}")
        if not os.path.exists(audio_path):
            logger.error(f"Le fichier audio n'existe pas: {audio_path}")
            raise FileNotFoundError(f"Le fichier audio n'existe pas: {audio_path}")
        segments, _ = model.transcribe(audio_path)
        logger.info(f"Transcription en cours pour {audio_path}")
        transcript_text = "\n".join([segment.text.strip() for segment in segments])
        logger.info(f"Texte de la transcription: {transcript_text[:100]}...")  # Affiche les 100 premiers caractères
        transcript_path = get_transcript_filepath(meetingId)
        logger.info(f"Transcription path {transcript_path}")

        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript_text)

        logger.info(f"Transcription terminee pour {audio_path}")
        return transcript_path
    except Exception as e:
        logger.error(f"Erreur pendant la transcription: {e}")
        raise
