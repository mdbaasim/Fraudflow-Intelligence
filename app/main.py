"""
FraudFlow Intelligence - FastAPI Application
SIH Problem Statement SIH26184
"""

import uuid
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, Response

from app.config import (
    PROJECT_NAME, PROJECT_SUBTITLE, PROBLEM_STATEMENT_ID,
    PROBLEM_STATEMENT_TITLE, VERSION, DISCLAIMER_TEXT,
    SIMULATED_CONNECTORS, SCENARIOS, BASE_DIR,
    LOOKBACK_WINDOWS, DEFAULT_LOOKBACK, INTELLIGENCE_FEEDS, DEFAULT_FEED
)
from app.database import init_db, get_db_connection, log_audit
from app.schemas import (
    CaseCreate, CaseResponse, TransactionCreate, TransactionResponse,
    IngestEventRequest, IngestEventResponse, AnalysisResponse,
    CaseOutcomeCreate, RiskCardData, AdminLoginRequest, AdminUserResponse,
    BlockchainBlockResponse, BlockchainVerifyResponse, FreezeDirectiveRequest,
    FreezeDirectiveResponse, TamperSimulationRequest
)
from app.graph import TransactionGraphEngine
from app.features import FeatureExtractor
from app.model import ml_model, FEATURE_COLUMNS
from app.services.geo import geo_service
from app.services.evidence import EvidenceEngine
from app.services.connectors import IngestionService
from app.blockchain import blockchain_ledger

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("fraudflow.app")

# Initialize database on module load
init_db()

app = FastAPI(
    title=PROJECT_NAME,
    description=f"{PROJECT_SUBTITLE} - SIH Problem Statement {PROBLEM_STATEMENT_ID}",
    version=VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VercelPathRewriteMiddleware:
    """
    ASGI middleware ensuring Vercel serverless request rewrites
    are restored to their intended API paths (/api/cases, /api/demo/seed, etc.)
    regardless of whether Vercel routes them as /api/index.py, /cases, or /api/cases.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            headers = dict(scope.get("headers", []))
            forwarded = (
                headers.get(b"x-forwarded-uri") or 
                headers.get(b"x-matched-path") or 
                headers.get(b"x-vercel-matched-path") or
                headers.get(b"x-rewrite-url") or
                headers.get(b"x-original-uri")
            )
            if forwarded:
                target_path = forwarded.decode("utf-8", errors="ignore").split("?")[0]
                scope["path"] = target_path
                scope["raw_path"] = target_path.encode("utf-8")
                path = target_path

            # If Vercel passed path with /api/index.py prefix
            if path.startswith("/api/index.py"):
                sub = path[len("/api/index.py"):]
                if not sub or sub == "/":
                    scope["path"] = "/"
                elif not sub.startswith("/api"):
                    scope["path"] = "/api" + sub
                else:
                    scope["path"] = sub
                scope["raw_path"] = scope["path"].encode("utf-8")
            # If Vercel stripped /api (e.g., /cases, /blockchain/verify, etc.)
            elif not path.startswith("/api") and path not in [
                "/", "/styles.css", "/app.js", "/favicon.ico",
                "/docs", "/openapi.json", "/redoc",
                "/download/codebase", "/download/zip", "/download/backend", "/download/backend-txt"
            ]:
                normalized = "/api" + (path if path.startswith("/") else "/" + path)
                scope["path"] = normalized
                scope["raw_path"] = normalized.encode("utf-8")

        await self.app(scope, receive, send)

app.add_middleware(VercelPathRewriteMiddleware)

@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

STATIC_DIR = BASE_DIR / "app" / "static"

# ---------------------------------------------------------------------------
# Authorized Investigative Officers & Forensic Admin Directory
# ---------------------------------------------------------------------------

AUTHORIZED_OFFICERS = {
    "officer.murthy": {
        "password": "TamilNadu@2026",
        "officer_name": "Inspector R. Murthy",
        "badge_number": "TN-CCB-4402",
        "designation": "Senior Cyber Forensic Inspector",
        "unit": "State Cyber Crime Investigation Cell (SCCIC)",
        "permissions": ["ANALYZE_CASE", "INGEST_BANK_EVENT", "RECORD_OUTCOME", "FIELD_DISPATCH"]
    },
    "admin": {
        "password": "admin123",
        "officer_name": "DySP S. Varma",
        "badge_number": "I4C-ADM-0091",
        "designation": "Nodal Financial Fraud Administrator",
        "unit": "Cyber Financial Fraud Coordination Wing",
        "permissions": ["ALL"]
    },
    "io.cyber": {
        "password": "Cyber@2026",
        "officer_name": "Sub-Inspector K. Anitha",
        "badge_number": "TN-CYBER-8114",
        "designation": "Cyber Crime Field Investigator",
        "unit": "Dindigul Cyber Crime Police Station",
        "permissions": ["ANALYZE_CASE", "INGEST_BANK_EVENT", "RECORD_OUTCOME"]
    }
}

@app.post("/api/auth/login", response_model=AdminUserResponse)
def officer_login(req: AdminLoginRequest):
    user = AUTHORIZED_OFFICERS.get(req.username.strip().lower())
    if not user or user["password"] != req.password:
        raise HTTPException(status_code=401, detail="Invalid officer credentials or badge authorization failure.")

    token = f"AUTH-{uuid.uuid4().hex[:12].upper()}"
    log_audit(None, "OFFICER_SIGN_IN", user["badge_number"], {"designation": user["designation"]})

    return AdminUserResponse(
        authenticated=True,
        token=token,
        username=req.username,
        officer_name=user["officer_name"],
        badge_number=user["badge_number"],
        designation=user["designation"],
        unit=user["unit"],
        permissions=user["permissions"]
    )

# ---------------------------------------------------------------------------
# Core Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": PROJECT_NAME,
        "version": VERSION,
        "problem_statement": PROBLEM_STATEMENT_ID,
        "positioning": "SYNTHETIC_PROTOTYPE_DECISION_SUPPORT",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/connectors")
def get_connectors():
    """List available simulated core banking and cyber fraud reporting connectors."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM data_sources")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/api/training/status")
