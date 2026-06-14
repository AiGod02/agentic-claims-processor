# Plum Claims Processing System

A production-grade, multi-agent health insurance claims processing system using LangGraph orchestration, Gemini Vision for document processing, and Llama 3.3 70B for policy reasoning.

**Live demo:** https://agentic-claims-processor.onrender.com/
> Hosted on Render free tier — first request may take 30-60s to wake the service.
>
**Demo video:** https://drive.google.com/file/d/1XwWnOy4zSd7fRZq4T8LFmf87V4z_BzrE/view?usp=sharing

**12/12 test cases passing** | **Full execution traces** | **Graceful degradation** | **Sub-second document blocking**

---

## Architecture

```
ClaimSubmission (FastAPI)
        │
        ▼
┌─────────────────────────────────────────────────────┐
│              LANGGRAPH STATE GRAPH                  │
│                                                     │
│  [document_agent]  ──── conditional edge ────►  END │
│       │                (blocking error)             │
│       │ (pass)                                      │
│       ▼                                             │
│  asyncio.gather()                                   │
│  ┌──────────────┐   ┌──────────────┐               │
│  │ policy_agent │   │ fraud_agent  │  (PARALLEL)   │
│  └──────────────┘   └──────────────┘               │
│       │                   │                         │
│       └─────────┬─────────┘                         │
│                 ▼                                   │
│         [decision_agent]                            │
│                 │                                   │
│                 ▼                                   │
│              [END]                                  │
└─────────────────────────────────────────────────────┘
```

---

## Quick Start

### Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set API keys in .env
# GEMINI_API_KEY=your_key_from_aistudio.google.com
# GROQ_API_KEY=your_key_from_console.groq.com

# Run server
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Run Tests

```bash
cd backend

# Unit tests (with freezegun)
python -m pytest tests/test_agents.py -v

# Full eval report (all 12 test cases)
python -m tests.test_cases_runner
```

---

## Key Design Decisions

### 1. Multi-Agent Design via LangGraph
Modular multi-agent system with 4 specialized agents. LangGraph provides clean state transitions, conditional branching (halting early on document errors), and state checkpointing out-of-the-box.

### 2. Parallel Processing (Policy & Fraud Agents)
`PolicyAgent` and `FraudAgent` run in true parallel using `asyncio.gather`. Neither depends on the other's output. Reduces backend latency by ~40-50%.

### 3. Dual LLM Strategy
- **Vision**: `gemini-3.1-flash-lite` — outstanding multimodal performance for messy handwritten prescriptions, phone photos, and stamps on Indian medical bills.
- **Reasoning**: `llama-3.3-70b-versatile` via Groq — ultra-high throughput (>150 tok/s) for near-instant structured JSON policy reasoning.

### 4. Rule-Based Fraud Detection
5 weighted fraud signals (same-day claims, multiple providers, monthly limit, high value, document alteration). 100% deterministic, auditable, and fast (~50ms).

### 5. Structured Trace System
Three-tier observability: `ClaimTrace` → `AgentStep` → `CheckResult`. Every check includes `rule_source` linking back to `policy_terms.json`. Operations team can reconstruct exactly why any claim received any decision.

### 6. Graceful Degradation
Every agent wraps its `run()` in try/except. On failure: degraded result, reduced confidence, trace records the failure. System never crashes.

---

## Test Cases

| ID | Name | Expected |
|----|------|----------|
| TC001 | Wrong Document Uploaded | Block — ask for correct document |
| TC002 | Unreadable Document | Block — ask for re-upload |
| TC003 | Different Patient Names | Block — name mismatch |
| TC004 | Clean Consultation | APPROVED ₹1,350 |
| TC005 | Diabetes Waiting Period | REJECTED |
| TC006 | Dental Partial Approval | PARTIAL ₹8,000 |
| TC007 | MRI Without Pre-Auth | REJECTED |
| TC008 | Per-Claim Limit Exceeded | REJECTED |
| TC009 | Same-Day Fraud Signal | MANUAL_REVIEW |
| TC010 | Network Hospital Discount | APPROVED ₹3,240 |
| TC011 | Component Failure | APPROVED (degraded) |
| TC012 | Excluded Treatment | REJECTED |

---

## Models Used

- **Vision (document processing)**: `gemini-3.1-flash-lite` via Google AI Studio
- **Text/reasoning (policy, fraud, decision)**: `llama-3.3-70b-versatile` via Groq
- **Vision fallback**: `llama-4-scout-17b-16e-instruct` via Groq

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/claims/submit` | Submit a claim |
| GET | `/api/v1/claims/{id}` | Get claim result |
| GET | `/api/v1/claims/{id}/trace` | Get execution trace |
| GET | `/api/v1/claims` | List all claims |
| GET | `/health` | Health check |

---

## Documentation

| Document | Description |
|----------|-------------|
| [architecture.md](./architecture.md) | Full system architecture with component diagrams and data flow |
| [component_contracts.md](./component_contracts.md) | Interface contracts for every component — inputs, outputs, errors |
| [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) | 12 Architecture Decision Records (ADRs) with alternatives considered |
| [TRADE_OFFS.md](./TRADE_OFFS.md) | Every conscious trade-off with rationale |
| [FUTURE_ENHANCEMENTS.md](./FUTURE_ENHANCEMENTS.md) | Production roadmap, scaling to 10M lives, and feature priorities |
| [ASSUMPTIONS_AND_LIMITATIONS.md](./ASSUMPTIONS_AND_LIMITATIONS.md) | All assumptions made and known limitations |
| [TESTING_STRATEGY.md](./TESTING_STRATEGY.md) | Three-tier testing approach and CI/CD recommendations |
| [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) | Annotated file tree with dependency graph |
| [deployment_and_testing_guide.md](./deployment_and_testing_guide.md) | Deployment steps + 12 manual test scenarios |
| [eval/eval_report.md](./eval/eval_report.md) | Full eval report — 12/12 cases with traces |

---

## Date Handling & Testing Environment Safety

- **Production / Live API**: Uses real `date.today()`. Policy validity periods are checked directly against actual calendar dates (with no automatic shifts), meaning expired policies will be correctly rejected as `POLICY_INACTIVE`.
- **Unit Tests**: Uses `freezegun` to freeze time to `2024-11-15` for stable mock assertions.
- **Evaluation Runner**: Dynamic freeze time is set to `treatment_date + 10 days` per case. This ensures that claims (such as TC006) do not fail the 30-day submission deadline.
- **Dynamic Year Shifting**: Enabled ONLY during tests/evaluations (when `PLUM_EVAL_MODE="true"` or `PYTEST_CURRENT_TEST` environment variables are set). It dynamically shifts policy validity periods and member join dates to match the year of the claim's treatment date.

---

## Storage Strategy

For this assessment, the system uses an **in-memory storage layer** ([claims_store.py](./backend/services/claims_store.py)) rather than an external database.

**Why**: Zero-config evaluation. `pip install` → run. No database setup.  
**Production path**: PostgreSQL + SQLAlchemy + Alembic. See [FUTURE_ENHANCEMENTS.md](./FUTURE_ENHANCEMENTS.md).

---

## Financial Calculation Order

**ALWAYS: Network discount FIRST, co-pay AFTER.**

```
TC010: Apollo Hospitals, ₹4500 consultation
  Step 1 — Network discount (20%): 4500 × 0.20 = 900  →  post_discount = 3600
  Step 2 — Co-pay (10%):           3600 × 0.10 = 360  →  approved = 3240
```
