import os
import json
import datetime
import uuid
from datetime import datetime
from typing import Dict, List, Any

from logger_config import logger

from models.meeting import Meeting

class MeetingManager:
    """
    Manages meeting records by storing their metadata in a local JSON file.
    """

    def __init__(self, storageFolder: str = "storage"):
        self.storageFolder = storageFolder
        os.makedirs(self.storageFolder, exist_ok=True)
        self.meetingsPath = os.path.join(self.storageFolder, "meetings.json")
        self.mappingPath = os.path.join(self.storageFolder, "calendar_mapping.json")

        logger.debug("Initializing MeetingManager with storage folder %s", self.storageFolder)
        self._loadMeetings()
        self._loadMapping()

    def _loadMeetings(self):
        if os.path.exists(self.meetingsPath):
            with open(self.meetingsPath, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.meetings: Dict[str, Meeting] = {m['meetingId']: Meeting(**m) for m in data}
            logger.info("Loaded %d meetings from %s", len(self.meetings), self.meetingsPath)
        else:
            self.meetings: Dict[str, Meeting] = {}
            logger.info("No meetings file found, starting fresh.")

    def _saveMeetings(self):
        with open(self.meetingsPath, "w", encoding="utf-8") as f:
            json.dump([m.dict() for m in self.meetings.values()], f, ensure_ascii=False, indent=2)
        logger.info("Saved %d meetings to %s", len(self.meetings), self.meetingsPath)

    def _loadMapping(self):
        if os.path.exists(self.mappingPath):
            with open(self.mappingPath, "r", encoding="utf-8") as f:
                self.calendarMapping: Dict[str, str] = json.load(f)
            logger.info("Loaded calendar mapping for %d events", len(self.calendarMapping))
        else:
            self.calendarMapping: Dict[str, str] = {}
            logger.info("No calendar mapping file found, starting fresh.")

    def _saveMapping(self):
        with open(self.mappingPath, "w", encoding="utf-8") as f:
            json.dump(self.calendarMapping, f, ensure_ascii=False, indent=2)
        logger.info("Saved calendar mapping for %d events", len(self.calendarMapping))

    def createMeeting(self, meetingId: str, title: str, startTimestamp: str) -> Meeting:
        """
        Create a new meeting entry with given ID, title, and start timestamp.
        """
        meeting = Meeting(
            meetingId=meetingId,
            title=title,
            startTimestamp=startTimestamp,
            endTimestamp=None,
            status="upcoming",
            audioFilename=f"{title}.wav",
            transcriptFilename=f"{title}.txt",
            summaryFilename=f"{title}_summary.txt"
        )
        self.meetings[meetingId] = meeting
        self._saveMeetings()
        logger.info("Created meeting %s with title '%s'", meetingId, title)
        return meeting

    def getOrCreateMeeting(self, calendarEventId: str, title: str, startDate: str) -> str:
        """
        Retrieve existing meetingId for the calendarEventId or create a new meeting.
        """
        if calendarEventId in self.calendarMapping:
            existingId = self.calendarMapping[calendarEventId]
            logger.debug("Found existing meeting %s for calendar event %s", existingId, calendarEventId)
            return existingId

        newMeetingId = str(uuid.uuid4())
        self.createMeeting(
            meetingId=newMeetingId,
            title=title,
            startTimestamp=startDate
        )
        self.calendarMapping[calendarEventId] = newMeetingId
        self._saveMapping()
        logger.info("Mapped calendar event %s to new meeting %s", calendarEventId, newMeetingId)
        return newMeetingId

    def getMeetingById(self, meetingId: str) -> Meeting:
        meeting = self.meetings.get(meetingId)
        if meeting:
            logger.debug("Retrieved meeting %s", meetingId)
        else:
            logger.warning("Meeting %s not found", meetingId)
        return meeting

    def listMeetings(self) -> List[Meeting]:
        """
        Return a list of all meetings.
        """
        logger.debug("Listing all %d meetings", len(self.meetings))
        return list(self.meetings.values())

    def updateMeeting(self, meetingId: str, **fields: Any) -> Meeting:
        """
        Update fields of an existing meeting and return the updated meeting.
        """
        meeting = self.meetings.get(meetingId)
        if not meeting:
            logger.error("Attempt to update nonexistent meeting %s", meetingId)
            raise KeyError(f"Meeting {meetingId} not found")
        for key, value in fields.items():
            if hasattr(meeting, key):
                setattr(meeting, key, value)
                logger.debug("Updated meeting %s field %s to %s", meetingId, key, value)
        self._saveMeetings()
        logger.info("Updated meeting %s", meetingId)
        return meeting

    def deleteMeeting(self, meetingId: str) -> None:
        """
        Delete a meeting and its calendar mapping.
        """
        if meetingId in self.meetings:
            del self.meetings[meetingId]
            self._saveMeetings()
            # Clean up mapping entries
            origCount = len(self.calendarMapping)
            self.calendarMapping = {k: v for k, v in self.calendarMapping.items() if v != meetingId}
            self._saveMapping()
            logger.info("Deleted meeting %s and cleaned up mapping (%d -> %d)", meetingId, origCount, len(self.calendarMapping))
        else:
            logger.error("Attempt to delete nonexistent meeting %s", meetingId)
            raise KeyError(f"Meeting {meetingId} not found")