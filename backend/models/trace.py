from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import time


class StepStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    WARNING = "WARNING"
    DEGRADED = "DEGRADED"


class CheckResult(BaseModel):
    check_name: str
    passed: bool
    expected: Optional[str] = None
    actual: Optional[str] = None
    detail: str
    rule_source: Optional[str] = None  # e.g. "policy_terms.json > waiting_periods > diabetes"


class AgentStep(BaseModel):
    agent_name: str
    node_name: str           # LangGraph node name
    status: StepStatus
    started_at: str
    completed_at: Optional[str] = None
    duration_ms: Optional[float] = None
    input_summary: str
    output_summary: str
    checks_performed: List[CheckResult] = []
    llm_calls: List[Dict[str, Any]] = []   # model, prompt_tokens, completion_tokens, latency_ms
    errors: List[str] = []
    confidence_impact: float = 0.0


class ClaimTrace(BaseModel):
    claim_id: str
    started_at: str
    completed_at: Optional[str] = None
    total_duration_ms: Optional[float] = None
    graph_path: List[str] = []          # ordered list of nodes that executed
    steps: List[AgentStep] = []
    initial_confidence: float = 1.0
    final_confidence: float = 1.0
    confidence_log: List[Dict[str, Any]] = []  # {"after": "agent_name", "delta": -0.2, "reason": "..."}

    def add_step(self, step: AgentStep) -> None:
        self.steps.append(step)
        self.graph_path.append(step.node_name)
        if step.confidence_impact != 0.0:
            self.final_confidence = max(0.0, min(1.0, self.final_confidence + step.confidence_impact))
            self.confidence_log.append({
                "after": step.agent_name,
                "delta": step.confidence_impact,
                "new_confidence": self.final_confidence,
                "reason": step.output_summary
            })

    def to_readable(self) -> str:
        lines = [
            f"CLAIM TRACE — {self.claim_id}",
            f"Duration: {self.total_duration_ms:.0f}ms" if self.total_duration_ms else "Duration: N/A",
            f"Graph path: {' → '.join(self.graph_path)}",
            f"Final confidence: {self.final_confidence:.2f}",
            "=" * 60
        ]
        for step in self.steps:
            lines.append(f"\n[{step.node_name}] {step.agent_name} — {step.status.value}")
            lines.append(f"  Duration: {step.duration_ms:.0f}ms" if step.duration_ms else "  Duration: N/A")
            lines.append(f"  Input:  {step.input_summary}")
            lines.append(f"  Output: {step.output_summary}")
            if step.checks_performed:
                lines.append("  Checks:")
                for c in step.checks_performed:
                    icon = "✓" if c.passed else "✗"
                    lines.append(f"    {icon} {c.check_name}: {c.detail}")
                    if c.rule_source:
                        lines.append(f"      Source: {c.rule_source}")
            if step.errors:
                lines.append(f"  Errors: {', '.join(step.errors)}")
            if step.confidence_impact != 0.0:
                lines.append(f"  Confidence impact: {step.confidence_impact:+.2f}")
        return "\n".join(lines)
