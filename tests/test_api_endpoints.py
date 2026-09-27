"""
Integration Tests for FastAPI Endpoints
"""

import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestApiEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_check(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "HEALTHY")
        self.assertEqual(data["problem_statement"], "SIH26184")

    def test_connectors_list(self):
        res = self.client.get("/api/connectors")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(len(data), 2)
        codes = [c["source_code"] for c in data]
        self.assertIn("MOCK-BANK-01", codes)
        self.assertIn("MOCK-CFCFRMS-01", codes)

    def test_training_status(self):
        res = self.client.get("/api/training/status")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("metrics", data)
        self.assertIn("offline_retraining_policy", data)

    def test_seed_demo_case_and_analyze(self):
        # 1. Seed demo
        res_seed = self.client.post("/api/demo/seed")
        self.assertEqual(res_seed.status_code, 200)
        seed_data = res_seed.json()
        case_id = seed_data["case_id"]

        # 2. Analyze case
        res_analyze = self.client.post(f"/api/cases/{case_id}/analyze")
        self.assertEqual(res_analyze.status_code, 200)
        data = res_analyze.json()
        self.assertIn("risks", data)
        self.assertIn("cashout_summary", data)
        self.assertIn("graph", data)
        self.assertIn("ranked_zones", data)
        self.assertIn("atm_candidates", data)
        self.assertIn("signals", data)
        self.assertIn("why_prediction", data)

        # Confirm 5 nodes and 4 edges in graph
        self.assertEqual(len(data["graph"]["nodes"]), 5)
        self.assertEqual(len(data["graph"]["edges"]), 4)

    def test_idempotent_event_ingestion(self):
        import uuid
        # Seed first
        self.client.post("/api/demo/seed")
        ext_id = f"TEST-DUP-EVT-{uuid.uuid4().hex[:8]}"
        payload = {
            "source_connector": "MOCK-BANK-01",
            "external_event_id": ext_id,
            "case_id": "CASE-DIN-2026-001",
            "source_account": "ACC-MULE-D-5104",
            "dest_account": "ACC-MULE-E-9912",
            "amount": 390000.0,
            "channel": "IMPS",
            "timestamp": "2026-09-06T10:20:00",
            "source_city": "Salem",
            "dest_city": "Chennai"
        }

        # First ingestion -> ACCEPTED
        res1 = self.client.post("/api/ingest/financial-event", json=payload)
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json()["status"], "ACCEPTED")

        # Second ingestion with same external_event_id -> DUPLICATE_IGNORED
        res2 = self.client.post("/api/ingest/financial-event", json=payload)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json()["status"], "DUPLICATE_IGNORED")

    def test_officer_login(self):
        # Valid login
        res = self.client.post("/api/auth/login", json={
            "username": "officer.murthy",
            "password": "TamilNadu@2026"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["authenticated"])
        self.assertEqual(data["badge_number"], "TN-CCB-4402")

        # Invalid login
        res_bad = self.client.post("/api/auth/login", json={
            "username": "officer.murthy",
            "password": "WrongPassword"
        })
        self.assertEqual(res_bad.status_code, 401)

if __name__ == "__main__":
    unittest.main()
