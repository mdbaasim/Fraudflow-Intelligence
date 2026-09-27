"""
Application Configuration and System Constants
FraudFlow Intelligence: Money-Flow & Cash-Out Intelligence
SIH Problem Statement SIH26184
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
# On Vercel serverless, SQLite DB must reside in writable /tmp
DB_PATH = Path("/tmp/fraudflow.db") if os.getenv("VERCEL") else (DATA_DIR / "fraudflow.db")
MODEL_PATH = DATA_DIR / "cashout_model.joblib"
CITIES_PATH = DATA_DIR / "indian_cities.json"

# Problem Statement & System Metadata
PROJECT_NAME = "FraudFlow Intelligence"
PROJECT_SUBTITLE = "Money-Flow & Cash-Out Intelligence"
PROBLEM_STATEMENT_ID = "SIH26184"
PROBLEM_STATEMENT_TITLE = (
    "Development of a Predictive Analytics Framework for Cybercrime Complaints "
    "to Forecast Likely Cash Withdrawal Locations in Advance."
)
VERSION = "1.0.0-poc"

# Disclaimers & Governance Notice
DISCLAIMER_TEXT = (
    "DEMONSTRATION PROTOTYPE ONLY: This system operates exclusively on synthetic transaction "
    "data and illustrative ATM points. It does not claim direct connection to NCRP, I4C, or live "
    "core banking networks. Predictions are probabilistic decision-support intelligence for "
    "investigative prioritization, not guaranteed criminal locations. The human investigator "
    "retains final decision-making authority."
)

# Scenario Types
SCENARIO_MULE_CHAIN = "mule_chain"
SCENARIO_MIXED = "mixed_uncertain"
SCENARIO_LEGITIMATE = "legitimate_emergency"

SCENARIOS = {
    SCENARIO_MULE_CHAIN: {
        "label": "High-Risk Mule Chain",
        "description": "Rapid layered fund dissipation across multiple intermediate accounts toward physical cash-out.",
        "risk_multiplier": 1.15,
        "cashout_bias": 1.20,
    },
    SCENARIO_MIXED: {
        "label": "Mixed / Uncertain Layering",
        "description": "Fragmented transactions with partial digital retention and unverified commercial entities.",
        "risk_multiplier": 1.0,
        "cashout_bias": 0.90,
    },
    SCENARIO_LEGITIMATE: {
        "label": "Legitimate Emergency Transfer",
        "description": "Urgent high-value transfer with verified personal or commercial linkage (anomaly ≠ fraud).",
        "risk_multiplier": 0.35,
        "cashout_bias": 0.20,
    },
}

# Configurable Historical Lookback Periods (Addressing Evaluator Item #4)
LOOKBACK_WINDOWS = {
    "24H": {"label": "24 Hours (Immediate Velocity)", "days": 1, "decay_weight": 1.25},
    "7D": {"label": "7 Days (Operational Cycle)", "days": 7, "decay_weight": 1.10},
    "30D": {"label": "30 Days (Mule Account Lifecycle)", "days": 30, "decay_weight": 1.00},
    "60D": {"label": "60 Days (Extended Layering Audit)", "days": 60, "decay_weight": 0.85},
    "CUSTOM": {"label": "Custom Window", "days": 14, "decay_weight": 1.00}
}
DEFAULT_LOOKBACK = "7D"

# Multi-Source Authorized Cybercrime & Financial Intelligence Feeds (Addressing Evaluator Item #1)
INTELLIGENCE_FEEDS = {
    "FEED_NCRP_ACTIVE": {
        "id": "FEED_NCRP_ACTIVE",
        "name": "NCRP Central Stream (I4C Active Incident Feed)",
        "agency": "Indian Cyber Crime Coordination Centre (I4C)",
        "protocol": "REST / Webhook v2",
        "sync_mode": "Event-Driven Micro-Batch (2-hr window)",
        "trust_score": 0.99
    },
    "FEED_FIU_STR": {
        "id": "FEED_FIU_STR",
        "name": "FIU-IND Suspicious Transaction Batch (AML / High Velocity)",
        "agency": "Financial Intelligence Unit - India",
        "protocol": "SFTP / Secure FIN-API",
        "sync_mode": "Automated Batch Sync",
        "trust_score": 0.98
    },
    "FEED_BANK_MULE_API": {
        "id": "FEED_BANK_MULE_API",
        "name": "Inter-Bank Mule Account Telemetry Switch",
        "agency": "NPCI / Scheduled Commercial Banks",
        "protocol": "ISO 20022 Financial Telemetry",
        "sync_mode": "Near Real-Time Telemetry",
        "trust_score": 0.97
    },
    "FEED_LE_COMPLAINT": {
        "id": "FEED_LE_COMPLAINT",
        "name": "Verified LE Citizen Incident Report (Station Level)",
        "agency": "State Cyber Crime Police Stations",
        "protocol": "Station Portal UI / CCTNS Ingest",
        "sync_mode": "Direct Officer Ingestion",
        "trust_score": 0.95
    }
}
DEFAULT_FEED = "FEED_NCRP_ACTIVE"

# Ingestion Source Connectors (Simulated Authorized Entities)
SIMULATED_CONNECTORS = {
    "MOCK-BANK-01": {
        "name": "State Core Banking Switch (Simulated)",
        "trust_score": 0.98,
        "protocol": "ISO 8583 / Financial API",
        "status": "ACTIVE_SIMULATED",
    },
    "MOCK-CFCFRMS-01": {
        "name": "Citizen Financial Cyber Fraud Reporting System (Simulated)",
        "trust_score": 0.99,
        "protocol": "NCRP Webhook / REST",
        "status": "ACTIVE_SIMULATED",
    },
    "MANUAL-INGEST": {
        "name": "Investigator Manual Entry",
        "trust_score": 0.90,
        "protocol": "Investigator Portal UI",
        "status": "ACTIVE",
    },
}

