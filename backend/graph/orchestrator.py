from langgraph.graph import StateGraph, END
from models.state import ClaimState
from models.claim import ClaimSubmission, ClaimResult, ClaimDecision
from models.trace import ClaimTrace
from graph.nodes import document_node, parallel_agents_node, decision_node
from graph.edges import route_after_documents
from services.policy_loader import load_policy
from services.claims_store import claims_store
from datetime import datetime, timezone
import uuid
import time


def build_graph():
    graph = StateGraph(ClaimState)

    graph.add_node("document_agent", document_node)
    graph.add_node("parallel_agents", parallel_agents_node)
    graph.add_node("decision_agent", decision_node)

    graph.set_entry_point("document_agent")

    graph.add_conditional_edges(
        "document_agent",
        route_after_documents,
        {"exit_early": END, "continue": "parallel_agents"}
    )

    graph.add_edge("parallel_agents", "decision_agent")
    graph.add_edge("decision_agent", END)

    return graph.compile()


claims_graph = build_graph()


async def process_claim(submission: ClaimSubmission) -> ClaimResult:
    claim_id = f"CLM_{uuid.uuid4().hex[:8].upper()}"
    start_time = time.time()

    policy_data = load_policy(submission.policy_id)

    db_claims = claims_store.list_all()

    # Automatically calculate YTD claims amount from historical approved/partial claims if not set
    if not submission.ytd_claims_amount:
        ytd_sum = sum(
            pc.approved_amount or 0.0
            for pc in db_claims
            if pc.member_id == submission.member_id
            and pc.decision in {ClaimDecision.APPROVED, ClaimDecision.PARTIAL}
        )
        submission.ytd_claims_amount = ytd_sum

    # Automatically query and populate/merge claims history from claims_store
    if submission.claims_history is None:
        submission.claims_history = []
    
    existing_ids = {c.get("claim_id") for c in submission.claims_history if c.get("claim_id")}
    for pc in db_claims:
        if pc.member_id == submission.member_id and pc.claim_id not in existing_ids:
            submission.claims_history.append({
                "claim_id": pc.claim_id,
                "date": str(pc.treatment_date) if pc.treatment_date else pc.created_at[:10],
                "amount": pc.claimed_amount,
                "provider": pc.hospital_name or "Unknown Provider"
            })

    trace = ClaimTrace(
        claim_id=claim_id,
        started_at=datetime.now(timezone.utc).isoformat(),
        initial_confidence=1.0,
        final_confidence=1.0
    )

    initial_state = {
        "claim_id": claim_id,
        "submission": submission,
        "trace": trace,
        "policy_data": policy_data,
        "classified_documents": [],
        "extracted_data": None,
        "blocking_error": None,
        "document_agent_passed": False,
        "policy_eval": None,
        "fraud_assessment": None,
        "decision": None,
        "approved_amount": None,
        "reason": None,
        "confidence_score": 1.0,
        "financial_breakdown": {},
        "line_items": [],
        "rejection_reasons": [],
        "fraud_signals": [],
        "manual_review_reasons": [],
        "degraded": False,
        "failed_agents": [],
    }

    final_state = await claims_graph.ainvoke(initial_state)

    total_ms = (time.time() - start_time) * 1000
    final_trace = final_state.get("trace", trace)
    final_trace.completed_at = datetime.now(timezone.utc).isoformat()
    final_trace.total_duration_ms = total_ms

    # Build the graph_path from trace steps
    graph_path = final_trace.graph_path

    decision = final_state.get("decision")
    blocking_error = final_state.get("blocking_error")

    # For blocking errors (TC001-TC003), decision is None
    if blocking_error and not decision:
        result_decision = None
        result_reason = blocking_error
    else:
        result_decision = decision
        result_reason = final_state.get("reason", "")

    # Determine hospital name from state or extract it
    extracted_data = final_state.get("extracted_data")
    extracted_hospital = (
        extracted_data.hospital_name.value 
        if extracted_data and extracted_data.hospital_name 
        else None
    )

    result = ClaimResult(
        claim_id=claim_id,
        member_id=submission.member_id,
        treatment_date=submission.treatment_date,
        hospital_name=submission.hospital_name or extracted_hospital,
        decision=result_decision,
        approved_amount=final_state.get("approved_amount"),
        claimed_amount=submission.claimed_amount,
        reason=result_reason,
        confidence_score=final_state.get("confidence_score", final_trace.final_confidence),
        financial_breakdown=final_state.get("financial_breakdown", {}),
        line_items=final_state.get("line_items", []),
        rejection_reasons=final_state.get("rejection_reasons", []),
        fraud_signals=final_state.get("fraud_signals", []),
        manual_review_reasons=final_state.get("manual_review_reasons", []),
        degraded=final_state.get("degraded", False),
        failed_agents=final_state.get("failed_agents", []),
        graph_path=graph_path,
        trace=final_trace,
        created_at=datetime.now(timezone.utc).isoformat()
    )

    claims_store.save(result)
    return result
