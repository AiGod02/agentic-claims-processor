from typing import Optional, List, Dict, Any
from typing_extensions import TypedDict
from models.claim import (
    ClaimSubmission, ClassifiedDocument, ExtractedClaimData,
    ClaimDecision, LineItemDecision
)
from models.trace import ClaimTrace


class ClaimState(TypedDict, total=False):
    """
    Shared state passed between all LangGraph nodes.
    Each node receives the full state and returns a dict of fields to update.
    Using TypedDict for LangGraph compatibility.
    """
    # Set at entry, never modified
    claim_id: str
    submission: ClaimSubmission
    trace: ClaimTrace
    policy_data: Dict[str, Any]

    # Set by document_agent node
    classified_documents: List[ClassifiedDocument]
    extracted_data: Optional[ExtractedClaimData]
    blocking_error: Optional[str]
    document_agent_passed: bool

    # Set by policy_agent node (runs in parallel with fraud_agent)
    policy_eval: Optional[Dict[str, Any]]

    # Set by fraud_agent node (runs in parallel with policy_agent)
    fraud_assessment: Optional[Dict[str, Any]]

    # Set by decision_agent node
    decision: Optional[ClaimDecision]
    approved_amount: Optional[float]
    reason: Optional[str]
    confidence_score: float
    financial_breakdown: Dict[str, float]
    line_items: List[LineItemDecision]
    rejection_reasons: List[str]
    fraud_signals: List[str]
    manual_review_reasons: List[str]

    # Degradation tracking
    degraded: bool
    failed_agents: List[str]
