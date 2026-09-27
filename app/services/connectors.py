"""
Ingestion Boundary & Mock Banking Connectors
Simulates authorized ingestion from MOCK-BANK-01 and MOCK-CFCFRMS-01.
Enforces payload hashing, idempotency, and audit trails.
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, Any, Tuple
from fastapi import HTTPException

from app.database import get_db_connection, log_audit
from app.config import SIMULATED_CONNECTORS
from app.schemas import IngestEventRequest, IngestEventResponse

logger = logging.getLogger("fraudflow.connectors")

class IngestionService:
    @staticmethod
    def ingest_financial_event(req: IngestEventRequest) -> IngestEventResponse:
        """
        Process financial transaction event through the production-style boundary.
        Validates idempotency, connector authorization, creates receipt, and inserts transaction.
        """
        # Validate connector
        connector_info = SIMULATED_CONNECTORS.get(req.source_connector)
        if not connector_info:
            raise HTTPException(
                status_code=400,
                detail=f"Unauthorized or unknown source connector: {req.source_connector}"
            )

        # Compute payload hash
        payload_repr = f"{req.external_event_id}:{req.case_id}:{req.source_account}:{req.dest_account}:{req.amount}:{req.timestamp}"
        payload_hash = hashlib.sha256(payload_repr.encode("utf-8")).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Check idempotency / duplicate event
        cursor.execute("SELECT id, status FROM event_receipts WHERE external_event_id = ?", (req.external_event_id,))
        existing = cursor.fetchone()
        if existing:
            conn.close()
            logger.warning("Duplicate transaction rejected: external_event_id=%s", req.external_event_id)
            return IngestEventResponse(
                status="DUPLICATE_IGNORED",
                receipt_id=existing["id"],
                external_event_id=req.external_event_id,
                case_id=req.case_id,
                message="Duplicate event previously processed. Idempotency enforced.",
                ingested_at=datetime.now().isoformat()
            )

        # 2. Check case exists
        cursor.execute("SELECT case_id FROM cases WHERE case_id = ?", (req.case_id,))
        case_row = cursor.fetchone()
        if not case_row:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Target case {req.case_id} does not exist.")

        now_str = datetime.now().isoformat()

        # 3. Create Event Receipt
        cursor.execute("""
            INSERT INTO event_receipts (external_event_id, source_connector, ingested_at, payload_hash, status)
            VALUES (?, ?, ?, ?, ?)
        """, (req.external_event_id, req.source_connector, now_str, payload_hash, "ACCEPTED"))
        receipt_id = cursor.lastrowid

        # 4. Insert Transaction
        cursor.execute("""
            INSERT INTO transactions (
                case_id, external_event_id, source_account, dest_account,
                amount, channel, timestamp, source_city, dest_city,
                dest_lat, dest_lng, is_terminal, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
        """, (
            req.case_id,
            req.external_event_id,
            req.source_account,
            req.dest_account,
            float(req.amount),
            req.channel,
            req.timestamp or now_str,
            req.source_city or "",
            req.dest_city or "",
            req.dest_lat,
            req.dest_lng,
            now_str
        ))

        # 5. Update case updated_at
        cursor.execute("UPDATE cases SET updated_at = ? WHERE case_id = ?", (now_str, req.case_id))

        conn.commit()
        conn.close()

        # 6. Audit Log
        log_audit(
            case_id=req.case_id,
            action="INGEST_TRANSACTION_EVENT",
            actor=req.source_connector,
            details={
                "external_event_id": req.external_event_id,
                "amount": req.amount,
                "source": req.source_account,
                "destination": req.dest_account,
                "channel": req.channel
            }
        )

        return IngestEventResponse(
            status="ACCEPTED",
            receipt_id=receipt_id,
            external_event_id=req.external_event_id,
            case_id=req.case_id,
            message=f"Event ingested successfully from {connector_info['name']}.",
            ingested_at=now_str
        )
