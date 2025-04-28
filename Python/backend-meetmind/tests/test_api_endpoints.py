import sys
# Make sure Python can find main.py and les modules du backend
sys.path.append("..")

import os
import shutil
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup_storage():
    # Nettoie le dossier storage avant et après chaque test
    if os.path.exists("storage"):
        shutil.rmtree("storage")
    yield
    if os.path.exists("storage"):
        shutil.rmtree("storage")

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_empty_meetings():
    response = client.get("/meetings")
    assert response.status_code == 200
    assert response.json() == []

def test_start_stop_and_delete_meeting(monkeypatch):
    # Stub pour éviter l'accès au micro
    monkeypatch.setattr("recorder.recorder.start_streaming_recording", lambda filename: None)
    monkeypatch.setattr("recorder.recorder.stop_streaming_recording", lambda: None)

    # Start recording
    response = client.post("/start_record")
    assert response.status_code == 200
    meeting_id = response.json()["meeting_id"]
    assert isinstance(meeting_id, str)

    # Vérifie que la réunion est listée en In Progress
    response = client.get("/meetings")
    assert response.status_code == 200
    assert {"meeting_id": meeting_id, "status": "In Progress"} in response.json()

    # Stop recording
    response = client.post("/stop_record", json={"meeting_id": meeting_id})
    assert response.status_code == 200
    assert response.json()["meeting_id"] == meeting_id

    # Vérifie que le statut passe à Completed
    response = client.get(f"/meetings/{meeting_id}")
    assert response.status_code == 200
    details = response.json()
    assert details["meeting_id"] == meeting_id
    assert details["status"] == "Completed"
    assert "end_timestamp" in details

    # Suppression de la réunion
    response = client.delete(f"/meetings/{meeting_id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "Meeting deleted."

    # Vérifie que la suppression renvoie 404
    response = client.get(f"/meetings/{meeting_id}")
    assert response.status_code == 404
