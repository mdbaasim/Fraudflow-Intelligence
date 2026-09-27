"""
Pydantic Schemas for Request/Response Payloads
FraudFlow Intelligence
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class CaseCreate(BaseModel):
    complaint_no: Optional[str] = None
    victim_name: str = "A. Murugesan"
    victim_city: str = "Dindigul"
    complaint_datetime: Optional[str] = None
    scenario_type: str = "mule_chain"
    evidence_coverage: float = Field(default=0.75, ge=0.1, le=1.0)
    initial_loss_amount: float = Field(default=500000.0, gt=0)

class CaseResponse(BaseModel):
    case_id: str
    complaint_no: str
    victim_name: str
    victim_city: str
    victim_lat: float
    victim_lng: float
    complaint_datetime: str
    scenario_type: str
    evidence_coverage: float
    initial_loss_amount: float
    status: str
    transaction_count: int
    created_at: str
    updated_at: str

class TransactionCreate(BaseModel):
    source_account: str
    dest_account: str
    amount: float
    channel: str = "IMPS"
    timestamp: Optional[str] = None
    source_city: Optional[str] = None
    dest_city: Optional[str] = None
    dest_lat: Optional[float] = None
    dest_lng: Optional[float] = None
    external_event_id: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    case_id: str
    external_event_id: str
    source_account: str
    dest_account: str
    amount: float
    channel: str
    timestamp: str
    source_city: Optional[str] = None
    dest_city: Optional[str] = None
    dest_lat: Optional[float] = None
    dest_lng: Optional[float] = None
    is_terminal: int
    created_at: str

class IngestEventRequest(BaseModel):
    source_connector: str = "MOCK-BANK-01"
    external_event_id: str
    case_id: str
    source_account: str
    dest_account: str
    amount: float
    channel: str = "IMPS"
    timestamp: str
    source_city: Optional[str] = None
    dest_city: Optional[str] = None
    dest_lat: Optional[float] = None
    dest_lng: Optional[float] = None

class IngestEventResponse(BaseModel):
    status: str
    receipt_id: int
    external_event_id: str
    case_id: str
    message: str
    ingested_at: str

class RiskCardData(BaseModel):
    fraud_risk: float  # 0 to 100
    digital_flow_risk: float
    cashout_risk: float
    confidence: float
    overall_level: str  # CRITICAL, HIGH, ELEVATED, LOW

class AtmCandidate(BaseModel):
    atm_id: str
    bank_name: str
    area_name: str
    city: str
    state: str
    lat: float
    lng: float
    distance_km: float
    confidence: float
    est_time_window: str
    google_maps_url: str

class CashoutZone(BaseModel):
    rank: int
    zone_name: str
    city: str
    state: str
    lat: float
    lng: float
    radius_km: float
    score: float
    confidence: float
    time_window: str
    primary_corridor: str

class ModelSignal(BaseModel):
    name: str
    label: str
    value: Any
    unit: str
    description: str
    level: str  # ALERT, ELEVATED, NORMAL

class EvidenceItem(BaseModel):
    category: str
    title: str
    description: str
    strength: str  # HIGH, MEDIUM, LOW
    signal_ref: str

class GraphNode(BaseModel):
    id: str
    label: str
    entity_type: str  # VICTIM, MULE, MERCHANT, ATM
    city: str
    balance_received: float
    balance_forwarded: float
    is_terminal: bool

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    amount: float
    channel: str
    timestamp: str
    is_latest: bool

class GraphData(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    latest_edge_id: Optional[str] = None

class AnalysisResponse(BaseModel):
    case_id: str
    case: Optional[Dict[str, Any]] = None
    risks: RiskCardData
    cashout_summary: Dict[str, Any]
    ranked_zones: List[CashoutZone]
    atm_candidates: List[AtmCandidate]
    historical_hotspots: List[Dict[str, Any]] = []
    primary_target_tuple: Optional[Dict[str, Any]] = None
    lookback_period: str = "7D"
    intelligence_source: str = "FEED_NCRP_ACTIVE"
    graph: GraphData
    signals: List[ModelSignal]
    why_prediction: List[EvidenceItem]
    timeline: List[Dict[str, Any]]
    disclaimer: str

class CaseOutcomeCreate(BaseModel):
    outcome_type: str  # e.g., CASHOUT_CONFIRMED_AT_ZONE, RECOVERED_ONLINE, FALSE_POSITIVE
    confirmed_cashout_location: Optional[str] = None
    confirmed_atm_id: Optional[str] = None
    recovered_amount: float = 0.0
    notes: Optional[str] = None
    recorded_by: str = "IO_CYBER_CRIME"

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminUserResponse(BaseModel):
    authenticated: bool
    token: str
    username: str
    officer_name: str
    badge_number: str
    designation: str
    unit: str
    permissions: List[str]

# ---------------------------------------------------------------------------
# Forensic Blockchain Schemas (Section 65B Indian Evidence Act)
# ---------------------------------------------------------------------------

class BlockchainBlockResponse(BaseModel):
    block_index: int
    block_hash: str
    previous_hash: str
    timestamp: str
    case_id: str
    officer_badge: str
    event_type: str
    payload: Dict[str, Any]
    payload_hash: str
    nonce: int
    is_tampered: bool

class BlockchainVerifyResponse(BaseModel):
    is_valid: bool
    block_count: int
    status: str = "CHAIN_INTEGRITY_VERIFIED"
    statutory_compliance: Optional[str] = None
    latest_block_hash: Optional[str] = None
    failed_at_index: Optional[int] = None
    reason: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class FreezeDirectiveRequest(BaseModel):
    case_id: str
    terminal_account: str
    target_bank: str = "STATE_BANK_OF_INDIA"
    amount: float
    reason: str = "High-confidence ATM cash-out predicted within active execution window."
    officer_badge: str = "TN-CCB-4402"

class FreezeDirectiveResponse(BaseModel):
    directive_id: str
    block_index: int
    block_hash: str
    digital_signature: str
    target_account: str
    freeze_amount: float
    status: str

class TamperSimulationRequest(BaseModel):
    block_index: int = 1

