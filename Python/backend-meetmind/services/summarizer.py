# backend-meetmind/services/summarizer.py

from utils.file_utils import get_summary_filepath
from utils.logger_config import logger
from openai import OpenAI
import os

from dotenv import load_dotenv
load_dotenv()

# Initialiser le client OpenAI avec la variable d'environnement
client = OpenAI()


def summarize_transcript(meetingId: str, transcript_path: str) -> str:
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript_text = f.read()

        prompt = (
            "Voici la transcription d'une reunion. Resumez-la en mettant en evidence les decisions cles, les actions et les points discutes :\n\n"
            + transcript_text
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=800
        )

        summary_text = response.choices[0].message.content.strip()
        summary_path = get_summary_filepath(meetingId)

        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary_text)

        logger.info(f"Resume genere pour {transcript_path}")
        return summary_path
    except Exception as e:
        logger.error(f"Erreur pendant la generation du resume: {e}")
        raise
