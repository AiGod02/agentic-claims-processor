# Component Contracts — Plum Claims Processing System

> This document defines the precise interface for every significant component. Each contract specifies inputs, outputs, error conditions, and invariants. Another engineer could reimplement any component using only this document.

---

## Table of Contents

1. [API Layer Contracts](#1-api-layer-contracts)
2. [Graph Orchestrator Contract](#2-graph-orchestrator-contract)
3. [DocumentAgent Contract](#3-documentagent-contract)
4. [PolicyAgent Contract](#4-policyagent-contract)
5. [FraudAgent Contract](#5-fraudagent-contract)
6. [DecisionAgent Contract](#6-decisionagent-contract)
7. [ClaimTrace Contract](#7-claimtrace-contract)
8. [Service Layer Contracts](#8-service-layer-contracts)
9. [Data Model Contracts](#9-data-model-contracts)

---

## 1. API Layer Contracts

### POST `/api/v1/claims/submit`

**Input** (multipart/form-data or JSON):
```json
{
  "member_id": "string (required) — e.g., 'EMP001'",
  "policy_id": "string (required) — e.g., 'PLUM_GHI_2024'",
  "claim_category": "enum (required) — CONSULTATION | DIAGNOSTIC | PHARMACY | DENTAL | VISION | ALTERNATIVE_MEDICINE",
  "treatment_date": "date (required) — ISO 8601 format: '2024-11-01'",
  "claimed_amount": "float (required) — must be > 0",
  "documents": "List[UploadedDocument] (required) — at least 1 document",
  "hospital_name": "string (optional) — e.g., 'Apollo Hospitals'",
  "ytd_claims_amount": "float (optional, default: 0.0) — year-to-date approved claims total",
  "claims_history": "List[{claim_id, date, amount, provider}] (optional, default: []) — prior claims for fraud detection",
  "simulate_component_failure": "bool (optional, default: false) — for testing graceful degradation"
}
```

**Output** (`ClaimResult`):
```json
{
  "claim_id": "string — 'CLM_XXXXXXXX'",
  "member_id": "string",
  "treatment_date": "date | null",
  "hospital_name": "string | null",
  "decision": "APPROVED | PARTIAL | REJECTED | MANUAL_REVIEW | null (for blocked claims)",
  "approved_amount": "float | null",
  "claimed_amount": "float",
  "reason": "string — human-readable explanation",
  "confidence_score": "float (0.0 to 1.0)",
  "financial_breakdown": "dict — {claimed, network_discount, post_discount, copay, final_approved}",
  "line_items": "List[{description, claimed_amount, approved_amount, status, reason}]",
  "rejection_reasons": "List[string] — e.g., ['WAITING_PERIOD_DIABETES', 'PER_CLAIM_LIMIT_EXCEEDED']",
  "fraud_signals": "List[string] — e.g., ['SAME_DAY_CLAIM_PATTERN']",
  "manual_review_reasons": "List[string]",
  "degraded": "bool — true if any agent failed",
  "failed_agents": "List[string] — e.g., ['fraud_agent']",
  "graph_path": "List[string] — ordered node names, e.g., ['document_agent', 'policy_agent', 'fraud_agent', 'decision_agent']",
  "trace": "ClaimTrace (see §7) — full execution trace JSON",
  "created_at": "string — ISO 8601 UTC timestamp"
}
```

**Error Responses**:
| Status | Condition | Body |
|---|---|---|
| 422 | Validation error (missing/invalid fields) | `{"detail": [{...}]}` |
| 500 | Unhandled exception | `{"detail": "Internal server error"}` |

**Invariants**:
- `claim_id` is always set (UUID-based, format `CLM_XXXXXXXX`).
- If `decision` is `null`, `reason` contains the blocking error message.
- If `decision` is `APPROVED`, `approved_amount > 0`.
- If `decision` is `REJECTED`, `approved_amount == 0` and `rejection_reasons` is non-empty.
- `confidence_score` is always between 0.0 and 1.0.
- `trace` is always present, even for blocked claims.

---

### GET `/api/v1/claims/{claim_id}`

**Input**: `claim_id` path parameter (string).  
**Output**: `ClaimResult` (same schema as above).  
**Error**: 404 if claim_id not found.

### GET `/api/v1/claims/{claim_id}/trace`

**Input**: `claim_id` path parameter.  
**Output**: `ClaimTrace` JSON (see §7).  
**Error**: 404 if claim_id not found.

### GET `/api/v1/claims`

**Input**: None.  
**Output**: `List[ClaimResult]` — all processed claims, ordered by creation time.

### GET `/health`

**Output**: `{"status": "ok", "version": "1.0.0"}`

---

## 2. Graph Orchestrator Contract

### `process_claim(submission: ClaimSubmission) → ClaimResult`

**Input**: Validated `ClaimSubmission` Pydantic model.

**Processing**:
1. Generate `claim_id` (`CLM_` + 8 hex chars).
2. Load policy data via `load_policy(policy_id)`.
3. Calculate `ytd_claims_amount` from `claims_store` if not provided.
4. Merge `claims_history` from `claims_store` (deduplicates by `claim_id`).
5. Create `ClaimTrace` with `initial_confidence=1.0`.
6. Build `ClaimState` (TypedDict) with all initial values.
7. Execute LangGraph state graph: `await claims_graph.ainvoke(initial_state)`.
8. Extract final state → build `ClaimResult` → save to `claims_store` → return.

**Output**: `ClaimResult` with all fields populated.

**Error Handling**: Never raises. All exceptions are caught and result in a `ClaimResult` with `degraded=True`.

**State Machine**:
```
Entry → document_agent → [route_after_documents] → exit_early → END
                                                  → continue  → parallel_agents → decision_agent → END
```

---

## 3. DocumentAgent Contract

### `DocumentAgent.run(state: dict) → dict`

**Agent Name**: `"DocumentAgent"`  
**Node Name**: `"document_agent"`

**Input**:
- `state["submission"].documents` — `List[UploadedDocument]`
- `state["submission"].claim_category` — `ClaimCategory` enum
- `state["trace"]` — `ClaimTrace` (mutable, steps will be added)

**Output** (dict with keys to merge into `ClaimState`):
```python
{
    "classified_documents": List[ClassifiedDocument],   # always set
    "extracted_data": ExtractedClaimData | None,        # set only if pipeline passes
    "document_agent_passed": bool,                      # True if all checks pass
    "blocking_error": str | None,                       # set if pipeline should halt
    "trace": ClaimTrace,                                # with 1-3 steps added
}
```

**Internal Sub-Steps**:

| Step | Name | Can Block? | Trace Status on Failure |
|---|---|---|---|
| 1. Classification | `document_classification` | No (failures degrade, don't block) | `DEGRADED` |
| 2. Quality & Integrity | `quality_integrity_check` | **Yes** — sets `blocking_error` | `FAILED` |
| 3. Extraction | `data_extraction` | No (failures set empty data) | `DEGRADED` |

**Blocking Conditions** (any triggers `blocking_error` + `document_agent_passed=False`):
1. **Missing required document type**: Required doc types come from `policy_terms.json > document_requirements > {claim_category}`. If submitted doc types don't cover requirements → block.
2. **Unreadable document**: Any document with `quality == UNREADABLE` → block.
3. **Patient name mismatch**: If patient names across documents don't match (fuzzy ratio < 0.8) → block.

**Error Messages** (MUST be specific and actionable):
- Missing doc: `"You submitted ['PRESCRIPTION'] but a HOSPITAL_BILL is required for a CONSULTATION claim. Please upload a HOSPITAL_BILL to proceed."`
- Unreadable: `"Your PHARMACY_BILL (file: blurry_bill.jpg) could not be read clearly. Please re-upload a clearer photo or scan of this document."`
- Name mismatch: `"The patient name on your PRESCRIPTION reads 'Rajesh Kumar' but your HOSPITAL_BILL shows 'Arjun Mehta'. All documents must belong to the same patient."`

**Never raises unhandled exceptions.**

---

## 4. PolicyAgent Contract

### `PolicyAgent.run(state: dict) → dict`

**Agent Name**: `"PolicyAgent"`  
**Node Name**: `"policy_agent"`

**Input**:
- `state["extracted_data"]` — `ExtractedClaimData`
- `state["submission"]` — `ClaimSubmission` (member_id, policy_id, claim_category, treatment_date, claimed_amount, hospital_name, ytd_claims_amount)
- `state["policy_data"]` — `dict` (raw policy_terms.json)
- `state["trace"]` — `ClaimTrace`

**Output**:
```python
{
    "policy_eval": {
        "rejection_reasons": List[str],         # e.g., ["WAITING_PERIOD_DIABETES — eligible from 2024-11-30"]
        "final_approved_amount": float,          # ₹0 if rejected, calculated amount otherwise
        "financial_breakdown": {
            "claimed_amount": float,
            "network_discount": float,           # ₹0 if non-network hospital
            "post_discount_amount": float,
            "copay_amount": float,
            "final_approved": float
        },
        "line_item_decisions": List[{
            "description": str,
            "claimed_amount": float,
            "approved_amount": float,
            "status": "COVERED" | "EXCLUDED",
            "reason": str | None
        }]
    },
    "trace": ClaimTrace  # with 1 step added
}
```

**Checks Performed** (in order, each generates a `CheckResult`):

| # | Check | Source | Can Reject? |
|---|---|---|---|
| 1 | `member_exists` | `policy_terms.json > members` | Yes (`MEMBER_NOT_FOUND`) |
| 2 | `policy_active` | `policy_terms.json > policy_holder` | Yes (`POLICY_INACTIVE`) |
| 3 | `submission_deadline` | `policy_terms.json > submission_rules > deadline_days_from_treatment` | Yes (`LATE_SUBMISSION`) |
| 4 | `minimum_claim_amount` | `policy_terms.json > submission_rules > minimum_claim_amount` | Yes (`BELOW_MINIMUM`) |
| 5 | `initial_waiting_period` | `policy_terms.json > waiting_periods > initial_waiting_period_days` | Yes (`INITIAL_WAITING_PERIOD`) |
| 6 | `condition_waiting_periods` | `policy_terms.json > waiting_periods > specific_conditions` | Yes (`WAITING_PERIOD_DIABETES`, etc.) |
| 7 | `exclusions` | `policy_terms.json > exclusions` | Yes (`EXCLUDED_CONDITION`) |
| 8 | `pre_authorization` | `policy_terms.json > pre_authorization` | Yes (`PRE_AUTH_MISSING`) |
| 9 | `per_claim_limit` | `policy_terms.json > coverage > per_claim_limit` | Yes (`PER_CLAIM_LIMIT_EXCEEDED`) |
| 10 | `annual_opd_limit` | `policy_terms.json > coverage > annual_opd_limit` | Yes (`ANNUAL_LIMIT_EXCEEDED`) |
| 11 | `network_discount` | `policy_terms.json > opd_categories > network_discount_percent` | No (adjusts amount) |
| 12 | `copay` | `policy_terms.json > opd_categories > {category} > copay_percent` | No (adjusts amount) |

**Financial Calculation**:
```
base_amount = min(claimed_amount, per_claim_limit, annual_remaining)
post_discount = base_amount - (base_amount × network_discount_percent)  [if network hospital]
final_approved = post_discount - (post_discount × copay_percent)
```

**Degradation**: On unhandled exception → returns `policy_eval` with `rejection_reasons=[]`, `final_approved_amount=0.0`, and `degraded=True`.

---

## 5. FraudAgent Contract

### `FraudAgent.run(state: dict) → dict`

**Agent Name**: `"FraudAgent"`  
**Node Name**: `"fraud_agent"`

**Input**:
- `state["submission"].claims_history` — `List[{claim_id, date, amount, provider}]`
- `state["submission"].claimed_amount` — `float`
- `state["submission"].treatment_date` — `date`
- `state["submission"].member_id` — `str`
- `state["extracted_data"]` — `ExtractedClaimData` (for document quality signals)
- `state["policy_data"]` — `dict` (fraud thresholds)
- `state["trace"]` — `ClaimTrace`

**Output**:
```python
{
    "fraud_assessment": {
        "fraud_score": float,                    # 0.0 to 1.0
        "flags": List[str],                      # e.g., ["SAME_DAY_CLAIM_PATTERN"]
        "flag_details": {                        # per-flag detail
            "SAME_DAY_CLAIM_PATTERN": "4 claims on 2024-10-30 (threshold: 2)"
        },
        "recommend_manual_review": bool,         # True if fraud_score ≥ 0.60
        "manual_review_reasons": List[str]       # reasons for manual review
    },
    "trace": ClaimTrace  # with 1 step added
}
```

**Fraud Signals**:

| Signal | Key | Weight | Threshold | Source |
|---|---|---|---|---|
| Same-day claims | `SAME_DAY_CLAIM_PATTERN` | 0.40 | >2 claims on same date | `fraud_thresholds.same_day_claims_limit` |
| Multiple providers | `MULTIPLE_PROVIDERS_SAME_DAY` | 0.25 | >1 distinct provider on same date | `fraud_thresholds` |
| Monthly limit | `MONTHLY_CLAIMS_EXCEEDED` | 0.15 | >6 claims in calendar month | `fraud_thresholds.monthly_claims_limit` |
| High value | `HIGH_VALUE_CLAIM` | 0.10 | >₹25,000 | `fraud_thresholds.high_value_claim_threshold` |
| Document alteration | `DOCUMENT_ALTERATION` | 0.10 | Quality flags from DocumentAgent | Quality assessment |

**Scoring Formula**:
```
fraud_score = sum(triggered_signal_weights) / sum(all_signal_weights)
recommend_manual_review = fraud_score ≥ 0.60
```

**No LLM calls.** Pure rule-based computation. Execution time: ~50ms.

---

## 6. DecisionAgent Contract

### `DecisionAgent.run(state: dict) → dict`

**Agent Name**: `"DecisionAgent"`  
**Node Name**: `"decision_agent"`

**Input**:
- `state["policy_eval"]` — `dict` (from PolicyAgent)
- `state["fraud_assessment"]` — `dict` (from FraudAgent)
- `state["submission"]` — `ClaimSubmission`
- `state["degraded"]` — `bool`
- `state["failed_agents"]` — `List[str]`
- `state["trace"]` — `ClaimTrace`

**Output**:
```python
{
    "decision": ClaimDecision,                  # APPROVED | PARTIAL | REJECTED | MANUAL_REVIEW
    "approved_amount": float,                    # from policy_eval.final_approved_amount
    "reason": str,                               # human-readable
    "confidence_score": float,                   # 0.0 to 1.0
    "financial_breakdown": dict,                 # from policy_eval
    "line_items": List[LineItemDecision],         # from policy_eval
    "rejection_reasons": List[str],              # from policy_eval
    "fraud_signals": List[str],                  # from fraud_assessment.flags
    "manual_review_reasons": List[str],          # from fraud_assessment
    "trace": ClaimTrace                          # with 1 step added
}
```

**Decision Priority**:
```
1. If fraud_assessment.recommend_manual_review == True → MANUAL_REVIEW
2. If policy_eval.rejection_reasons is not empty → REJECTED (approved_amount = 0)
3. If approved_amount < claimed_amount and approved_amount > 0 → PARTIAL
4. If approved_amount > 0 → APPROVED
5. Fallback → REJECTED
```

**Confidence Adjustment**:
```
base_confidence = trace.final_confidence (from agent pipeline)
if degraded:       confidence -= 0.35
if MANUAL_REVIEW:  confidence = min(confidence, 0.50)
if REJECTED:       confidence = min(confidence + 0.05, 1.0)
final = clamp(confidence, 0.0, 1.0)
```

---

## 7. ClaimTrace Contract

### Structure

```
ClaimTrace
├── claim_id: str
├── started_at: str (ISO 8601)
├── completed_at: str (ISO 8601)
├── total_duration_ms: float
├── graph_path: List[str]              # ordered node names
├── initial_confidence: float (1.0)
├── final_confidence: float
├── confidence_log: List[{after, delta, new_confidence, reason}]
└── steps: List[AgentStep]
    └── AgentStep
        ├── agent_name: str
        ├── node_name: str
        ├── status: PASSED | FAILED | SKIPPED | WARNING | DEGRADED
        ├── started_at / completed_at: str
        ├── duration_ms: float
        ├── input_summary: str
        ├── output_summary: str
        ├── confidence_impact: float
        ├── llm_calls: List[{model, latency_ms, prompt_tokens, completion_tokens}]
        ├── errors: List[str]
        └── checks_performed: List[CheckResult]
            └── CheckResult
                ├── check_name: str          # e.g., "waiting_period_diabetes"
                ├── passed: bool
                ├── expected: str | null
                ├── actual: str | null
                ├── detail: str              # human-readable explanation
                └── rule_source: str | null  # e.g., "policy_terms.json > waiting_periods > diabetes"
```

### Invariants

1. Every agent **MUST** call `self._start_step()` at start and `self._finish_step()` before returning.
2. Every agent **MUST** call `state["trace"].add_step(step)` to record its execution.
3. Every `CheckResult` **MUST** include a `rule_source` linking back to the policy terms or agent logic.
4. `graph_path` is always consistent with the steps list (same order).
5. `confidence_log` records every non-zero `confidence_impact`.
6. `total_duration_ms` is set by the orchestrator after all agents complete.

---

## 8. Service Layer Contracts

### `call_gemini_vision(image_base64, media_type, prompt) → dict`

**Input**: Base64-encoded image, MIME type, text prompt.  
**Output**: Parsed JSON dict with `_meta: {model, latency_ms}`.  
**Retry**: 3 attempts, exponential backoff (4-15s).  
**Errors**: Raises `ValueError` if JSON cannot be extracted from response.

### `call_groq(prompt, system, temperature) → dict`

**Input**: Text prompt, optional system message, temperature (default 0.1).  
**Output**: Parsed JSON dict with `_meta: {model, latency_ms, prompt_tokens, completion_tokens}`.  
**Retry**: 3 attempts, exponential backoff (2-10s).  
**Model**: `llama-3.3-70b-versatile`.  
**Errors**: Raises `ValueError` if JSON cannot be parsed.

### `load_policy(policy_id) → dict`

**Input**: Policy ID string (e.g., `"PLUM_GHI_2024"`).  
**Output**: Raw dict from `policy_terms.json`.  
**Behavior**: Reads and parses JSON file from `POLICY_FILE_PATH` config. Currently returns the same policy regardless of `policy_id` (single-policy system).

### `claims_store`

**Interface**:
- `save(result: ClaimResult) → None` — stores claim by `claim_id`.
- `get(claim_id: str) → ClaimResult | None` — retrieves by ID.
- `list_all() → List[ClaimResult]` — returns all stored claims.

**Behavior**: In-memory Python dict. Data lost on server restart.

---

## 9. Data Model Contracts

### Enums

| Enum | Values |
|---|---|
| `ClaimCategory` | `CONSULTATION`, `DIAGNOSTIC`, `PHARMACY`, `DENTAL`, `VISION`, `ALTERNATIVE_MEDICINE` |
| `DocumentType` | `PRESCRIPTION`, `HOSPITAL_BILL`, `LAB_REPORT`, `PHARMACY_BILL`, `DENTAL_REPORT`, `DISCHARGE_SUMMARY`, `DIAGNOSTIC_REPORT`, `UNKNOWN` |
| `DocumentQuality` | `GOOD`, `PARTIAL`, `UNREADABLE` |
| `ClaimDecision` | `APPROVED`, `PARTIAL`, `REJECTED`, `MANUAL_REVIEW` |
| `StepStatus` | `PASSED`, `FAILED`, `SKIPPED`, `WARNING`, `DEGRADED` |

### UploadedDocument

```python
{
    "file_id": str,                          # required
    "file_name": str,                        # default ""
    "file_content_base64": str | None,       # raw image data (production mode)
    "actual_type": DocumentType | None,      # test injection — bypasses Gemini classification
    "quality": DocumentQuality | None,       # test injection — bypasses quality check
    "patient_name_on_doc": str | None,       # test injection — for name mismatch tests
    "content": dict | None                   # test injection — structured content for extraction
}
```

### ExtractedClaimData

```python
{
    "patient_name": ExtractedField,          # {value, confidence, note}
    "doctor_name": ExtractedField,
    "doctor_registration": ExtractedField,
    "diagnosis": List[str],
    "treatment_date": ExtractedField,
    "hospital_name": ExtractedField,
    "line_items": List[{description, amount, coverage_status}],
    "total_amount": ExtractedField,
    "extraction_confidence": float,          # 0.0 to 1.0
    "raw_extractions": dict                  # raw LLM outputs for debugging
}
```
