import json
import unittest
from pathlib import Path
from meeting_manager import MeetingManager

def test_initial_empty(tmp_path):
    # Initialize MeetingManager with a temporary storage directory
    storage_dir = tmp_path / "storage"
    manager = MeetingManager(storage_dir=str(storage_dir), filename="meetings.json")

    # The directory and JSON file should be created
    assert storage_dir.exists()
    meetings_file = storage_dir / "meetings.json"

    assert meetings_file.exists()

    # list_all should return an empty list initially
    assert manager.list_all() == []

def test_create_meeting(tmp_path):
    storage_dir = tmp_path / "storage"
    manager = MeetingManager(storage_dir=str(storage_dir), filename="meetings.json")

    # Create a new meeting
    meeting = manager.create("id1")
    assert meeting["meetingId"] == "id1"
    assert meeting["status"] == "In Progress"

    # The JSON file should contain the new meeting
    meetings_file = storage_dir / "meetings.json"
    data = json.loads(meetings_file.read_text(encoding="utf-8"))
    assert any(m["meetingId"] == "id1" for m in data["meetings"])

def test_update_status(tmp_path):
    storage_dir = tmp_path / "storage"
    manager = MeetingManager(storage_dir=str(storage_dir), filename="meetings.json")
    manager.create("id1")

    # Update the status to 'Transcribed'
    updated = manager.update_status("id1", "Transcribed", transcriptPath="storage/id1.txt")
    assert updated["status"] == "Transcribed"
    assert updated["transcriptPath"] == "storage/id1.txt"
    # endTimestamp remains None until Completed
    assert updated["endTimestamp"] is None

    # Trying to update a nonexistent meeting should return None
    assert manager.update_status("nonexistent", "Error") is None

def test_get_and_delete(tmp_path):
    storage_dir = tmp_path / "storage"
    manager = MeetingManager(storage_dir=str(storage_dir), filename="meetings.json")
    manager.create("id1")

    # Retrieve existing meeting
    meeting = manager.get("id1")
    assert meeting and meeting["meetingId"] == "id1"

    # Retrieving a nonexistent meeting returns None
    assert manager.get("not_exists") is None

    # Delete existing meeting
    assert manager.delete("id1") is True
    assert manager.get("id1") is None

    # Deleting a nonexistent meeting returns False
    assert manager.delete("id2") is False
