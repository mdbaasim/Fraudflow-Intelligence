"""
Unit and Integration Tests for Forensic Blockchain Ledger (SIH26184)
Validates SHA-256 block hashing, Proof-of-Authority mining,
Section 65B verification, tamper detection, and freeze directives.
"""

import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.blockchain import ForensicBlockchain, ForensicBlock, blockchain_ledger

class TestForensicBlockchain(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.ledger = blockchain_ledger

    def test_genesis_block_exists(self):
        blocks = self.ledger.get_all_blocks()
        self.assertGreaterEqual(len(blocks), 1)
        genesis = blocks[0]
        self.assertEqual(genesis["block_index"], 0)
        self.assertEqual(genesis["previous_hash"], "0" * 64)
        self.assertTrue(genesis["block_hash"].startswith("00"))

    def test_chain_verification_initially_valid(self):
        # Repair first in case earlier tests tampered
        self.ledger.repair_chain()
        res = self.ledger.verify_chain()
        self.assertTrue(res["is_valid"], f"Chain should be valid: {res}")
        self.assertEqual(res["status"], "CHAIN_INTEGRITY_VERIFIED")

    def test_block_mining_and_hashing(self):
        block = self.ledger.record_event(
            case_id="TEST-CASE-BC-001",
            officer_badge="TEST-OFFICER-01",
            event_type="TEST_EVENT",
            payload={"test_key": "test_val", "amount": 100000}
        )
        self.assertIsNotNone(block.block_hash)
        self.assertTrue(block.block_hash.startswith("00"))
        self.assertEqual(block.case_id, "TEST-CASE-BC-001")

        # Check that chain is still valid with new block
        verify_res = self.ledger.verify_chain()
        self.assertTrue(verify_res["is_valid"])

    def test_tamper_detection_and_repair(self):
        blocks = self.ledger.get_all_blocks()
        target_index = blocks[-1]["block_index"]

        # 1. Simulate Tamper
        tamper_res = self.ledger.simulate_tamper(target_index)
        self.assertEqual(tamper_res["status"], "TAMPER_SIMULATED")

        # 2. Verification must detect failure
        verify_res = self.ledger.verify_chain()
        self.assertFalse(verify_res["is_valid"], "Verification must fail on tampered block!")
        self.assertEqual(verify_res["failed_at_index"], target_index)

        # 3. Repair must restore valid state
        repair_res = self.ledger.repair_chain()
        self.assertEqual(repair_res["status"], "CHAIN_RESTORED")
        verify_after_repair = self.ledger.verify_chain()
        self.assertTrue(verify_after_repair["is_valid"], "Chain must be valid after repair")

    def test_freeze_directive_minting(self):
        res = self.ledger.issue_freeze_directive(
            case_id="TEST-CASE-FREEZE",
            terminal_account="ACC-MULE-TERMINAL-99",
            target_bank="HDFC_BANK_NODAL",
            amount=350000.0,
            reason="High cash-out probability predicted.",
            officer_badge="TN-CCB-4402"
        )
        self.assertTrue(res["directive_id"].startswith("DIR-CRPC91-"))
        self.assertEqual(res["target_account"], "ACC-MULE-TERMINAL-99")
        self.assertEqual(res["freeze_amount"], 350000.0)
        self.assertIsNotNone(res["digital_signature"])

    def test_blockchain_api_endpoints(self):
        # 1. GET /api/blockchain/blocks
        resp = self.client.get("/api/blockchain/blocks")
        self.assertEqual(resp.status_code, 200)
        blocks = resp.json()
        self.assertIsInstance(blocks, list)
        self.assertGreaterEqual(len(blocks), 1)

        # 2. GET /api/blockchain/verify
        resp = self.client.get("/api/blockchain/verify")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("is_valid", data)

        # 3. POST /api/blockchain/directive
        resp = self.client.post("/api/blockchain/directive", json={
            "case_id": "TEST-CASE-API",
            "terminal_account": "ACC-MULE-API-11",
            "target_bank": "STATE_BANK_OF_INDIA",
            "amount": 250000.0,
            "reason": "Test freeze directive from API",
            "officer_badge": "TN-CCB-4402"
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn("directive_id", resp.json())

if __name__ == "__main__":
    unittest.main()
