# Architecture — Plum Claims Processing System

## System Overview

A production-grade, multi-agent health insurance claims processing system built with Python (FastAPI backend) and React (Vite frontend). The system automates claim submission, document verification, policy evaluation, fraud detection, and decision synthesis — with full observability via a structured trace system.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CLIENT (React SPA)                             │
│                                                                         │
│  ┌──────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐ │
│  │ClaimForm │  │DecisionView  │  │TraceViewer  │  │GraphVisualizer │ │
│  └─────┬────┘  └──────────────┘  └─────────────┘  └──────────────────┘ │
└────────┼────────────────────────────────────────────────────────────────┘
         │ HTTP (JSON + multipart/form-data)
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       FastAPI APPLICATION                                │
│                                                                         │
│  ┌─────────────────┐  ┌────────────┐  ┌───────────────────────────┐    │
│  │  Routes Layer    │  │  Config    │  │  Services                 │    │
│  │  /api/v1/claims  │  │  .env      │  │  ┌───────────────────┐   │    │
│  │  /health         │  │  settings  │  │  │  gemini_client    │   │    │
│  └────────┬────────┘  └────────────┘  │  │  groq_client      │   │    │
│           │                            │  │  policy_loader    │   │    │
│           ▼                            │  │  claims_store     │   │    │
│  ┌────────────────────────────────┐   │  └───────────────────┘   │    │
│  │    LangGraph State Graph       │   └───────────────────────────┘    │
│  │    (Orchestrator)              │                                     │
│  │                                │                                     │
│  │  ┌──────────────┐             │                                     │
│  │  │document_agent│─────────────┼──► Gemini 2.0 Flash Lite (Vision)   │
│  │  └──────┬───────┘             │                                     │
│  │         │ conditional edge     │                                     │
│  │    ┌────▼────┐ ┌──────────┐  │                                     │
│  │    │exit_early│ │ continue │  │                                     │
│  │    │→ END     │ │          │  │                                     │
│  │    └─────────┘ └────┬─────┘  │                                     │
│  │                     ▼         │                                     │
│  │         asyncio.gather()      │                                     │
│  │    ┌────────────┐ ┌────────┐ │                                     │
│  │    │policy_agent│ │fraud   │ │                                     │
│  │    │            │ │agent   │ │                                     │
│  │    └─────┬──────┘ └───┬────┘ │                                     │
│  │          │   Llama    │ Pure  │                                     │
│  │          │   3.3 70B  │ Rules │                                     │
│  │          └──────┬─────┘      │                                     │
│  │                 ▼             │                                     │
│  │        ┌──────────────┐      │                                     │
│  │        │decision_agent│──────┼──► Llama 3.3 70B via Groq           │
│  │        └──────┬───────┘      │                                     │
│  │               ▼               │                                     │
│  │             [END]             │                                     │
│  └────────────────────────────────┘                                     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### 1. Frontend (React + Vite)

| Component | File | Responsibility |
|---|---|---|
| `ClaimForm` | `components/ClaimForm.jsx` | Multi-step claim submission form with document upload. Collects member ID, category, treatment date, amount, hospital name, and files. |
| `DecisionView` | `components/DecisionView.jsx` | Renders the claim decision with color-coded status (APPROVED/PARTIAL/REJECTED/MANUAL_REVIEW), financial breakdown, line-item decisions, and rejection reasons. |
| `TraceViewer` | `components/TraceViewer.jsx` | Collapsible execution trace showing each agent step, checks performed (✓/✗), LLM calls, confidence impacts, and timing. |
| `GraphVisualizer` | `components/GraphVisualizer.jsx` | Visual representation of the LangGraph execution path with node status indicators (green/red/grey). |
| `App` | `App.jsx` | Root component managing state between form and result views. |

### 2. Backend (FastAPI)

#### Layer 1: API Routes (`routes/`)
- `claims.py` — `POST /api/v1/claims/submit`, `GET /api/v1/claims/{id}`, `GET /api/v1/claims/{id}/trace`, `GET /api/v1/claims`
- `health.py` — `GET /health` — health check endpoint.