def get_training_status():
    """Retrieve machine learning model metadata, training accuracy, and feature set."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM model_versions WHERE is_active = 1 ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    metrics = json.loads(row["metrics_json"]) if row else {}
    return {
        "model_version": row["version"] if row else "v1.0.0-rf-synthetic",
        "model_type": row["model_type"] if row else "RandomForest",
        "trained_at": row["trained_at"] if row else "N/A",
        "metrics": metrics,
        "offline_retraining_policy": (
            "Model parameters are frozen during investigative runtime. Retraining is executed "
            "strictly offline upon validated confirmation of case outcomes."
        )
    }

@app.get("/api/config/feeds")
def get_intelligence_feeds():
    """List available multi-source intelligence feeds and configurable lookback windows."""
    return {
        "active_feed": DEFAULT_FEED,
        "feeds": INTELLIGENCE_FEEDS,
        "default_lookback": DEFAULT_LOOKBACK,
        "lookback_windows": LOOKBACK_WINDOWS,
        "architecture_mode": "Event-Driven Stream & Micro-Batch (2-hr I4C Synchronization)"
    }

@app.get("/api/models/benchmarks")
def get_model_benchmarks():
    """Retrieve comparative evaluation matrix across AI/ML models (Addressing Evaluator Item #5)."""
    return ml_model.get_model_benchmarks()

# ---------------------------------------------------------------------------
# Forensic Blockchain & Chain of Custody Endpoints (Section 65B Indian Evidence Act)
# ---------------------------------------------------------------------------

@app.get("/api/blockchain/blocks", response_model=List[BlockchainBlockResponse])
def get_blockchain_blocks(case_id: Optional[str] = None):
    """Retrieve immutable blockchain ledger blocks (full chain or filtered by case)."""
    return blockchain_ledger.get_all_blocks(case_id)

@app.get("/api/blockchain/verify", response_model=BlockchainVerifyResponse)
def verify_blockchain_integrity():
    """Verify cryptographic hash integrity and previous-hash continuity across the entire ledger."""
    return blockchain_ledger.verify_chain()

@app.post("/api/blockchain/directive", response_model=FreezeDirectiveResponse)
def issue_freeze_directive(req: FreezeDirectiveRequest):
    """Issue a cryptographically signed Section 91/102 CrPC inter-bank freeze directive."""
    result = blockchain_ledger.issue_freeze_directive(
        case_id=req.case_id,
        terminal_account=req.terminal_account,
        target_bank=req.target_bank,
        amount=req.amount,
        reason=req.reason,
        officer_badge=req.officer_badge
    )
    log_audit(req.case_id, "ISSUE_CRPC_FREEZE_DIRECTIVE", req.officer_badge, {
        "directive_id": result["directive_id"],
        "target_account": req.terminal_account,
        "amount": req.amount
    })
    return result

@app.post("/api/blockchain/simulate-tamper")
def simulate_tamper(req: TamperSimulationRequest):
    """Simulate an illicit database modification on a block to demonstrate detection capability."""
    try:
        return blockchain_ledger.simulate_tamper(req.block_index)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/blockchain/repair")
def repair_blockchain():
    """Repair and re-anchor blockchain cryptographic integrity."""
    return blockchain_ledger.repair_chain()

@app.get("/api/geo/search")
def search_geo(q: str = Query(..., min_length=1)):
    """Search Indian cities and transit coordinates for autocomplete."""
    return geo_service.search_cities(q)

@app.get("/api/cases", response_model=List[CaseResponse])
def list_cases():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, COUNT(t.id) as transaction_count
        FROM cases c
        LEFT JOIN transactions t ON c.case_id = t.case_id
        GROUP BY c.case_id
        ORDER BY c.created_at DESC
    """)
    rows = cursor.fetchall()
    if not rows:
        conn.close()
        seed_demo_case()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, COUNT(t.id) as transaction_count
            FROM cases c
            LEFT JOIN transactions t ON c.case_id = t.case_id
            GROUP BY c.case_id
            ORDER BY c.created_at DESC
        """)
        rows = cursor.fetchall()
    conn.close()
    return [
        CaseResponse(
            case_id=r["case_id"],
            complaint_no=r["complaint_no"],
            victim_name=r["victim_name"],
            victim_city=r["victim_city"],
            victim_lat=r["victim_lat"],
            victim_lng=r["victim_lng"],
            complaint_datetime=r["complaint_datetime"],
            scenario_type=r["scenario_type"],
            evidence_coverage=r["evidence_coverage"],
            initial_loss_amount=r["initial_loss_amount"],
            status=r["status"],
            transaction_count=r["transaction_count"],
            created_at=r["created_at"],
            updated_at=r["updated_at"]
        ) for r in rows
    ]

