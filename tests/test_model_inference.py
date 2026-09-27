"""
Unit Tests for Machine Learning Risk Inference
"""

import unittest
from app.model import ml_model, FEATURE_COLUMNS

class TestModelInference(unittest.TestCase):
    def test_model_loaded(self):
        self.assertIsNotNone(ml_model.model)

    def test_high_risk_mule_prediction(self):
        feature_dict = {
            "amount": 420000.0,
            "velocity_amount_per_min": 35000.0,
            "num_hops": 4,
            "fan_out": 1,
            "fan_in": 1,
            "in_degree": 1,
            "out_degree": 0,
            "amount_retention_ratio": 0.84,
            "complaint_hour": 10,
            "night_activity": 0,
            "network_density": 0.20,
            "inter_hop_minutes": 4.5,
            "clustering_coeff": 0.0,
            "evidence_coverage": 0.85
        }

        preds = ml_model.predict(feature_dict, scenario_type="mule_chain")
        self.assertIn("fraud_risk", preds)
        self.assertIn("digital_flow_risk", preds)
        self.assertIn("cashout_risk", preds)
        self.assertIn("confidence", preds)

        # High risk checks
        self.assertGreaterEqual(preds["fraud_risk"], 70.0)
        self.assertGreaterEqual(preds["cashout_risk"], 65.0)
        self.assertIn(preds["overall_level"], ["CRITICAL", "HIGH"])

    def test_legitimate_emergency_scenario_discount(self):
        feature_dict = {
            "amount": 200000.0,
            "velocity_amount_per_min": 2000.0,
            "num_hops": 1,
            "fan_out": 1,
            "fan_in": 1,
            "in_degree": 1,
            "out_degree": 0,
            "amount_retention_ratio": 1.0,
            "complaint_hour": 14,
            "night_activity": 0,
            "network_density": 0.1,
            "inter_hop_minutes": 60.0,
            "clustering_coeff": 0.0,
            "evidence_coverage": 0.90
        }

        preds_mule = ml_model.predict(feature_dict, scenario_type="mule_chain")
        preds_legit = ml_model.predict(feature_dict, scenario_type="legitimate_emergency")

        self.assertLess(preds_legit["fraud_risk"], preds_mule["fraud_risk"])
        self.assertLess(preds_legit["cashout_risk"], preds_mule["cashout_risk"])

if __name__ == "__main__":
    unittest.main()
