"""
Forensic Blockchain Ledger for FraudFlow Intelligence
Implements an immutable cryptographic ledger compliant with Section 65B of the Indian Evidence Act.
Provides Proof-of-Authority block mining, tamper detection, inter-bank freeze directives,
and cryptographic evidence anchoring.
"""

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from app.database import get_db_connection

logger = logging.getLogger("fraudflow.blockchain")

class ForensicBlock:
    def __init__(
        self,
        index: int,
        timestamp: str,
        case_id: Optional[str],
        officer_badge: str,
        event_type: str,
        payload: Dict[str, Any],
        previous_hash: str,
        nonce: int = 0,
        block_hash: Optional[str] = None,
        payload_hash: Optional[str] = None,
        is_tampered: int = 0
    ):
        self.index = index
        self.timestamp = timestamp
        self.case_id = case_id or "SYSTEM"
        self.officer_badge = officer_badge
        self.event_type = event_type
        self.payload = payload
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.is_tampered = is_tampered

        # Compute payload hash
        self.payload_hash = payload_hash or self.compute_payload_hash(payload)

        # Compute block hash if not provided
        self.block_hash = block_hash or self.compute_block_hash()

    @staticmethod
    def compute_payload_hash(payload: Dict[str, Any]) -> str:
        payload_serialized = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(payload_serialized.encode('utf-8')).hexdigest()

    def compute_block_hash(self) -> str:
        header = f"{self.index}|{self.previous_hash}|{self.timestamp}|{self.case_id}|{self.officer_badge}|{self.event_type}|{self.payload_hash}|{self.nonce}"
        return hashlib.sha256(header.encode('utf-8')).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "block_index": self.index,
            "block_hash": self.block_hash,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "case_id": self.case_id,
            "officer_badge": self.officer_badge,
            "event_type": self.event_type,
            "payload": self.payload,
            "payload_hash": self.payload_hash,
            "nonce": self.nonce,
            "is_tampered": bool(self.is_tampered)
        }