def generate_case_transactions(conn, cursor, case_id: str, victim_name: str, victim_city: str, initial_loss_amount: float, complaint_dt: Optional[str] = None):
    """Dynamically generate a coherent 4-hop money laundering chain for any case."""
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE case_id = ?", (case_id,))
    if cursor.fetchone()[0] > 0:
        return

    city_obj = geo_service.find_city(victim_city) or {
        "city": victim_city, "lat": 10.3673, "lng": 77.9803, "transit_hubs": ["Madurai", "Tiruchirappalli", "Salem", "Chennai"]
    }
    raw_hubs = city_obj.get("transit_hubs") or ["Madurai", "Tiruchirappalli", "Salem", "Chennai"]
    dest_cities = list(raw_hubs)
    default_fallbacks = ["Tiruchirappalli", "Salem", "Chennai", "Bengaluru", "Mumbai"]
    for fb in default_fallbacks:
        if len(dest_cities) >= 4:
            break
        if fb not in dest_cities and fb != city_obj["city"]:
            dest_cities.append(fb)
    while len(dest_cities) < 4:
        dest_cities.append("Chennai")

    city_code = "".join([c for c in victim_city if c.isalpha()][:3]).upper() or "VIC"
    first_name = victim_name.split()[0] if victim_name else "Complainant"
    rand_suffix = uuid.uuid4().hex[:4].upper()
    vic_acc = f"ACC-VIC-{city_code}-{rand_suffix} ({first_name})"

    now = datetime.now()
    if complaint_dt:
        try:
            now = datetime.fromisoformat(complaint_dt.replace("Z", ""))
        except Exception:
            pass

    t0 = now - timedelta(minutes=24)
    t1 = t0 + timedelta(minutes=4, seconds=30)
    t2 = t1 + timedelta(minutes=5, seconds=15)
    t3 = t2 + timedelta(minutes=4, seconds=45)

    amt0 = float(initial_loss_amount) if initial_loss_amount else 500000.0
    amt1 = round(amt0 * 0.94, 2)
    amt2 = round(amt0 * 0.88, 2)
    amt3 = round(amt0 * 0.84, 2)

    now_str = datetime.now().isoformat()

    c1 = geo_service.find_city(dest_cities[0]) or {"lat": 9.9252, "lng": 78.1198}
    c2 = geo_service.find_city(dest_cities[1]) or {"lat": 10.7905, "lng": 78.7047}
    c3 = geo_service.find_city(dest_cities[2]) or {"lat": 11.6643, "lng": 78.1460}
    c4 = geo_service.find_city(dest_cities[3]) or {"lat": 13.0827, "lng": 80.2707}

    tag_a = uuid.uuid4().hex[:4].upper()
    tag_b = uuid.uuid4().hex[:4].upper()
    tag_c = uuid.uuid4().hex[:4].upper()
    tag_d = uuid.uuid4().hex[:4].upper()

    mule_a = f"ACC-MULE-A-{tag_a}"
    mule_b = f"ACC-MULE-B-{tag_b}"
    mule_c = f"ACC-MULE-C-{tag_c}"
    mule_d = f"ACC-MULE-D-{tag_d}"

    txs = [
        (case_id, f"AUTO-EVT-{tag_a}-01", vic_acc, mule_a, amt0, "IMPS", t0.isoformat(), city_obj["city"], dest_cities[0], c1["lat"], c1["lng"], 0, now_str),
        (case_id, f"AUTO-EVT-{tag_b}-02", mule_a, mule_b, amt1, "NEFT", t1.isoformat(), dest_cities[0], dest_cities[1], c2["lat"], c2["lng"], 0, now_str),
        (case_id, f"AUTO-EVT-{tag_c}-03", mule_b, mule_c, amt2, "IMPS", t2.isoformat(), dest_cities[1], dest_cities[2], c3["lat"], c3["lng"], 0, now_str),
        (case_id, f"AUTO-EVT-{tag_d}-04", mule_c, mule_d, amt3, "UPI", t3.isoformat(), dest_cities[2], dest_cities[3], c4["lat"], c4["lng"], 1, now_str),
    ]

    for tx in txs:
        cursor.execute("""
            INSERT INTO transactions (
                case_id, external_event_id, source_account, dest_account,
                amount, channel, timestamp, source_city, dest_city,
                dest_lat, dest_lng, is_terminal, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tx)
    conn.commit()

@app.post("/api/cases", response_model=CaseResponse)
def create_case(case_in: CaseCreate):
    case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"
    complaint_no = case_in.complaint_no or f"NCRP-2026-{uuid.uuid4().hex[:6].upper()}"
    
    city_data = geo_service.find_city(case_in.victim_city) or {
        "city": case_in.victim_city,
        "lat": 10.3673,
        "lng": 77.9803
    }
    
    now_str = datetime.now().isoformat()
    complaint_dt = case_in.complaint_datetime or now_str

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT case_id FROM cases WHERE complaint_no = ?", (complaint_no,))
    if cursor.fetchone():
        complaint_no = f"{complaint_no}-{uuid.uuid4().hex[:4].upper()}"

    cursor.execute("""
        INSERT INTO cases (
            case_id, complaint_no, victim_name, victim_city,
            victim_lat, victim_lng, complaint_datetime,
            scenario_type, evidence_coverage, initial_loss_amount,
            status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        case_id, complaint_no, case_in.victim_name, city_data["city"],
        city_data["lat"], city_data["lng"], complaint_dt,
        case_in.scenario_type, case_in.evidence_coverage,
        case_in.initial_loss_amount, "OPEN", now_str, now_str
    ))
    conn.commit()

    # Automatically generate realistic multi-hop transactions for this case
    generate_case_transactions(
        conn, cursor, case_id,
        victim_name=case_in.victim_name,
        victim_city=city_data["city"],
        initial_loss_amount=case_in.initial_loss_amount,
        complaint_dt=complaint_dt
    )
    conn.close()

    log_audit(case_id, "CREATE_CASE", "INVESTIGATOR_PORTAL", {"complaint_no": complaint_no})

    # Anchor complaint intake on Blockchain Ledger (Section 65B)
    try:
        blockchain_ledger.record_event(
            case_id=case_id,
            officer_badge="TN-CCB-4402",
            event_type="COMPLAINT_REGISTERED",
            payload={
                "complaint_no": complaint_no,
                "victim_name": case_in.victim_name,
                "victim_city": city_data["city"],
                "initial_loss_amount_inr": case_in.initial_loss_amount,
                "scenario_type": case_in.scenario_type
            }
        )
    except Exception as e:
        logger.warning("Blockchain block mining failed for case %s: %s", case_id, e)

    return CaseResponse(
        case_id=case_id,
        complaint_no=complaint_no,
        victim_name=case_in.victim_name,
        victim_city=city_data["city"],
        victim_lat=city_data["lat"],
        victim_lng=city_data["lng"],
        complaint_datetime=complaint_dt,
        scenario_type=case_in.scenario_type,
        evidence_coverage=case_in.evidence_coverage,
        initial_loss_amount=case_in.initial_loss_amount,
        status="OPEN",
        transaction_count=0,
        created_at=now_str,
        updated_at=now_str
    )