#### Layer 2: Graph Orchestrator (`graph/`)
- `orchestrator.py` — Builds and compiles the LangGraph `StateGraph`. Entry point: `process_claim(submission)`.
- `nodes.py` — Wraps agent instances as LangGraph node functions. Implements `parallel_agents_node` with `asyncio.gather`.
- `edges.py` — `route_after_documents()` — conditional routing function.

#### Layer 3: Agents (`agents/`)
- `base.py` — `BaseAgent` ABC with `_start_step()` / `_finish_step()` helper methods for trace recording.
- `document_agent.py` — 3-step pipeline: classify → quality check → extract. Uses Gemini for vision tasks.
- `policy_agent.py` — 12 policy rule checks (member exists, policy active, waiting periods, limits, exclusions, financial calculation).
- `fraud_agent.py` — 5 weighted fraud signals (same-day, multiple providers, monthly limit, high value, document alteration).
- `decision_agent.py` — Synthesizes final decision. Priority: MANUAL_REVIEW > REJECTED > PARTIAL > APPROVED.

#### Layer 4: Models (`models/`)
- `claim.py` — Core Pydantic models: `ClaimSubmission`, `ClaimResult`, `ClassifiedDocument`, `ExtractedClaimData`, enums.
- `state.py` — `ClaimState` TypedDict (LangGraph-compatible shared state).
- `trace.py` — `ClaimTrace`, `AgentStep`, `CheckResult`, `StepStatus` — the full observability data model.
- `policy.py` — Policy-related type definitions.

#### Layer 5: Services (`services/`)
- `gemini_client.py` — Google Gemini API wrapper with retry logic (tenacity), JSON extraction, and metadata tracking.
- `groq_client.py` — Groq API wrapper (Llama 3.3 70B) with retry, JSON extraction, and token usage tracking.
- `policy_loader.py` — Loads and caches `policy_terms.json`.
- `claims_store.py` — In-memory claim storage (Python dict).

---

## Data Flow

### Happy Path (e.g., TC004 — APPROVED)

```
1. Frontend submits ClaimSubmission via POST /api/v1/claims/submit
2. Orchestrator creates ClaimState with claim_id, trace, policy_data
3. document_agent:
   a. Classify documents (test: actual_type bypass / prod: Gemini vision)
   b. Quality check (readability, required doc types)
   c. Extract structured data (patient name, diagnosis, amounts, line items)
   d. Result: document_agent_passed=True, extracted_data populated
4. route_after_documents → "continue"
5. parallel_agents (asyncio.gather):
   a. policy_agent: 12 checks → approved_amount=₹1350, no rejections
   b. fraud_agent: 5 signals → fraud_score=0.0, no flags
6. decision_agent: synthesize → APPROVED, ₹1350, confidence=0.90
7. ClaimResult saved to claims_store, returned to frontend
8. Frontend renders DecisionView + TraceViewer + GraphVisualizer
```

### Early Exit Path (e.g., TC001 — Wrong Document)

```
1. Frontend submits ClaimSubmission
2. document_agent:
   a. Classify documents → [PRESCRIPTION, PRESCRIPTION]
   b. Quality check → HOSPITAL_BILL missing → blocking_error set
3. route_after_documents → "exit_early" → END
4. ClaimResult: decision=None, reason="You submitted [PRESCRIPTION] but a HOSPITAL_BILL is required..."
```

---

## Agent Pipeline Detail

### DocumentAgent (3 Internal Sub-Steps)

```
Input: ClaimState.submission.documents[]

Step 1 — Classification:
  For each document:
    - Test mode: Use document.actual_type directly
    - Production: Send image to Gemini → classify as PRESCRIPTION/HOSPITAL_BILL/etc.
  Output: classified_documents[]

Step 2 — Quality & Integrity:
  - Check required document types present (from policy_terms.json > document_requirements)
  - Check document readability (quality != UNREADABLE)
  - Check patient name consistency across all documents
  - If ANY check fails → set blocking_error, return immediately

Step 3 — Extraction:
  - Test mode: Build ExtractedClaimData from document.content dicts
  - Production: Send documents to Gemini → extract structured JSON
  - Validate patient names match across documents
  Output: extracted_data (ExtractedClaimData)
```

