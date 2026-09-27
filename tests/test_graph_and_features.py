"""
Unit Tests for NetworkX Graph & Automatic Feature Extraction
"""

import unittest
from datetime import datetime, timedelta
from app.graph import TransactionGraphEngine
from app.features import FeatureExtractor

class TestGraphAndFeatures(unittest.TestCase):
    def setUp(self):
        self.case = {
            "case_id": "CASE-TEST-001",
            "initial_loss_amount": 500000.0,
            "evidence_coverage": 0.85,
            "complaint_datetime": "2026-09-06T10:00:00",
            "victim_city": "Dindigul",
            "scenario_type": "mule_chain"
        }
        
        t0 = datetime.fromisoformat("2026-09-06T10:00:00")
        self.transactions = [
            {
                "id": 1,
                "source_account": "ACC-VIC",
                "dest_account": "ACC-MULE-A",
                "amount": 500000.0,
                "channel": "IMPS",
                "timestamp": t0.isoformat(),
                "dest_city": "Madurai"
            },
            {
                "id": 2,
                "source_account": "ACC-MULE-A",
                "dest_account": "ACC-MULE-B",
                "amount": 470000.0,
                "channel": "NEFT",
                "timestamp": (t0 + timedelta(minutes=4)).isoformat(),
                "dest_city": "Trichy"
            },
            {
                "id": 3,
                "source_account": "ACC-MULE-B",
                "dest_account": "ACC-MULE-C",
                "amount": 440000.0,
                "channel": "IMPS",
                "timestamp": (t0 + timedelta(minutes=9)).isoformat(),
                "dest_city": "Salem"
            },
            {
                "id": 4,
                "source_account": "ACC-MULE-C",
                "dest_account": "ACC-MULE-D",
                "amount": 420000.0,
                "channel": "UPI",
                "timestamp": (t0 + timedelta(minutes=14)).isoformat(),
                "dest_city": "Chennai"
            }
        ]

    def test_graph_construction_and_terminal_node(self):
        engine = TransactionGraphEngine(self.transactions, victim_account="ACC-VIC")
        metrics = engine.compute_graph_metrics()
        
        self.assertEqual(metrics["num_nodes"], 5)
        self.assertEqual(metrics["num_edges"], 4)
        self.assertEqual(metrics["max_hops"], 4)
        
        terminals = engine.get_terminal_nodes()
        self.assertIn("ACC-MULE-D", terminals)
        
        serialized = engine.serialize_for_ui()
        self.assertEqual(len(serialized["nodes"]), 5)
        self.assertEqual(len(serialized["edges"]), 4)

    def test_feature_extraction(self):
        engine = TransactionGraphEngine(self.transactions, victim_account="ACC-VIC")
        extractor = FeatureExtractor(self.case, self.transactions, engine)
        features = extractor.extract_features()

        self.assertEqual(features["num_hops"], 4)
        self.assertEqual(features["terminal_amount"], 420000.0)
        self.assertAlmostEqual(features["amount_retention_ratio"], 420000.0 / 500000.0, places=2)
        self.assertGreater(features["velocity_amount_per_min"], 10000)
        self.assertLessEqual(features["inter_hop_minutes"], 10.0)
        
        signals = extractor.get_ui_signals(features)
        self.assertTrue(any(s["name"] == "transaction_velocity" for s in signals))
        self.assertTrue(any(s["name"] == "number_of_hops" for s in signals))

if __name__ == "__main__":
    unittest.main()
