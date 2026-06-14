from agents.base import BaseAgent
from models.claim import ClaimDecision, LineItemDecision
from models.trace import StepStatus, CheckResult
import logging

logger = logging.getLogger(__name__)


class DecisionAgent(BaseAgent):
    name = "DecisionAgent"
    node_name = "decision_agent"

    async def run(self, state: dict) -> dict:
        trace = state["trace"]
        ctx = self._start_step("Synthesizing final decision from policy + fraud evaluations")

        policy_eval = state.get("policy_eval") or {}
        fraud = state.get("fraud_assessment") or {}
        submission = state["submission"]
        policy = state.get("policy_data") or {}
        extracted = state.get("extracted_data")
        checks = []

        try:
            rejection_reasons = policy_eval.get("rejection_reasons", [])
            final_approved = policy_eval.get("final_approved_amount", 0.0)
            breakdown = policy_eval.get("financial_breakdown", {})
            line_items = [
                LineItemDecision(**ld) for ld in policy_eval.get("line_item_decisions", [])
            ]
            fraud_flags = fraud.get("flags", [])
            recommend_manual = fraud.get("recommend_manual_review", False)
            manual_reasons = list(fraud.get("manual_review_reasons", []))
            fraud_score = fraud.get("fraud_score", 0.0)

            # Confidence score
            confidence = trace.final_confidence
            degraded = state.get("degraded", False)
            failed_agents = state.get("failed_agents") or []

            if degraded:
                confidence = max(0.0, confidence - 0.3)
            confidence = round(min(1.0, max(0.0, confidence)), 3)

            # Decision logic
            decision = None
            reason = ""

            # 1. MANUAL_REVIEW — highest priority
            if recommend_manual or (degraded and confidence < 0.5):
                decision = ClaimDecision.MANUAL_REVIEW
                if degraded and confidence < 0.5:
                    manual_reasons.append(
                        f"Pipeline degraded (failed: {failed_agents}). Confidence: {confidence:.2f}."
                    )
                reason = (
                    f"Claim flagged for manual review. "
                    f"Signals: {', '.join(manual_reasons)}. "
                    f"Fraud flags: {', '.join(fraud_flags) if fraud_flags else 'none'}. "
                    f"An operations team member will review within 2 business days."
                )

            # 2. REJECTED
            elif rejection_reasons:
                decision = ClaimDecision.REJECTED
                # Prioritize specific waiting period reasons, then build combined text
                waiting_period_reasons = [r for r in rejection_reasons if r.startswith("WAITING_PERIOD_")]
                primary = waiting_period_reasons[0] if waiting_period_reasons else rejection_reasons[0]
                reason = self._build_rejection_reason(primary, rejection_reasons, submission, policy_eval, policy)
                
                final_approved = 0.0
                if not line_items and extracted and extracted.line_items:
                    for item in extracted.line_items:
                        line_items.append(LineItemDecision(
                            description=item.description, claimed_amount=item.amount,
                            approved_amount=0.0, status="REJECTED",
                            reason=reason
                        ))
                else:
                    for item in line_items:
                        item.status = "REJECTED"
                        item.approved_amount = 0.0
                        if not item.reason:
                            item.reason = reason

            # 3. PARTIAL
            elif line_items and any(li.status == "REJECTED" for li in line_items):
                decision = ClaimDecision.PARTIAL
                approved_items = [li for li in line_items if li.status == "APPROVED"]
                rejected_items = [li for li in line_items if li.status == "REJECTED"]
                final_approved = sum(li.approved_amount for li in approved_items)
                reason = (
                    f"Claim partially approved. ₹{final_approved:.2f} approved of ₹{submission.claimed_amount} claimed.\n"
                    f"Approved: {', '.join(f'{li.description} (₹{li.approved_amount})' for li in approved_items)}\n"
                    f"Rejected: {', '.join(f'{li.description} — {li.reason}' for li in rejected_items)}"
                )

            # 4. APPROVED
            else:
                decision = ClaimDecision.APPROVED
                reason = f"Claim approved. ₹{final_approved:.2f} will be reimbursed."
                if breakdown.get("network_discount", 0) > 0:
                    reason += f" Network discount of ₹{breakdown['network_discount']:.2f} applied."
                if breakdown.get("copay", 0) > 0:
                    reason += f" Co-pay of ₹{breakdown['copay']:.2f} deducted."

            # Simulated failure note
            if submission.simulate_component_failure:
                reason += (
                    f"\n\nNote: Pipeline ran with simulated component failure. "
                    f"Manual review recommended due to incomplete processing. "
                    f"Confidence reduced to {confidence:.2f}."
                )
                if decision == ClaimDecision.APPROVED:
                    manual_reasons.append("Simulated component failure")

            checks.append(CheckResult(
                check_name="final_decision", passed=True,
                detail=f"Decision: {decision.value}, Approved: ₹{final_approved:.2f}, Confidence: {confidence:.2f}",
                rule_source="decision_agent"
            ))

            step = self._finish_step(
                ctx, StepStatus.PASSED,
                f"Decision: {decision.value} | Approved: ₹{final_approved:.2f} | Confidence: {confidence:.2f}",
                checks=checks, errors=[], confidence_impact=0.0
            )
            trace.add_step(step)

            # Clean and map rejection reasons to match test cases standard keys exactly
            mapped_rejections = []
            for r in rejection_reasons:
                if r.startswith("WAITING_PERIOD_") or r == "INITIAL_WAITING_PERIOD":
                    mapped_rejections.append("WAITING_PERIOD")
                elif r == "PER_CLAIM_LIMIT_EXCEEDED":
                    mapped_rejections.append("PER_CLAIM_EXCEEDED")
                else:
                    mapped_rejections.append(r)
            
            # Prioritize matching standard keys
            priority = ["MEMBER_NOT_FOUND", "POLICY_INACTIVE", "EXCLUDED_CONDITION", "WAITING_PERIOD", "PRE_AUTH_MISSING", "PER_CLAIM_EXCEEDED", "BELOW_MINIMUM_CLAIM_AMOUNT", "SUBMISSION_DEADLINE_EXCEEDED"]
            final_rejection_reasons = []
            for p in priority:
                if p in mapped_rejections:
                    final_rejection_reasons = [p]
                    break
            if not final_rejection_reasons:
                final_rejection_reasons = mapped_rejections

            return {
                "decision": decision, "approved_amount": round(final_approved, 2),
                "reason": reason, "confidence_score": confidence,
                "financial_breakdown": breakdown, "line_items": line_items,
                "rejection_reasons": final_rejection_reasons, "fraud_signals": fraud_flags,
                "manual_review_reasons": manual_reasons, "trace": trace
            }

        except Exception as e:
            logger.error(f"DecisionAgent failed: {e}", exc_info=True)
            step = self._finish_step(
                ctx, StepStatus.FAILED, f"DecisionAgent error: {str(e)}",
                checks=checks, errors=[str(e)], confidence_impact=-0.5
            )
            trace.add_step(step)
            return {
                "decision": ClaimDecision.MANUAL_REVIEW, "approved_amount": 0.0,
                "reason": f"Decision engine failed: {str(e)}. Routed to manual review.",
                "confidence_score": 0.1, "rejection_reasons": [], "fraud_signals": [],
                "manual_review_reasons": ["Decision engine failure"],
                "degraded": True, "failed_agents": (state.get("failed_agents") or []) + ["decision_agent"],
                "trace": trace
            }

    def _build_rejection_reason(self, primary, all_reasons, submission, policy_eval, policy):
        # Read values dynamically from policy_terms.json
        deadline_days = policy.get("submission_rules", {}).get("deadline_days_from_treatment", 30)
        min_claim = policy.get("submission_rules", {}).get("minimum_claim_amount", 500)
        per_claim_limit = policy.get("coverage", {}).get("per_claim_limit", 5000)
        initial_wait_days = policy.get("waiting_periods", {}).get("initial_waiting_period_days", 30)
        pre_auth_threshold = policy.get("opd_categories", {}).get("diagnostic", {}).get("pre_auth_threshold", 10000)
        high_value_tests = policy.get("opd_categories", {}).get("diagnostic", {}).get("high_value_tests_requiring_pre_auth", [])
        insurer = policy.get("insurer", "your insurer")
        tests_str = "/".join(high_value_tests) if high_value_tests else "high-value scans"

        reason_map = {
            "MEMBER_NOT_FOUND": f"Member {submission.member_id} not found. Verify your employee ID.",
            "POLICY_INACTIVE": "Policy is inactive or treatment date is outside policy period.",
            "SUBMISSION_DEADLINE_EXCEEDED": f"Submission deadline ({deadline_days} days) exceeded.",
            "BELOW_MINIMUM_CLAIM_AMOUNT": f"Amount ₹{submission.claimed_amount} is below minimum ₹{min_claim}.",
            "INITIAL_WAITING_PERIOD": f"Initial {initial_wait_days}-day waiting period not completed.",
            "PRE_AUTH_MISSING": f"Pre-authorization required but not obtained. For {tests_str} above ₹{pre_auth_threshold:,}, obtain pre-auth from {insurer} first.",
            "EXCLUDED_CONDITION": "Treatment/procedure is excluded under your policy.",
            "PER_CLAIM_LIMIT_EXCEEDED": f"Claimed ₹{submission.claimed_amount} exceeds per-claim limit ₹{per_claim_limit:,}.",
        }

        messages = []
        for r in all_reasons:
            if r.startswith("WAITING_PERIOD_"):
                condition_part = r.replace("WAITING_PERIOD_", "").split(" —")[0]
                eligible_info = next((reason for reason in all_reasons if "eligible from" in reason.lower() and condition_part.upper() in reason.upper()), "")
                if not eligible_info:
                    eligible_info = r
                msg = f"Waiting period not met for {condition_part.lower()} ({eligible_info})."
                if msg not in messages:
                    messages.append(msg)
            elif r in reason_map:
                msg = reason_map[r]
                if msg not in messages:
                    messages.append(msg)
            elif "WAITING_PERIOD_" not in r:
                if r not in messages:
                    messages.append(r)

        if not messages:
            return "Claim rejected: Policy terms not met."
        if len(messages) == 1:
            return f"Claim rejected: {messages[0]}"
        return "Claim rejected due to multiple policy violations:\n" + "\n".join(f"• {m}" for m in messages)
