import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logger_config import logger
from transformers import pipeline

def summarize_text(meeting_id: str, model_name: str = "facebook/bart-large-cnn") -> str:
    """
    Load the transcript text and generate a concise summary using a transformers pipeline.
    Saves summary to storage/<meeting_id>_summary.txt.
    """
    text_path = os.path.join("storage", f"{meeting_id}.txt")
    if not os.path.exists(text_path):
        msg = f"Transcript file not found for ID {meeting_id}: {text_path}"
        logger.error(msg)
        raise FileNotFoundError(msg)

    logger.info(f"Starting summarization for ID {meeting_id} with model '{model_name}'")
    try:
        # initialize summarization pipeline
        summarizer = pipeline("summarization", model=model_name, device=-1)
        
        # read transcript
        with open(text_path, "r", encoding="utf-8") as f:
            transcript = f.read()

        # generate summary (adjust max_length/min_length as needed)
        result = summarizer(transcript, max_length=150, min_length=40, do_sample=False)
        summary = result[0]["summary_text"]
        logger.info(f"Summarization completed for ID {meeting_id}")

        # save summary
        summary_path = os.path.join("storage", f"{meeting_id}_summary.txt")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary)
        logger.info(f"Summary saved to {summary_path}")

        return summary

    except Exception as e:
        logger.error(f"Error during summarization for ID {meeting_id}: {e}", exc_info=True)
        raise