@app.get("/api/cases/{case_id}")
def get_case(case_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
    case_row = cursor.fetchone()
    if not case_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Case not found")

    cursor.execute("SELECT * FROM transactions WHERE case_id = ? ORDER BY timestamp ASC", (case_id,))
    tx_rows = cursor.fetchall()

    cursor.execute("SELECT * FROM audit_log WHERE case_id = ? ORDER BY timestamp DESC LIMIT 20", (case_id,))
    audit_rows = cursor.fetchall()
    conn.close()

    return {
        "case": dict(case_row),
        "transactions": [dict(t) for t in tx_rows],
        "audit_logs": [dict(a) for a in audit_rows]
    }

@app.post("/api/cases/{case_id}/transactions", response_model=TransactionResponse)
def add_transaction(case_id: str, tx_in: TransactionCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
    case_row = cursor.fetchone()
    if not case_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Case not found")

    now_str = datetime.now().isoformat()
    ext_id = tx_in.external_event_id or f"TX-EVT-{uuid.uuid4().hex[:8].upper()}"
    ts = tx_in.timestamp or now_str

    # Auto resolve lat/lng if city provided
    dest_lat = tx_in.dest_lat
    dest_lng = tx_in.dest_lng
    if tx_in.dest_city and (dest_lat is None or dest_lng is None):
        city_match = geo_service.find_city(tx_in.dest_city)
        if city_match:
            dest_lat = city_match["lat"]
            dest_lng = city_match["lng"]

    try:
        cursor.execute("""
            INSERT INTO transactions (
                case_id, external_event_id, source_account, dest_account,
                amount, channel, timestamp, source_city, dest_city,
                dest_lat, dest_lng, is_terminal, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
        """, (
            case_id, ext_id, tx_in.source_account, tx_in.dest_account,
            float(tx_in.amount), tx_in.channel, ts,
            tx_in.source_city or "", tx_in.dest_city or "",
            dest_lat, dest_lng, now_str
        ))
        tx_id = cursor.lastrowid
        cursor.execute("UPDATE cases SET updated_at = ? WHERE case_id = ?", (now_str, case_id))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Failed to record transaction: {e}")

    conn.close()

    log_audit(case_id, "ADD_TRANSACTION", "INVESTIGATOR_UI", {
        "external_event_id": ext_id,
        "amount": tx_in.amount,
        "source": tx_in.source_account,
        "destination": tx_in.dest_account
    })

    # Anchor transaction hop on Blockchain Ledger (Section 65B)
    try:
        blockchain_ledger.record_event(
            case_id=case_id,
            officer_badge="TN-CCB-4402",
            event_type="GRAPH_HOP_MINED",
            payload={
                "external_event_id": ext_id,
                "source_account": tx_in.source_account,
                "dest_account": tx_in.dest_account,
                "amount_inr": tx_in.amount,
                "channel": tx_in.channel,
                "dest_city": tx_in.dest_city or "Transit Hub",
                "timestamp": ts
            }
        )
    except Exception as e:
        logger.warning("Blockchain block mining failed for transaction: %s", e)

    return TransactionResponse(
        id=tx_id,
        case_id=case_id,
        external_event_id=ext_id,
        source_account=tx_in.source_account,
        dest_account=tx_in.dest_account,
        amount=tx_in.amount,
        channel=tx_in.channel,
        timestamp=ts,
        source_city=tx_in.source_city,
        dest_city=tx_in.dest_city,
        dest_lat=dest_lat,
        dest_lng=dest_lng,
        is_terminal=1,
        created_at=now_str
    )

@app.post("/api/ingest/financial-event", response_model=IngestEventResponse)
def ingest_event(req: IngestEventRequest):
    """Production-style ingestion boundary for authorized banking / cyber-fraud sources."""
    return IngestionService.ingest_financial_event(req)

@app.post("/api/cases/{case_id}/outcome")
def record_outcome(case_id: str, outcome: CaseOutcomeCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT case_id FROM cases WHERE case_id = ?", (case_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Case not found")

    now_str = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO case_outcomes (
            case_id, outcome_type, confirmed_cashout_location,
            confirmed_atm_id, recovered_amount, notes, recorded_by, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        case_id, outcome.outcome_type, outcome.confirmed_cashout_location,
        outcome.confirmed_atm_id, outcome.recovered_amount, outcome.notes,
        outcome.recorded_by, now_str
    ))
    cursor.execute("UPDATE cases SET status = 'RESOLVED', updated_at = ? WHERE case_id = ?", (now_str, case_id))
    conn.commit()
    conn.close()

    log_audit(case_id, "RECORD_CASE_OUTCOME", outcome.recorded_by, {
        "outcome": outcome.outcome_type,
        "recovered": outcome.recovered_amount
    })

    # Anchor validated outcome on Blockchain Ledger (Section 65B)
    try:
        blockchain_ledger.record_event(
            case_id=case_id,
            officer_badge=outcome.recorded_by,
            event_type="OUTCOME_VERIFIED",
            payload={
                "outcome_type": outcome.outcome_type,
                "confirmed_cashout_location": outcome.confirmed_cashout_location or "N/A",
                "recovered_amount_inr": outcome.recovered_amount,
                "investigator_notes": outcome.notes or "Official field outcome validated."
            }
        )
    except Exception as e:
        logger.warning("Blockchain block mining failed for outcome: %s", e)

    return {"status": "SUCCESS", "message": "Case outcome logged and cryptographically anchored."}

# ---------------------------------------------------------------------------
# Core Analytical Pipeline: Graph -> Features -> ML -> Geo -> Evidence
# ---------------------------------------------------------------------------

@app.put("/api/cases/{case_id}", response_model=CaseResponse)
def update_case(case_id: str, case_in: CaseCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Case not found")

    city_data = geo_service.find_city(case_in.victim_city) or {
        "city": case_in.victim_city,
        "lat": 10.3673,
        "lng": 77.9803
    }
    now_str = datetime.now().isoformat()
    complaint_no = case_in.complaint_no or row["complaint_no"]
    cursor.execute("""
        UPDATE cases SET
            complaint_no = ?,
            victim_name = ?,
            victim_city = ?,
            victim_lat = ?,
            victim_lng = ?,
            initial_loss_amount = ?,
            scenario_type = ?,
            updated_at = ?
        WHERE case_id = ?
    """, (
        complaint_no,
        case_in.victim_name,
        city_data["city"],
        city_data["lat"],
        city_data["lng"],
        case_in.initial_loss_amount,
        case_in.scenario_type,
        now_str,
        case_id
    ))
    cursor.execute("DELETE FROM transactions WHERE case_id = ?", (case_id,))
    generate_case_transactions(
        conn, cursor, case_id,
        victim_name=case_in.victim_name,
        victim_city=city_data["city"],
        initial_loss_amount=float(case_in.initial_loss_amount),
        complaint_dt=row["complaint_datetime"]
    )
    cursor.execute("""
        SELECT c.*, COUNT(t.id) as transaction_count
        FROM cases c
        LEFT JOIN transactions t ON c.case_id = t.case_id
        WHERE c.case_id = ?
        GROUP BY c.case_id
    """, (case_id,))
    updated_row = cursor.fetchone()
    conn.commit()
    conn.close()

    return CaseResponse(
        case_id=updated_row["case_id"],
        complaint_no=updated_row["complaint_no"],
        victim_name=updated_row["victim_name"],
        victim_city=updated_row["victim_city"],
        victim_lat=updated_row["victim_lat"],
        victim_lng=updated_row["victim_lng"],
        complaint_datetime=updated_row["complaint_datetime"],
        scenario_type=updated_row["scenario_type"],
        evidence_coverage=updated_row["evidence_coverage"],
        initial_loss_amount=updated_row["initial_loss_amount"],
        status=updated_row["status"],
        transaction_count=updated_row["transaction_count"],
        created_at=updated_row["created_at"],
        updated_at=updated_row["updated_at"]
    )

@app.post("/api/cases/{case_id}/analyze", response_model=AnalysisResponse)
def analyze_case(
    case_id: str,
    scenario_override: Optional[str] = None,
    evidence_coverage: Optional[float] = None,
    victim_city_override: Optional[str] = None,
    victim_name_override: Optional[str] = None,
    initial_loss_amount_override: Optional[float] = None,
    terminal_city_override: Optional[str] = None,
    lookback_period: Optional[str] = DEFAULT_LOOKBACK,
    intelligence_source: Optional[str] = DEFAULT_FEED
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
    case_row = cursor.fetchone()
    if not case_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Case not found")

    case_dict = dict(case_row)
    if scenario_override and scenario_override in SCENARIOS:
        case_dict["scenario_type"] = scenario_override
    if evidence_coverage is not None:
        case_dict["evidence_coverage"] = float(evidence_coverage)

    should_regenerate = False

    if victim_name_override and victim_name_override.strip() and victim_name_override.strip() != case_dict.get("victim_name"):
        case_dict["victim_name"] = victim_name_override.strip()
        cursor.execute("UPDATE cases SET victim_name = ?, updated_at = ? WHERE case_id = ?",
                       (case_dict["victim_name"], datetime.now().isoformat(), case_id))
        conn.commit()

    if initial_loss_amount_override is not None:
        try:
            new_amount = float(initial_loss_amount_override)
            if new_amount > 0 and abs(new_amount - float(case_dict.get("initial_loss_amount", 0))) > 1.0:
                case_dict["initial_loss_amount"] = new_amount
                cursor.execute("UPDATE cases SET initial_loss_amount = ?, updated_at = ? WHERE case_id = ?",
                               (new_amount, datetime.now().isoformat(), case_id))
                conn.commit()
                should_regenerate = True
        except (ValueError, TypeError):
            pass

    # Dynamic Location Override Support
    if victim_city_override and victim_city_override.strip():
        resolved_city = geo_service.find_city(victim_city_override.strip())
        if resolved_city:
            if resolved_city["city"] != case_dict.get("victim_city"):
                should_regenerate = True
            case_dict["victim_city"] = resolved_city["city"]
            case_dict["victim_lat"] = resolved_city["lat"]
            case_dict["victim_lng"] = resolved_city["lng"]
            cursor.execute(
                "UPDATE cases SET victim_city = ?, victim_lat = ?, victim_lng = ?, updated_at = ? WHERE case_id = ?",
                (resolved_city["city"], resolved_city["lat"], resolved_city["lng"], datetime.now().isoformat(), case_id)
            )
            conn.commit()

    if should_regenerate:
        cursor.execute("DELETE FROM transactions WHERE case_id = ?", (case_id,))
        conn.commit()

    cursor.execute("SELECT * FROM transactions WHERE case_id = ? ORDER BY timestamp ASC", (case_id,))
    tx_rows = [dict(r) for r in cursor.fetchall()]
    if not tx_rows:
        generate_case_transactions(
            conn, cursor, case_id,
            victim_name=case_dict.get("victim_name", "Complainant"),
            victim_city=case_dict.get("victim_city", "Dindigul"),
            initial_loss_amount=float(case_dict.get("initial_loss_amount", 500000.0)),
            complaint_dt=case_dict.get("complaint_datetime")
        )
        cursor.execute("SELECT * FROM transactions WHERE case_id = ? ORDER BY timestamp ASC", (case_id,))
        tx_rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    # 1. NetworkX Graph Engine
    victim_account = f"ACC-VIC-{case_dict['victim_city'][:3].upper()}-9041"
    if tx_rows:
        victim_account = tx_rows[0]["source_account"]

    graph_engine = TransactionGraphEngine(tx_rows, victim_account=victim_account)
    serialized_graph = graph_engine.serialize_for_ui()

    # 2. Automatic Feature Extraction
    feature_extractor = FeatureExtractor(case_dict, tx_rows, graph_engine)
    features = feature_extractor.extract_features()
    signals_ui = feature_extractor.get_ui_signals(features)

    # 3. Machine Learning Inference (Random Forest Baseline + Lookback Decay)
    selected_lookback = lookback_period or DEFAULT_LOOKBACK
    risks = ml_model.predict(features, scenario_type=case_dict["scenario_type"], lookback_period=selected_lookback)

    # 4. Geospatial Cash-Out Location & Dual-Layer Hotspots (Historical vs Forecasted)
    cashout_summary, ranked_zones, atm_candidates, historical_hotspots = geo_service.predict_cashout_locations(
        victim_city_name=case_dict["victim_city"],
        transactions=tx_rows,
        cashout_risk=risks["cashout_risk"],
        digital_risk=risks["digital_flow_risk"],
        confidence=risks["confidence"],
        inter_hop_minutes=features["inter_hop_minutes"],
        terminal_city_override=terminal_city_override
    )

    # 5. Evidence & Explainability Engine
    evidence_items = EvidenceEngine.generate_evidence_items(
        features=features,
        risks=risks,
        scenario_type=case_dict["scenario_type"],
        terminal_city=cashout_summary.get("terminal_city", "Metropolitan Hub")
    )

    # 6. Timeline
    timeline = []
    for tx in tx_rows:
        timeline.append({
            "timestamp": tx["timestamp"],
            "title": f"Transfer: {tx['source_account']} -> {tx['dest_account']}",
            "amount": f"₹{float(tx['amount']):,.0f}",
            "channel": tx["channel"],
            "location": tx.get("dest_city") or "Transit Hub"
        })

    log_audit(case_id, "RUN_ANALYSIS", "INVESTIGATOR_UI", {
        "fraud_risk": risks["fraud_risk"],
        "cashout_risk": risks["cashout_risk"],
        "scenario": case_dict["scenario_type"],
        "lookback_period": selected_lookback,
        "intelligence_source": intelligence_source or DEFAULT_FEED
    })

    return AnalysisResponse(
        case_id=case_id,
        case=case_dict,
        risks=RiskCardData(**risks),
        cashout_summary=cashout_summary,
        ranked_zones=ranked_zones,
        atm_candidates=atm_candidates,
        historical_hotspots=historical_hotspots,
        primary_target_tuple=cashout_summary.get("primary_target_tuple"),
        lookback_period=selected_lookback,
        intelligence_source=intelligence_source or DEFAULT_FEED,
        graph=serialized_graph,
        signals=signals_ui,
        why_prediction=evidence_items,
        timeline=timeline,
        disclaimer=DISCLAIMER_TEXT
    )

@app.post("/api/cases/{case_id}/predict-cashout")
def predict_cashout_only(case_id: str):
    """Refreshed cash-out prediction specifically focused on tactical deployment."""
    return analyze_case(case_id)

@app.post("/api/cases/{case_id}/reset")
def reset_case_demo(case_id: str):
    """Reset case transactions back to initial state or clear completely."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE case_id = ?", (case_id,))
    cursor.execute("DELETE FROM event_receipts WHERE external_event_id LIKE ?", (f"%{case_id}%",))
    cursor.execute("UPDATE cases SET status = 'RESET', updated_at = ? WHERE case_id = ?", (datetime.now().isoformat(), case_id))
    conn.commit()
    conn.close()

    log_audit(case_id, "RESET_CASE", "INVESTIGATOR_UI", {"action": "PURGE_TRANSACTIONS"})
    return {"status": "SUCCESS", "message": f"Case {case_id} transactions reset."}

# ---------------------------------------------------------------------------
# Demo Seeding Helper: Dindigul ₹5,00,000 Social Engineering Chain
# ---------------------------------------------------------------------------

@app.post("/api/demo/seed")
def seed_demo_case():
    """Seed the official SIH demo case: Dindigul complainant losing ₹5,00,000."""
    case_id = "CASE-DIN-2026-001"
    complaint_no = "NCRP-2026-TN-981240"
    victim_name = "A. Murugesan"
    victim_city = "Dindigul"
    initial_amount = 500000.0

    conn = get_db_connection()
    cursor = conn.cursor()

    # Clean existing for all demo cases
    all_demo_case_ids = ("CASE-DIN-2026-001", "CASE-BLR-2026-042", "CASE-MUM-2026-108", "CASE-HYD-2026-019")
    cursor.execute("DELETE FROM cases WHERE case_id IN (?, ?, ?, ?)", all_demo_case_ids)
    cursor.execute("DELETE FROM transactions WHERE case_id IN (?, ?, ?, ?)", all_demo_case_ids)
    cursor.execute("DELETE FROM event_receipts WHERE external_event_id LIKE 'SEED-%'")

    now = datetime.now()
    t0 = (now - timedelta(minutes=25)).replace(microsecond=0)
    t1 = t0 + timedelta(minutes=4, seconds=15)
    t2 = t1 + timedelta(minutes=5, seconds=15)
    t3 = t2 + timedelta(minutes=5, seconds=15)

    now_str = now.isoformat()

    cursor.execute("""
        INSERT INTO cases (
            case_id, complaint_no, victim_name, victim_city,
            victim_lat, victim_lng, complaint_datetime,
            scenario_type, evidence_coverage, initial_loss_amount,
            status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        case_id, complaint_no, victim_name, victim_city,
        10.3673, 77.9803, t0.isoformat(),
        "mule_chain", 0.85, initial_amount,
        "ACTIVE_INVESTIGATION", now_str, now_str
    ))

    # The 4-hop chain:
    # Victim (Dindigul) -> Mule-A ₹5,00,000
    # Mule-A -> Mule-B ₹4,70,000
    # Mule-B -> Mule-C ₹4,40,000
    # Mule-C -> Mule-D ₹4,20,000 (Chennai)
    tx_chain = [
        {
            "ext_id": "SEED-EVT-01",
            "src": "ACC-VIC-DIN-9041 (Murugesan)",
            "dst": "ACC-MULE-A-8120",
            "amt": 500000.0,
            "channel": "IMPS",
            "ts": t0.isoformat(),
            "scity": "Dindigul",
            "dcity": "Madurai",
            "dlat": 9.9252,
            "dlng": 78.1198
        },
        {
            "ext_id": "SEED-EVT-02",
            "src": "ACC-MULE-A-8120",
            "dst": "ACC-MULE-B-3319",
            "amt": 470000.0,
            "channel": "NEFT",
            "ts": t1.isoformat(),
            "scity": "Madurai",
            "dcity": "Tiruchirappalli",
            "dlat": 10.7905,
            "dlng": 78.7047
        },
        {
            "ext_id": "SEED-EVT-03",
            "src": "ACC-MULE-B-3319",
            "dst": "ACC-MULE-C-7742",
            "amt": 440000.0,
            "channel": "IMPS",
            "ts": t2.isoformat(),
            "scity": "Tiruchirappalli",
            "dcity": "Salem",
            "dlat": 11.6643,
            "dlng": 78.1460
        },
        {
            "ext_id": "SEED-EVT-04",
            "src": "ACC-MULE-C-7742",
            "dst": "ACC-MULE-D-5104",
            "amt": 420000.0,
            "channel": "UPI",
            "ts": t3.isoformat(),
            "scity": "Salem",
            "dcity": "Chennai",
            "dlat": 13.0827,
            "dlng": 80.2707
        }
    ]

    for tx in tx_chain:
        cursor.execute("""
            INSERT INTO transactions (
                case_id, external_event_id, source_account, dest_account,
                amount, channel, timestamp, source_city, dest_city,
                dest_lat, dest_lng, is_terminal, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
        """, (
            case_id, tx["ext_id"], tx["src"], tx["dst"],
            tx["amt"], tx["channel"], tx["ts"],
            tx["scity"], tx["dcity"], tx["dlat"], tx["dlng"],
            now_str
        ))
        cursor.execute("""
            INSERT INTO event_receipts (external_event_id, source_connector, ingested_at, payload_hash, status)
            VALUES (?, ?, ?, ?, ?)
        """, (tx["ext_id"], "MOCK-BANK-01", now_str, "DEMO_PRELOAD", "ACCEPTED"))

    # Seed Case 2: Bengaluru -> Hosur Corridor
    blr_case_id = "CASE-BLR-2026-042"
    cursor.execute("""
        INSERT INTO cases (
            case_id, complaint_no, victim_name, victim_city,
            victim_lat, victim_lng, complaint_datetime,
            scenario_type, evidence_coverage, initial_loss_amount,
            status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        blr_case_id, "NCRP-2026-BLR-0421", "Anand K. Rao", "Bengaluru",
        12.9716, 77.5946, (now - timedelta(hours=1, minutes=15)).isoformat(),
        "mule_chain", 0.90, 1250000.0,
        "ACTIVE_INVESTIGATION", now_str, now_str
    ))
    cursor.execute("""
        INSERT INTO transactions (
            case_id, external_event_id, source_account, dest_account,
            amount, channel, timestamp, source_city, dest_city,
            dest_lat, dest_lng, is_terminal, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
    """, (
        blr_case_id, "SEED-EVT-BLR-01", "ACC-VIC-BLR-1002", "ACC-MULE-KA-5501",
        1250000.0, "RTGS", (now - timedelta(hours=1, minutes=10)).isoformat(),
        "Bengaluru", "Hosur", 12.7409, 77.8253, now_str
    ))

    # Seed Case 3: Navi Mumbai -> Thane Transit
    mum_case_id = "CASE-MUM-2026-108"
    cursor.execute("""
        INSERT INTO cases (
            case_id, complaint_no, victim_name, victim_city,
            victim_lat, victim_lng, complaint_datetime,
            scenario_type, evidence_coverage, initial_loss_amount,
            status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        mum_case_id, "NCRP-2026-MUM-1082", "Sunita Deshmukh", "Mumbai",
        19.0760, 72.8777, (now - timedelta(hours=2, minutes=30)).isoformat(),
        "mule_chain", 0.88, 820000.0,
        "ACTIVE_INVESTIGATION", now_str, now_str
    ))
    cursor.execute("""
        INSERT INTO transactions (
            case_id, external_event_id, source_account, dest_account,
            amount, channel, timestamp, source_city, dest_city,
            dest_lat, dest_lng, is_terminal, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
    """, (
        mum_case_id, "SEED-EVT-MUM-01", "ACC-VIC-MUM-4491", "ACC-MULE-MH-9102",
        820000.0, "IMPS", (now - timedelta(hours=2, minutes=20)).isoformat(),
        "Mumbai", "Thane", 19.2183, 72.9781, now_str
    ))

    # Seed Case 4: Hyderabad -> Secunderabad
    hyd_case_id = "CASE-HYD-2026-019"
    cursor.execute("""
        INSERT INTO cases (
            case_id, complaint_no, victim_name, victim_city,
            victim_lat, victim_lng, complaint_datetime,
            scenario_type, evidence_coverage, initial_loss_amount,
            status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        hyd_case_id, "NCRP-2026-HYD-0194", "Vikram Reddy", "Hyderabad",
        17.3850, 78.4867, (now - timedelta(hours=3, minutes=10)).isoformat(),
        "mule_chain", 0.82, 340000.0,
        "ACTIVE_INVESTIGATION", now_str, now_str
    ))
    cursor.execute("""
        INSERT INTO transactions (
            case_id, external_event_id, source_account, dest_account,
            amount, channel, timestamp, source_city, dest_city,
            dest_lat, dest_lng, is_terminal, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
    """, (
        hyd_case_id, "SEED-EVT-HYD-01", "ACC-VIC-HYD-8003", "ACC-MULE-TS-1209",
        340000.0, "UPI", (now - timedelta(hours=3)).isoformat(),
        "Hyderabad", "Secunderabad", 17.4399, 78.4983, now_str
    ))

    # Reset blockchain ledger for demo case (keep Genesis block at index 0)
    cursor.execute("DELETE FROM blockchain_ledger WHERE block_index > 0")
    conn.commit()
    conn.close()

    # Re-seed benchmark cryptographic blocks
    try:
        # 1. Complaint Registered Block
        blockchain_ledger.record_event(
            case_id=case_id,
            officer_badge="TN-CCB-4402",
            event_type="COMPLAINT_REGISTERED",
            payload={
                "complaint_no": complaint_no,
                "victim_name": victim_name,
                "victim_city": victim_city,
                "initial_loss_amount_inr": initial_amount,
                "statutory_act": "Information Technology Act 66D & IPC 420"
            }
        )

        # 2-5. Ingested Transaction Hop Blocks
        for tx in tx_chain:
            blockchain_ledger.record_event(
                case_id=case_id,
                officer_badge="TN-CCB-4402",
                event_type="GRAPH_HOP_MINED",
                payload={
                    "external_event_id": tx["ext_id"],
                    "source_account": tx["src"],
                    "dest_account": tx["dst"],
                    "amount_inr": tx["amt"],
                    "channel": tx["channel"],
                    "source_city": tx["scity"],
                    "dest_city": tx["dcity"]
                }
            )

        # 6. AI Inference Forecast Anchor Block
        blockchain_ledger.record_event(
            case_id=case_id,
            officer_badge="TN-CCB-4402",
            event_type="AI_PREDICTION_COMMITTED",
            payload={
                "fraud_risk": 94.2,
                "digital_retention_risk": 52.8,
                "cashout_risk": 89.5,
                "confidence": 86.0,
                "terminal_hub": "Chennai Metropolitan Area",
                "top_candidate_zone": "T. Nagar Commercial Hub",
                "top_atm_candidate": "SBI-ATM-CH-4412",
                "model_engine": "MultiOutput Random Forest v1.0.0-rf-synthetic"
            }
        )

        # 7. Inter-Bank Rapid Freeze Directive Block
        blockchain_ledger.issue_freeze_directive(
            case_id=case_id,
            terminal_account="ACC-MULE-D-5104",
            target_bank="STATE_BANK_OF_INDIA",
            amount=420000.0,
            reason="High-probability ATM cash-out forecasted within 20 to 40 minute operational window.",
            officer_badge="TN-CCB-4402"
        )
    except Exception as e:
        logger.warning("Error seeding benchmark blockchain blocks: %s", e)

    log_audit(case_id, "SEED_DEMO_SCENARIO", "SYSTEM_SEED", {"initial_amount": initial_amount})
    return {"status": "SUCCESS", "case_id": case_id, "message": "Dindigul demo case and blockchain ledger seeded successfully."}

# Auto seed demo case on startup if not present
try:
    conn_chk = get_db_connection()
    c_chk = conn_chk.cursor()
    c_chk.execute("SELECT COUNT(*) FROM cases WHERE case_id = 'CASE-DIN-2026-001'")
    if c_chk.fetchone()[0] == 0:
        conn_chk.close()
        seed_demo_case()
    else:
        conn_chk.close()
except Exception as e:
    logger.warning("Startup seeding check encountered: %s", e)



# Mount frontend static assets
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
@app.get("/api/index.py")
@app.get("/api")
@app.get("/api/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(
            str(index_file),
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    return JSONResponse({"message": "FraudFlow Intelligence API is running. Frontend assets under /static."})

@app.get("/styles.css")
@app.get("/api/index.py/styles.css")
@app.get("/api/styles.css")
def serve_root_styles():
    return FileResponse(
        STATIC_DIR / "styles.css",
        media_type="text/css",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate, max-age=0", "Pragma": "no-cache", "Expires": "0"}
    )

@app.get("/app.js")
@app.get("/api/index.py/app.js")
@app.get("/api/app.js")
def serve_root_js():
    return FileResponse(
        STATIC_DIR / "app.js",
        media_type="application/javascript",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate, max-age=0", "Pragma": "no-cache", "Expires": "0"}
    )

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)

@app.get("/download/codebase")
def download_codebase():
    file_path = BASE_DIR / "FRAUDFLOW_INTELLIGENCE_FULL_CODEBASE.txt"
    if file_path.exists():
        return FileResponse(
            path=str(file_path),
            filename="FRAUDFLOW_INTELLIGENCE_FULL_CODEBASE.txt",
            media_type="text/plain"
        )
    raise HTTPException(status_code=404, detail="Codebase file not found")

@app.get("/download/zip")
def download_zip():
    file_path = Path(r"C:\Users\mdbaa\.gemini\antigravity\brain\bf37c023-795b-4097-b04c-d14515dabbd2\FraudFlow_Intelligence_National.zip")
    if not file_path.exists():
        file_path = BASE_DIR / "FraudFlow_Intelligence_National.zip"
    if file_path.exists():
        return FileResponse(
            path=str(file_path),
            filename="FraudFlow_Intelligence_National.zip",
            media_type="application/zip"
        )
    raise HTTPException(status_code=404, detail="ZIP archive not found")

@app.get("/download/backend")
def download_backend():
    file_path = BASE_DIR / "FraudFlow_Backend_Only.zip"
    if not file_path.exists():
        file_path = Path(r"C:\Users\mdbaa\Downloads\FraudFlow_Backend_Only.zip")
    if file_path.exists():
        return FileResponse(
            path=str(file_path),
            filename="FraudFlow_Backend_Only.zip",
            media_type="application/zip"
        )
    raise HTTPException(status_code=404, detail="Backend ZIP archive not found")

@app.get("/download/backend-txt")
def download_backend_txt():
    file_path = BASE_DIR / "FRAUDFLOW_BACKEND_CODEBASE.txt"
    if not file_path.exists():
        file_path = Path(r"C:\Users\mdbaa\Downloads\FRAUDFLOW_BACKEND_CODEBASE.txt")
    if file_path.exists():
        return FileResponse(
            path=str(file_path),
            filename="FRAUDFLOW_BACKEND_CODEBASE.txt",
            media_type="text/plain"
        )
    raise HTTPException(status_code=404, detail="Backend text codebase not found")

