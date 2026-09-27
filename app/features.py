"""
Automatic Feature Engineering Engine
Extracts behavioral, topological, temporal, and monetary features directly
from transaction events and NetworkX graph metrics without manual investigator input.
"""

from datetime import datetime
from typing import List, Dict, Any, Tuple
import logging
from app.graph import TransactionGraphEngine

logger = logging.getLogger("fraudflow.features")

def parse_iso_datetime(dt_str: str) -> datetime:
    """Parse various ISO and standard date formats gracefully."""
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        pass
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    return datetime.now()

class FeatureExtractor:
    def __init__(
        self,
        case: Dict[str, Any],
        transactions: List[Dict[str, Any]],
        graph_engine: TransactionGraphEngine
    ):
        self.case = case
        self.transactions = sorted(transactions, key=lambda x: x.get("timestamp", ""))
        self.graph_engine = graph_engine
        self.graph_metrics = graph_engine.compute_graph_metrics()

    def extract_features(self) -> Dict[str, Any]:
        """Compute complete numerical feature dictionary for model inference."""
        initial_amount = float(self.case.get("initial_loss_amount", 500000.0))
        coverage = float(self.case.get("evidence_coverage", 0.75))

        # Defaults for empty transactions
        if not self.transactions:
            complaint_dt = parse_iso_datetime(self.case.get("complaint_datetime", datetime.now().isoformat()))
            complaint_hour = complaint_dt.hour
            is_night = 1 if (complaint_hour >= 23 or complaint_hour < 5) else 0

            return {
                "amount": initial_amount,
                "velocity_amount_per_min": 0.0,
                "num_hops": 0,
                "fan_out": 0,
                "fan_in": 0,
                "in_degree": 0,
                "out_degree": 0,
                "amount_retention_ratio": 1.0,
                "complaint_hour": complaint_hour,
                "night_activity": is_night,
                "network_density": 0.0,
                "inter_hop_minutes": 60.0,
                "clustering_coeff": 0.0,
                "evidence_coverage": coverage,
                "terminal_amount": initial_amount,
                "total_flow_volume": initial_amount
            }

        # Terminal and amounts
        last_tx = self.transactions[-1]
        terminal_amount = float(last_tx["amount"])
        total_volume = sum(float(tx["amount"]) for tx in self.transactions)
        amount_ratio = min(1.0, terminal_amount / initial_amount) if initial_amount > 0 else 1.0

        # Timing and Velocity
        timestamps = [parse_iso_datetime(tx["timestamp"]) for tx in self.transactions if tx.get("timestamp")]
        if len(timestamps) >= 2:
            time_deltas_min = [
                max(0.1, (t2 - t1).total_seconds() / 60.0)
                for t1, t2 in zip(timestamps[:-1], timestamps[1:])
            ]
            inter_hop_minutes = sum(time_deltas_min) / len(time_deltas_min)
            total_duration_min = max(0.5, (timestamps[-1] - timestamps[0]).total_seconds() / 60.0)
            velocity_amount_per_min = total_volume / total_duration_min
        else:
            inter_hop_minutes = 15.0
            velocity_amount_per_min = terminal_amount / 15.0

        # Complaint hour and Night activity
        complaint_dt = parse_iso_datetime(self.case.get("complaint_datetime", datetime.now().isoformat()))
        complaint_hour = complaint_dt.hour
        night_activity = 0
        for ts in timestamps:
            if ts.hour >= 23 or ts.hour < 5:
                night_activity = 1
                break

        # Topology from NetworkX
        num_hops = self.graph_metrics.get("max_hops", len(self.transactions))
        fan_out = self.graph_metrics.get("max_fan_out", 1)
        fan_in = self.graph_metrics.get("max_fan_in", 1)
        density = self.graph_metrics.get("density", 0.0)
        clustering = self.graph_metrics.get("clustering_coeff", 0.0)
        in_degree = self.graph_metrics.get("terminal_in_degree", 1)
        out_degree = self.graph_metrics.get("terminal_out_degree", 0)

        return {
            "amount": terminal_amount,
            "velocity_amount_per_min": round(velocity_amount_per_min, 2),
            "num_hops": num_hops,
            "fan_out": fan_out,
            "fan_in": fan_in,
            "in_degree": in_degree,
            "out_degree": out_degree,
            "amount_retention_ratio": round(amount_ratio, 3),
            "complaint_hour": complaint_hour,
            "night_activity": night_activity,
            "network_density": density,
            "inter_hop_minutes": round(inter_hop_minutes, 1),
            "clustering_coeff": clustering,
            "evidence_coverage": coverage,
            "terminal_amount": terminal_amount,
            "total_flow_volume": total_volume
        }

    def get_ui_signals(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate structured signals for the UI 'Model Signals' panel."""
        velocity = features["velocity_amount_per_min"]
        vel_level = "ALERT" if velocity > 40000 else ("ELEVATED" if velocity > 10000 else "NORMAL")

        hops = features["num_hops"]
        hop_level = "ALERT" if hops >= 3 else ("ELEVATED" if hops >= 2 else "NORMAL")

        inter_hop = features["inter_hop_minutes"]
        inter_level = "ALERT" if inter_hop <= 8.0 else ("ELEVATED" if inter_hop <= 20.0 else "NORMAL")

        retention = features["amount_retention_ratio"]
        ret_level = "ALERT" if retention >= 0.75 else "NORMAL"

        night = features["night_activity"]
        night_level = "ALERT" if night == 1 else "NORMAL"

        fan_out = features["fan_out"]
        fan_level = "ELEVATED" if fan_out > 2 else "NORMAL"

        return [
            {
                "name": "transaction_velocity",
                "label": "Flow Velocity",
                "value": f"₹{velocity:,.0f} / min",
                "unit": "INR/min",
                "description": "Rate of fund dissipation across successive transit accounts.",
                "level": vel_level
            },
            {
                "name": "number_of_hops",
                "label": "Layering Depth (Hops)",
                "value": hops,
                "unit": "hops",
                "description": "Observed chain distance from victim account to active terminal node.",
                "level": hop_level
            },
            {
                "name": "inter_hop_interval",
                "label": "Inter-Hop Interval",
                "value": f"{inter_hop:.1f} min",
                "unit": "minutes",
                "description": "Average elapsed time between successive account handoffs.",
                "level": inter_level
            },
            {
                "name": "amount_retention",
                "label": "Fund Retention Ratio",
                "value": f"{retention * 100:.1f}%",
                "unit": "%",
                "description": "Proportion of initial defrauded capital remaining in active terminal flow.",
                "level": ret_level
            },
            {
                "name": "fan_out_degree",
                "label": "Max Fan-Out Degree",
                "value": fan_out,
                "unit": "branches",
                "description": "Degree of fund fragmentation across parallel mule accounts.",
                "level": fan_level
            },
            {
                "name": "night_window",
                "label": "Off-Hour / Night Window",
                "value": "Detected (23:00-05:00)" if night == 1 else "Standard Daytime",
                "unit": "temporal",
                "description": "Indicates high-risk laundering outside standard banking operational hours.",
                "level": night_level
            },
            {
                "name": "network_density",
                "label": "Graph Density",
                "value": f"{features['network_density']:.3f}",
                "unit": "index",
                "description": "Topology connectivity ratio of observed financial transaction graph.",
                "level": "NORMAL"
            }
        ]