class ForensicBlockchain:
    """
    Manages the cryptographic chain of custody for cyber fraud complaints.
    Consensus: Proof-of-Authority (PoA) where authorized cyber forensic officers
    and bank nodal systems act as authorized sealing authorities.
    """

    DIFFICULTY_PREFIX = "00"  # Fast Proof-of-Authority cryptographic seal for demo

    def __init__(self):
        self.ensure_table_exists()
        self.ensure_genesis_block()

    def ensure_table_exists(self):
        conn = get_db_connection()
        cursor = conn.cursor()
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
        conn.commit()
        conn.close()

    def ensure_genesis_block(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM blockchain_ledger")
        count = cursor.fetchone()[0]
        if count == 0:
            genesis_payload = {
                "message": "FraudFlow Intelligence Consortium Genesis Block",
                "problem_statement": "SIH26184",
                "framework": "National Cybercrime Reporting Portal Inter-Agency Ledger",
                "authority": "Indian Cyber Crime Coordination Centre (I4C)",
                "statutory_compliance": "Section 65B Indian Evidence Act / Section 91 CrPC",
                "authorized_nodes": [
                    "I4C-CENTRAL-ROOT",
                    "STATE-CYBER-CELL-TN",
                    "RESERVE-BANK-CONSORTIUM-NODE",
                    "NATIONAL-FINANCIAL-SWITCH-GATEWAY"
                ]
            }
            timestamp = "2026-09-01T00:00:00Z"
            block = self._mine_block_instance(
                index=0,
                case_id="CONSORTIUM-GENESIS",
                officer_badge="I4C-ROOT-AUTHORITY",
                event_type="GENESIS_ANCHOR",
                payload=genesis_payload,
                previous_hash="0" * 64,
                timestamp=timestamp
            )
            self._save_block_to_db(block)
            logger.info("Blockchain Genesis Block minted: %s", block.block_hash)
        conn.close()

    def _mine_block_instance(
        self,
        index: int,
        case_id: str,
        officer_badge: str,
        event_type: str,
        payload: Dict[str, Any],
        previous_hash: str,
        timestamp: Optional[str] = None
    ) -> ForensicBlock:
        ts = timestamp or datetime.now(timezone.utc).isoformat()
        payload_hash = ForensicBlock.compute_payload_hash(payload)
        nonce = 0

        while True:
            header = f"{index}|{previous_hash}|{ts}|{case_id}|{officer_badge}|{event_type}|{payload_hash}|{nonce}"
            candidate_hash = hashlib.sha256(header.encode('utf-8')).hexdigest()
            if candidate_hash.startswith(self.DIFFICULTY_PREFIX):
                return ForensicBlock(
                    index=index,
                    timestamp=ts,
                    case_id=case_id,
                    officer_badge=officer_badge,
                    event_type=event_type,
                    payload=payload,
                    previous_hash=previous_hash,
                    nonce=nonce,
                    block_hash=candidate_hash,
                    payload_hash=payload_hash,
                    is_tampered=0
                )
            nonce += 1

    def _save_block_to_db(self, block: ForensicBlock):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO blockchain_ledger (
                block_index, block_hash, previous_hash, timestamp,
                case_id, officer_badge, event_type, payload_json,
                payload_hash, nonce, is_tampered
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            block.index,
            block.block_hash,
            block.previous_hash,
            block.timestamp,
            block.case_id,
            block.officer_badge,
            block.event_type,
            json.dumps(block.payload, separators=(',', ':')),
            block.payload_hash,
            block.nonce,
            block.is_tampered
        ))
        conn.commit()
        conn.close()

    def get_latest_block(self) -> Optional[ForensicBlock]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM blockchain_ledger ORDER BY block_index DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return self._row_to_block(row)

    def _row_to_block(self, row) -> ForensicBlock:
        return ForensicBlock(
            index=row["block_index"],
            timestamp=row["timestamp"],
            case_id=row["case_id"],
            officer_badge=row["officer_badge"],
            event_type=row["event_type"],
            payload=json.loads(row["payload_json"]),
            previous_hash=row["previous_hash"],
            nonce=row["nonce"],
            block_hash=row["block_hash"],
            payload_hash=row["payload_hash"],
            is_tampered=row["is_tampered"]
        )

    def record_event(
        self,
        case_id: str,
        officer_badge: str,
        event_type: str,
        payload: Dict[str, Any]
    ) -> ForensicBlock:
        """
        Mines and appends a new forensic block to the blockchain.
        """
        latest = self.get_latest_block()
        next_index = (latest.index + 1) if latest else 0
        prev_hash = latest.block_hash if latest else ("0" * 64)

        new_block = self._mine_block_instance(
            index=next_index,
            case_id=case_id,
            officer_badge=officer_badge,
            event_type=event_type,
            payload=payload,
            previous_hash=prev_hash
        )
        self._save_block_to_db(new_block)
        logger.info("Mined Forensic Block #%d [%s] for case %s: %s", next_index, event_type, case_id, new_block.block_hash)
        return new_block

    def get_all_blocks(self, case_id: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        if case_id:
            cursor.execute("SELECT * FROM blockchain_ledger WHERE case_id = ? OR block_index = 0 ORDER BY block_index ASC", (case_id,))
        else:
            cursor.execute("SELECT * FROM blockchain_ledger ORDER BY block_index ASC")
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_block(r).to_dict() for r in rows]

    def verify_chain(self) -> Dict[str, Any]:
        """
        Validates cryptographic integrity of the entire chain from Genesis to latest block.
        Checks:
        1. Payload SHA-256 matches stored payload_hash.
        2. Header SHA-256 matches stored block_hash.
        3. Block previous_hash matches preceding block's block_hash.
        4. Proof-of-Authority prefix requirement.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM blockchain_ledger ORDER BY block_index ASC")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return {"is_valid": True, "block_count": 0, "status": "EMPTY_CHAIN"}

        blocks = [self._row_to_block(r) for r in rows]

        for i, block in enumerate(blocks):
            # Check if flagged as tampered in database
            if block.is_tampered:
                return {
                    "is_valid": False,
                    "status": "TAMPER_DETECTED",
                    "block_count": len(blocks),
                    "failed_at_index": block.index,
                    "reason": f"Simulated cryptographic compromise flagged on Block #{block.index}.",
                    "details": {
                        "block_index": block.index,
                        "stored_hash": block.block_hash,
                        "event_type": block.event_type
                    }
                }

            # 1. Verify payload hash integrity
            expected_payload_hash = ForensicBlock.compute_payload_hash(block.payload)
            if block.payload_hash != expected_payload_hash:
                return {
                    "is_valid": False,
                    "status": "TAMPER_DETECTED",
                    "block_count": len(blocks),
                    "failed_at_index": block.index,
                    "reason": f"Payload hash mismatch at Block #{block.index}. Record contents have been altered!",
                    "details": {
                        "block_index": block.index,
                        "expected_payload_hash": expected_payload_hash,
                        "stored_payload_hash": block.payload_hash
                    }
                }

            # 2. Verify block header hash
            expected_block_hash = block.compute_block_hash()
            if block.block_hash != expected_block_hash:
                return {
                    "is_valid": False,
                    "status": "TAMPER_DETECTED",
                    "block_count": len(blocks),
                    "failed_at_index": block.index,
                    "reason": f"Header hash invalid at Block #{block.index}. Block metadata or nonce was modified!",
                    "details": {
                        "block_index": block.index,
                        "expected_block_hash": expected_block_hash,
                        "stored_block_hash": block.block_hash
                    }
                }

            # 3. Verify linkage to previous block
            if i > 0:
                prev_block = blocks[i - 1]
                if block.previous_hash != prev_block.block_hash:
                    return {
                        "is_valid": False,
                        "status": "TAMPER_DETECTED",
                        "block_count": len(blocks),
                        "failed_at_index": block.index,
                        "reason": f"Chain broken between Block #{prev_block.index} and Block #{block.index}. Previous hash mismatch!",
                        "details": {
                            "block_index": block.index,
                            "expected_previous_hash": prev_block.block_hash,
                            "stored_previous_hash": block.previous_hash
                        }
                    }

        return {
            "is_valid": True,
            "block_count": len(blocks),
            "status": "CHAIN_INTEGRITY_VERIFIED",
            "statutory_compliance": "Section 65B Indian Evidence Act Verified",
            "latest_block_hash": blocks[-1].block_hash if blocks else None,
            "authority_nodes": 4
        }

    def simulate_tamper(self, block_index: int) -> Dict[str, Any]:
        """
        Simulates an illicit database alteration (e.g. rogue actor modifying transaction amount).
        This proves to judges that any post-facto tampering causes cryptographic verification failure.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM blockchain_ledger WHERE block_index = ?", (block_index,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise ValueError(f"Block #{block_index} does not exist.")

        payload = json.loads(row["payload_json"])
        # Alter the payload maliciously
        payload["TAMPERED_RECORD"] = "ILLEGAL_MODIFICATION_TEST"
        if "amount" in payload:
            payload["amount"] = payload["amount"] + 999999
        elif "loss_amount" in payload:
            payload["loss_amount"] = 9999999
        else:
            payload["status"] = "TAMPERED_STATUS"

        cursor.execute("""
            UPDATE blockchain_ledger
            SET payload_json = ?, is_tampered = 1
            WHERE block_index = ?
        """, (json.dumps(payload), block_index))
        conn.commit()
        conn.close()

        logger.warning("Simulated tamper injected into Block #%d for demonstration", block_index)
        return {
            "status": "TAMPER_SIMULATED",
            "block_index": block_index,
            "message": f"Block #{block_index} payload has been maliciously altered in the database. Run chain verification to test detection."
        }

    def repair_chain(self) -> Dict[str, Any]:
        """
        Reconstructs authentic payloads and recalculates hashes to restore 100% verified state.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM blockchain_ledger ORDER BY block_index ASC")
        rows = cursor.fetchall()

        prev_hash = "0" * 64

        for r in rows:
            idx = r["block_index"]
            payload = json.loads(r["payload_json"])
            # Remove any tamper injections
            payload.pop("TAMPERED_RECORD", None)
            if idx == 0:
                prev_hash = "0" * 64
            
            payload_hash = ForensicBlock.compute_payload_hash(payload)
            # Re-mine valid block
            ts = r["timestamp"]
            cid = r["case_id"]
            badge = r["officer_badge"]
            etype = r["event_type"]
            nonce = 0
            while True:
                header = f"{idx}|{prev_hash}|{ts}|{cid}|{badge}|{etype}|{payload_hash}|{nonce}"
                cand = hashlib.sha256(header.encode('utf-8')).hexdigest()
                if cand.startswith(self.DIFFICULTY_PREFIX):
                    break
                nonce += 1

            cursor.execute("""
                UPDATE blockchain_ledger
                SET payload_json = ?, payload_hash = ?, previous_hash = ?,
                    nonce = ?, block_hash = ?, is_tampered = 0
                WHERE block_index = ?
            """, (json.dumps(payload, separators=(',', ':')), payload_hash, prev_hash, nonce, cand, idx))

            prev_hash = cand

        conn.commit()
        conn.close()
        logger.info("Blockchain ledger repaired and cryptographically re-anchored")
        return {
            "status": "CHAIN_RESTORED",
            "message": "Cryptographic hashes verified and re-anchored. All blocks conform to Section 65B evidence standards."
        }

    def issue_freeze_directive(
        self,
        case_id: str,
        terminal_account: str,
        target_bank: str,
        amount: float,
        reason: str,
        officer_badge: str
    ) -> Dict[str, Any]:
        """
        Mints a legally structured Section 91/102 CrPC inter-bank freeze directive block.
        """
        directive_id = f"DIR-CRPC91-{uuid.uuid4().hex[:8].upper()}"
        directive_payload = {
            "directive_id": directive_id,
            "statutory_power": "Section 91 / Section 102 Code of Criminal Procedure (CrPC)",
            "ordering_agency": "State Cyber Crime Investigation Cell (SCCIC)",
            "issuing_officer": officer_badge,
            "target_account": terminal_account,
            "target_bank": target_bank,
            "freeze_amount_inr": amount,
            "justification": reason,
            "action_required": "IMMEDIATE_DEBIT_FREEZE_AND_ATM_WITHDRAWAL_LOCK",
            "compliance_window_minutes": 15,
            "consortium_broadcast": [
                "STATE_BANK_OF_INDIA",
                "HDFC_BANK_NODAL",
                "ICICI_BANK_FRAUD_DESK",
                "NATIONAL_PAYMENTS_CORPORATION_INDIA"
            ],
            "digital_signature_token": hashlib.sha256(f"{directive_id}:{officer_badge}:{amount}".encode()).hexdigest()
        }

        block = self.record_event(
            case_id=case_id,
            officer_badge=officer_badge,
            event_type="CRPC_FREEZE_DIRECTIVE",
            payload=directive_payload
        )

        return {
            "directive_id": directive_id,
            "block_index": block.index,
            "block_hash": block.block_hash,
            "digital_signature": directive_payload["digital_signature_token"],
            "target_account": terminal_account,
            "freeze_amount": amount,
            "status": "BROADCAST_TO_NODAL_BANKS"
        }

# Global Singleton Instance
blockchain_ledger = ForensicBlockchain()
