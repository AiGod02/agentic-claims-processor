from abc import ABC, abstractmethod
from models.trace import AgentStep, StepStatus
import time
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    name: str
    node_name: str

    def _start_step(self, input_summary: str) -> dict:
        return {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "input_summary": input_summary,
            "start_time": time.time()
        }

    def _finish_step(
        self,
        ctx: dict,
        status: StepStatus,
        output_summary: str,
        checks: list,
        errors: list,
        confidence_impact: float,
        llm_calls: list = []
    ) -> AgentStep:
        duration_ms = (time.time() - ctx["start_time"]) * 1000
        return AgentStep(
            agent_name=self.name,
            node_name=self.node_name,
            status=status,
            started_at=ctx["started_at"],
            completed_at=datetime.now(timezone.utc).isoformat(),
            duration_ms=duration_ms,
            input_summary=ctx["input_summary"],
            output_summary=output_summary,
            checks_performed=checks,
            llm_calls=llm_calls,
            errors=errors,
            confidence_impact=confidence_impact
        )

    @abstractmethod
    async def run(self, state: dict) -> dict:
        """
        Execute agent logic. Receives state as a dict (TypedDict).
        Returns a dict of ClaimState fields to update.
        Must NEVER raise an unhandled exception — catch everything and return degraded state.
        Must always add a step to the trace before returning.
        """
        ...
