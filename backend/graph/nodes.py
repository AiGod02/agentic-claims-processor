import asyncio
import copy
from agents.document_agent import DocumentAgent
from agents.policy_agent import PolicyAgent
from agents.fraud_agent import FraudAgent
from agents.decision_agent import DecisionAgent

document_agent = DocumentAgent()
policy_agent = PolicyAgent()
fraud_agent = FraudAgent()
decision_agent_instance = DecisionAgent()


async def document_node(state: dict) -> dict:
    return await document_agent.run(state)


async def parallel_agents_node(state: dict) -> dict:
    """
    Runs policy_agent and fraud_agent in TRUE parallel using asyncio.gather.
    If simulate_component_failure is True, fraud_agent is skipped.
    """
    submission = state["submission"]

    if submission.simulate_component_failure:
        policy_result = await policy_agent.run(state)
        trace = policy_result.get("trace", state["trace"])
        fraud_result = {
            "fraud_assessment": {
                "fraud_score": 0.0, "flags": [], "flag_details": {},
                "recommend_manual_review": False, "manual_review_reasons": []
            },
        }
        return {
            **policy_result,
            **fraud_result,
            "trace": trace,
            "degraded": True,
            "failed_agents": ["fraud_agent"],
        }
    else:
        # Deep copy state so both agents get independent snapshots
        # but share the same trace object for step recording
        state_for_policy = dict(state)
        state_for_fraud = dict(state)

        policy_result, fraud_result = await asyncio.gather(
            policy_agent.run(state_for_policy),
            fraud_agent.run(state_for_fraud)
        )

        # Merge: policy_eval from policy, fraud_assessment from fraud
        merged = {}
        merged["policy_eval"] = policy_result.get("policy_eval")
        merged["fraud_assessment"] = fraud_result.get("fraud_assessment")

        # Merge trace: the trace object is shared by reference
        trace = state["trace"]
        merged["trace"] = trace

        # Merge degradation
        failed = list(set(
            (policy_result.get("failed_agents") or []) +
            (fraud_result.get("failed_agents") or [])
        ))
        merged["failed_agents"] = failed
        merged["degraded"] = (
            policy_result.get("degraded", False) or
            fraud_result.get("degraded", False)
        )

        return merged


async def decision_node(state: dict) -> dict:
    return await decision_agent_instance.run(state)
