import sys
import os
import shutil
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestAPIEndpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Nettoie le dossier storage avant tous les tests
        if os.path.exists("storage"):
            shutil.rmtree("storage")

    @classmethod
    def tearDownClass(cls):
        # Nettoie le dossier storage après tous les tests
        if os.path.exists("storage"):
            shutil.rmtree("storage")

    def setUp(self):
        # Nettoie le dossier storage avant chaque test
        if os.path.exists("storage"):
            shutil.rmtree("storage")

    def tearDown(self):
        # Nettoie le dossier storage après chaque test
        if os.path.exists("storage"):
            shutil.rmtree("storage")

    def test_health(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_empty_meetings(self):
        response = client.get("/meetings")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    @patch("recorder.recorder.start_streaming_recording", lambda filename: None)
    @patch("recorder.recorder.stop_streaming_recording", lambda: None)
    def test_start_stop_and_delete_meeting(self):
        # Start recording
        response = client.post("/start_record")
        self.assertEqual(response.status_code, 200)
        meeting_id = response.json()["meeting_id"]
        self.assertIsInstance(meeting_id, str)

        # Vérifie que la réunion est listée en In Progress
        response = client.get("/meetings")
        self.assertEqual(response.status_code, 200)
        self.assertIn({"meeting_id": meeting_id, "status": "In Progress"}, response.json())

        # Stop recording
        response = client.post("/stop_record", json={"meeting_id": meeting_id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["meeting_id"], meeting_id)

        # Vérifie que le statut passe à Completed
        response = client.get(f"/meetings/{meeting_id}")
        self.assertEqual(response.status_code, 200)
        details = response.json()
        self.assertEqual(details["meeting_id"], meeting_id)
        self.assertEqual(details["status"], "Completed")
        self.assertIn("end_timestamp", details)

        # Suppression de la réunion
        response = client.delete(f"/meetings/{meeting_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["detail"], "Meeting deleted.")

        # Vérifie que la suppression renvoie 404
        response = client.get(f"/meetings/{meeting_id}")
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()