### PolicyAgent (12 Rule Checks)

```
Input: ClaimState.extracted_data + ClaimState.submission + ClaimState.policy_data

Checks (in order):
  1. member_exists — Is member_id in the member roster?
  2. policy_active — Is the policy status ACTIVE and treatment_date within validity period?
  3. submission_deadline — Is the claim within 30 days of treatment?
  4. minimum_claim_amount — Is claimed_amount ≥ ₹500?
  5. initial_waiting_period — Has 30 days passed since member join date?
  6. condition_waiting_periods — Diabetes (90 days), Hypertension (90 days), etc.
  7. exclusions — Is the diagnosis/treatment in the excluded conditions list?
  8. pre_authorization — Does the treatment type require pre-auth above a threshold?
  9. per_claim_limit — Is claimed_amount within per-claim limit for the category?
  10. annual_opd_limit — Is YTD + claimed within annual limit?
  11. network_discount — Apply hospital network discount if applicable
  12. copay — Apply co-pay percentage on post-discount amount

Output: policy_eval dict with rejection_reasons[], final_approved_amount, financial_breakdown
```

### FraudAgent (5 Weighted Signals)

```
Input: ClaimState.submission.claims_history + ClaimState.extracted_data

Signals:
  1. same_day_claims (weight: 0.40) — >2 claims on same treatment date
  2. multiple_providers_same_day (weight: 0.25) — >1 distinct provider on same date
  3. monthly_claims_limit (weight: 0.15) — >6 claims in same calendar month
  4. high_value_claim (weight: 0.10) — claimed_amount > ₹25,000
  5. document_alteration (weight: 0.10) — quality flags from DocumentAgent

Scoring: weighted_sum / max_possible_score × 100
Threshold: fraud_score ≥ 0.60 → recommend_manual_review = True

Output: fraud_assessment dict with fraud_score, flags[], recommend_manual_review
```

### DecisionAgent

```
Input: ClaimState.policy_eval + ClaimState.fraud_assessment

Priority logic:
  1. If fraud → recommend_manual_review → decision = MANUAL_REVIEW
  2. If rejection_reasons not empty → decision = REJECTED
  3. If approved_amount < claimed_amount → decision = PARTIAL
  4. Else → decision = APPROVED

Confidence calculation:
  base = trace.final_confidence
  - If degraded: -0.35
  - If MANUAL_REVIEW: set to 0.5
  - If REJECTED: +0.05 (high confidence in rejection)

Output: decision, approved_amount, reason, confidence_score
```

---

## External Dependencies

| Dependency | Purpose | Version |
|---|---|---|
| FastAPI | Web framework | 0.115.0 |
| LangGraph | Agent orchestration | 0.2.28 |
| Pydantic | Data validation | 2.7.4 |
| Google Generative AI | Gemini API client | 0.8.3 |
| Groq | Llama API client | 0.11.0 |
| Tenacity | Retry logic | 8.2.3 |
| React | Frontend UI | 18.3.1 |
| Vite | Frontend build tool | 5.4.2 |

---

## Key Design Decisions

See [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) for the full ADR catalog.  
See [TRADE_OFFS.md](./TRADE_OFFS.md) for all conscious trade-offs.  
See [FUTURE_ENHANCEMENTS.md](./FUTURE_ENHANCEMENTS.md) for the production roadmap.

---

## Financial Calculation Order

**ALWAYS: Network discount FIRST, co-pay AFTER.**

```
TC010: Apollo Hospitals, ₹4500 consultation
  Step 1 — Network discount (20%): 4500 × 0.20 = 900  →  post_discount = 3600
  Step 2 — Co-pay (10%):           3600 × 0.10 = 360  →  approved = 3240
```

This follows standard Indian health insurance practice where network discounts are institutional agreements that reduce the effective cost, and co-pay is calculated on the reduced amount.
