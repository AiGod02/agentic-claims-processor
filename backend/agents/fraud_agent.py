from agents.base import BaseAgent
from models.trace import StepStatus, CheckResult
import logging

logger = logging.getLogger(__name__)


class FraudAgent(BaseAgent):
    name = "FraudAgent"
    node_name = "fraud_agent"

    async def run(self, state: dict) -> dict:
        submission = state["submission"]
        policy = state["policy_data"]
        trace = state["trace"]
        extracted = state.get("extracted_data")

        ctx = self._start_step(
            f"Fraud assessment for member {submission.member_id}, ₹{submission.claimed_amount}"
        )
        thresholds = policy["fraud_thresholds"]
        checks = []
        flags = []
        flag_details = {}

        try:
            treatment_date_str = str(submission.treatment_date)
            claims_history = submission.claims_history or []

            # Signal 1: Same-day claims
            same_day = [c for c in claims_history if c.get("date") == treatment_date_str]
            same_day_limit = thresholds["same_day_claims_limit"]
            if len(same_day) >= same_day_limit:
                flags.append("SAME_DAY_CLAIM_PATTERN")
                flag_details["same_day"] = {"count": len(same_day) + 1, "limit": same_day_limit}
            checks.append(CheckResult(
                check_name="same_day_claims",
                passed=len(same_day) < same_day_limit,
                detail=f"{len(same_day)} existing claims on {treatment_date_str} (limit: {same_day_limit})",
                rule_source="policy_terms.json > fraud_thresholds > same_day_claims_limit"
            ))

            # Signal 2: Multiple providers same day
            same_day_providers = list({c.get("provider") for c in same_day if c.get("provider")})
            if len(same_day_providers) > 1:
                flags.append("MULTIPLE_PROVIDERS_SAME_DAY")
                flag_details["multiple_providers"] = {"providers": same_day_providers}
            checks.append(CheckResult(
                check_name="multiple_providers_same_day",
                passed=len(same_day_providers) <= 1,
                detail=f"Same-day providers: {same_day_providers}",
                rule_source="policy_terms.json > fraud_thresholds"
            ))

            # Signal 3: Monthly claims count
            treatment_month = str(submission.treatment_date)[:7]
            monthly_claims = [c for c in claims_history if str(c.get("date", ""))[:7] == treatment_month]
            monthly_limit = thresholds["monthly_claims_limit"]
            if len(monthly_claims) >= monthly_limit:
                flags.append("MONTHLY_LIMIT_EXCEEDED")
                flag_details["monthly"] = {"count": len(monthly_claims) + 1, "limit": monthly_limit}
            checks.append(CheckResult(
                check_name="monthly_claims_limit",
                passed=len(monthly_claims) < monthly_limit,
                detail=f"{len(monthly_claims)} claims this month (limit: {monthly_limit})",
                rule_source="policy_terms.json > fraud_thresholds > monthly_claims_limit"
            ))

            # Signal 4: High value claim
            high_value_threshold = thresholds["high_value_claim_threshold"]
            is_high_value = submission.claimed_amount >= high_value_threshold
            if is_high_value:
                flags.append("HIGH_VALUE_CLAIM")
                flag_details["high_value"] = {"amount": submission.claimed_amount, "threshold": high_value_threshold}
            checks.append(CheckResult(
                check_name="high_value_claim",
                passed=not is_high_value,
                detail=f"Claimed ₹{submission.claimed_amount} vs threshold ₹{high_value_threshold}",
                rule_source="policy_terms.json > fraud_thresholds > high_value_claim_threshold"
            ))

            # Signal 5: Document alteration
            if extracted:
                for doc_id, raw in extracted.raw_extractions.items():
                    notes = str(raw).lower()
                    if "correction" in notes or "crossed out" in notes or "alteration" in notes:
                        flags.append("DOCUMENT_ALTERATION")
                        flag_details["document_alteration"] = {"document": doc_id}
                        checks.append(CheckResult(
                            check_name="document_alteration", passed=False,
                            detail=f"Possible alteration in {doc_id}",
                            rule_source="document_agent.extractor"
                        ))
                        break

            # Compute fraud score dynamically from policy if available, otherwise fallback to defaults
            policy_weights = policy.get("fraud_weights") or {}
            weights = {
                "SAME_DAY_CLAIM_PATTERN": policy_weights.get("SAME_DAY_CLAIM_PATTERN", 0.4),
                "MULTIPLE_PROVIDERS_SAME_DAY": policy_weights.get("MULTIPLE_PROVIDERS_SAME_DAY", 0.4),
                "MONTHLY_LIMIT_EXCEEDED": policy_weights.get("MONTHLY_LIMIT_EXCEEDED", 0.3),
                "HIGH_VALUE_CLAIM": policy_weights.get("HIGH_VALUE_CLAIM", 0.2),
                "DOCUMENT_ALTERATION": policy_weights.get("DOCUMENT_ALTERATION", 0.3)
            }
            fraud_score = min(1.0, sum(weights.get(f, 0.1) for f in flags))

            auto_review_threshold = thresholds["auto_manual_review_above"]
            fraud_threshold = thresholds["fraud_score_manual_review_threshold"]
            recommend_manual = (
                fraud_score >= fraud_threshold or
                submission.claimed_amount >= auto_review_threshold
            )

            manual_review_reasons = []
            if fraud_score >= fraud_threshold:
                manual_review_reasons.append(f"Fraud score {fraud_score:.2f} exceeds threshold {fraud_threshold}")
            if submission.claimed_amount >= auto_review_threshold:
                manual_review_reasons.append(f"Amount ₹{submission.claimed_amount} exceeds auto-review threshold ₹{auto_review_threshold}")

            fraud_assessment = {
                "fraud_score": fraud_score, "flags": flags, "flag_details": flag_details,
                "recommend_manual_review": recommend_manual, "manual_review_reasons": manual_review_reasons
            }

            confidence_impact = -0.1 * len(flags) if flags else 0.0
            step = self._finish_step(
                ctx, StepStatus.WARNING if flags else StepStatus.PASSED,
                f"Fraud score: {fraud_score:.2f}. Flags: {flags or 'none'}. Manual review: {recommend_manual}",
                checks=checks, errors=[], confidence_impact=confidence_impact
            )
            trace.add_step(step)

            return {"fraud_assessment": fraud_assessment, "trace": trace}

        except Exception as e:
            logger.error(f"FraudAgent failed: {e}", exc_info=True)
            step = self._finish_step(
                ctx, StepStatus.FAILED, f"FraudAgent error: {str(e)}",
                checks=checks, errors=[str(e)], confidence_impact=-0.1
            )
            trace.add_step(step)
            return {
                "fraud_assessment": {"fraud_score": 0.0, "flags": [], "flag_details": {},
                                     "recommend_manual_review": False, "manual_review_reasons": []},
                "degraded": True,
                "failed_agents": (state.get("failed_agents") or []) + ["fraud_agent"],
                "trace": trace
            }
