"""
Evidence & Explainability Engine
Produces human-readable investigative rationale ('Why this prediction?')
based on multi-signal behavioral, topological, and temporal criteria.
Ensures anomaly ≠ fraud and explains scenario impact.
"""

from typing import List, Dict, Any

class EvidenceEngine:
    @staticmethod
    def generate_evidence_items(
        features: Dict[str, Any],
        risks: Dict[str, float],
        scenario_type: str,
        terminal_city: str
    ) -> List[Dict[str, Any]]:
        evidence = []

        velocity = features.get("velocity_amount_per_min", 0.0)
        hops = features.get("num_hops", 1)
        inter_hop = features.get("inter_hop_minutes", 60.0)
        retention = features.get("amount_retention_ratio", 1.0)
        night = features.get("night_activity", 0)
        coverage = features.get("evidence_coverage", 0.75)
        amount = features.get("amount", 0.0)

        # 1. Velocity and Inter-Hop Interval
        if inter_hop <= 8.0:
            evidence.append({
                "category": "Velocity & Cadence",
                "title": f"Extreme Layering Velocity ({inter_hop:.1f} min avg interval)",
                "description": (
                    f"Rapid consecutive fund transfers averaging {inter_hop:.1f} minutes between accounts. "
                    f"Dissipation velocity reached ₹{velocity:,.0f}/min, a classic signature of automated "
                    f"or orchestrated mule hopping designed to outrun bank lien placing."
                ),
                "strength": "HIGH",
                "signal_ref": "inter_hop_interval"
            })
        elif inter_hop <= 20.0:
            evidence.append({
                "category": "Velocity & Cadence",
                "title": f"Accelerated Account Handoff ({inter_hop:.1f} min interval)",
                "description": (
                    f"Successive account transactions occur faster than typical commercial vendor cycles, "
                    f"raising suspicion of structured layering."
                ),
                "strength": "MEDIUM",
                "signal_ref": "inter_hop_interval"
            })
        else:
            evidence.append({
                "category": "Velocity & Cadence",
                "title": f"Normal Transfer Intervals ({inter_hop:.1f} min interval)",
                "description": (
                    f"Transfer timing aligns with standard manual or scheduled banking behavior, "
                    f"moderating automated panic-layering indicators."
                ),
                "strength": "LOW",
                "signal_ref": "inter_hop_interval"
            })

        # 2. Multi-Hop Topology
        if hops >= 3:
            evidence.append({
                "category": "Network Topology",
                "title": f"Multi-Tier Mule Chain ({hops} Hops Detected)",
                "description": (
                    f"Funds traversed {hops} distinct intermediate entities from initial complaint origin. "
                    f"Terminal node currently holds ~₹{amount:,.0f} with zero outward forwarding, "
                    f"indicating preparation for physical withdrawal or conversion."
                ),
                "strength": "HIGH",
                "signal_ref": "num_hops"
            })
        elif hops == 2:
            evidence.append({
                "category": "Network Topology",
                "title": "Two-Tier Transit Flow",
                "description": (
                    "Initial pass-through mule identified forwarding to a secondary beneficiary account."
                ),
                "strength": "MEDIUM",
                "signal_ref": "num_hops"
            })

        # 3. Capital Dissipation & Retention
        if retention >= 0.80:
            evidence.append({
                "category": "Capital Preservation",
                "title": f"Concentrated Fund Retention ({retention * 100:.1f}%)",
                "description": (
                    f"Over {retention * 100:.1f}% of the original defrauded amount remains intact at the terminal node, "
                    f"indicating the laundering syndicate is concentrating liquidity for high-value liquidation."
                ),
                "strength": "HIGH",
                "signal_ref": "amount_retention"
            })
        elif retention <= 0.40:
            evidence.append({
                "category": "Capital Dispersion",
                "title": f"High Dissipation / Smurfing ({retention * 100:.1f}% retained)",
                "description": (
                    f"Capital has been splintered across multiple endpoints, elevating digital tracking complexity."
                ),
                "strength": "MEDIUM",
                "signal_ref": "amount_retention"
            })

        # 4. Off-Hour / Temporal Pattern
        if night == 1:
            evidence.append({
                "category": "Temporal Behavioral Risk",
                "title": "Night / Off-Hours Operational Activity",
                "description": (
                    "Transactions occurred between 23:00 and 05:00 IST, an off-hour window commonly exploited "
                    "to capitalize on reduced manual compliance monitoring in commercial banks."
                ),
                "strength": "HIGH",
                "signal_ref": "night_activity"
            })

        # 5. Geographic Cash-Out Vector
        if risks.get("cashout_risk", 0.0) >= 60.0:
            evidence.append({
                "category": "Geospatial Vector",
                "title": f"Terminal Hub Convergence ({terminal_city})",
                "description": (
                    f"Money trail routes from complainant origin toward {terminal_city}, a high-density "
                    f"commercial transit corridor. Historical patterns indicate organized mule syndicates "
                    f"utilize high-footfall metro ATM clusters to obscure physical withdrawal."
                ),
                "strength": "HIGH",
                "signal_ref": "geo_corridor"
            })

        # 6. Scenario Interpretation & Anomaly != Fraud Guardrail
        if scenario_type == "legitimate_emergency":
            evidence.append({
                "category": "Investigative Guardrail (Anomaly ≠ Fraud)",
                "title": "Legitimate Context Filter Applied",
                "description": (
                    "High transfer amount alone was checked against known commercial and emergency patterns. "
                    "In the absence of rapid dissipation across anonymous entities, risk scores are appropriately discounted."
                ),
                "strength": "HIGH",
                "signal_ref": "anomaly_guardrail"
            })
        elif scenario_type == "mixed_uncertain":
            evidence.append({
                "category": "Investigative Ambiguity",
                "title": "Mixed Electronic & Physical Footprint",
                "description": (
                    "Transactions exhibit both digital merchant attributes and unverified intermediary accounts. "
                    "Confidence is moderated pending additional core banking audit records."
                ),
                "strength": "MEDIUM",
                "signal_ref": "mixed_scenario"
            })

        return evidence
