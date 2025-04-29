import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logger_config import logger
from faster_whisper import WhisperModel

def transcribe_audio(meetingId: str, model_size: str = "small") -> str:
    """
    Loads the Faster-Whisper model and transcribes the WAV file for the given meetingId.
    Saves the transcript to storage/<meetingId>.txt.
    """
    audio_path = os.path.join("storage", f"{meetingId}.wav")
    if not os.path.exists(audio_path):
        msg = f"Audio file not found for ID {meetingId}: {audio_path}"
        logger.error(msg)
        raise FileNotFoundError(msg)

    logger.info(f"Starting transcription for ID {meetingId} using model '{model_size}'")
    try:
        # Load (or download) the model
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, info = model.transcribe(audio_path, beam_size=5)

        # Concatenate all segment text
        transcript = "".join(segment.text for segment in segments)
        logger.info(f"Transcription finished for ID {meetingId}, audio duration: {info.duration}s")

        # Save transcript to file
        if not os.path.exists("storage"):
            os.makedirs("storage")
        text_path = os.path.join("storage", f"{meetingId}.txt")
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        logger.info(f"Transcript saved to {text_path}")

        return transcript

    except Exception as e:
        logger.error(f"Error during transcription for ID {meetingId}: {e}", exc_info=True)
        raise
