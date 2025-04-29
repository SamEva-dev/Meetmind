import os
import json
import datetime

from logger_config import logger

class MeetingManager:
    """
    Manages meeting records by storing their metadata in a local JSON file.
    """

    def __init__(self, storage_dir="storage", filename="meetings.json"):
        # Ensure storage directory exists
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Define full path to JSON file
        self.filepath = os.path.join(self.storage_dir, filename)
        
        # Initialize the file if it doesn't exist
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump({"meetings": []}, f, indent=2)
            logger.info(f"Created new meetings store at {self.filepath}")

    def _load(self):
        """Load meetings data from JSON file."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("meetings", [])
        except Exception as e:
            logger.error(f"Failed to load meetings from {self.filepath}: {e}", exc_info=True)
            return []

    def _save(self, meetings):
        """Save meetings data to JSON file."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump({"meetings": meetings}, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save meetings to {self.filepath}: {e}", exc_info=True)

    def create(self, meetingId: str):
        """Create a new meeting entry with initial status 'In Progress'."""
        meetings = self._load()
        existing = next((m for m in meetings if m.get("meetingId") == meetingId), None)
        if existing:
            logger.warning(f"Meeting {meetingId} already exists. Skipping creation.")
            return existing

        new_meeting = {
            "meetingId": meetingId,
            "status": "In Progress",
            "startTimestamp": datetime.datetime.utcnow().isoformat() + 'Z',
            "endTimestamp": '',
            "transcriptPath": '',
            "summaryPath": ''
        }
        meetings.append(new_meeting)
        self._save(meetings)
        logger.info(f"Created meeting record: {meetingId}")
        return new_meeting

    def update_status(self, meetingId: str, status: str, **kwargs):
        """Update the status of an existing meeting and optional metadata."""
        meetings = self._load()
        for m in meetings:
            if m.get("meetingId") == meetingId:
                m["status"] = status
                # Optionally update timestamp or file paths
                if status == "Completed":
                    m["endTimestamp"] = datetime.datetime.utcnow().isoformat() + 'Z'
                if "transcriptPath" in kwargs:
                    m["transcriptPath"] = kwargs.get("transcriptPath")
                if "summaryPath" in kwargs:
                    m["summaryPath"] = kwargs.get("summaryPath")
                self._save(meetings)
                logger.info(f"Updated meeting {meetingId} to status '{status}'")
                return m
        logger.error(f"Meeting {meetingId} not found for status update.")
        return None

    def list_all(self):
        """Return a list of all meetings with basic info."""
        meetings = self._load()
        # Return only ID and status
        return [{"meetingId": m.get("meetingId"), "status": m.get("status")} for m in meetings]

    def get(self, meetingId: str):
        """Return full details of a single meeting."""
        
        meetings = self._load()
        logger.info(f"meetings: {meetings}")
        meeting = next((m for m in meetings if m.get("meetingId") == meetingId), None)
        logger.warning(f"Meeting {meetingId} ******************** found.")
        if not meeting:
            logger.warning(f"Meeting {meetingId} not found.")
        return meeting

    def delete(self, meetingId: str):
        """Delete a meeting record from the store."""
        meetings = self._load()
        filtered = [m for m in meetings if m.get("meetingId") != meetingId]
        if len(filtered) == len(meetings):
            logger.warning(f"Meeting {meetingId} not found. Nothing to delete.")
            return False
        self._save(filtered)
        logger.info(f"Deleted meeting record: {meetingId}")
        return True
