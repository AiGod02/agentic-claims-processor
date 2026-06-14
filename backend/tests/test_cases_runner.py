"""
Runs all 12 official test cases against the pipeline.
Generates eval/eval_report.md automatically.
Usage: cd backend && python -m tests.test_cases_runner
"""
import asyncio
import json
import time
from pathlib import Path
from freezegun import freeze_time
from models.claim import ClaimSubmission, UploadedDocument, ClaimCategory, DocumentType, DocumentQuality
from graph.orchestrator import process_claim
from datetime import date


async def run_single_test_case(tc: dict) -> dict:
    """Process a single test case and return results."""
    inp = tc["input"]
    docs = []
    for d in inp.get("documents", []):
        docs.append(UploadedDocument(
            file_id=d["file_id"],
            file_name=d.get("file_name", f"{d['file_id']}.jpg"),
            actual_type=DocumentType(d["actual_type"]) if "actual_type" in d else None,
            quality=DocumentQuality(d["quality"]) if "quality" in d else None,
            patient_name_on_doc=d.get("patient_name_on_doc"),
            content=d.get("content")
        ))

    submission = ClaimSubmission(
        member_id=inp["member_id"],
        policy_id=inp["policy_id"],
        claim_category=ClaimCategory(inp["claim_category"]),
        treatment_date=date.fromisoformat(inp["treatment_date"]),
        claimed_amount=float(inp["claimed_amount"]),
        documents=docs,
        hospital_name=inp.get("hospital_name"),
        ytd_claims_amount=float(inp.get("ytd_claims_amount", 0)),
        claims_history=inp.get("claims_history", []),
        simulate_component_failure=inp.get("simulate_component_failure", False)
    )

    from datetime import timedelta
    treatment_dt = date.fromisoformat(inp["treatment_date"])
    freeze_dt = treatment_dt + timedelta(days=10)
    freeze_str = freeze_dt.isoformat()

    start = time.time()
    try:
        with freeze_time(freeze_str):
            result = await process_claim(submission)
        duration_ms = (time.time() - start) * 1000

        expected = tc["expected"]
        expected_decision = expected.get("decision")
        actual_decision = result.decision.value if result.decision else None
        matched = expected_decision == actual_decision if expected_decision else True

        # Also check expected amount if specified
        if matched and expected.get("approved_amount") is not None:
            if result.approved_amount is not None:
                amount_match = abs(result.approved_amount - expected["approved_amount"]) < 1.0
                if not amount_match:
                    matched = False

        return {
            "case_id": tc["case_id"],
            "case_name": tc["case_name"],
            "expected_decision": expected_decision,
            "actual_decision": actual_decision,
            "matched": matched,
            "expected_amount": expected.get("approved_amount"),
            "actual_amount": result.approved_amount,
            "confidence": result.confidence_score,
            "reason": result.reason,
            "rejection_reasons": result.rejection_reasons,
            "fraud_signals": result.fraud_signals,
            "graph_path": result.graph_path,
            "duration_ms": duration_ms,
            "trace": result.trace.model_dump() if result.trace else {},
            "mismatch_analysis": "" if matched else analyze_mismatch(tc, result)
        }
    except Exception as e:
        return {
            "case_id": tc["case_id"],
            "case_name": tc["case_name"],
            "expected_decision": tc["expected"].get("decision"),
            "actual_decision": "ERROR",
            "matched": False,
            "error": str(e),
            "duration_ms": (time.time() - start) * 1000,
            "mismatch_analysis": f"Pipeline raised exception: {str(e)}"
        }


async def run_all_test_cases():
    with open("test_cases.json") as f:
        test_data = json.load(f)

    results = []

    for tc in test_data["test_cases"]:
        print(f"Running {tc['case_id']}: {tc['case_name']}...")
        result = await run_single_test_case(tc)
        results.append(result)
        print(f"  → {'✅' if result['matched'] else '❌'} {result.get('actual_decision', 'ERROR')}")

        # Rate limit protection
        await asyncio.sleep(1)

    write_eval_report(results)
    passed = sum(1 for r in results if r['matched'])
    total = len(results)
    print(f"\nEval complete. {passed}/{total} matched.")
    return results


def analyze_mismatch(tc: dict, result) -> str:
    expected = tc["expected"]
    lines = [f"Expected: {expected.get('decision')}, Got: {result.decision}"]
    if expected.get("rejection_reasons"):
        lines.append(f"Expected rejection reasons: {expected['rejection_reasons']}")
        lines.append(f"Actual rejection reasons: {result.rejection_reasons}")
    if expected.get("approved_amount"):
        lines.append(f"Expected amount: ₹{expected['approved_amount']}, "
                     f"Got: ₹{result.approved_amount}")
    lines.append(f"Reason: {result.reason}")
    return " | ".join(lines)


def write_eval_report(results: list):
    Path("../eval").mkdir(exist_ok=True)
    lines = [
        "# Plum Claims Processing — Eval Report",
        f"\n**Total cases:** {len(results)}",
        f"**Passed:** {sum(1 for r in results if r['matched'])}",
        f"**Failed:** {sum(1 for r in results if not r['matched'])}",
        "\n---\n"
    ]

    for r in results:
        icon = "✅" if r["matched"] else "❌"
        lines.append(f"## {icon} {r['case_id']} — {r['case_name']}")
        lines.append(f"| Field | Value |")
        lines.append(f"|-------|-------|")
        lines.append(f"| Expected Decision | `{r['expected_decision']}` |")
        lines.append(f"| Actual Decision | `{r['actual_decision']}` |")
        lines.append(f"| Matched | {'Yes' if r['matched'] else 'No'} |")
        if r.get("expected_amount"):
            lines.append(f"| Expected Amount | ₹{r['expected_amount']} |")
        if r.get("actual_amount") is not None:
            lines.append(f"| Actual Amount | ₹{r['actual_amount']} |")
        lines.append(f"| Confidence | {r.get('confidence', 'N/A')} |")
        lines.append(f"| Duration | {r.get('duration_ms', 0):.0f}ms |")
        lines.append(f"| Graph Path | `{' → '.join(r.get('graph_path', []))}` |")
        lines.append(f"\n**Reason:** {r.get('reason', '')}\n")
        if r.get("mismatch_analysis"):
            lines.append(f"**Mismatch Analysis:** {r['mismatch_analysis']}\n")
        if r.get("error"):
            lines.append(f"**Error:** {r['error']}\n")
        if r.get("trace"):
            lines.append("<details><summary>Full Trace (JSON)</summary>\n")
            lines.append(f"```json\n{json.dumps(r['trace'], indent=2, default=str)}\n```\n")
            lines.append("</details>\n")
        lines.append("\n---\n")

    with open("../eval/eval_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("Eval report written to eval/eval_report.md")


if __name__ == "__main__":
    import os
    os.environ["PLUM_EVAL_MODE"] = "true"
    # The production code uses real date.today() — the freeze inside run_single_test_case affects agent execution dates.
    asyncio.run(run_all_test_cases())
