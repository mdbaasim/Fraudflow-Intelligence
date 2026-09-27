"""
Database layer for FraudFlow Intelligence
Uses SQLite for persistent storage of cases, transactions, audit logs, and outcomes.
Includes idempotent event ingestion and audit trail generation.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
from app.config import DB_PATH, SIMULATED_CONNECTORS

logger = logging.getLogger("fraudflow.db")

def get_db_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("PRAGMA journal_mode = WAL")
    cursor = conn.cursor()

    # Cases Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            complaint_no TEXT UNIQUE NOT NULL,
            victim_name TEXT NOT NULL,
            victim_city TEXT NOT NULL,
            victim_lat REAL NOT NULL,
            victim_lng REAL NOT NULL,
            complaint_datetime TEXT NOT NULL,
            scenario_type TEXT NOT NULL,
            evidence_coverage REAL DEFAULT 0.75,
            initial_loss_amount REAL NOT NULL,
            status TEXT DEFAULT 'OPEN',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # Transactions Table (with UNIQUE external_event_id for deduplication)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT NOT NULL,
            external_event_id TEXT UNIQUE NOT NULL,
            source_account TEXT NOT NULL,
            dest_account TEXT NOT NULL,
            amount REAL NOT NULL,
            channel TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            source_city TEXT,
            dest_city TEXT,
            dest_lat REAL,
            dest_lng REAL,
            is_terminal INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
        )
    """)

    # Audit Log Table (Investigative Governance & Chain of Custody)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT,
            action TEXT NOT NULL,
            actor TEXT NOT NULL,
            details_json TEXT,
            timestamp TEXT NOT NULL
        )
    """)

    # Data Sources Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            status TEXT NOT NULL,
            trust_score REAL NOT NULL,
            simulated_latency_ms INTEGER DEFAULT 120,
            last_sync TEXT NOT NULL
        )
    """)

    # Event Receipts (Idempotency and Ingestion Boundary)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            external_event_id TEXT UNIQUE NOT NULL,
            source_connector TEXT NOT NULL,
            ingested_at TEXT NOT NULL,
            payload_hash TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    # Case Outcomes (Human-in-the-Loop Feedback for Future Offline Retraining)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS case_outcomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT NOT NULL,
            outcome_type TEXT NOT NULL,
            confirmed_cashout_location TEXT,
            confirmed_atm_id TEXT,
            recovered_amount REAL DEFAULT 0.0,
            notes TEXT,
            recorded_by TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
        )
    """)

    # Model Versions Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS model_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT UNIQUE NOT NULL,
            model_type TEXT NOT NULL,
            trained_at TEXT NOT NULL,
            metrics_json TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        )
    """)

    # Blockchain Ledger Table (Forensic Chain of Custody & Section 65B Compliance)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blockchain_ledger (
            block_index INTEGER PRIMARY KEY,
            block_hash TEXT UNIQUE NOT NULL,
            previous_hash TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            case_id TEXT,
            officer_badge TEXT NOT NULL,
            event_type TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            payload_hash TEXT NOT NULL,
            nonce INTEGER NOT NULL,
            is_tampered INTEGER DEFAULT 0
        )
    """)

    # Populate Data Sources if empty
    cursor.execute("SELECT COUNT(*) FROM data_sources")
    if cursor.fetchone()[0] == 0:
        now = datetime.now().isoformat()
        for code, info in SIMULATED_CONNECTORS.items():
            cursor.execute("""
                INSERT INTO data_sources (source_code, name, status, trust_score, simulated_latency_ms, last_sync)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (code, info["name"], info["status"], info["trust_score"], 140, now))

    # Populate Initial Model Version record if empty
    cursor.execute("SELECT COUNT(*) FROM model_versions")
    if cursor.fetchone()[0] == 0:
        now = datetime.now().isoformat()
        metrics = {
            "accuracy": 0.894,
            "f1_score": 0.887,
            "roc_auc": 0.942,
            "estimator": "RandomForestClassifier + MultiOutputRegressor",
            "trees": 100,
            "synthetic_samples": 4500,
            "features_used": [
                "amount", "velocity_amount_per_min", "num_hops", "fan_out",
                "fan_in", "in_degree", "out_degree", "amount_retention_ratio",
                "complaint_hour", "night_activity", "network_density",
                "inter_hop_minutes", "clustering_coeff", "evidence_coverage"
            ]
        }
        cursor.execute("""
            INSERT INTO model_versions (version, model_type, trained_at, metrics_json, is_active)
            VALUES (?, ?, ?, ?, 1)
        """, ("v1.0.0-rf-synthetic", "RandomForest", now, json.dumps(metrics)))

    conn.commit()
    conn.close()
    logger.info("Database initialized successfully at %s", DB_PATH)

def log_audit(case_id: Optional[str], action: str, actor: str = "INVESTIGATOR_SYSTEM", details: Optional[Dict[str, Any]] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_log (case_id, action, actor, details_json, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (case_id, action, actor, json.dumps(details or {}), datetime.now().isoformat()))
    conn.commit()
    conn.close()
