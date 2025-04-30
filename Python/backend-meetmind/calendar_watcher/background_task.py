import asyncio
import datetime
import pytz
import httpx
from calendar_watcher.calendar_watcher import get_next_events
from logger_config import logger

CHECK_INTERVAL_SECONDS = 60  # Check calendar every 1 min
TRIGGER_BEFORE_EVENT_MINUTES = 5  # Trigger recording X minutes before event
API_BASE_URL = "http://127.0.0.1:5000"  # Local FastAPI server

triggered_events = set()  # Keep track of already triggered event titles

async def calendar_monitor():
    """
    Periodically checks the calendar for upcoming events and triggers recording once per event.
    """
    logger.info("Calendar background monitor started.")
    
    while True:
        try:
            now = datetime.datetime.now(pytz.utc)

            events = get_next_events(max_results=5)

            for start_str, summary in events:
                try:
                    event_start = datetime.datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                    event_start = event_start.replace(tzinfo=pytz.utc)  # Ensure event_start is timezone-aware
                    time_until_start = (event_start - now).total_seconds() / 60

                    event_key = f"{event_start.isoformat()}_{summary}"

                    if 0 <= time_until_start <= TRIGGER_BEFORE_EVENT_MINUTES:
                        if event_key not in triggered_events:
                            logger.info(f"Detected meeting '{summary}' starting in {time_until_start:.1f} minutes. Triggering recording...")

                            async with httpx.AsyncClient() as client:
                                response = await client.post(f"{API_BASE_URL}/start_record")
                                if response.status_code == 200:
                                    logger.info("Recording successfully started via API.")
                                    triggered_events.add(event_key)
                                else:
                                    logger.error(f"Failed to start recording. Status: {response.status_code}, Detail: {response.text}")

                            await asyncio.sleep(60)  # Wait to avoid re-triggering in the same minute
                            break  # Only trigger one event at a time
                        else:
                            logger.info(f"Meeting '{summary}' already triggered. Skipping.")

                except Exception as e:
                    logger.error(f"Error processing an event: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Calendar monitoring failed: {e}", exc_info=True)

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
        logger.info(f"Checked calendar events. Next check in {CHECK_INTERVAL_SECONDS} seconds.")
        # Sleep for the specified interval before checking again